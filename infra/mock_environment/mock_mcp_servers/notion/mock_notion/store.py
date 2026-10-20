"""Seed workspace plus copy-on-write state per conversation.

Reads come from the conversation's overlay if it has written anything, otherwise
from the shared seed. The first write in a conversation deep-copies the seed into
an overlay keyed by the host's conversation ID. Overlays expire after ``ttl``
seconds idle and the store keeps at most ``max_entries`` (least recently used
evicted). One conversation never sees another's overlay.
"""

from __future__ import annotations

import copy
import json
import threading
import time
from collections import OrderedDict
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Iterator

SEED_PATH = Path(__file__).resolve().parent.parent / "seed_files" / "workspace.json"


class Workspace:
    """Plain-dict workspace with lookup helpers. Mutate through the store's ``write``."""

    def __init__(self, data: dict) -> None:
        self.data = data

    @property
    def pages(self) -> list[dict]:
        return self.data["pages"]

    @property
    def databases(self) -> list[dict]:
        return self.data["databases"]

    def page(self, pid: str) -> dict | None:
        return next((p for p in self.pages if p["id"] == pid), None)

    def database(self, did: str) -> dict | None:
        return next((d for d in self.databases if d["id"] == did), None)

    def data_source(self, cid: str) -> dict | None:
        return next((d for d in self.databases if d["data_source_id"] == cid), None)

    def view(self, vid: str) -> dict | None:
        return next((d for d in self.databases if d["view_id"] == vid), None)

    def row(self, rid: str) -> tuple[dict, dict] | tuple[None, None]:
        for db in self.databases:
            for row in db["rows"]:
                if row["id"] == rid:
                    return db, row
        return None, None

    def title_of(self, oid: str) -> str:
        obj = self.page(oid) or self.database(oid)
        return obj["title"] if obj else ""

    def ancestors(self, parent_id: str | None) -> list[dict]:
        """Nearest first: [{"kind": "page"|"database", "obj": ...}, ...]."""
        chain, seen = [], set()
        while parent_id and parent_id not in seen:
            seen.add(parent_id)
            obj = self.page(parent_id)
            if obj:
                chain.append({"kind": "page", "obj": obj})
            else:
                obj = self.database(parent_id)
                if not obj:
                    break
                chain.append({"kind": "database", "obj": obj})
            parent_id = obj.get("parent_id")
        return chain

    def path(self, parent_id: str | None) -> str:
        return " / ".join(a["obj"]["title"] for a in reversed(self.ancestors(parent_id)))

    def next_seq(self) -> int:
        self.data["_seq"] = self.data.get("_seq", 0) + 1
        return self.data["_seq"]


class StateStore:
    def __init__(
        self,
        seed: dict,
        ttl_seconds: float = 2 * 3600,
        max_entries: int = 5000,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        self._seed = Workspace(seed)
        self._ttl = ttl_seconds
        self._max = max_entries
        self._now = monotonic
        self._lock = threading.RLock()
        self._overlays: "OrderedDict[str, tuple[float, Workspace]]" = OrderedDict()

    @classmethod
    def from_file(cls, path: Path = SEED_PATH, **kwargs) -> "StateStore":
        return cls(json.loads(path.read_text(encoding="utf-8")), **kwargs)

    def _purge(self) -> None:
        cutoff = self._now() - self._ttl
        while self._overlays:
            key, (touched, _) = next(iter(self._overlays.items()))
            if touched >= cutoff:
                break
            del self._overlays[key]

    def _touch(self, key: str) -> Workspace | None:
        entry = self._overlays.get(key)
        if entry is None:
            return None
        self._overlays[key] = (self._now(), entry[1])
        self._overlays.move_to_end(key)
        return entry[1]

    def read(self, conversation_id: str | None) -> Workspace:
        with self._lock:
            self._purge()
            if conversation_id:
                found = self._touch(conversation_id)
                if found is not None:
                    return found
            return self._seed

    @contextmanager
    def write(self, conversation_id: str | None) -> Iterator[Workspace]:
        """Yield a workspace to mutate. Without a conversation ID the changes are discarded."""
        with self._lock:
            self._purge()
            if not conversation_id:
                yield Workspace(copy.deepcopy(self._seed.data))
                return
            ws = self._touch(conversation_id)
            if ws is None:
                ws = Workspace(copy.deepcopy(self._seed.data))
                self._overlays[conversation_id] = (self._now(), ws)
                while len(self._overlays) > self._max:
                    self._overlays.popitem(last=False)
            # Apply to a scratch copy so a failed write leaves the overlay untouched.
            scratch = Workspace(copy.deepcopy(ws.data))
            yield scratch
            ws.data = scratch.data

    def __len__(self) -> int:
        with self._lock:
            self._purge()
            return len(self._overlays)
