"""The org plus copy-on-write state per conversation (the iManage mock's pattern).

Reads come from the conversation's overlay if it has written anything, otherwise from the shared seed. The first
write in a conversation deep-copies the seed into an overlay keyed by the host's conversation ID. Overlays expire
after ``ttl`` seconds idle and the store keeps at most ``max_entries`` (least recently used evicted). One
conversation never sees another's overlay. Records created in a conversation are indexed by ID, so a SalesDesk link
the model builds from a new record's ID still opens that conversation's org in the viewer.
"""

from __future__ import annotations

import copy
import hashlib
import hmac
import os
import threading
import time
from collections import OrderedDict
from contextlib import contextmanager
from typing import Callable, Iterator

from .ids import created_id, normalize
from .schema import OBJECTS, PREFIXES, stage_info
from .seed import build_seed
from .timeutil import et_date, parse_date, parse_dt


class Org:
    """Plain-dict org: ``data["objects"][ApiName]`` is a list of records. Mutate through ``StateStore.write``."""

    def __init__(self, data: dict) -> None:
        self.data = data

    @property
    def domain(self) -> str:
        return self.data["domain"]

    @property
    def current_user_id(self) -> str:
        return self.data["current_user"]

    def records(self, obj: str) -> list[dict]:
        return self.data["objects"].setdefault(obj, [])

    def get(self, record_id: str | None) -> tuple[str, dict] | None:
        if not record_id or len(record_id) not in (15, 18):
            return None
        record_id = normalize(record_id)
        obj = PREFIXES.get(record_id[:3])
        if not obj:
            return None
        found = next((r for r in self.records(obj) if r["Id"].lower() == record_id.lower()), None)
        if found is None:
            return None
        return obj, found

    def user(self, uid: str | None) -> dict | None:
        hit = self.get(uid)
        return hit[1] if hit and hit[0] == "User" else None

    def take_id(self, obj: str, conversation_id: str | None) -> str:
        number = self.data["next_created"]
        self.data["next_created"] = number + 1
        new = created_id(OBJECTS[obj]["prefix"], conversation_id, number)
        self.data.setdefault("created", []).append(new)
        return new

    def derive(self) -> None:
        """Recompute the formula and system fields SalesDesk maintains (names, stage-driven flags, AccountId)."""
        for obj in ("User", "Contact", "Lead"):
            for rec in self.records(obj):
                rec["Name"] = " ".join(p for p in (rec.get("FirstName"), rec.get("LastName")) if p)
        for opp in self.records("Opportunity"):
            probability, forecast = stage_info(opp.get("StageName"))
            if opp.get("_probability_set") is None:
                opp["Probability"] = float(probability)
            opp["ForecastCategoryName"] = forecast
            opp["IsClosed"] = str(opp.get("StageName", "")).startswith("Closed")
            opp["IsWon"] = opp.get("StageName") == "Closed Won"
            amount = opp.get("Amount")
            opp["ExpectedRevenue"] = round(amount * opp["Probability"] / 100, 2) if amount is not None else None
            close = parse_date(opp.get("CloseDate"))
            opp["FiscalYear"] = close.year if close else None
            opp["FiscalQuarter"] = (close.month - 1) // 3 + 1 if close else None
        for task in self.records("Task"):
            task["IsClosed"] = task.get("Status") in ("Completed", "Deferred")
            task["IsHighPriority"] = task.get("Priority") == "High"
            task.setdefault("TaskSubtype", "Task")
            task["AccountId"] = self._activity_account(task)
        for event in self.records("Event"):
            start, end = parse_dt(event.get("StartDateTime")), parse_dt(event.get("EndDateTime"))
            event["ActivityDateTime"] = event.get("StartDateTime")
            event["ActivityDate"] = et_date(event.get("StartDateTime")).isoformat() if start else None
            event["EndDate"] = et_date(event.get("EndDateTime")).isoformat() if end else None
            event["DurationInMinutes"] = int((end - start).total_seconds() // 60) if start and end else None
            event["EventSubtype"] = "Event"
            event.setdefault("IsAllDayEvent", False)
            event["AccountId"] = self._activity_account(event)

    def _activity_account(self, activity: dict) -> str | None:
        what = self.get(activity.get("WhatId"))
        if what and what[0] == "Account":
            return what[1]["Id"]
        if what and what[0] == "Opportunity":
            return what[1].get("AccountId")
        who = self.get(activity.get("WhoId"))
        if who and who[0] == "Contact":
            return who[1].get("AccountId")
        return None


class StateStore:
    def __init__(
        self,
        seed: dict | None = None,
        ttl_seconds: float = 2 * 3600,
        max_entries: int = 5000,
        monotonic: Callable[[], float] = time.monotonic,
        secret: bytes | None = None,
    ) -> None:
        self._seed = Org(copy.deepcopy(seed) if seed is not None else build_seed())
        self._seed.derive()
        self._ttl = ttl_seconds
        self._max = max_entries
        self._now = monotonic
        self._lock = threading.RLock()
        self._overlays: "OrderedDict[str, tuple[float, Org]]" = OrderedDict()
        # View tokens let a browser open a conversation's org without knowing its ID. They are an HMAC of the
        # conversation ID, so they can't be guessed or reversed; the secret is per process unless
        # SALESDESK_VIEW_SECRET is set (overlays don't survive a restart either).
        env_secret = os.environ.get("SALESDESK_VIEW_SECRET")
        self._secret = secret or (env_secret.encode() if env_secret else os.urandom(32))
        self._tokens: dict[str, str] = {}
        self._created: dict[str, str] = {}

    @property
    def seed(self) -> Org:
        return self._seed

    def _forget(self, conversation_id: str) -> None:
        self._tokens.pop(self.view_token(conversation_id), None)
        for rid in [k for k, v in self._created.items() if v == conversation_id]:
            del self._created[rid]

    def _purge(self) -> None:
        cutoff = self._now() - self._ttl
        while self._overlays:
            key, (touched, _) = next(iter(self._overlays.items()))
            if touched >= cutoff:
                break
            del self._overlays[key]
            self._forget(key)

    def _touch(self, key: str) -> Org | None:
        entry = self._overlays.get(key)
        if entry is None:
            return None
        self._overlays[key] = (self._now(), entry[1])
        self._overlays.move_to_end(key)
        return entry[1]

    def read(self, conversation_id: str | None) -> Org:
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
    def write(self, conversation_id: str | None) -> Iterator[Org]:
        """Yield an org to mutate. Without a conversation ID the changes are discarded."""
        with self._lock:
            self._purge()
            if not conversation_id:
                scratch = Org(copy.deepcopy(self._seed.data))
                yield scratch
                scratch.derive()
                return
            org = self._touch(conversation_id)
            if org is None:
                org = Org(copy.deepcopy(self._seed.data))
                self._overlays[conversation_id] = (self._now(), org)
                self._tokens[self.view_token(conversation_id)] = conversation_id
                while len(self._overlays) > self._max:
                    evicted, _ = self._overlays.popitem(last=False)
                    self._forget(evicted)
            # Apply to a scratch copy so a failed write leaves the overlay untouched.
            scratch = Org(copy.deepcopy(org.data))
            yield scratch
            scratch.derive()
            org.data = scratch.data
            for rid in org.data.get("created", []):
                self._created[rid] = conversation_id

    def view_token(self, conversation_id: str) -> str:
        return hmac.new(self._secret, conversation_id.encode(), hashlib.sha256).hexdigest()[:20]

    def read_by_token(self, token: str | None) -> tuple[Org, bool]:
        """(org, True) for a live conversation's overlay; otherwise (seed, False)."""
        with self._lock:
            self._purge()
            conversation_id = self._tokens.get(token or "")
            if conversation_id:
                found = self._touch(conversation_id)
                if found is not None:
                    return found, True
            return self._seed, False

    def token_for_record(self, record_id: str) -> str | None:
        """View token of the live conversation that created ``record_id``, if any."""
        with self._lock:
            self._purge()
            conversation_id = self._created.get(normalize(record_id))
            if conversation_id is None and len(record_id) == 15:
                conversation_id = next((c for r, c in self._created.items() if r[:15] == record_id), None)
            return self.view_token(conversation_id) if conversation_id else None

    def __len__(self) -> int:
        with self._lock:
            self._purge()
            return len(self._overlays)
