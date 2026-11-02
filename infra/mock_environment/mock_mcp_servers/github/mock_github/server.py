"""GitHub mock MCP server: eight read-only tools of github/github-mcp-server over the zava-lab/aurora-status pull
requests, with a GitHub look-alike viewer next to /mcp."""

from __future__ import annotations

from mockmcp import Clock, InvalidParams, ServerSpec, ToolError

from .store import Store
from .tools import TOOLS, load_schemas
from .web import build_routes

NAME = "github"
VERSION = "1.0.0"
DEFAULT_NOW = "2026-10-29T13:00:00Z"
INSTRUCTIONS = (
    "Mock of the GitHub MCP server with read-only tools. The zava-lab organization has one repository, "
    "zava-lab/aurora-status (Aurora hub status service), with four pull requests and their reviews. Use "
    "search_pull_requests to find pull requests by text such as a Jira key, pull_request_read (methods get, "
    "get_reviews, get_comments, get_review_comments) for details and reviews, and list_pull_requests, "
    "search_repositories, search_users, list_label, get_label and get_me for context. The mock has no write tools "
    "and no diffs, files, commits or check runs."
)


def render_error(error: ToolError, tool: str) -> str:
    if isinstance(error, InvalidParams):
        # The live server reports the first problem, e.g. "missing required parameter: owner".
        issue = error.issues[0] if error.issues else "invalid arguments"
        if "required property" in issue:
            return "missing required parameter: " + issue.split("'")[1] if "'" in issue else issue
        return issue
    return error.message


def build_spec(store: Store | None = None) -> ServerSpec:
    """Tool results link to the viewer at env PUBLIC_BASE_URL (default http://localhost:8000)."""
    if store is None:
        store = Store()
    schemas = load_schemas()
    tools = [cls(store, schemas) for cls in TOOLS]

    def clock_factory() -> Clock:
        return Clock.from_env(default=DEFAULT_NOW)

    return ServerSpec(NAME, VERSION, tools, instructions=INSTRUCTIONS, render_error=render_error,
                      clock_factory=clock_factory, routes=build_routes(store, clock_factory))
