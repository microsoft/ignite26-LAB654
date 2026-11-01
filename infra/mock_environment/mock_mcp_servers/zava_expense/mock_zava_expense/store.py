"""Seed data plus copy-on-write state per conversation.

Reads come from the conversation's overlay if it has written anything, otherwise from the
shared seed (seed_files/expense_seed.json, built by scripts/build_seed.py). The first write in a conversation deep-copies the
seed into an overlay keyed by the host's ``x-microsoft-ai-conversationid``. Overlays expire
after ``ttl_seconds`` idle and the store keeps at most ``max_entries`` (least recently used
evicted). One conversation never sees another's changes, so lab seats don't collide and
there is nothing to reset between sessions.
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

SEED_PATH = Path(__file__).resolve().parent.parent / "seed_files" / "expense_seed.json"


class StateStore:
    def __init__(self, seed: dict | None = None, ttl_seconds: float = 2 * 3600, max_entries: int = 5000,
                 monotonic: Callable[[], float] = time.monotonic) -> None:
        self._seed = seed if seed is not None else json.loads(SEED_PATH.read_text(encoding="utf-8"))
        self._ttl = ttl_seconds
        self._max = max_entries
        self._now = monotonic
        self._lock = threading.RLock()
        self._overlays: "OrderedDict[str, tuple[float, dict]]" = OrderedDict()

    def seed(self) -> dict:
        """The shared seed. Callers must not mutate it."""
        return self._seed

    def _purge(self) -> None:
        cutoff = self._now() - self._ttl
        while self._overlays:
            key, (touched, _) = next(iter(self._overlays.items()))
            if touched >= cutoff:
                break
            del self._overlays[key]

    def _touch(self, key: str) -> dict | None:
        entry = self._overlays.get(key)
        if entry is None:
            return None
        self._overlays[key] = (self._now(), entry[1])
        self._overlays.move_to_end(key)
        return entry[1]

    def read(self, conversation_id: str | None) -> dict:
        with self._lock:
            self._purge()
            if conversation_id:
                found = self._touch(conversation_id)
                if found is not None:
                    return found
            return self.seed()

    @contextmanager
    def write(self, conversation_id: str | None) -> Iterator[dict]:
        """Yield data to mutate. Without a conversation ID the changes are discarded."""
        with self._lock:
            self._purge()
            if not conversation_id:
                yield copy.deepcopy(self.seed())
                return
            data = self._touch(conversation_id)
            if data is None:
                data = copy.deepcopy(self.seed())
                self._overlays[conversation_id] = (self._now(), data)
                while len(self._overlays) > self._max:
                    self._overlays.popitem(last=False)
            # Apply to a scratch copy so a failed write leaves the overlay untouched.
            scratch = copy.deepcopy(data)
            yield scratch
            self._overlays[conversation_id] = (self._now(), scratch)

    def __len__(self) -> int:
        with self._lock:
            self._purge()
            return len(self._overlays)
