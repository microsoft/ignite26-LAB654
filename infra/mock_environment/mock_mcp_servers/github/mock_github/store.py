"""Seed and per-conversation state for the GitHub mock: one org (zava-lab), one repo (aurora-status) and its pull
requests.

Writes made in a conversation go to that conversation's own copy of the seed, so later reads in the same
conversation see them and other conversations (and the shared lab data) don't.
"""

from __future__ import annotations

import copy
import hashlib
import hmac
import json
import os
import threading
import time
from collections import OrderedDict
from contextlib import contextmanager
from functools import cached_property
from pathlib import Path
from typing import Callable, Iterator

SEED_PATH = Path(__file__).resolve().parent.parent / "seed_files" / "seed.json"
COPILOT_REVIEWER = "copilot-pull-request-reviewer[bot]"
# First IDs handed out for things a conversation creates; well clear of the seed's IDs.
FIRST_IDS = {"issue_comment": 3101000001, "review_comment": 2201000001, "review": 4910000001,
             "reaction": 6101000001, "label": 6}


def base_url() -> str:
    return os.environ.get("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")


def normalise(data: dict) -> dict:
    """Give every pull request the collections the write tools add to."""
    data.setdefault("next_id", dict(FIRST_IDS))
    for repo in data["repos"]:
        for pr in repo["pulls"]:
            for key in ("comments", "review_comments", "threads", "requested_reviewers", "reactions"):
                pr.setdefault(key, [])
            pr.setdefault("maintainer_can_modify", True)
            pr.setdefault("base", repo["default_branch"])
    return data


class Store:
    def __init__(self, path: Path = SEED_PATH, data: dict | None = None) -> None:
        self.data = normalise(data if data is not None else json.loads(path.read_text(encoding="utf-8")))

    @classmethod
    def from_data(cls, data: dict) -> "Store":
        return cls(data=data)

    @cached_property
    def users(self) -> dict[str, dict]:
        return {u["login"]: u for u in self.data["users"]}

    @property
    def org(self) -> dict:
        return self.data["org"]

    @property
    def me(self) -> dict:
        return self.users[self.data["me"]]

    @property
    def repos(self) -> list[dict]:
        return self.data["repos"]

    def user(self, login: str | None) -> dict | None:
        if not login:
            return None
        return next((u for k, u in self.users.items() if k.lower() == login.lower()), None)

    def repo(self, owner: str | None, name: str | None) -> dict | None:
        if not owner or not name:
            return None
        return next((r for r in self.repos
                     if r["owner"].lower() == owner.lower() and r["name"].lower() == name.lower()), None)

    def owner_exists(self, owner: str) -> bool:
        return owner.lower() == self.org["login"].lower() or self.user(owner) is not None

    def next_id(self, kind: str) -> int:
        value = self.data["next_id"][kind]
        self.data["next_id"][kind] = value + 1
        return value


class StateStore:
    """The seed plus one overlay per conversation (x-microsoft-ai-conversationid), kept for ``ttl_seconds`` after
    last use. Keep the app at one replica: overlays live in process memory."""

    def __init__(self, seed: Store | None = None, ttl_seconds: float = 2 * 3600, max_entries: int = 5000,
                 monotonic: Callable[[], float] = time.monotonic, secret: bytes | None = None) -> None:
        self._seed = seed if seed is not None else Store()
        self._ttl = ttl_seconds
        self._max = max_entries
        self._now = monotonic
        self._lock = threading.RLock()
        self._overlays: "OrderedDict[str, tuple[float, Store]]" = OrderedDict()
        # View tokens let a browser open a conversation's copy without knowing its ID: an HMAC of the ID, so they
        # can't be guessed or reversed. The secret is per process unless GITHUB_VIEW_SECRET is set.
        env_secret = os.environ.get("GITHUB_VIEW_SECRET")
        self._secret = secret or (env_secret.encode() if env_secret else os.urandom(32))
        self._tokens: dict[str, str] = {}

    @property
    def seed(self) -> Store:
        return self._seed

    def _purge(self) -> None:
        cutoff = self._now() - self._ttl
        while self._overlays:
            key, (touched, _) = next(iter(self._overlays.items()))
            if touched >= cutoff:
                break
            del self._overlays[key]
            self._tokens.pop(self.view_token(key), None)

    def _touch(self, key: str) -> Store | None:
        entry = self._overlays.get(key)
        if entry is None:
            return None
        self._overlays[key] = (self._now(), entry[1])
        self._overlays.move_to_end(key)
        return entry[1]

    def read(self, conversation_id: str | None) -> Store:
        with self._lock:
            self._purge()
            if conversation_id:
                found = self._touch(conversation_id)
                if found is not None:
                    return found
            return self._seed

    def has_overlay(self, conversation_id: str | None) -> bool:
        with self._lock:
            self._purge()
            return bool(conversation_id) and conversation_id in self._overlays

    @contextmanager
    def write(self, conversation_id: str | None) -> Iterator[Store]:
        """Yield a store to change. Changes are kept only if the block succeeds, and only for a conversation."""
        with self._lock:
            self._purge()
            current = self._touch(conversation_id) if conversation_id else None
            scratch = Store.from_data(copy.deepcopy((current or self._seed).data))
            yield scratch
            if not conversation_id:
                return
            self._overlays[conversation_id] = (self._now(), scratch)
            self._overlays.move_to_end(conversation_id)
            self._tokens[self.view_token(conversation_id)] = conversation_id
            while len(self._overlays) > self._max:
                evicted, _ = self._overlays.popitem(last=False)
                self._tokens.pop(self.view_token(evicted), None)

    def view_token(self, conversation_id: str) -> str:
        return hmac.new(self._secret, conversation_id.encode(), hashlib.sha256).hexdigest()[:20]

    def read_by_token(self, token: str | None) -> tuple[Store, bool]:
        """(store, True) for a live conversation's copy; otherwise (seed, False)."""
        with self._lock:
            self._purge()
            conversation_id = self._tokens.get(token or "")
            if conversation_id:
                found = self._touch(conversation_id)
                if found is not None:
                    return found, True
            return self._seed, False

    def __len__(self) -> int:
        with self._lock:
            self._purge()
            return len(self._overlays)
