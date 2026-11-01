"""Identifiers, links and result builders shared by the iManage tools.

Shapes follow the recorded Office (Word) trace of the live iManage Work MCP server, with the Office wrapper keys
(entityKey, citationKey, title, snippet, type, id, displayName) removed. The quirks are kept on purpose: workspaces
and folders are ``Dev!<n>`` while documents are ``DEV!<n>.<v>``, ``get_container_children`` pages with camelCase
``hasMore`` while the other tools use ``has_more``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlsplit

from mockmcp import InvalidParams, NotEntitled, ToolError, UpstreamError, dumps

from .store import Matter

DEFAULT_BASE_URL = "http://localhost:8000"
DOC_ID = re.compile(r"^([^!]+)!(\d+)\.(\d+)$")
NOT_FOUND = "The requested resource was not found or you do not have access to it."


@dataclass(frozen=True)
class Links:
    """Where tool results point. ``base`` is the public origin; ``scope`` is ``/v/<token>`` for a conversation."""

    base: str
    scope: str = ""

    @property
    def host(self) -> str:
        return urlsplit(self.base).netloc

    def workspace(self, cid: str) -> str:
        return f"{self.base}{self.scope}/work/link/w/{cid}"

    def folder(self, fid: str) -> str:
        return f"{self.base}{self.scope}/work/link/f/{fid}"

    def document(self, matter: Matter, doc: dict) -> str:
        return f"{self.base}{self.scope}/work/link/d/{doc_id(matter, doc)}"


def doc_id(matter: Matter, doc: dict) -> str:
    return f"{matter.library}!{doc['number']}.{doc['version']}"


def parse_doc_id(value: str) -> tuple[int, int]:
    match = DOC_ID.match(value)
    if not match:
        raise InvalidParams([f"Invalid document id: {value}"])
    return int(match.group(2)), int(match.group(3))


def find_document(matter: Matter, value: str) -> dict:
    number, version = parse_doc_id(value)
    library = value.split("!", 1)[0]
    doc = matter.document(number)
    if doc is None or library.upper() != matter.library or version != doc["version"]:
        raise UpstreamError(NOT_FOUND, 404)
    return doc


def full_file_name(doc: dict) -> str:
    return f"{doc['name']}.{doc['extension']}"


def iwl(links: Links, library: str, number: int, version: int = 1) -> str:
    return f"iwl:dms={links.host}&&lib={library}&&num={number}&&ver={version}"


def user_fields(matter: Matter, key: str, uid: str) -> dict:
    user = matter.user(uid) or {}
    return {
        key: uid,
        f"{key}_description": user.get("full_name", uid),
        f"{key}_info": {"is_external": False, "allow_logon": True},
    }


def workspace_item(matter: Matter, links: Links) -> dict:
    ws = matter.workspace
    url = links.workspace(ws["id"])
    owner = matter.user(ws["owner"]) or {}
    return {
        "basic_properties": f"<span><a href={url}>{ws['name']}</a></span>",
        "create_date": ws["create_date"],
        "database": matter.library,
        "default_security": "private",
        "document_number": ws["document_number"],
        "edit_date": ws["edit_date"],
        "has_subfolders": bool(matter.subfolders(ws["id"])),
        "is_external": False,
        "is_external_as_normal": False,
        "is_hipaa": False,
        "iwl": iwl(links, "Dev", ws["document_number"]),
        "name": ws["name"],
        "owner": ws["owner"],
        "owner_description": owner.get("full_name", ws["owner"]),
        "wstype": "workspace",
        "workspace_url": url,
    }


def workspace_profile(matter: Matter, links: Links) -> dict:
    ws = matter.workspace
    item = workspace_item(matter, links)
    item.update({"id": ws["id"], "description": ws["description"], "custom1_description": ws["client"]})
    return dict(sorted(item.items()))


def folder_item(matter: Matter, links: Links, folder: dict) -> dict:
    return {
        "id": folder["id"],
        "name": folder["name"],
        "wstype": "folder",
        "owner": folder["owner"],
        "folder_type": "regular",
        "has_subfolders": bool(matter.subfolders(folder["id"])),
        "url": links.folder(folder["id"]),
    }


def document_hit(matter: Matter, links: Links, doc: dict) -> dict:
    return {"url": links.document(matter, doc), "name": doc["name"], "wstype": "document", "text": ""}


def document_child(matter: Matter, links: Links, doc: dict) -> dict:
    return {
        "id": doc_id(matter, doc),
        "name": doc["name"],
        "extension": doc["extension"],
        "wstype": "document",
        "edit_date": doc["edit_date"],
        "url": links.document(matter, doc),
    }


def size_label(size: int) -> str:
    return f"{size / 1024:.2f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.2f} MB"


def document_profile(matter: Matter, links: Links, doc: dict) -> dict:
    url = links.document(matter, doc)
    ws = matter.workspace
    profile = {
        "access": "read_write",
        **user_fields(matter, "author", doc["author"]),
        "class": "DOC",
        "class_description": "Document",
        "content_type": "D",
        "create_date": doc["create_date"],
        "database": matter.library,
        "default_security": "private",
        "document_number": doc["number"],
        "document_url": url,
        "edit_date": doc["edit_date"],
        "edit_profile_date": doc["edit_profile_date"],
        "extension": doc["extension"],
        "file_create_date": doc["create_date"],
        "file_edit_date": doc["edit_date"],
        "full_file_name": full_file_name(doc),
        "basic_properties": (
            f"<span><a href={url}>{full_file_name(doc)}</a>&nbsp;({size_label(doc['size'])})</span>"
        ),
        "is_checked_out": False,
        "is_declared": False,
        "is_external": False,
        "is_external_as_normal": False,
        "is_hipaa": False,
        "is_in_use": False,
        "is_latest": True,
        "is_related": False,
        "is_restorable": True,
        "iwl": iwl(links, matter.library, doc["number"], doc["version"]),
        **user_fields(matter, "last_user", doc["author"]),
        "latest": doc_id(matter, doc),
        "name": doc["name"],
        **user_fields(matter, "operator", doc["author"]),
        "retain_days": 10,
        "size": doc["size"],
        "type_description": doc["type_description"],
        "version": doc["version"],
        "workspace_id": ws["id"],
        "workspace_name": ws["name"],
        "wstype": "document",
    }
    return profile


def page(items: list, cursor: str | int | None, limit: int) -> tuple[list, int | None]:
    """Slice by a numeric offset cursor. Returns (page, next_offset or None)."""
    try:
        start = int(cursor or 0)
    except (TypeError, ValueError):
        raise InvalidParams([f"Invalid cursor: {cursor}"]) from None
    if start < 0:
        raise InvalidParams([f"Invalid cursor: {cursor}"])
    chunk = items[start:start + limit]
    end = start + len(chunk)
    return chunk, (end if end < len(items) else None)


def render_error(error: ToolError, tool: str) -> str:
    if isinstance(error, InvalidParams):
        body = {"error": {"status": 400, "message": "Invalid request", "details": error.issues}}
    elif isinstance(error, UpstreamError):
        body = {"error": {"status": error.status, "message": error.message}}
    elif isinstance(error, NotEntitled):
        body = {"error": {"status": 403, "message": error.message}}
    else:
        body = {"error": {"status": 500, "message": error.message}}
    return dumps(body)
