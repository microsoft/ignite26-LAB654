"""MCP Apps (``io.modelcontextprotocol/ui``) support: HTML widgets bound to tool results.

A tool opts in by setting ``ui_resource`` to a ``ui://`` URI. The server lists that URI in
the tool's ``_meta.ui.resourceUri`` and serves the HTML through ``resources/read`` with the
``text/html;profile=mcp-app`` MIME type. The host renders it in a sandboxed iframe and pushes
the tool's ``CallToolResult`` (including ``structuredContent``) into it over ``postMessage``.

Hosts apply a strict CSP by default (no network, inline scripts and styles only), so widgets
must be single, self-contained HTML documents. ``load_html`` inlines shared files referenced
as ``<!-- include:NAME -->`` so several widgets can share one bridge and component kit.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

UI_MIME_TYPE = "text/html;profile=mcp-app"
UI_EXTENSION_ID = "io.modelcontextprotocol/ui"
_INCLUDE = re.compile(r"<!--\s*include:([\w.\-]+)\s*-->")


@dataclass(frozen=True)
class UiResource:
    uri: str
    name: str
    html: str
    title: str | None = None
    description: str | None = None
    prefers_border: bool = True
    csp: dict[str, list[str]] = field(default_factory=dict)
    # Extra resource ``_meta`` keys (e.g. ``openai/widgetCSP``), deep-merged over the generated ``ui`` key.
    extra_meta: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.uri.startswith("ui://"):
            raise ValueError(f"UI resource URIs must use the ui:// scheme: {self.uri}")

    @property
    def meta(self) -> dict[str, Any]:
        ui: dict[str, Any] = {"prefersBorder": self.prefers_border}
        if self.csp:
            ui["csp"] = self.csp
        return merge_meta({"ui": ui}, self.extra_meta)


def merge_meta(base: dict[str, Any], extra: dict[str, Any] | None) -> dict[str, Any]:
    """Deep-merge ``extra`` into a copy of ``base``; nested dicts merge, other values replace."""
    out = dict(base)
    for key, value in (extra or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = merge_meta(out[key], value)
        else:
            out[key] = value
    return out


def load_html(folder: Path, filename: str) -> str:
    """Read ``folder/filename`` and inline every ``<!-- include:NAME -->`` from the same folder."""
    folder = Path(folder)

    def expand(match: re.Match) -> str:
        return (folder / match.group(1)).read_text(encoding="utf-8")

    return _INCLUDE.sub(expand, (folder / filename).read_text(encoding="utf-8"))
