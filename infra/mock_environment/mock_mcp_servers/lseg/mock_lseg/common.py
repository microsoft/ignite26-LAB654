"""Pieces every LSEG tool shares: data access, the QA envelope and error wording."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from functools import cached_property
from pathlib import Path
from typing import Any

from mockfin import World
from mockmcp import InvalidParams, JsonStore, NotEntitled, Seeded, ToolError, UpstreamError, dumps, tidy
from mockmcp.tool import CallContext

SEED_DIR = Path(__file__).resolve().parent.parent / "seed_files"


@dataclass
class LsegData:
    """Read-only handle on the shared finance world plus LSEG-specific seed overlays."""

    world: World
    store: JsonStore

    @classmethod
    def default(cls) -> "LsegData":
        return cls(World.default(), JsonStore(SEED_DIR))

    @cached_property
    def gaps(self) -> dict:
        return self.store.view("coverage")["gaps"] if self.store.has("coverage") else {}

    def has_gap(self, ticker: str, kind: str, scope: str, code: str) -> bool:
        return code in self.gaps.get(ticker, {}).get(kind, {}).get(scope, [])


def query_time(ctx: CallContext, *key: Any) -> float:
    """A plausible, deterministic ``qaQueryTime`` (ms) for one request."""
    return tidy(Seeded("lseg", "qaQueryTime").uniform(1800.0, 7600.0, ctx.tool, dumps(list(key))), 4)


def envelope(ctx: CallContext, message: str, *key: Any, success: bool = True) -> dict:
    return {"success": success, "message": message, "timestamp": ctx.clock.iso(), "qaQueryTime": query_time(ctx, *key)}


class Issues:
    """Collects validation problems, then raises them together like the live server."""

    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, issue: str) -> None:
        self.items.append(issue)

    def raise_if_any(self) -> None:
        if self.items:
            raise InvalidParams(self.items)


def render_error(error: ToolError, tool: str) -> str:
    """Match the live LSEG server's error text (the MCP client adds its own prefix)."""
    if isinstance(error, InvalidParams):
        bullets = "\n".join(f"• {issue}" for issue in error.issues)
        return (
            "❌ **Validation Error**\n\nPlease fix the following issues:\n"
            f"{bullets}\n\n**Suggested action**: retry with corrected parameter"
        )
    if isinstance(error, UpstreamError):
        return f"🔧 **Technical Error**\nRequest failed with status code {error.status}"
    if isinstance(error, NotEntitled):
        return f"🔒 **Access Denied**\n{error.message}"
    return error.message


def positive_int(issues: Issues, name: str, value: Any, maximum: int | None = None) -> None:
    """The live server reports both problems when ``count`` arrives as a string."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        issues.add(f"{name} must be a positive number")
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        issues.add(f"{name} must be a positive integer")
    elif maximum is not None and value > maximum:
        issues.add(f"{name} must be less than or equal to {maximum}")


def parse_date(issues: Issues, name: str, value: Any) -> date | None:
    if value in (None, ""):
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        issues.add(f"{name} must be a date in YYYY-MM-DD format")
        return None
