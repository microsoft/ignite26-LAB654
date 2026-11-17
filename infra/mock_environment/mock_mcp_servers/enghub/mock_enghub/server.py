"""EngHub mock MCP server: the 41 tools of the EngHub MCP server over the Zava Aurora EngHub project and
EngHub Docs space, scoped per conversation, with EngHub and EngHub Docs look-alike viewers next to /mcp."""

from __future__ import annotations

import json
from pathlib import Path

from mockmcp import Clock, InvalidParams, ServerSpec, ToolError, UiResource, load_html

from .store import StateStore
from .tools import OPENAI_WIDGET_URI, TOOLS, WIDGET_CSP, WIDGET_TOOL_META, WIDGET_URI, JiraError, load_schemas
from .web import build_routes

UI_DIR = Path(__file__).parent / "ui"

NAME = "enghub"
VERSION = "1.0.0"
DEFAULT_NOW = "2026-10-29T13:00:00Z"
INSTRUCTIONS = (
    "Mock of the EngHub MCP server for the zava-online site. EngHub holds the Aurora (AUR) project with the "
    "active sprint Aurora Sprint 24. Call getAccessibleAtlassianResources for the cloudId, then use the EngHub tools "
    "(searchJiraIssuesUsingJql, getJiraIssue, createJiraIssue, editJiraIssue, transitionJiraIssue, "
    "addCommentToJiraIssue, addWorklogToJiraIssue, createIssueLink). EngHub Docs holds the Aurora Engineering (AUR) "
    "space with the Lakeshore Retail delivery commitments, ADR-014, the sprint plan and the cutover runbook: use "
    "searchConfluenceUsingCql, getConfluencePage and the comment tools, or the EngHub search and fetch tools across both "
    "products. There is no Compass access. Writes are kept per conversation: later reads in the same conversation see them, other conversations "
    "don't, and they reset after about 2 hours idle."
)


def render_error(error: ToolError, tool: str) -> str:
    if isinstance(error, JiraError):
        body = error.body
    elif isinstance(error, InvalidParams):
        # Mock-defined wording: the live server's validation text wasn't captured.
        body = {"error": True, "message": f"Invalid arguments for tool {tool}: " + "; ".join(error.issues)}
    else:
        body = {"error": True, "message": error.message}
    return json.dumps(body, ensure_ascii=False, separators=(",", ":"))


def ui_resources() -> list[UiResource]:
    """The EngHub widget, under both the MCP Apps URI and the OpenAI Apps template URI the live server advertises."""
    html = load_html(UI_DIR, "enghub-widget.html")
    return [UiResource(uri, "enghub-widget", html, title="EngHub", description="Displays EngHub issues.", csp=WIDGET_CSP,
                       extra_meta=WIDGET_TOOL_META) for uri in (WIDGET_URI, OPENAI_WIDGET_URI)]


def build_spec(store: StateStore | None = None) -> ServerSpec:
    """Tool results link to the viewer at env PUBLIC_BASE_URL (default http://localhost:8000)."""
    if store is None:
        store = StateStore()
    schemas = load_schemas()
    tools = [cls(store, schemas) for cls in TOOLS]

    def clock_factory() -> Clock:
        return Clock.from_env(default=DEFAULT_NOW)

    return ServerSpec(NAME, VERSION, tools, instructions=INSTRUCTIONS, render_error=render_error,
                      clock_factory=clock_factory, resources=ui_resources(),
                      routes=build_routes(store, clock_factory))
