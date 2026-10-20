"""IDs, URLs and the Notion error envelope."""

from __future__ import annotations

import contextlib
import contextvars
import hashlib
import json
import re
import uuid
from typing import Iterator

from mockmcp import InvalidParams, ToolError, UpstreamError, dumps

APP = "https://app.notion.com/p/"
_HEX32 = re.compile(r"([0-9a-f]{32})(?![0-9a-f])")
_DASHED = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


def dashed(hex_or_uuid: str) -> str:
    h = hex_or_uuid.replace("-", "").lower()
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


_APP_LINK = re.compile(r"https://(?:app\.notion\.com/p/|(?:www\.)?notion\.so/(?:[\w-]+/)?)(?:[\w-]*?-)?([0-9a-f]{32})")
# Where page links point for the current tool call: the real Notion domain, or this server's own
# page viewer (with the conversation's view token) when PUBLIC_BASE_URL is set.
_LINK_PREFIX: contextvars.ContextVar[str] = contextvars.ContextVar("notion_link_prefix", default=APP)


@contextlib.contextmanager
def link_prefix(prefix: str) -> Iterator[None]:
    token = _LINK_PREFIX.set(prefix)
    try:
        yield
    finally:
        _LINK_PREFIX.reset(token)


def page_url(object_id: str, pvs: bool = False) -> str:
    url = _LINK_PREFIX.get() + object_id.replace("-", "")
    return url + "?pvs=204" if pvs else url


def rewrite_links(text: str, prefix: str | None = None) -> str:
    """Point app.notion.com / notion.so page links in stored content at the current link prefix."""
    target = prefix if prefix is not None else _LINK_PREFIX.get()
    if target == APP:
        return text
    return _APP_LINK.sub(lambda m: target + m.group(1), text)


def parse_ref(ref: str) -> tuple[str, str] | None:
    """``id``/URL/``collection://``/``view://`` -> (kind, dashed uuid). kind is page|collection|view."""
    text = ref.strip().strip("{}").strip().lower()
    kind = "page"
    if text.startswith("collection://"):
        kind, text = "collection", text[len("collection://"):]
    elif text.startswith("view://"):
        kind, text = "view", text[len("view://"):]
    else:
        text = text.split("?", 1)[0].split("#", 1)[0]
    m = _DASHED.search(text)
    if m:
        return kind, m.group(0)
    m = _HEX32.search(text.replace("-", "") if kind != "page" else text)
    if m:
        return kind, dashed(m.group(1))
    return None


def stable_uuid(*parts: str) -> str:
    h = hashlib.sha1("|".join(parts).encode()).hexdigest()
    return f"3ff6c630-c178-81{h[0:2]}-{h[2:6]}-{h[6:18]}"


class NotionError(ToolError):
    """An APIResponseError from the Notion API."""

    def __init__(self, message: str, code: str = "validation_error", status: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.status = status


def not_found(ref: str) -> NotionError:
    return NotionError(
        f"Could not find page or database with ID: {ref}. Make sure the relevant pages and databases are "
        "shared with your integration.",
        code="object_not_found",
        status=404,
    )


def render_error(error: ToolError, tool: str) -> str:
    if isinstance(error, NotionError):
        code, status, message = error.code, error.status, error.message
    elif isinstance(error, InvalidParams):
        code, status, message = "validation_error", 400, "; ".join(error.issues)
    elif isinstance(error, UpstreamError):
        code, status, message = "internal_server_error", error.status, error.message
    else:
        code, status, message = "internal_server_error", 500, error.message
    request_id = str(uuid.UUID(hashlib.md5(f"{tool}|{message}".encode()).hexdigest()))
    if status == 400:
        extra = {"tool_error_code": "invalid_input", "tool_error_class": "validation", "tool_error_retryable": "false"}
    elif status == 404:
        extra = {"tool_error_code": "not_found", "tool_error_class": "validation", "tool_error_retryable": "false"}
    else:
        extra = {"tool_error_code": "internal", "tool_error_class": "server", "tool_error_retryable": "true"}
    body = {"object": "error", "status": status, "code": code, "message": message,
            "additional_data": extra, "request_id": request_id}
    return dumps({
        "name": "APIResponseError",
        "code": code,
        "status": status,
        "headers": {},
        "body": json.dumps(body, ensure_ascii=False, separators=(",", ":")),
        "additional_data": extra,
        "request_id": request_id,
        "message": message,
    })
