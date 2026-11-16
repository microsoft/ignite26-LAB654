"""Rovo mock MCP server: the 41 tools of the Atlassian Rovo MCP server over the Northwind Support Jira project and
the Customer Success and Product Roadmap Confluence spaces, scoped per conversation, with Jira and Confluence
look-alike viewers next to /mcp."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from mockmcp import Clock, InvalidParams, ServerSpec, ToolError

from .store import StateStore
from .tools import TOOLS, JiraError, load_schemas
from .web import build_routes

NAME = "atlassian"
VERSION = "1.0.0"
INSTRUCTIONS = (
    "Atlassian Rovo MCP server for the northwind-ltd site. Jira holds the Northwind Support (INC) "
    "project: customer incidents, with the customer in a customer-<name> label (customer-contoso is Contoso Ltd; "
    "customer-contoso-pharma is a different customer). Call getAccessibleAtlassianResources for the cloudId, then use "
    "the Jira tools (searchJiraIssuesUsingJql, getJiraIssue, lookupJiraAccountId, editJiraIssue, "
    "addCommentToJiraIssue, transitionJiraIssue, createJiraIssue, createIssueLink). Confluence holds the Customer "
    "Success (CS) space with account overviews and QBR action items, and the Product Roadmap (PROD) space with the "
    "dates approved for customer commitments: use searchConfluenceUsingCql, getConfluencePage and the comment tools, "
    "or the Rovo search and fetch tools across both products. There is no Compass access."
)


def _default_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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
        return Clock.from_env(default=_default_now())

    return ServerSpec(NAME, VERSION, tools, instructions=INSTRUCTIONS, render_error=render_error,
                      clock_factory=clock_factory, routes=build_routes(store, clock_factory))
