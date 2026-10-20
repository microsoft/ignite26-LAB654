"""The Notion tools. Reads are pure; writes go through the per-conversation store."""

from __future__ import annotations

import re
import sqlite3
from typing import Any

from mockmcp import CallContext, Tool

from .common import NotionError, dashed, not_found, page_url, parse_ref, stable_uuid
from .render import (
    collection_url,
    compact,
    data_source_block,
    database_text,
    page_fetch,
    row_values,
    sql_columns,
    view_config,
)
from .store import StateStore, Workspace

WRITE = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False}
DESTRUCTIVE = {**WRITE, "destructiveHint": True}
COLORS = ("default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red")


def minute(ts: str) -> str:
    return ts[:16] + ":00.000Z"


def option_id(*parts: str) -> str:
    return stable_uuid(*parts).replace("-", "")[-6:]


class NotionTool(Tool):
    def __init__(self, store: StateStore) -> None:
        self.store = store


# --- notion-search ----------------------------------------------------------------------------------------------

_WORD = re.compile(r"[a-z0-9]+")


def _words(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def _bold(text: str, words: set[str]) -> str:
    out = re.sub(r"[A-Za-z0-9]+", lambda m: f"**{m.group(0)}**" if m.group(0).lower() in words else m.group(0), text)
    return out.replace("** **", " ")


def _snippets(content: str, words: set[str], limit: int = 3) -> list[str]:
    hits = []
    for line in content.splitlines():
        clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line).lstrip("#-* ").strip()
        if clean and set(_words(clean)) & words:
            hits.append(_bold(clean if len(clean) <= 110 else clean[:110].rsplit(" ", 1)[0] + "...", words))
        if len(hits) == limit:
            break
    return hits


class Search(NotionTool):
    name = "notion-search"
    title = "Search Notion workspace and connected sources"
    description = (
        "Perform a search over:\n"
        "- \"internal\": Semantic search over Notion workspace and connected sources.\n"
        "- \"user\": Search for users by name or email.\n\n"
        "Use the `fetch` tool to see the full contents of a result. Use `data_source_url` to search within the "
        "pages of a specific database's data source (find it by fetching the database first), or `page_url` to "
        "search within a page and its children. Results include each match's id, title, url, type, highlight, "
        "last-edited timestamp and path."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "minLength": 1, "description": "Semantic search query over your entire "
                      "Notion workspace and connected sources."},
            "query_type": {"type": "string", "enum": ["internal", "user"]},
            "data_source_url": {"type": "string", "description": "Optionally, the URL of a Data source to search "
                                "(collection://...)."},
            "page_url": {"type": "string", "description": "Optionally, the URL or ID of a page to search within."},
            "teamspace_id": {"type": "string"},
            "filters": {"type": "object"},
            "page_size": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
            "max_highlight_length": {"type": "integer"},
        },
        "required": ["query"],
    }

    def run(self, args: dict, ctx: CallContext) -> Any:
        ws = self.store.read(ctx.conversation_id)
        query = args["query"]
        if args.get("query_type") == "user":
            words = set(_words(query))
            users = [u for u in ws.data.get("users", []) if words & set(_words(u["name"]))]
            return {"results": [{"id": u["id"], "name": u["name"], "type": u["type"]} for u in users],
                    "type": "user_search"}
        words = set(_words(query))
        phrase = " ".join(_words(query))
        scope_db = scope_page = None
        if args.get("data_source_url"):
            ref = parse_ref(args["data_source_url"])
            scope_db = ref and (ws.data_source(ref[1]) or ws.database(ref[1]))
            if not scope_db:
                raise not_found(args["data_source_url"])
        if args.get("page_url"):
            ref = parse_ref(args["page_url"])
            if not ref or not (ws.page(ref[1]) or ws.database(ref[1])):
                raise not_found(args["page_url"])
            scope_page = ref[1]

        docs = []
        for p in ws.pages:
            docs.append(("page", p, p["title"], p.get("content", ""), p.get("parent_id"), None))
        for d in ws.databases:
            docs.append(("database", d, d["title"], "", d.get("parent_id"), None))
            for r in d["rows"]:
                vals = row_values(d, r, with_url=False)
                title = next((r["properties"].get(p["name"]) for p in d["schema"] if p["type"] == "title"), "") or ""
                body = "\n".join(f"{k}: {v}" for k, v in vals.items() if isinstance(v, str) and v and v != title)
                docs.append(("page", r, title, body, d["id"], d))

        scored = []
        for kind, obj, title, body, parent_id, db in docs:
            if scope_db is not None and db is not scope_db:
                continue
            if scope_page and scope_page not in {obj["id"]} | {a["obj"]["id"] for a in ws.ancestors(parent_id)}:
                continue
            tw, bw = set(_words(title)), set(_words(body))
            score = 3 * len(words & tw) + len(words & bw)
            if phrase and phrase in " ".join(_words(title)):
                score += 10
            if score:
                scored.append((score, obj.get("edited", ""), kind, obj, title, body, parent_id))
        scored.sort(key=lambda s: s[1], reverse=True)
        scored.sort(key=lambda s: -s[0])

        results = []
        for score, edited, kind, obj, title, body, parent_id in scored[: args.get("page_size", 10)]:
            parts = [_bold(title, words)] if words & set(_words(title)) else []
            parts += [s for s in _snippets(body, words) if s.replace("**", "") != title]
            entry = {"id": obj["id"], "title": title, "url": page_url(obj["id"], pvs=True), "type": kind,
                     "highlight": " --- ".join(parts) or title, "timestamp": minute(edited or ctx.clock.iso())}
            path = ws.path(parent_id)
            if path:
                entry["path"] = path
            entry["verification"] = {"state": "unverified"}
            results.append(entry)
        return {"results": results, "type": "workspace_search"}


