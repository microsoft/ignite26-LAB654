"""Salesforce mock MCP server: the five Salesforce Hosted MCP tools (describe, discover, dispatch,
dispatch_readonly, display_widget) over a small Northwind Ltd org, scoped per conversation, with a Lightning look-alike
viewer next to /mcp."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from mockmcp import Clock, InvalidParams, NotEntitled, ServerSpec, ToolError, UiResource, UpstreamError, load_html

from .store import StateStore
from .tools import TOOLS, load_schemas
from .web import build_routes
from .widget import RESOURCE_URI

NAME = "salesforce"
VERSION = "1.0.0"

UI_DIR = Path(__file__).parent / "ui"
INSTRUCTIONS = (
    "Salesforce Hosted MCP server for the Northwind Ltd org (Sales Cloud). The signed-in user is Megan Bowen. Contoso Ltd and Contoso Pharmaceuticals are different accounts. Use discover to find REST, SOQL or "
    "GraphQL capabilities, describe for a capability's details, dispatch_readonly for reads (SOQL queries, sObject "
    "reads, GraphQL, search) and dispatch for writes (create, update, delete). display_widget renders a dynamic "
    "widget definition."
)


def render_error(error: ToolError, tool: str) -> str:
    if isinstance(error, InvalidParams):
        body = [{"errorCode": "INVALID_INPUT", "message": "; ".join(error.issues)}]
    elif isinstance(error, NotEntitled):
        body = [{"errorCode": "INSUFFICIENT_ACCESS", "message": error.message}]
    elif isinstance(error, UpstreamError):
        body = [{"errorCode": "UNKNOWN_EXCEPTION", "message": error.message, "statusCode": error.status}]
    else:
        body = [{"errorCode": "UNKNOWN_EXCEPTION", "message": error.message}]
    return json.dumps(body, ensure_ascii=False, separators=(",", ":"))


def ui_resources() -> list[UiResource]:
    return [UiResource(RESOURCE_URI, "salesforce-widget-renderer", load_html(UI_DIR, "widget.html"),
                       title="Salesforce widget", description="Renders a dynamic Salesforce widget definition.")]


def build_spec(store: StateStore | None = None) -> ServerSpec:
    """Tool results link to the viewer at env PUBLIC_BASE_URL (default http://localhost:8000)."""
    if store is None:
        store = StateStore()
    schemas = load_schemas()
    tools = [cls(store, schemas) for cls in TOOLS]

    def clock_factory() -> Clock:
        return Clock.from_env(default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    return ServerSpec(NAME, VERSION, tools, instructions=INSTRUCTIONS, render_error=render_error,
                      clock_factory=clock_factory, resources=ui_resources(),
                      routes=build_routes(store, clock_factory))
