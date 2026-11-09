"""Rovo mock MCP server: the 41 tools of the Atlassian Rovo MCP server over the Zava Aurora Jira project and
Confluence space, scoped per conversation, with Jira and Confluence look-alike viewers next to /mcp."""

from __future__ import annotations

import json
from pathlib import Path

from mockmcp import Clock, InvalidParams, ServerSpec, ToolError, UiResource, load_html

from .store import StateStore
from .tools import OPENAI_WIDGET_URI, TOOLS, WIDGET_CSP, WIDGET_TOOL_META, WIDGET_URI, JiraError, load_schemas
from .web import build_routes

UI_DIR = Path(__file__).parent / "ui"

NAME = "atlassian"
VERSION = "1.0.0"
DEFAULT_NOW = "2026-10-29T13:00:00Z"
INSTRUCTIONS = (
    "Mock of the Atlassian Rovo MCP server for the zava-online site. Jira holds the Aurora (AUR) project with the "
    "active sprint Aurora Sprint 24. Call getAccessibleAtlassianResources for the cloudId, then use the Jira tools "
    "(searchJiraIssuesUsingJql, getJiraIssue, createJiraIssue, editJiraIssue, transitionJiraIssue, "
    "addCommentToJiraIssue, addWorklogToJiraIssue, createIssueLink). Confluence holds the Aurora Engineering (AUR) "
    "space with the Lakeshore Retail delivery commitments, ADR-014, the sprint plan and the cutover runbook: use "
    "searchConfluenceUsingCql, getConfluencePage and the comment tools, or the Rovo search and fetch tools across both "
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
    """The Jira widget, under both the MCP Apps URI and the OpenAI Apps template URI the live server advertises."""
    html = load_html(UI_DIR, "jira-widget.html")
    return [UiResource(uri, "jira-widget", html, title="Jira", description="Displays Jira issues.", csp=WIDGET_CSP,
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
