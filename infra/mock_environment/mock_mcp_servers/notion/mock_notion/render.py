"""Text formats copied from the real Notion MCP server's responses."""

from __future__ import annotations

import json

from .common import page_url, rewrite_links
from .store import Workspace

SQL_COMMENTS = {
    "createdTime": "ISO-8601 datetime string, automatically set. This is the canonical time for when the page was created.",
    "start": "ISO-8601 date or datetime string. Use the expanded property (date:<column_name>:start) to set this value.",
    "end": "ISO-8601 date or datetime string, can be empty. Must be NULL if the date is a single date, and must be "
    "present if the date is a range. Use the expanded property (date:<column_name>:end) to set this value.",
    "is_datetime": "1 if the date is a datetime, 0 if it is a date, NULL defaults to 0. Use the expanded property "
    "(date:<column_name>:is_datetime) to set this value.",
}


def compact(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def collection_url(db: dict) -> str:
    return f"collection://{db['data_source_id']}"


def option_url(db: dict, prop: dict, option: dict) -> str:
    return f"collectionPropertyOption://{db['data_source_id']}/{prop['id']}/{option['id']}"


def schema_state(db: dict) -> dict:
    schema = {}
    for prop in db["schema"]:
        entry = {"description": "", "name": prop["name"], "type": prop["type"]}
        if prop["type"] == "select":
            entry["options"] = [
                {"color": o["color"], "description": "", "name": o["name"], "url": option_url(db, prop, o)}
                for o in prop["options"]
            ]
        elif prop["type"] == "date":
            n = prop["name"]
            entry["querySqlColumns"] = {
                "columns": [
                    {"name": f"date:{n}:start", "sqlType": "TEXT"},
                    {"name": f"date:{n}:end", "sqlType": "TEXT"},
                    {"name": f"date:{n}:is_datetime", "sqlType": "INTEGER"},
                ],
                "usage": "For connections.notion.querySql. Main schema name not queryable.",
            }
        schema[prop["name"]] = entry
    return {"name": db["title"], "schema": schema, "url": collection_url(db)}


def sql_columns(db: dict) -> list[tuple[str, str, str | None]]:
    """(column, sql type, comment) in table order."""
    cols = [("url", "TEXT UNIQUE", None), ("createdTime", "TEXT", SQL_COMMENTS["createdTime"])]
    for prop in db["schema"]:
        n, t = prop["name"], prop["type"]
        if t == "date":
            cols += [
                (f"date:{n}:start", "TEXT", SQL_COMMENTS["start"]),
                (f"date:{n}:end", "TEXT", SQL_COMMENTS["end"]),
                (f"date:{n}:is_datetime", "INTEGER", SQL_COMMENTS["is_datetime"]),
            ]
        elif t == "select":
            names = json.dumps([o["name"] for o in prop["options"]], ensure_ascii=False)
            cols.append((n, "TEXT", f"one of {names}"))
        elif t == "number":
            cols.append((n, "REAL", None))
        else:
            cols.append((n, "TEXT", None))
    return cols


def sqlite_table(db: dict) -> str:
    cols = sql_columns(db)
    lines = []
    for i, (name, sql_type, comment) in enumerate(cols):
        quoted = name if name in ("url", "createdTime") else f'"{name}"'
        sep = "," if i < len(cols) - 1 else ""
        lines.append(f"\t{quoted} {sql_type}{sep}" + (f" -- {comment}" if comment else ""))
    return f'CREATE TABLE IF NOT EXISTS "{collection_url(db)}" (\n' + "\n".join(lines) + "\n)"


def ancestor_path(ws: Workspace, parent_id: str | None, data_source: dict | None = None) -> list[str]:
    entries = []
    if data_source is not None:
        entries.append(("data-source", f'url="{collection_url(data_source)}" title="{data_source["title"]}"'))
        parent_id = data_source["id"]
    for a in ws.ancestors(parent_id):
        tag = "page" if a["kind"] == "page" else "database"
        entries.append((tag, f'url="{page_url(a["obj"]["id"])}" title="{a["obj"]["title"]}"'))
    if not entries:
        return []
    lines = ["<ancestor-path>"]
    for depth, (tag, attrs) in enumerate(entries, start=1):
        prefix = "parent" if depth == 1 else f"ancestor-{depth}"
        lines.append(f"<{prefix}-{tag} {attrs}/>")
    lines.append("</ancestor-path>")
    return lines


def data_source_block(db: dict) -> list[str]:
    return [
        f'<data-source url="{{{{{collection_url(db)}}}}}">',
        f"The title of this Data Source is: {db['title']}",
        "",
        "Here is the database's configurable state:",
        "Properties with `readOnly: true` are synced or system-managed. Do not try to update their values with "
        "page update tools.",
        "<data-source-state>",
        compact(schema_state(db)),
        "</data-source-state>",
        "",
        "Here is the SQLite table definition for this data source.",
        "<sqlite-table>",
        sqlite_table(db),
        "</sqlite-table>",
        "</data-source>",
    ]


def view_config(db: dict) -> dict:
    return {
        "dataSourceUrl": f"{{{{{collection_url(db)}}}}}",
        "displayProperties": db["view"],
        "name": "Show All",
        "type": "table",
    }


def database_text(ws: Workspace, db: dict, views: bool = True) -> str:
    lines = [
        f'<database url="{{{{{page_url(db["id"])}}}}}" inline="false">',
        f"The title of this Database is: {db['title']}",
        *ancestor_path(ws, db.get("parent_id")),
        "Here are the Database's Data Sources:",
        'You can use the "fetch" tool on the URL of any Data Source to see its full schema configuration.',
        "<data-sources>",
        *data_source_block(db),
        "</data-sources>",
    ]
    if views:
        lines += [
            "Here are the Database's Views:",
            'You can use the "fetch" tool on the URL of any View to see its full configuration.',
            "<views>",
            f'<view url="{{{{view://{db["view_id"]}}}}}">',
            compact(view_config(db)),
            "</view>",
            "</views>",
        ]
    lines.append("</database>")
    return "\n".join(lines)


def row_values(db: dict, row: dict, with_url: bool = True) -> dict:
    """A row the way notion-query-data-sources returns it (schema order, dates expanded)."""
    out: dict = {}
    for prop in db["schema"]:
        n, value = prop["name"], row["properties"].get(prop["name"])
        if prop["type"] == "date":
            if value and value.get("start"):
                out[f"date:{n}:start"] = value["start"]
                if value.get("end"):
                    out[f"date:{n}:end"] = value["end"]
                out[f"date:{n}:is_datetime"] = value.get("is_datetime") or 0
        elif prop["type"] in ("text", "title"):
            out[n] = value or ""
        else:
            out[n] = value
    if with_url:
        out["url"] = page_url(row["id"])
    return out


def child_refs(ws: Workspace, parent_id: str) -> list[str]:
    refs = [f'<page url="{{{{{page_url(p["id"])}}}}}">{p["title"]}</page>' for p in ws.pages if p.get("parent_id") == parent_id]
    refs += [
        f'<database url="{{{{{page_url(d["id"])}}}}}" inline="false" data-source-url="{{{{{collection_url(d)}}}}}">'
        f'{d["title"]}</database>'
        for d in ws.databases
        if d.get("parent_id") == parent_id
    ]
    return refs


def page_fetch(ws: Workspace, page: dict, db: dict | None, as_of: str) -> dict:
    url = page_url(page["id"])
    if db is None:
        properties = {"title": page["title"]}
        title = page["title"]
        ancestors = ancestor_path(ws, page.get("parent_id"))
        path = ws.path(page.get("parent_id"))
    else:
        properties = row_values(db, page, with_url=False)
        title = next((page["properties"].get(p["name"]) for p in db["schema"] if p["type"] == "title"), "") or ""
        ancestors = ancestor_path(ws, None, data_source=db)
        path = " / ".join(filter(None, [ws.path(db.get("parent_id")), db["title"]]))
    content = rewrite_links(page.get("content", ""))
    refs = child_refs(ws, page["id"]) if db is None else []
    if refs:
        content = (content + "\n" if content else "") + "\n".join(refs)
    edited = page.get("edited", as_of)
    text = "\n".join([
        f'Here is the result of "fetch" for the Page with URL {url} as of {edited}:',
        f'<page url="{url}">',
        *ancestors,
        "<properties>",
        json.dumps(properties, ensure_ascii=False, separators=(",", ":")),
        "</properties>",
        "<iconMetadata>null</iconMetadata>",
        "<content>",
        content,
        "</content>",
        "</page>",
    ])
    result = {"metadata": {"type": "page"}, "title": title, "url": page_url(page["id"], pvs=True), "text": text,
              "cover": None, "icon": None}
    if path:
        result["path"] = path
    result["verification"] = {"state": "unverified"}
    result["page_last_edited_at"] = edited
    return result
