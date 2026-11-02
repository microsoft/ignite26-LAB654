"""Jira mock MCP server: the 41 tools of the Atlassian Rovo MCP server over the Zava Aurora project, scoped per
conversation, with a Jira look-alike viewer next to /mcp."""

from __future__ import annotations

import json

from mockmcp import Clock, InvalidParams, ServerSpec, ToolError

from .store import StateStore
from .tools import TOOLS, JiraError, load_schemas
from .web import build_routes

NAME = "jira"
VERSION = "1.0.0"
DEFAULT_NOW = "2026-10-29T13:00:00Z"
INSTRUCTIONS = (
    "Mock of the Atlassian Rovo MCP server for the zava-online site. Jira holds the Aurora (AUR) project with the "
    "active sprint Aurora Sprint 24. Call getAccessibleAtlassianResources for the cloudId, then use the Jira tools "
    "(searchJiraIssuesUsingJql, getJiraIssue, createJiraIssue, editJiraIssue, transitionJiraIssue, "
    "addCommentToJiraIssue, addWorklogToJiraIssue, createIssueLink). The site has no Confluence spaces and no Compass "
    "access. Writes are kept per conversation: later reads in the same conversation see them, other conversations "
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


def build_spec(store: StateStore | None = None) -> ServerSpec:
    """Tool results link to the viewer at env PUBLIC_BASE_URL (default http://localhost:8000)."""
    if store is None:
        store = StateStore()
    schemas = load_schemas()
    tools = [cls(store, schemas) for cls in TOOLS]

    def clock_factory() -> Clock:
        return Clock.from_env(default=DEFAULT_NOW)

    return ServerSpec(NAME, VERSION, tools, instructions=INSTRUCTIONS, render_error=render_error,
                      clock_factory=clock_factory, routes=build_routes(store, clock_factory))
