"""The Northwind Atlassian site (one Jira project, Northwind Support) and the per-conversation overlay store.

The seed is ``seed_files/seed.json``. Writes made by a conversation go to that conversation's own copy, so later
reads in the same conversation see them and other conversations don't.

Jira issue dates are relative: the seed's ``_anchor`` day is moved to the mock's "today" (``MOCK_NOW``, or the real
date when it's unset), so ticket ages are the same on any rehearsal day. Confluence dates stay fixed. ``{domain}`` in
user emails becomes ``TENANT_EMAIL_DOMAIN``.
"""

from __future__ import annotations

import copy
import hashlib
import hmac
import json
import os
import re
import threading
import time
from collections import OrderedDict
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Iterator

SEED_PATH = Path(__file__).resolve().parent.parent / "seed_files" / "seed.json"
DEFAULT_EMAIL_DOMAIN = "northwind-ltd.example"
_STAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})$")


def mock_today() -> date:
    raw = os.environ.get("MOCK_NOW")
    if raw:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc).date()
    return datetime.now(timezone.utc).date()


def _shift(value: Any, delta: timedelta) -> Any:
    if isinstance(value, dict):
        return {k: _shift(v, delta) for k, v in value.items()}
    if isinstance(value, list):
        return [_shift(v, delta) for v in value]
    if isinstance(value, str) and _STAMP.match(value):
        moved = datetime.fromisoformat(value[:10]) + delta
        return moved.strftime("%Y-%m-%d") + value[10:]
    return value


def build_seed(path: Path = SEED_PATH, today: date | None = None) -> dict:
    domain = os.environ.get("TENANT_EMAIL_DOMAIN") or DEFAULT_EMAIL_DOMAIN
    data = json.loads(path.read_text(encoding="utf-8").replace("{domain}", domain))
    data.pop("_source", None)
    anchor = data.pop("_anchor", None)
    if anchor:
        delta = timedelta(days=((today or mock_today()) - date.fromisoformat(anchor)).days)
        if delta:
            data["issues"] = _shift(data["issues"], delta)
    data.setdefault("created", [])
    data.setdefault("remoteLinks", {})
    data.setdefault("nextIds", {})
    for issue in data["issues"]:
        issue.setdefault("comments", [])
        issue.setdefault("links", [])
        issue.setdefault("worklogs", [])
        issue.setdefault("resolution", None)
        issue.setdefault("parent", None)
        issue.setdefault("components", [])
    wiki = data.setdefault("confluence", {})
    for key in ("spaces", "pages", "comments"):
        wiki.setdefault(key, [])
    for page in wiki["pages"]:
        page.setdefault("parentId", None)
        page.setdefault("labels", [])
        page.setdefault("status", "current")
        page.setdefault("versionMessage", "")
    for comment in wiki["comments"]:
        comment.setdefault("parentId", None)
        comment.setdefault("type", "footer")
        comment.setdefault("version", 1)
    return data


class Site:
    """The site data plus lookup indexes. Call ``derive`` after changing ``data``."""

    def __init__(self, data: dict) -> None:
        self.data = data
        self.derive()

    def derive(self) -> None:
        d = self.data
        self.users = {u["key"]: u for u in d["users"]}
        self.users_by_id = {u["accountId"]: u for u in d["users"]}
        self.issues = {i["key"]: i for i in d["issues"]}
        self.issues_by_id = {i["id"]: i for i in d["issues"]}
        self.statuses = {s["name"]: s for s in d["statuses"]}
        self.statuses_by_id = {s["id"]: s for s in d["statuses"]}
        self.types = {t["name"]: t for t in d["issueTypes"]}
        self.types_by_id = {t["id"]: t for t in d["issueTypes"]}
        self.priorities = {p["name"]: p for p in d["priorities"]}
        self.priorities_by_id = {p["id"]: p for p in d["priorities"]}
        self.sprints = {s["id"]: s for s in d["sprints"]}
        self.link_types = {t["name"]: t for t in d["linkTypes"]}
        wiki = d["confluence"]
        self.spaces = {s["id"]: s for s in wiki["spaces"]}
        self.spaces_by_key = {s["key"].upper(): s for s in wiki["spaces"]}
        self.pages = {p["id"]: p for p in wiki["pages"]}
        self.wiki_comments = {c["id"]: c for c in wiki["comments"]}

    @property
    def project(self) -> dict:
        return self.data["project"]

    @property
    def current_user(self) -> dict:
        return self.users[self.data["currentUser"]]

    def issue(self, ref: str | None) -> dict | None:
        """An issue by key (any case) or numeric id."""
        if not ref:
            return None
        ref = str(ref).strip()
        return self.issues.get(ref.upper()) or self.issues_by_id.get(ref)

    def user(self, ref: str | None) -> dict | None:
        """A user by account ID, key, email or display name."""
        if not ref:
            return None
        ref = str(ref).strip()
        if ref in self.users_by_id:
            return self.users_by_id[ref]
        low = ref.lower()
        for u in self.data["users"]:
            if low in (u["key"], u["email"].lower(), u["displayName"].lower()):
                return u
        return None

    def space(self, ref: str | None) -> dict | None:
        """A Confluence space by numeric ID or key (any case)."""
        if not ref:
            return None
        ref = str(ref).strip()
        return self.spaces.get(ref) or self.spaces_by_key.get(ref.upper())

    def next_id(self, kind: str, start: int) -> str:
        counters = self.data["nextIds"]
        value = counters.get(kind, start)
        counters[kind] = value + 1
        return str(value)

    def next_issue(self) -> tuple[str, str]:
        numbers = [int(i["key"].split("-")[1]) for i in self.data["issues"]]
        number = max(numbers) + 1
        ids = [int(i["id"]) for i in self.data["issues"]]
        return str(max(ids) + 1), f"{self.project['key']}-{number}"