# --- notion-fetch -----------------------------------------------------------------------------------------------


class Fetch(NotionTool):
    name = "notion-fetch"
    title = "Fetch Notion entities"
    description = (
        "Retrieves details about a Notion entity (page, database, or data source) by URL or ID.\n"
        "Provide the URL or ID in the `id` parameter. Accepts Notion page URLs, page or database IDs (with or "
        "without dashes), and data source URLs (collection://...).\n"
        "Pages are returned in Notion-flavored Markdown with their properties. Databases return their data "
        "sources, each with its schema (property names, types and select options), a SQLite table definition and "
        "views; use notion-query-data-sources to read the rows. When a page or database update needs exact "
        "property names or select options, fetch the database first."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "The ID or URL of the Notion page, database or data source to "
                   "fetch. Supports notion.so and app.notion.com URLs, IDs and collection:// URLs."},
            "include_discussions": {"type": "boolean"},
            "include_transcript": {"type": "boolean"},
        },
        "required": ["id"],
    }

    def run(self, args: dict, ctx: CallContext) -> Any:
        ws = self.store.read(ctx.conversation_id)
        ref = parse_ref(args["id"])
        if not ref:
            raise NotionError(f"Invalid ID or URL: {args['id']}")
        kind, oid = ref
        if kind == "collection" or (kind == "page" and ws.data_source(oid)):
            db = ws.data_source(oid)
            if not db:
                raise not_found(args["id"])
            return {"metadata": {"type": "data_source"}, "title": db["title"], "url": collection_url(db),
                    "text": "\n".join(data_source_block(db))}
        if kind == "view" or ws.view(oid):
            db = ws.view(oid)
            if not db:
                raise not_found(args["id"])
            return {"metadata": {"type": "view"}, "title": "Show All", "url": f"view://{db['view_id']}",
                    "text": f'<view url="{{{{view://{db["view_id"]}}}}}">\n{compact(view_config(db))}\n</view>'}
        db = ws.database(oid)
        if db:
            return {"metadata": {"type": "database"}, "title": db["title"], "url": page_url(db["id"], pvs=True),
                    "text": database_text(ws, db)}
        page = ws.page(oid)
        if page:
            return page_fetch(ws, page, None, ctx.clock.iso())
        parent_db, row = ws.row(oid)
        if row:
            return page_fetch(ws, row, parent_db, ctx.clock.iso())
        raise not_found(args["id"])


# --- notion-query-data-sources ----------------------------------------------------------------------------------


def _filter_value(row: dict, prop: str) -> Any:
    if prop in row:
        return row[prop]
    return row.get(f"date:{prop}:start")


