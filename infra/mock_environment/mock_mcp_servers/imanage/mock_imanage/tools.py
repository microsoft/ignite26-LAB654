"""The 14 traced iManage Work tools plus two inferred write tools (upload_document, create_folder).

Read-tool names, descriptions and input schemas are loaded verbatim from ``seed_files/tool_schemas.json`` (built by
``scripts/build_seed.py`` from the recorded trace). Result shapes follow the trace where it shows them and are
inferred elsewhere; see the README for which is which.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from mockmcp import CallContext, InvalidParams, Tool, UpstreamError

from .common import (
    DEFAULT_BASE_URL,
    NOT_FOUND,
    Links,
    doc_id,
    document_child,
    document_hit,
    document_profile,
    find_document,
    folder_item,
    full_file_name,
    page,
    workspace_item,
    workspace_profile,
)
from .store import Matter, StateStore

SCHEMAS_PATH = Path(__file__).resolve().parent.parent / "seed_files" / "tool_schemas.json"
FETCH_CHUNK = 150_000  # characters per fetch/download_document page (the live limit isn't known)
SEARCH_PAGE = 25
MAX_CHILDREN = 500
UPLOAD_LIMIT = 128 * 1024
WRITE = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False}
_WORD = re.compile(r"\w+")


def load_schemas(path: Path = SCHEMAS_PATH) -> dict[str, dict]:
    return {t["name"]: t for t in json.loads(path.read_text(encoding="utf-8"))}


def _words(text: str) -> set[str]:
    return set(_WORD.findall(text.lower()))


def _matches_all(query: str, *fields: str) -> bool:
    terms = _WORD.findall(query.lower())
    haystack = _words(" ".join(f or "" for f in fields))
    return bool(terms) and all(t in haystack for t in terms)


def _contains(value: str | None, needle: str | None) -> bool:
    return not needle or needle.lower() in (value or "").lower()


def _folder_name_matches(pattern: str, name: str) -> bool:
    for part in (p.strip() for p in pattern.split(",")):
        if part and re.fullmatch(".*".join(map(re.escape, part.split("*"))), name, re.IGNORECASE):
            return True
    return False


class IManageTool(Tool):
    """Base: binds the store and the public base URL, and resolves per-call links."""

    traced = True

    def __init__(self, store: StateStore, schemas: dict[str, dict], public_base_url: str | None = None) -> None:
        self.store = store
        self.base = (public_base_url or DEFAULT_BASE_URL).rstrip("/")
        if self.traced:
            spec = schemas[self.name]
            self.description = spec["description"]
            self.input_schema = spec["inputSchema"]

    def links(self, ctx: CallContext) -> Links:
        scope = f"/v/{self.store.view_token(ctx.conversation_id)}" if ctx.conversation_id else ""
        return Links(self.base, scope)

    def run(self, args: dict, ctx: CallContext) -> Any:
        return self.handle(self.store.read(ctx.conversation_id), self.links(ctx), args, ctx)

    def handle(self, matter: Matter, links: Links, args: dict, ctx: CallContext) -> Any:
        raise NotImplementedError


def _check_library(matter: Matter, library: str | None) -> None:
    if library and library.upper() != matter.library:
        raise UpstreamError(f"Library '{library}' was not found or you do not have access to it.", 404)


def _text_page(matter: Matter, links: Links, doc: dict, cursor: str | None) -> dict:
    text = doc["text"]
    try:
        start = int(cursor or 0)
    except ValueError:
        raise InvalidParams([f"Invalid cursor: {cursor}"]) from None
    if start < 0 or (start and start >= len(text)):
        raise InvalidParams([f"Invalid cursor: {cursor}"])
    end = min(start + FETCH_CHUNK, len(text))
    metadata: dict = {"has_more": end < len(text)}
    if end < len(text):
        metadata["cursor"] = str(end)
    return {"title": full_file_name(doc), "url": links.document(matter, doc), "text": text[start:end],
            "metadata": metadata}


# --- traced read tools --------------------------------------------------------------------------------------------


class GetDocumentProfile(IManageTool):
    name = "get_document_profile"

    def handle(self, matter, links, args, ctx):
        return document_profile(matter, links, find_document(matter, args["documentId"]))


class GetWorkspaceProfile(IManageTool):
    name = "get_workspace_profile"

    def handle(self, matter, links, args, ctx):
        if args["workspaceId"].lower() != matter.workspace["id"].lower():
            raise UpstreamError(NOT_FOUND, 404)
        return workspace_profile(matter, links)


class DownloadDocument(IManageTool):
    name = "download_document"

    def handle(self, matter, links, args, ctx):
        return _text_page(matter, links, find_document(matter, args["documentId"]), args.get("cursor"))


class Fetch(IManageTool):
    name = "fetch"

    def handle(self, matter, links, args, ctx):
        return _text_page(matter, links, find_document(matter, args["id"]), args.get("cursor"))


class GetLibraries(IManageTool):
    name = "get_libraries"

    def handle(self, matter, links, args, ctx):
        return {"items": [{"id": matter.library, "name": matter.library, "type": "worksite", "is_preferred": True}]}


class GetRecentDocuments(IManageTool):
    name = "get_recent_documents"

    def handle(self, matter, links, args, ctx):
        f = args.get("filters") or {}
        ws = matter.workspace
        docs = [
            d for d in matter.documents
            if _contains(ws["client"], f.get("custom1")) and _contains(ws["name"], f.get("custom2"))
            and _contains(d.get("comment"), f.get("comments"))
            and (not f.get("anywhere") or _matches_all(f["anywhere"], d["name"], d.get("comment", ""), d["text"]))
            and (not f.get("create_date_from") or d["create_date"] >= f["create_date_from"])
            and (not f.get("create_date_to") or d["create_date"] <= f["create_date_to"])
        ]
        docs.sort(key=lambda d: (d["edit_date"], d["number"]), reverse=True)
        chunk, nxt = page(docs, args.get("cursor"), args.get("limit", 100))
        out: dict = {"has_more": nxt is not None}
        if nxt is not None:
            out["cursor"] = str(nxt)
        out["items"] = [document_profile(matter, links, d) for d in chunk]
        return out


class GetRecentWorkspaces(IManageTool):
    name = "get_recent_workspaces"

    def handle(self, matter, links, args, ctx):
        f = args.get("filters") or {}
        ws = matter.workspace
        hit = (_contains(ws["client"], f.get("custom1")) and _contains(ws["name"], f.get("custom2"))
               and (_contains(ws["name"], f.get("name_or_description"))
                    or _contains(ws["description"], f.get("name_or_description"))))
        chunk, nxt = page([ws] if hit else [], args.get("cursor"), args.get("limit", 100))
        return {"has_more": nxt is not None, "items": [workspace_item(matter, links) for _ in chunk]}


class GetUserInformation(IManageTool):
    name = "get_user_information"

    def handle(self, matter, links, args, ctx):
        _check_library(matter, args.get("libraryId"))
        query = (args.get("query") or "").strip().lower()
        if not query:
            users = [matter.user(matter.data["current_user"])]
        else:
            users = [u for u in matter.users
                     if query in u["id"].lower() or query in u["full_name"].lower() or query in u["email"].lower()]
        return {"has_more": False, "items": [
            {"id": u["id"], "full_name": u["full_name"], "email": u["email"], "job_title": u["job_title"],
             "preferred_library": matter.library, "is_external": False, "allow_logon": True}
            for u in users
        ]}


class Search(IManageTool):
    name = "search"

    def handle(self, matter, links, args, ctx):
        _check_library(matter, args.get("libraryId"))
        query = args["query"]
        ws = matter.workspace
        hits: list[dict] = []
        if _matches_all(query, ws["name"], ws["description"]):
            item = workspace_item(matter, links)
            hits.append({"url": item["workspace_url"], "name": ws["name"], "wstype": "workspace", "text": ""})
        docs = [d for d in matter.documents
                if _matches_all(query, d["name"], d.get("comment", ""), d.get("doc_type", ""), d["text"])]
        docs.sort(key=lambda d: (not _matches_all(query, d["name"]), d["number"]))
        hits += [document_hit(matter, links, d) for d in docs]
        chunk, nxt = page(hits, args.get("cursor"), SEARCH_PAGE)
        out: dict = {"has_more": nxt is not None}
        if nxt is not None:
            out["cursor"] = str(nxt)
        out["items"] = chunk
        return out


class GetWorkspaceTemplates(IManageTool):
    name = "get_workspace_templates"

    def handle(self, matter, links, args, ctx):
        _check_library(matter, args.get("libraryId"))
        return {"has_more": False, "items": []}


class SearchWorkspaces(IManageTool):
    name = "search_workspaces"

    def handle(self, matter, links, args, ctx):
        p = args["searchParams"]
        ws = matter.workspace
        owner = matter.user(ws["owner"]) or {}
        hit = (
            _contains(ws["name"], p.get("name"))
            and (_contains(ws["owner"], p.get("owner")) or _contains(owner.get("full_name"), p.get("owner")))
            and _contains(ws["description"], p.get("description"))
            and _contains(ws["client"], p.get("custom1"))
            and _contains(ws["name"], p.get("custom2"))
            and not p.get("subclass")
            and (not p.get("anywhere") or any(_contains(v, p["anywhere"]) for v in
                                               (ws["name"], ws["description"], ws["client"], ws["owner"])))
        )
        chunk, nxt = page([ws] if hit else [], p.get("cursor") or args.get("cursor"), args.get("limit", 100))
        out: dict = {}
        if chunk:
            out.update(topMatchingId=ws["id"], topMatchingName=ws["name"])
        out["has_more"] = nxt is not None
        out["items"] = [workspace_item(matter, links) for _ in chunk]
        return out


class SearchFolders(IManageTool):
    name = "search_folders"

    def handle(self, matter, links, args, ctx):
        container = matter.container(args["container_id"])
        if container is None:
            raise UpstreamError(NOT_FOUND, 404)
        found = [f for f in matter.descendant_folders(container["id"])
                 if _folder_name_matches(args["name"], f["name"])]
        chunk, nxt = page(found, args.get("cursor"), args.get("limit", 100))
        out: dict = {"has_more": nxt is not None}
        if nxt is not None:
            out["cursor"] = str(nxt)
        out["items"] = [folder_item(matter, links, f) for f in chunk]
        return out


class GetContainerChildren(IManageTool):
    name = "get_container_children"

    def handle(self, matter, links, args, ctx):
        cid, ctype = args["container_id"], args["container_type"]
        is_workspace = cid.lower() == matter.workspace["id"].lower()
        if (ctype == "workspace") != is_workspace or matter.container(cid) is None:
            raise UpstreamError(NOT_FOUND, 404)
        children = [folder_item(matter, links, f) for f in matter.subfolders(cid)]
        children += [document_child(matter, links, d) for d in matter.documents_in(cid)]
        start = args.get("cursor") or 0
        if start != int(start) or start < 0:
            raise InvalidParams([f"Invalid cursor: {start}"])
        chunk, nxt = page(children, int(start), MAX_CHILDREN)
        return {"cursor": int(start) + len(chunk), "hasMore": nxt is not None, "items": chunk}


class GetDocumentVersions(IManageTool):
    name = "get_document_versions"

    def handle(self, matter, links, args, ctx):
        doc = find_document(matter, args["documentId"])
        chunk, nxt = page([doc], args.get("cursor"), args.get("limit", 100))
        out: dict = {"has_more": nxt is not None}
        out["items"] = [document_profile(matter, links, d) for d in chunk]
        return out


# --- inferred write tools -----------------------------------------------------------------------------------------

_CONTAINER_ID = {"type": "string", "pattern": "^[^!]+!\\d+$"}


def _writable_folder(matter: Matter, fid: str) -> dict:
    folder = matter.folder(fid)
    if folder is None and fid.lower() != matter.workspace["id"].lower():
        raise UpstreamError(NOT_FOUND, 404)
    if folder is None or not folder.get("writable"):
        allowed = ", ".join(f"{f['name']} ({f['id']})" for f in matter.folders if f.get("writable"))
        raise UpstreamError(f"You do not have permission to add items to this container. Writable folders: {allowed}.",
                            403)
    return folder


class UploadDocument(IManageTool):
    name = "upload_document"
    traced = False
    annotations = WRITE
    description = (
        "Uploads a new document to a folder in iManage Work and returns its document profile. Provide the text "
        "content of the document; it is saved as a PDF (default) or Word (docx) file named after `name`. Only "
        "folders the current user can write to accept new documents."
    )
    input_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "folder_id": {**_CONTAINER_ID, "description": "Specifies the ID of the folder to upload the document to."},
            "name": {"type": "string", "minLength": 1, "maxLength": 200,
                     "description": "Specifies the name of the document, without the file extension."},
            "content": {"type": "string", "minLength": 1, "maxLength": UPLOAD_LIMIT,
                        "description": "Specifies the text content of the document. Markdown headings, lists and "
                                       "tables are kept as plain text."},
            "format": {"type": "string", "enum": ["pdf", "docx"], "default": "pdf",
                       "description": "Specifies the file format to save the document as."},
            "comment": {"type": "string", "maxLength": 1000,
                        "description": "Specifies an optional comment stored on the document profile."},
        },
        "required": ["folder_id", "name", "content"],
        "additionalProperties": False,
    }

    def run(self, args: dict, ctx: CallContext) -> Any:
        links = self.links(ctx)
        fmt = args.get("format", "pdf")
        name = re.sub(rf"\.{fmt}$", "", args["name"].strip(), flags=re.IGNORECASE).strip()
        if not name:
            raise InvalidParams(["name: must not be empty"])
        with self.store.write(ctx.conversation_id) as matter:
            folder = _writable_folder(matter, args["folder_id"])
            now = ctx.clock.iso()
            doc = {
                "number": matter.take_document_number(),
                "version": 1,
                "name": name,
                "extension": fmt,
                "type_description": "ACROBAT" if fmt == "pdf" else "WORD 2007",
                "folder_id": folder["id"],
                "author": matter.data["current_user"],
                "comment": args.get("comment", ""),
                "doc_type": "Draft",
                "size": len(args["content"].encode("utf-8")),
                "create_date": now,
                "edit_date": now,
                "edit_profile_date": now,
                "text": args["content"] if args["content"].endswith("\n") else args["content"] + "\n",
            }
            matter.documents.append(doc)
            folder["edit_date"] = now
            return {"id": doc_id(matter, doc), **document_profile(matter, links, doc)}


class CreateFolder(IManageTool):
    name = "create_folder"
    traced = False
    annotations = WRITE
    description = (
        "Creates a new folder inside an existing folder in iManage Work and returns the new folder. Only folders "
        "the current user can write to accept new subfolders."
    )
    input_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "parent_id": {**_CONTAINER_ID, "description": "Specifies the ID of the folder to create the folder in."},
            "name": {"type": "string", "minLength": 1, "maxLength": 200,
                     "description": "Specifies the name of the new folder."},
            "description": {"type": "string", "maxLength": 1000,
                            "description": "Specifies an optional description of the folder."},
        },
        "required": ["parent_id", "name"],
        "additionalProperties": False,
    }

    def run(self, args: dict, ctx: CallContext) -> Any:
        links = self.links(ctx)
        name = args["name"].strip()
        if not name:
            raise InvalidParams(["name: must not be empty"])
        with self.store.write(ctx.conversation_id) as matter:
            parent = _writable_folder(matter, args["parent_id"])
            if any(f["name"].lower() == name.lower() for f in matter.subfolders(parent["id"])):
                raise UpstreamError(f"A folder named '{name}' already exists in this location.", 409)
            now = ctx.clock.iso()
            folder = {
                "id": matter.take_folder_id(),
                "name": name,
                "parent_id": parent["id"],
                "description": args.get("description", ""),
                "writable": True,
                "owner": matter.data["current_user"],
                "create_date": now,
                "edit_date": now,
            }
            matter.folders.append(folder)
            return folder_item(matter, links, folder)


READ_TOOLS = (
    GetDocumentProfile, GetWorkspaceProfile, DownloadDocument, GetLibraries, GetRecentDocuments,
    GetRecentWorkspaces, GetUserInformation, Search, Fetch, GetWorkspaceTemplates, SearchWorkspaces,
    SearchFolders, GetContainerChildren, GetDocumentVersions,
)
WRITE_TOOLS = (UploadDocument, CreateFolder)