SHARED_KEY = "shared-demo-state"

class StateStore:
    def __init__(
        self,
        seed: dict | None = None,
        ttl_seconds: float = 2 * 3600,
        max_entries: int = 5000,
        monotonic: Callable[[], float] = time.monotonic,
        secret: bytes | None = None,
    ) -> None:
        self._seed = Site(copy.deepcopy(seed) if seed is not None else build_seed())
        self._ttl = ttl_seconds
        self._max = max_entries
        self._now = monotonic
        self._lock = threading.RLock()
        self._overlays: "OrderedDict[str, tuple[float, Site]]" = OrderedDict()
        # View tokens let a browser open a conversation's site without knowing its ID. They are an HMAC of the
        # conversation ID, so they can't be guessed or reversed; the secret is per process unless JIRA_VIEW_SECRET
        # is set (overlays don't survive a restart either).
        env_secret = os.environ.get("JIRA_VIEW_SECRET")
        self._secret = secret or (env_secret.encode() if env_secret else os.urandom(32))
        self._tokens: dict[str, str] = {}
        self._shared = os.environ.get("MOCK_SHARED_STATE", "").lower() in ("1", "true", "yes")
        self._created: dict[str, str] = {}

    @property
    def seed(self) -> Site:
        return self._seed

    def _key(self, conversation_id: str | None) -> str | None:
        """With MOCK_SHARED_STATE=1 every conversation (and header-less calls) shares one overlay, so a demo can
        read in one surface what it wrote in another."""
        return SHARED_KEY if self._shared else conversation_id

    def _forget(self, conversation_id: str) -> None:
        self._tokens.pop(self.view_token(conversation_id), None)
        for key in [k for k, v in self._created.items() if v == conversation_id]:
            del self._created[key]

    def _purge(self) -> None:
        cutoff = self._now() - self._ttl
        while self._overlays:
            key, (touched, _) = next(iter(self._overlays.items()))
            if touched >= cutoff:
                break
            del self._overlays[key]
            self._forget(key)

    def _touch(self, key: str) -> Site | None:
        entry = self._overlays.get(key)
        if entry is None:
            return None
        self._overlays[key] = (self._now(), entry[1])
        self._overlays.move_to_end(key)
        return entry[1]

    def read(self, conversation_id: str | None) -> Site:
        conversation_id = self._key(conversation_id)
        with self._lock:
            self._purge()
            if conversation_id:
                found = self._touch(conversation_id)
                if found is not None:
                    return found
            return self._seed

    def has_overlay(self, conversation_id: str | None) -> bool:
        conversation_id = self._key(conversation_id)
        with self._lock:
            self._purge()
            return bool(conversation_id) and conversation_id in self._overlays

    @contextmanager
    def write(self, conversation_id: str | None) -> Iterator[Site]:
        """Yield a site to mutate. Without a conversation ID the changes are discarded."""
        conversation_id = self._key(conversation_id)
        with self._lock:
            self._purge()
            if not conversation_id:
                scratch = Site(copy.deepcopy(self._seed.data))
                yield scratch
                scratch.derive()
                return
            site = self._touch(conversation_id)
            if site is None:
                site = Site(copy.deepcopy(self._seed.data))
                self._overlays[conversation_id] = (self._now(), site)
                self._tokens[self.view_token(conversation_id)] = conversation_id
                while len(self._overlays) > self._max:
                    evicted, _ = self._overlays.popitem(last=False)
                    self._forget(evicted)
            # Apply to a scratch copy so a failed write leaves the overlay untouched.
            scratch = Site(copy.deepcopy(site.data))
            yield scratch
            scratch.derive()
            site.data = scratch.data
            site.derive()
            for key in site.data.get("created", []):
                self._created[key] = conversation_id

    def view_token(self, conversation_id: str) -> str:
        return hmac.new(self._secret, conversation_id.encode(), hashlib.sha256).hexdigest()[:20]

    def read_by_token(self, token: str | None) -> tuple[Site, bool]:
        """(site, True) for a live conversation's overlay; otherwise (seed, False)."""
        with self._lock:
            self._purge()
            conversation_id = SHARED_KEY if self._shared and not token else self._tokens.get(token or "")
            if conversation_id:
                found = self._touch(conversation_id)
                if found is not None:
                    return found, True
            return self._seed, False

    def token_for_issue(self, key: str) -> str | None:
        """View token of the live conversation that created issue ``key``, if any."""
        with self._lock:
            self._purge()
            conversation_id = self._created.get(key.upper())
            return self.view_token(conversation_id) if conversation_id else None

    def token_for_page(self, page_id: str) -> str | None:
        """View token of the live conversation that created Confluence page ``page_id``, if any."""
        return self.token_for_issue("PAGE:" + page_id)

    def __len__(self) -> int:
        with self._lock:
            self._purge()
            return len(self._overlays)