def _matches(row: dict, flt: Any) -> bool:
    if not isinstance(flt, dict):
        return True
    if isinstance(flt.get("and"), list):
        return all(_matches(row, f) for f in flt["and"])
    if isinstance(flt.get("or"), list):
        return any(_matches(row, f) for f in flt["or"]) if flt["or"] else True
    prop = flt.get("property")
    if not isinstance(prop, str):
        return True
    # Accept both {"property", "<op>": v} and Notion API style {"property", "<type>": {"<op>": v}}.
    conds = {k: v for k, v in flt.items() if k != "property"}
    for key in list(conds):
        if isinstance(conds[key], dict):
            conds.update(conds.pop(key))
    value = _filter_value(row, prop)
    text = "" if value is None else str(value)
    for op, want in conds.items():
        w = "" if want is None else str(want)
        if op == "equals" and text != w:
            return False
        if op == "does_not_equal" and text == w:
            return False
        if op == "contains" and w.lower() not in text.lower():
            return False
        if op == "does_not_contain" and w.lower() in text.lower():
            return False
        if op == "is_empty" and want and text:
            return False
        if op == "is_not_empty" and want and not text:
            return False
        if op in ("before", "on_or_before", "after", "on_or_after") and text:
            if op == "before" and not text < w:
                return False
            if op == "on_or_before" and not text[:len(w)] <= w:
                return False
            if op == "after" and not text[:len(w)] > w:
                return False
            if op == "on_or_after" and not text >= w:
                return False
        if op in ("before", "on_or_before", "after", "on_or_after") and not text:
            return False
    return True


class QueryDataSources(NotionTool):
    name = "notion-query-data-sources"
    title = "Query Notion data sources"
    description = (
        "Query the rows of one or more Notion data sources (databases).\n"
        "Mode \"rows\": pass `data_source_url` (collection://...) with optional `filter`, `sort` "
        "([{property, direction}]) and `limit`. Mode \"sql\": pass `data_source_urls` and a read-only SQLite "
        "`query` against the tables described by notion-fetch (table name is the collection:// URL, dates use "
        "the expanded date:<column>:start columns).\n"
        "Fetch the database first to learn its data source URL and property names."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "data": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string", "enum": ["rows", "sql"], "default": "rows"},
                    "data_source_url": {"type": "string"},
                    "data_source_urls": {"type": "array", "items": {"type": "string"}},
                    "filter": {"type": "object"},
                    "sort": {"type": "array", "items": {"type": "object"}},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                    "query": {"type": "string"},
                    "params": {"type": "array"},
                },
            },
        },
        "required": ["data"],
    }

    def _db(self, ws: Workspace, url: str) -> dict:
        ref = parse_ref(url)
        db = ref and (ws.data_source(ref[1]) or ws.database(ref[1]))
        if not db:
            raise not_found(url)
        return db

    def run(self, args: dict, ctx: CallContext) -> Any:
        ws = self.store.read(ctx.conversation_id)
        data = args["data"]
        urls = data.get("data_source_urls") or ([data["data_source_url"]] if data.get("data_source_url") else [])
        if not urls:
            raise NotionError("data_source_url is required.")
        dbs = [self._db(ws, u) for u in urls]
        if data.get("mode") == "sql" or (data.get("query") and data.get("mode") != "rows"):
            return self._sql(dbs, data)
        db = dbs[0]
        rows = [row_values(db, r) for r in db["rows"]]
        rows = [r for r in rows if _matches(r, data.get("filter"))]
        for spec in reversed(data.get("sort") or []):
            prop = spec.get("property") or spec.get("timestamp", "")
            key = f"date:{prop}:start" if any(p["name"] == prop and p["type"] == "date" for p in db["schema"]) else prop
            desc = str(spec.get("direction", "ascending")).lower().startswith("desc")
            present = [r for r in rows if r.get(key) not in (None, "")]
            missing = [r for r in rows if r.get(key) in (None, "")]
            present.sort(key=lambda r: str(r[key]), reverse=desc)
            rows = present + missing
        limit = data.get("limit", 100)
        return {"results": rows[:limit], "has_more": len(rows) > limit}

    def _sql(self, dbs: list[dict], data: dict) -> Any:
        query = (data.get("query") or "").strip()
        if not re.match(r"(?is)^\s*(select|with)\b", query):
            raise NotionError("Only read-only SELECT queries are supported.")
        conn = sqlite3.connect(":memory:")
        try:
            for db in dbs:
                cols = sql_columns(db)
                names = [c[0] for c in cols]
                conn.execute(f'CREATE TABLE "{collection_url(db)}" (' + ", ".join(f'"{n}"' for n in names) + ")")
                for r in db["rows"]:
                    vals = row_values(db, r)
                    vals["createdTime"] = r.get("created")
                    conn.execute(f'INSERT INTO "{collection_url(db)}" VALUES (' + ",".join("?" * len(names)) + ")",
                                 [vals.get(n) for n in names])
            conn.execute("PRAGMA query_only = ON")
            cur = conn.execute(query, data.get("params") or [])
            cols = [d[0] for d in cur.description or []]
            rows = [dict(zip(cols, rec)) for rec in cur.fetchmany(101)]
        except sqlite3.Error as exc:
            raise NotionError(f"SQL error: {exc}") from None
        finally:
            conn.close()
        return {"results": rows[:100], "has_more": len(rows) > 100}


