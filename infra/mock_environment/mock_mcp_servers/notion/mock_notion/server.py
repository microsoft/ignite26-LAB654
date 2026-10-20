"""Notion mock MCP server: search, fetch and query, plus page and data-source writes scoped to each conversation."""

from __future__ import annotations

from mockmcp import Clock, ServerSpec

from .common import render_error
from .store import StateStore
from .tools import CreatePages, Fetch, QueryDataSources, Search, UpdateDataSource, UpdatePage

NAME = "notion"
VERSION = "1.0.0"
TODAY = "2026-10-12T13:00:00Z"
INSTRUCTIONS = (
    "Mock of the Notion MCP server for the LAB654 Ignite lab (Verdantis workspace). Use notion-search to find "
    "pages and databases, notion-fetch to read them (databases return their schema and data source URL), and "
    "notion-query-data-sources to read database rows. Writes (notion-update-page, notion-create-pages, "
    "notion-update-data-source) are kept per conversation: later reads in the same conversation see them, other "
    "conversations don't, and they reset after about 2 hours idle."
)


def build_spec(store: StateStore | None = None) -> ServerSpec:
    if store is None:
        store = StateStore.from_file()
    tools = [Search(store), Fetch(store), QueryDataSources(store), UpdatePage(store), CreatePages(store),
             UpdateDataSource(store)]
    return ServerSpec(NAME, VERSION, tools, instructions=INSTRUCTIONS, render_error=render_error,
                      clock_factory=lambda: Clock.from_env(TODAY))
