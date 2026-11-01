"""Zava Expense mock MCP server: Zava's in-house expense system, for the custom connector scenario."""

from __future__ import annotations

from mockmcp import Clock, ServerSpec

from .store import StateStore
from .tools import TOOLS

NAME = "zava-expense"
VERSION = "1.0.0"
DEFAULT_NOW = "2026-11-16T14:00:00Z"
INSTRUCTIONS = (
    "Mock of Zava Expense, Zava's in-house expense system. The user is Emil Vanggaard. Read expense reports, "
    "card charges, the travel policy and travel spend vs budget; create, update and submit expense reports. "
    "Always confirm with the user before submit_expense_report. Writes are kept per conversation: later reads in "
    "the same conversation see them, other conversations don't, and they reset after about 2 hours idle."
)


def build_spec(store: StateStore | None = None) -> ServerSpec:
    if store is None:
        store = StateStore()
    return ServerSpec(NAME, VERSION, [cls(store) for cls in TOOLS], instructions=INSTRUCTIONS,
                      clock_factory=lambda: Clock.from_env(default=DEFAULT_NOW))