# --- shared write helpers ---------------------------------------------------------------------------------------


def _prop(db: dict, name: str) -> dict | None:
    return next((p for p in db["schema"] if p["name"] == name), None) or next(
        (p for p in db["schema"] if p["name"].lower() == name.lower()), None)


def apply_properties(db: dict, row: dict, props: dict) -> None:
    """Set row properties using the names notion-fetch advertises. Validates before mutating."""
    staged: dict[str, Any] = {}
    for key, value in props.items():
        m = re.fullmatch(r"date:(.+):(start|end|is_datetime)", key)
        name = m.group(1) if m else key
        prop = _prop(db, name)
        if prop is None and name.lower() == "title":
            prop = next(p for p in db["schema"] if p["type"] == "title")
        if prop is None:
            raise NotionError(f"Property \"{name}\" does not exist in this data source. Valid properties: "
                              + ", ".join(f'"{p["name"]}"' for p in db["schema"]) + ".")
        n = prop["name"]
        if prop["type"] == "date":
            current = dict(staged.get(n) or row["properties"].get(n) or {"start": None, "end": None, "is_datetime": 0})
            part = m.group(2) if m else "start"
            if isinstance(value, dict):
                current.update({k: value.get(k) for k in ("start", "end", "is_datetime") if k in value})
            elif part == "is_datetime":
                current["is_datetime"] = int(value or 0)
            else:
                if value is not None and not re.fullmatch(r"\d{4}-\d{2}-\d{2}(T[\d:.]+(Z|[+-]\d{2}:\d{2})?)?", str(value)):
                    raise NotionError(f"Invalid date for property \"{n}\": \"{value}\". Use an ISO-8601 date "
                                      "such as 2026-10-23.")
                current[part] = value
            staged[n] = current if current.get("start") else None
        elif prop["type"] == "select":
            if value in (None, ""):
                staged[n] = None
                continue
            names = [o["name"] for o in prop["options"]]
            if value not in names:
                raise NotionError(
                    f"Invalid select value for property \"{n}\": \"{value}\". Value must be one of the following: "
                    + ", ".join(f'"{x}"' for x in names)
                    + ". If a new select option is needed, the data source must be updated to add it.")
            staged[n] = value
        elif prop["type"] == "number":
            try:
                staged[n] = None if value in (None, "") else float(value)
            except (TypeError, ValueError):
                raise NotionError(f"Invalid number for property \"{n}\": \"{value}\".") from None
        else:
            staged[n] = "" if value is None else str(value)
    row["properties"].update(staged)


# --- notion-update-page -----------------------------------------------------------------------------------------


