"""iManage Work mock MCP server: the 14 traced read tools plus upload_document and create_folder, scoped per
conversation, with a browsable matter viewer next to /mcp."""

from __future__ import annotations

import os

from mockmcp import Clock, ServerSpec

from .common import render_error
from .store import StateStore
from .tools import READ_TOOLS, WRITE_TOOLS, load_schemas
from .web import build_routes

NAME = "imanage"
VERSION = "1.0.0"
DEFAULT_NOW = "2026-10-26T15:00:00Z"
INSTRUCTIONS = (
    "Mock of the iManage Work MCP server (library DEV, one matter workspace). Use search_workspaces or search to "
    "find the workspace, get_container_children or search_folders to browse folders, search to find documents by "
    "keyword, and fetch (or download_document) with a document ID such as DEV!252567.1 to read a document's text. "
    "upload_document and create_folder write only to writable folders. Writes are kept per conversation: later "
    "reads in the same conversation see them, other conversations don't, and they reset after about 2 hours idle."
)


def build_spec(store: StateStore | None = None, public_base_url: str | None = None) -> ServerSpec:
    """``public_base_url`` (or env PUBLIC_BASE_URL) makes tool results link to this server's own matter viewer."""
    if store is None:
        store = StateStore.from_file()
    if public_base_url is None:
        public_base_url = os.environ.get("PUBLIC_BASE_URL") or None
    schemas = load_schemas()
    tools = [cls(store, schemas, public_base_url) for cls in (*READ_TOOLS, *WRITE_TOOLS)]
    return ServerSpec(NAME, VERSION, tools, instructions=INSTRUCTIONS, render_error=render_error,
                      clock_factory=lambda: Clock.from_env(default=DEFAULT_NOW), routes=build_routes(store))
