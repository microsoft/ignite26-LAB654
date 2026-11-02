"""Seed matter plus copy-on-write state per conversation.

Reads come from the conversation's overlay if it has written anything, otherwise from the shared
seed. The first write in a conversation deep-copies the seed into an overlay keyed by the host's
conversation ID. Overlays expire after ``ttl`` seconds idle and the store keeps at most
``max_entries`` (least recently used evicted). One conversation never sees another's overlay.
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
from pathlib import Path
from typing import Callable, Iterator

SEED_PATH = Path(__file__).resolve().parent.parent / "seed_files" / "workspace.json"


class Matter:
    """Plain-dict library (one workspace, its folders and documents). Mutate through ``StateStore.write``."""

    def __init__(self, data: dict) -> None:
        self.data = data

    @property
    def library(self) -> str:
        return self.data["library"]

    @property
    def workspace(self) -> dict:
        return self.data["workspace"]

    @property
    def folders(self) -> list[dict]:
        return self.data["folders"]

    @property
    def documents(self) -> list[dict]:
        return self.data["documents"]

    @property
    def users(self) -> list[dict]:
        return self.data["users"]

    def user(self, uid: str) -> dict | None:
        return next((u for u in self.users if u["id"] == uid), None)

    def folder(self, fid: str) -> dict | None:
        return next((f for f in self.folders if f["id"].lower() == fid.lower()), None)

    def container(self, cid: str) -> dict | None:
        if cid.lower() == self.workspace["id"].lower():
            return self.workspace
        return self.folder(cid)

    def document(self, number: int) -> dict | None:
        return next((d for d in self.documents if d["number"] == number), None)

    def subfolders(self, parent_id: str) -> list[dict]:
        return [f for f in self.folders if f["parent_id"].lower() == parent_id.lower()]

    def descendant_folders(self, parent_id: str) -> list[dict]:
        found, queue = [], [parent_id]
        while queue:
            for child in self.subfolders(queue.pop(0)):
                found.append(child)
                queue.append(child["id"])
        return found

    def documents_in(self, folder_id: str) -> list[dict]:
        return [d for d in self.documents if d["folder_id"].lower() == folder_id.lower()]

    def take_folder_id(self) -> str:
        number = self.data["next_folder"]
        self.data["next_folder"] = number + 1
        return f"Dev!{number}"

    def take_document_number(self) -> int:
        number = self.data["next_document"]
        self.data["next_document"] = number + 1
        return number


class StateStore:
    def __init__(
        self,
        seed: dict,
        ttl_seconds: float = 2 * 3600,
        max_entries: int = 5000,
        monotonic: Callable[[], float] = time.monotonic,
        secret: bytes | None = None,
    ) -> None:
        self._seed = Matter(seed)
        self._ttl = ttl_seconds
        self._max = max_entries
        self._now = monotonic
        self._lock = threading.RLock()
        self._overlays: "OrderedDict[str, tuple[float, Matter]]" = OrderedDict()
        # View tokens let a browser open a conversation's matter without knowing its ID. They are an HMAC of
        # the conversation ID, so they can't be guessed or reversed; the secret is per process unless
        # IMANAGE_VIEW_SECRET is set (overlays don't survive a restart either).
        env_secret = os.environ.get("IMANAGE_VIEW_SECRET")
        self._secret = secret or (env_secret.encode() if env_secret else os.urandom(32))
        self._tokens: dict[str, str] = {}

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
            self._tokens.pop(self.view_token(key), None)

    def _touch(self, key: str) -> Matter | None:
        entry = self._overlays.get(key)
        if entry is None:
            return None
        self._overlays[key] = (self._now(), entry[1])
        self._overlays.move_to_end(key)
        return entry[1]

    def read(self, conversation_id: str | None) -> Matter:
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
    def write(self, conversation_id: str | None) -> Iterator[Matter]:
        """Yield a matter to mutate. Without a conversation ID the changes are discarded."""
        with self._lock:
            self._purge()
            if not conversation_id:
                yield Matter(copy.deepcopy(self._seed.data))
                return
            matter = self._touch(conversation_id)
            if matter is None:
                matter = Matter(copy.deepcopy(self._seed.data))
                self._overlays[conversation_id] = (self._now(), matter)
                self._tokens[self.view_token(conversation_id)] = conversation_id
                while len(self._overlays) > self._max:
                    evicted, _ = self._overlays.popitem(last=False)
                    self._tokens.pop(self.view_token(evicted), None)
            # Apply to a scratch copy so a failed write leaves the overlay untouched.
            scratch = Matter(copy.deepcopy(matter.data))
            yield scratch
            matter.data = scratch.data

    def view_token(self, conversation_id: str) -> str:
        return hmac.new(self._secret, conversation_id.encode(), hashlib.sha256).hexdigest()[:20]

    def read_by_token(self, token: str | None) -> tuple[Matter, bool]:
        """(matter, True) for a live conversation's overlay; otherwise (seed, False)."""
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