class UpdatePage(NotionTool):
    name = "notion-update-page"
    title = "Update Notion page"
    description = (
        "Update a Notion page's properties or content.\n"
        "Commands:\n"
        "- \"update_properties\": set `properties`. For database rows use the exact property names from the data "
        "source schema; dates use the expanded keys date:<column>:start, date:<column>:end and "
        "date:<column>:is_datetime; select values must be existing options (update the data source to add one). "
        "For standalone pages the only property is \"title\".\n"
        "- \"replace_content\": replace the page body with `new_str` (Notion-flavored Markdown).\n"
        "- \"insert_content_after\": insert `new_str` after the text matched by `selection_with_ellipsis` "
        "(\"start...end\").\n"
        "- \"replace_content_range\": replace the text matched by `selection_with_ellipsis` with `new_str`.\n"
        "Fetch the page (and its database) first to get the exact property names and options."
    )
    annotations = WRITE
    input_schema = {
        "type": "object",
        "properties": {
            "page_id": {"type": "string", "description": "The ID or URL of the page to update."},
            "command": {"type": "string", "enum": ["update_properties", "replace_content", "insert_content_after",
                                                     "replace_content_range"]},
            "properties": {"type": "object"},
            "new_str": {"type": "string"},
            "selection_with_ellipsis": {"type": "string"},
            "allow_deleting_content": {"type": "boolean"},
            "allow_async": {"type": "boolean"},
        },
        "required": ["page_id", "command"],
    }

    def run(self, args: dict, ctx: CallContext) -> Any:
        ref = parse_ref(args["page_id"])
        if not ref:
            raise NotionError(f"Invalid page ID: {args['page_id']}")
        oid = ref[1]
        with self.store.write(ctx.conversation_id) as ws:
            db, row = ws.row(oid)
            target = row or ws.page(oid)
            if target is None:
                raise not_found(args["page_id"])
            cmd = args["command"]
            if cmd == "update_properties":
                props = args.get("properties")
                if not isinstance(props, dict) or not props:
                    raise NotionError("properties is required for update_properties.")
                if db is not None:
                    apply_properties(db, row, props)
                else:
                    unknown = [k for k in props if k != "title"]
                    if unknown:
                        raise NotionError(f"Property \"{unknown[0]}\" does not exist on this page. Pages that are "
                                          "not in a database only have a \"title\" property.")
                    target["title"] = str(props["title"])
            else:
                new = args.get("new_str")
                if new is None:
                    raise NotionError(f"new_str is required for {cmd}.")
                content = target.get("content", "")
                if cmd == "replace_content":
                    content = new
                else:
                    sel = args.get("selection_with_ellipsis") or ""
                    start, _, end = sel.partition("...")
                    i = content.find(start) if start else -1
                    j = content.find(end, i + len(start)) if end and i >= 0 else i + len(start) - len(end)
                    if i < 0 or j < 0:
                        raise NotionError("Could not find the text matching selection_with_ellipsis in the page.")
                    stop = j + len(end)
                    content = content[:stop] + "\n" + new + content[stop:] if cmd == "insert_content_after" \
                        else content[:i] + new + content[stop:]
                target["content"] = content
            target["edited"] = ctx.clock.iso()
            if db is not None:
                db["edited"] = target["edited"]
        return {"page_id": dashed(oid)}


# --- notion-create-pages ----------------------------------------------------------------------------------------


class CreatePages(NotionTool):
    name = "notion-create-pages"
    title = "Create Notion pages"
    description = (
        "Create one or more Notion pages.\n"
        "To add rows to a database, set `parent` to {\"type\": \"data_source_id\", \"data_source_id\": ...} "
        "(from notion-fetch on the database) and give each page `properties` keyed by the data source's property "
        "names; dates use date:<column>:start / date:<column>:is_datetime and select values must be existing "
        "options. To create a standalone page, set `parent` to {\"type\": \"page_id\", \"page_id\": ...} and give "
        "each page a \"title\" property. Optional `content` is Notion-flavored Markdown."
    )
    annotations = WRITE
    input_schema = {
        "type": "object",
        "properties": {
            "parent": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["page_id", "database_id", "data_source_id"]},
                    "page_id": {"type": "string"},
                    "database_id": {"type": "string"},
                    "data_source_id": {"type": "string"},
                },
            },
            "pages": {
                "type": "array",
                "minItems": 1,
                "maxItems": 100,
                "items": {"type": "object", "properties": {"properties": {"type": "object"},
                                                           "content": {"type": "string"}}},
            },
            "allow_async": {"type": "boolean"},
        },
        "required": ["pages"],
    }

    def run(self, args: dict, ctx: CallContext) -> Any:
        parent = args.get("parent") or {}
        created = []
        with self.store.write(ctx.conversation_id) as ws:
            db = page_parent = None
            ref_text = parent.get("data_source_id") or parent.get("database_id") or parent.get("page_id")
            if ref_text:
                ref = parse_ref(ref_text)
                oid = ref[1] if ref else ""
                db = ws.data_source(oid) or ws.database(oid)
                if db is None:
                    page_parent = ws.page(oid)
                    if page_parent is None:
                        raise not_found(ref_text)
            else:
                page_parent = next(p for p in ws.pages if not p.get("parent_id"))
            now = ctx.clock.iso()
            for spec in args["pages"]:
                props = dict(spec.get("properties") or {})
                new_id = stable_uuid("created", ctx.conversation_id or "anonymous", str(ws.next_seq()))
                if db is not None:
                    row = {"id": new_id, "created": now, "edited": now, "content": spec.get("content", ""),
                           "properties": {p["name"]: ("" if p["type"] in ("text", "title") else None)
                                          for p in db["schema"]}}
                    apply_properties(db, row, props)
                    db["rows"].append(row)
                    db["edited"] = now
                    vals = row_values(db, row, with_url=False)
                    out_props = {k: v for k, v in vals.items() if v not in (None, "")}
                else:
                    title = props.pop("title", None) or props.pop("Title", None)
                    if props:
                        raise NotionError(f"Property \"{next(iter(props))}\" is not valid for a page whose parent "
                                          "is not a database. Use \"title\".")
                    page = {"id": new_id, "title": str(title or "Untitled"), "parent_id": page_parent["id"],
                            "created": now, "edited": now, "content": spec.get("content", "")}
                    ws.pages.append(page)
                    out_props = {"title": page["title"]}
                created.append({"id": new_id, "url": page_url(new_id, pvs=True),
                                "properties": dict(sorted(out_props.items()))})
        return {"pages": created}


