"""The tool contract every mock server implements."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

DEFAULT_NOW = "2026-10-16T09:00:00Z"
READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}


@dataclass(frozen=True)
class Clock:
    """The mock's notion of "now".

    Fixed by default so responses are reproducible. Set ``MOCK_NOW`` (ISO 8601) to
    move the whole mock world, e.g. ``MOCK_NOW=2026-11-18T15:00:00Z``.
    """

    now: datetime

    @classmethod
    def from_env(cls, default: str = DEFAULT_NOW) -> "Clock":
        raw = os.environ.get("MOCK_NOW", default)
        return cls(datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc))

    @property
    def today(self):
        return self.now.date()

    def iso(self, millis: bool = True) -> str:
        text = self.now.strftime("%Y-%m-%dT%H:%M:%S")
        return f"{text}.{self.now.microsecond // 1000:03d}Z" if millis else f"{text}Z"


@dataclass(frozen=True)
class CallContext:
    tool: str
    clock: Clock


@dataclass(frozen=True)
class ToolOutput:
    """What a handler returns when it needs more than a plain JSON payload.

    ``payload`` is serialised as the text content. ``structured`` (optional) becomes
    ``structuredContent``. Plain return values are wrapped as ``ToolOutput(value)``.
    """

    payload: Any
    structured: Any | None = None


class Tool(ABC):
    """One MCP tool: identity, published schema and a pure handler.

    Subclasses set ``name``, ``description`` and ``input_schema`` and implement
    ``run``. ``run`` receives arguments that already passed ``input_schema``
    validation (unless ``validate_args`` is False) and either returns a payload or
    raises a ``ToolError``. It must not depend on wall-clock time or global state;
    use ``ctx.clock`` and ``Seeded`` instead.
    """

    name: str
    description: str
    input_schema: dict
    title: str | None = None
    validate_args: bool = True
    annotations: dict = READ_ONLY

    @abstractmethod
    def run(self, args: dict, ctx: CallContext) -> Any | ToolOutput: ...
