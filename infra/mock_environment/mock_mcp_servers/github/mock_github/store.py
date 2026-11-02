"""Read-only seed for the GitHub mock: one org (zava-lab), one repo (aurora-status) and its pull requests."""

from __future__ import annotations

import json
import os
from functools import cached_property
from pathlib import Path

SEED_PATH = Path(__file__).resolve().parent.parent / "seed_files" / "seed.json"


def base_url() -> str:
    return os.environ.get("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")


class Store:
    """The mock exposes read tools only, so the seed is never changed and needs no per-conversation state."""

    def __init__(self, path: Path = SEED_PATH) -> None:
        self.data = json.loads(path.read_text(encoding="utf-8"))

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