# --- notion-update-data-source ----------------------------------------------------------------------------------

_STMT = re.compile(
    r'''(?isx)^\s*(?:
        ALTER\s+COLUMN\s+"(?P<alter>[^"]+)"\s+SET\s+(?P<alter_type>.+)
      | ADD\s+COLUMN\s+"(?P<add>[^"]+)"\s+(?P<add_type>.+)
      | RENAME\s+COLUMN\s+"(?P<old>[^"]+)"\s+TO\s+"(?P<new>[^"]+)"
      | DROP\s+COLUMN\s+"(?P<drop>[^"]+)"
    )\s*$''')
_OPTION = re.compile(r"""'((?:[^']|'')*)'\s*(?::\s*([a-z_]+))?""")


def _split_statements(text: str) -> list[str]:
    out, buf, quote = [], [], None
    for ch in text:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
            buf.append(ch)
        elif ch == ";":
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    out.append("".join(buf))
    return [s.strip() for s in out if s.strip()]


def _type_spec(db: dict, name: str, spec: str, existing: dict | None) -> dict:
    spec = spec.strip()
    upper = spec.upper()
    prop = {"name": name, "id": existing["id"] if existing else option_id(db["data_source_id"], name)}
    if upper.startswith("SELECT"):
        inner = spec[spec.find("(") + 1: spec.rfind(")")] if "(" in spec else ""
        old = {o["name"]: o for o in (existing or {}).get("options", [])}
        options = []
        for raw, color in _OPTION.findall(inner):
            label = raw.replace("''", "'")
            if color and color not in COLORS:
                raise NotionError(f"Invalid color \"{color}\" for option \"{label}\". Use one of: {', '.join(COLORS)}.")
            base = old.get(label)
            options.append({"name": label, "color": color or (base["color"] if base else "default"),
                            "id": base["id"] if base else option_id(db["data_source_id"], name, label)})
        prop.update(type="select", options=options)
    elif upper in ("TEXT", "RICH_TEXT"):
        prop["type"] = "text"
    elif upper == "DATE":
        prop["type"] = "date"
    elif upper in ("NUMBER", "REAL"):
        prop["type"] = "number"
    else:
        raise NotionError(f"Unsupported column type: {spec}. Supported: TEXT, NUMBER, DATE, SELECT('a':color, ...).")
    return prop


def _convert(value: Any, old_type: str, new_type: str) -> Any:
    if old_type == new_type or value in (None, ""):
        return value if old_type == new_type else (None if new_type in ("select", "date", "number") else "")
    if old_type == "date":
        value = value.get("start")
    if new_type == "date":
        return {"start": str(value)[:10], "end": None, "is_datetime": 0} if re.match(r"\d{4}-\d{2}-\d{2}", str(value)) else None
    if new_type == "number":
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
    return str(value)


