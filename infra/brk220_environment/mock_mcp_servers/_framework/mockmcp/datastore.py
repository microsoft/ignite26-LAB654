"""Read-only JSON data layer.

Every mock server keeps its data as JSON files in a folder (usually ``seed_files/``).
``JsonStore`` loads them lazily, caches them and hands out deep copies so a handler
can never mutate shared state by accident.
"""

from __future__ import annotations

import copy
import json
from functools import cached_property
from pathlib import Path
from typing import Any


class JsonStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self._cache: dict[str, Any] = {}

    def _load(self, name: str) -> Any:
        if name not in self._cache:
            path = self.root / f"{name}.json"
            if not path.is_file():
                raise FileNotFoundError(f"Seed file not found: {path}")
            with path.open(encoding="utf-8") as handle:
                self._cache[name] = json.load(handle)
        return self._cache[name]

    def get(self, name: str) -> Any:
        """Return a private copy of ``<root>/<name>.json``."""
        return copy.deepcopy(self._load(name))

    def view(self, name: str) -> Any:
        """Return the cached object without copying. Callers must not mutate it."""
        return self._load(name)

    def has(self, name: str) -> bool:
        return (self.root / f"{name}.json").is_file()

    @cached_property
    def names(self) -> list[str]:
        return sorted(p.stem for p in self.root.glob("*.json"))
