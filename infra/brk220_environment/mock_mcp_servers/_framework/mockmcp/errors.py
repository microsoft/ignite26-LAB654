"""Errors a tool handler can raise.

Handlers raise these; the server's ``ErrorRenderer`` turns them into the text the
real upstream server would have returned, so error handling stays out of tool logic.
"""

from __future__ import annotations


class ToolError(Exception):
    """Base class. ``message`` is plain text; renderers decide the final wording."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class InvalidParams(ToolError):
    """The arguments failed validation. ``issues`` holds one line per problem."""

    def __init__(self, issues: list[str]) -> None:
        super().__init__("; ".join(issues))
        self.issues = issues


class UpstreamError(ToolError):
    """The (simulated) upstream API failed, e.g. an HTTP 404 for an unknown code."""

    def __init__(self, message: str, status: int = 500) -> None:
        super().__init__(message)
        self.status = status


class NotEntitled(ToolError):
    """The capability exists upstream but isn't provisioned in this mock environment."""
