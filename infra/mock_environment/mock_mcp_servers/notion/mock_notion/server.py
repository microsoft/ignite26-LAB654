"""Notion mock MCP server: search, fetch and query, plus page and data-source writes scoped to each conversation."""

from __future__ import annotations

import os

from mockmcp import Clock, ServerSpec

from .common import render_error
from .store import StateStore
from .timeline import now_utc
from .web import build_routes
from .tools import CreatePages, Fetch, QueryDataSources, Search, UpdateDataSource, UpdatePage

NAME = "notion"
VERSION = "1.0.0"
INSTRUCTIONS = (
    "Mock of the Notion MCP server for the LAB654 Ignite lab (Verdantis workspace). Use notion-search to find "
    "pages and databases, notion-fetch to read them (databases return their schema and data source URL), and "
    "notion-query-data-sources to read database rows. Writes (notion-update-page, notion-create-pages, "
    "notion-update-data-source) are kept per conversation: later reads in the same conversation see them, other "
    "conversations don't, and they reset after about 2 hours idle."
)


def build_spec(store: StateStore | None = None, public_base_url: str | None = None) -> ServerSpec:
    """``public_base_url`` (or env PUBLIC_BASE_URL) makes tool results link to this server's own page viewer."""
    if store is None:
        store = StateStore.from_file()
    if public_base_url is None:
        public_base_url = os.environ.get("PUBLIC_BASE_URL") or None
    tools = [cls(store, public_base_url) for cls in
             (Search, Fetch, QueryDataSources, UpdatePage, CreatePages, UpdateDataSource)]
    return ServerSpec(NAME, VERSION, tools, instructions=INSTRUCTIONS, render_error=render_error,
                      clock_factory=lambda: Clock(now_utc()), routes=build_routes(store))