class UpdateDataSource(NotionTool):
    name = "notion-update-data-source"
    title = "Update Notion data source"
    description = (
        "Update a Notion data source's schema with SQL DDL-style `statements`, separated by semicolons:\n"
        "- ALTER COLUMN \"Name\" SET SELECT('Option A':green, 'Option B':red) — set the full list of select options "
        "(include the existing ones to keep them). Also converts a text column to a select.\n"
        "- ALTER COLUMN \"Name\" SET TEXT | NUMBER | DATE\n"
        "- ADD COLUMN \"Name\" TEXT | NUMBER | DATE | SELECT(...)\n"
        "- RENAME COLUMN \"Old\" TO \"New\"\n"
        "- DROP COLUMN \"Name\"\n"
        "Colors: default, gray, brown, orange, yellow, green, blue, purple, pink, red. Optionally rename the data "
        "source with `title`. Returns the updated schema."
    )
    annotations = DESTRUCTIVE
    input_schema = {
        "type": "object",
        "properties": {
            "data_source_id": {"type": "string", "description": "The data source ID or collection:// URL."},
            "statements": {"type": "string"},
            "title": {"type": "string"},
        },
        "required": ["data_source_id"],
    }

    def run(self, args: dict, ctx: CallContext) -> Any:
        ref = parse_ref(args["data_source_id"])
        with self.store.write(ctx.conversation_id) as ws:
            db = ref and (ws.data_source(ref[1]) or ws.database(ref[1]))
            if not db:
                raise not_found(args["data_source_id"])
            statements = _split_statements(args.get("statements") or "")
            if not statements and not args.get("title"):
                raise NotionError("Provide at least one statement or a title.")
            for stmt in statements:
                self._apply(db, stmt)
            if args.get("title"):
                db["title"] = args["title"]
            db["edited"] = ctx.clock.iso()
            text = database_text(ws, db, views=False)
        return {"result": "Updated data source: " + text}

    @staticmethod
    def _apply(db: dict, stmt: str) -> None:
        m = _STMT.match(stmt)
        if not m:
            raise NotionError(f"Could not parse statement: {stmt}")
        schema = db["schema"]
        if m.group("alter"):
            existing = _prop(db, m.group("alter"))
            if existing is None:
                raise NotionError(f"Column \"{m.group('alter')}\" does not exist.")
            if existing["type"] == "title":
                raise NotionError("The title column's type cannot be changed.")
            new = _type_spec(db, existing["name"], m.group("alter_type"), existing)
            if new["type"] == "select" and existing["type"] != "select":
                have = {o["name"] for o in new["options"]}
                for r in db["rows"]:
                    v = _convert(r["properties"].get(existing["name"]), existing["type"], "text")
                    if v and v not in have:
                        new["options"].append({"name": v, "color": "gray",
                                               "id": option_id(db["data_source_id"], existing["name"], v)})
                        have.add(v)
            for r in db["rows"]:
                r["properties"][existing["name"]] = _convert(r["properties"].get(existing["name"]), existing["type"],
                                                             new["type"])
            schema[schema.index(existing)] = new
        elif m.group("add"):
            if _prop(db, m.group("add")):
                raise NotionError(f"Column \"{m.group('add')}\" already exists.")
            new = _type_spec(db, m.group("add"), m.group("add_type"), None)
            schema.insert(0, new)
            db["view"].append(new["name"])
            for r in db["rows"]:
                r["properties"][new["name"]] = "" if new["type"] == "text" else None
        elif m.group("old"):
            existing = _prop(db, m.group("old"))
            if existing is None:
                raise NotionError(f"Column \"{m.group('old')}\" does not exist.")
            if _prop(db, m.group("new")) and m.group("new").lower() != existing["name"].lower():
                raise NotionError(f"Column \"{m.group('new')}\" already exists.")
            old, new_name = existing["name"], m.group("new")
            existing["name"] = new_name
            db["view"] = [new_name if v == old else v for v in db["view"]]
            for r in db["rows"]:
                r["properties"][new_name] = r["properties"].pop(old, None)
        else:
            existing = _prop(db, m.group("drop"))
            if existing is None:
                raise NotionError(f"Column \"{m.group('drop')}\" does not exist.")
            if existing["type"] == "title":
                raise NotionError("The title column cannot be dropped.")
            schema.remove(existing)
            db["view"] = [v for v in db["view"] if v != existing["name"]]
            for r in db["rows"]:
                r["properties"].pop(existing["name"], None)
