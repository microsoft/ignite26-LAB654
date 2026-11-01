"""Browsable, read-only HTML pages for the mock matter, loosely styled like iManage Work's web client.

Routes (served next to /mcp), matching the links tool results return:
* ``/work/link/w/{id}``, ``/work/link/f/{id}``, ``/work/link/d/{id}``: workspace, folder and document pages for the
  original (seed) matter.
* ``/v/{token}/work/link/...``: the same pages as one conversation left the matter (uploads, new folders). ``token``
  is the store's view token for that conversation. Unknown or expired tokens fall back to the seed with a notice.
* ``/`` and ``/v/{token}/``: redirect to the workspace page.
"""

from __future__ import annotations

import html
import re
from datetime import datetime

from .common import DOC_ID, doc_id, full_file_name, size_label
from .store import Matter, StateStore

_TOKEN = re.compile(r"[0-9a-f]{20}")
_FOLDER_ICON = '<span class="ico folder" aria-hidden="true"></span>'
_WS_ICON = '<span class="ico ws" aria-hidden="true">W</span>'
_EXT_COLORS = {"docx": "#2b579a", "doc": "#2b579a", "xlsx": "#217346", "pdf": "#c4314b", "pptx": "#b7472a"}


def _e(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _date(value: str | None) -> str:
    try:
        dt = datetime.fromisoformat((value or "").replace("Z", "+00:00"))
    except ValueError:
        return value or ""
    return f"{dt.strftime('%b')} {dt.day}, {dt.year} {dt.strftime('%I:%M %p').lstrip('0')}"


def _file_icon(ext: str) -> str:
    return f'<span class="ico file" style="background:{_EXT_COLORS.get(ext, "#605e5c")}">{_e(ext[:4].upper())}</span>'


def document_body(text: str) -> str:
    """Plain extracted text -> HTML. Runs of two or more ``a | b`` lines become a table."""
    lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").split("\n")]
    out: list[str] = []
    i = 0
    while i < len(lines):
        if " | " in lines[i]:
            j = i
            while j < len(lines) and " | " in lines[j]:
                j += 1
            if j - i >= 2:
                rows = [lines[k].split(" | ") for k in range(i, j)]
                head = "".join(f"<th>{_e(c)}</th>" for c in rows[0])
                body = "".join("<tr>" + "".join(f"<td>{_e(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
                out.append(f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead>'
                           f"<tbody>{body}</tbody></table></div>")
                i = j
                continue
        if lines[i].strip():
            out.append(f"<p>{_e(lines[i])}</p>")
        i += 1
    return "".join(out)


class Site:
    def __init__(self, matter: Matter, prefix: str) -> None:
        self.m = matter
        self.prefix = prefix

    def ws_link(self) -> str:
        return f"{self.prefix}w/{self.m.workspace['id']}"

    def folder_link(self, fid: str) -> str:
        return f"{self.prefix}f/{fid}"

    def doc_link(self, doc: dict) -> str:
        return f"{self.prefix}d/{doc_id(self.m, doc)}"

    def tree(self, current: str | None) -> str:
        def branch(parent: str, depth: int) -> str:
            out = []
            for f in sorted(self.m.subfolders(parent), key=lambda f: f["name"].lower()):
                active = " active" if current and f["id"].lower() == current.lower() else ""
                out.append(f'<a class="node{active}" style="padding-left:{12 + depth * 16}px" '
                           f'href="{self.folder_link(f["id"])}">{_FOLDER_ICON}<span>{_e(f["name"])}</span></a>')
                out.append(branch(f["id"], depth + 1))
            return "".join(out)

        ws = self.m.workspace
        active = " active" if current and current.lower() == ws["id"].lower() else ""
        return (f'<a class="node{active}" href="{self.ws_link()}">{_WS_ICON}<span>{_e(ws["name"])}</span></a>'
                + branch(ws["id"], 1))

    def crumbs(self, folder_id: str | None, tail: str | None = None) -> str:
        chain = []
        fid = folder_id
        while fid:
            f = self.m.folder(fid)
            if f is None:
                break
            chain.insert(0, f'<a href="{self.folder_link(f["id"])}">{_e(f["name"])}</a>')
            fid = f["parent_id"]
        parts = [f'<a href="{self.ws_link()}">{_e(self.m.workspace["name"])}</a>', *chain]
        if tail:
            parts.append(f"<span>{_e(tail)}</span>")
        return '<span class="sep">/</span>'.join(parts)

    def listing(self, container_id: str) -> str:
        rows = []
        for f in sorted(self.m.subfolders(container_id), key=lambda f: f["name"].lower()):
            owner = self.m.user(f["owner"]) or {}
            rows.append(f'<tr><td class="name"><a href="{self.folder_link(f["id"])}">{_FOLDER_ICON}'
                        f'<span>{_e(f["name"])}</span></a></td><td></td><td>{_e(owner.get("full_name", f["owner"]))}'
                        f'</td><td>{_e(_date(f["edit_date"]))}</td><td></td></tr>')
        for d in sorted(self.m.documents_in(container_id), key=lambda d: d["name"].lower()):
            author = self.m.user(d["author"]) or {}
            rows.append(f'<tr><td class="name"><a href="{self.doc_link(d)}">{_file_icon(d["extension"])}'
                        f'<span>{_e(d["name"])}</span></a></td><td>{d["number"]}</td>'
                        f'<td>{_e(author.get("full_name", d["author"]))}</td><td>{_e(_date(d["edit_date"]))}</td>'
                        f'<td>{_e(size_label(d["size"]))}</td></tr>')
        if not rows:
            return '<p class="empty">This folder is empty.</p>'
        return ('<table class="list"><thead><tr><th>Name</th><th>Doc #</th><th>Author / owner</th><th>Modified</th>'
                f'<th>Size</th></tr></thead><tbody>{"".join(rows)}</tbody></table>')


def _shell(site: Site, *, title: str, crumbs: str, current: str | None, body: str, scoped: bool,
           notice: str | None) -> str:
    state = "Showing this conversation's changes" if scoped else "Showing the original matter data"
    notice_html = f'<div class="notice">{_e(notice)}</div>' if notice else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{_e(title)} | Mock iManage Work</title>
<style>{CSS}</style></head>
<body>
<header class="appbar"><span class="brand">iManage <b>Work</b></span><span class="lib">Library: {_e(site.m.library)}</span></header>
<div class="layout">
<aside class="tree">{site.tree(current)}</aside>
<main>
  <div class="crumbs">{crumbs}</div>
  {notice_html}
  <h1>{_e(title)}</h1>
  {body}
</main>
</div>
<div class="mock-badge" title="This is a mock iManage Work page served by a mock MCP server. It is not a real iManage library.">
  <span class="mb-top">MOCK IMANAGE</span><span class="mb-sub">{state}</span>
</div>
</body></html>"""


def _profile_table(site: Site, doc: dict) -> str:
    author = site.m.user(doc["author"]) or {}
    folder = site.m.folder(doc["folder_id"]) or {}
    rows = [
        ("Document", f"{doc_id(site.m, doc)} ({full_file_name(doc)})"),
        ("Version", doc["version"]),
        ("Type", f"{doc['type_description']} / {doc.get('doc_type', '')}".rstrip(" /")),
        ("Author", author.get("full_name", doc["author"])),
        ("Folder", folder.get("name", "")),
        ("Created", _date(doc["create_date"])),
        ("Modified", _date(doc["edit_date"])),
        ("Size", size_label(doc["size"])),
        ("Comment", doc.get("comment", "")),
    ]
    return '<dl class="profile">' + "".join(
        f"<dt>{_e(k)}</dt><dd>{_e(v)}</dd>" for k, v in rows if v not in ("", None)) + "</dl>"


def render(matter: Matter, kind: str, ident: str, prefix: str, scoped: bool, notice: str | None) -> str | None:
    site = Site(matter, prefix)
    if kind == "w":
        ws = matter.workspace
        if ident.lower() != ws["id"].lower():
            return None
        owner = matter.user(ws["owner"]) or {}
        meta = (f'<p class="meta">Client: {_e(ws["client"])} &middot; Owner: {_e(owner.get("full_name", ws["owner"]))}'
                f'</p><p class="desc">{_e(ws["description"])}</p>')
        return _shell(site, title=ws["name"], crumbs=site.crumbs(None), current=ws["id"],
                      body=meta + site.listing(ws["id"]), scoped=scoped, notice=notice)
    if kind == "f":
        folder = matter.folder(ident)
        if folder is None:
            return None
        desc = f'<p class="desc">{_e(folder["description"])}</p>' if folder.get("description") else ""
        return _shell(site, title=folder["name"], crumbs=site.crumbs(folder["parent_id"]), current=folder["id"],
                      body=desc + site.listing(folder["id"]), scoped=scoped, notice=notice)
    if kind == "d":
        match = DOC_ID.match(ident)
        doc = matter.document(int(match.group(2))) if match else None
        if doc is None or match.group(1).upper() != matter.library or int(match.group(3)) != doc["version"]:
            return None
        body = _profile_table(site, doc) + f'<article class="doc">{document_body(doc["text"])}</article>'
        return _shell(site, title=full_file_name(doc), crumbs=site.crumbs(doc["folder_id"], full_file_name(doc)),
                      current=doc["folder_id"], body=body, scoped=scoped, notice=notice)
    return None


def not_found_page(matter: Matter, prefix: str, scoped: bool, notice: str | None) -> str:
    site = Site(matter, prefix)
    body = ("<p>This item doesn\u2019t exist in this library, or it was created in a conversation whose changes "
            f'aren\u2019t available here.</p><p><a class="back" href="{site.ws_link()}">Back to the workspace</a></p>')
    return _shell(site, title="Item not found", crumbs="<span>Item not found</span>", current=None, body=body,
                  scoped=scoped, notice=notice)


def build_routes(store: StateStore) -> list:
    from starlette.responses import HTMLResponse, RedirectResponse
    from starlette.routing import Route

    def resolve(request) -> tuple[Matter, str, bool, str | None] | None:
        token = request.path_params.get("token")
        if token is None:
            matter, _ = store.read_by_token(None)
            return matter, "/work/link/", False, None
        if not _TOKEN.fullmatch(token):
            return None
        matter, scoped = store.read_by_token(token)
        notice = None if scoped else (
            "No saved changes were found for this conversation (nothing was changed yet, or the changes expired "
            "after about 2 hours). Showing the original matter data.")
        return matter, f"/v/{token}/work/link/", scoped, notice

    headers = {"Cache-Control": "no-store", "X-Robots-Tag": "noindex, nofollow"}

    def handler(kind: str):
        async def page(request):
            found = resolve(request)
            if found is None:
                matter, _ = store.read_by_token(None)
                return HTMLResponse(not_found_page(matter, "/work/link/", False, None), status_code=404,
                                    headers=headers)
            matter, prefix, scoped, notice = found
            text = render(matter, kind, request.path_params["ident"], prefix, scoped, notice)
            if text is None:
                return HTMLResponse(not_found_page(matter, prefix, scoped, notice), status_code=404, headers=headers)
            return HTMLResponse(text, headers=headers)
        return page

    async def home(request):
        found = resolve(request)
        if found is None:
            return RedirectResponse("/", status_code=302)
        matter, prefix, _, _ = found
        return RedirectResponse(f"{prefix}w/{matter.workspace['id']}", status_code=302)

    routes = [Route("/", home), Route("/v/{token}", home), Route("/v/{token}/", home)]
    for kind in ("w", "f", "d"):
        routes.append(Route(f"/work/link/{kind}/{{ident}}", handler(kind)))
        routes.append(Route(f"/v/{{token}}/work/link/{kind}/{{ident}}", handler(kind)))
    return routes


CSS = """
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{font-family:"Segoe UI",-apple-system,BlinkMacSystemFont,Roboto,Helvetica,Arial,sans-serif;color:#201f1e;background:#faf9f8;font-size:14px;line-height:1.45;display:flex;flex-direction:column}
a{color:#0f5a9c;text-decoration:none}
a:hover{text-decoration:underline}
.appbar{height:48px;flex:none;display:flex;align-items:center;justify-content:space-between;padding:0 18px;background:#0b2a4a;color:#fff}
.brand{font-size:17px;letter-spacing:.01em}
.brand b{font-weight:700}
.lib{font-size:12px;opacity:.85}
.layout{flex:1;display:flex;min-height:0}
.tree{width:290px;flex:none;overflow:auto;background:#fff;border-right:1px solid #e1dfdd;padding:10px 0}
.node{display:flex;align-items:center;gap:8px;padding:5px 12px;color:#323130;white-space:nowrap;overflow:hidden}
.node span:last-child{overflow:hidden;text-overflow:ellipsis}
.node:hover{background:#f3f2f1;text-decoration:none}
.node.active{background:#deecf9;font-weight:600}
.ico{flex:none;display:inline-flex;align-items:center;justify-content:center}
.ico.folder{width:18px;height:13px;background:#dcb048;border-radius:2px;position:relative;margin-top:2px}
.ico.folder:before{content:"";position:absolute;left:0;top:-3px;width:8px;height:4px;background:#dcb048;border-radius:2px 2px 0 0}
.ico.ws{width:18px;height:18px;border-radius:3px;background:#0b2a4a;color:#fff;font-size:11px;font-weight:700}
.ico.file{min-width:30px;height:18px;border-radius:3px;color:#fff;font-size:9px;font-weight:700;padding:0 3px}
main{flex:1;overflow:auto;padding:16px 28px 120px;min-width:0}
.crumbs{font-size:13px;color:#605e5c;margin-bottom:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.crumbs .sep{margin:0 6px;color:#a19f9d}
h1{font-size:22px;font-weight:600;margin:4px 0 10px}
.meta{color:#605e5c;margin:0 0 4px}
.desc{margin:0 0 14px;max-width:900px}
.notice{background:#fff4ce;color:#3b2f00;border-radius:4px;padding:9px 12px;margin:8px 0 12px;max-width:900px}
table.list{border-collapse:collapse;width:100%;max-width:1100px;background:#fff;border:1px solid #e1dfdd}
table.list th{text-align:left;font-weight:600;color:#605e5c;padding:8px 10px;border-bottom:1px solid #e1dfdd;background:#faf9f8}
table.list td{padding:7px 10px;border-bottom:1px solid #f3f2f1;white-space:nowrap}
table.list td.name a{display:flex;align-items:center;gap:8px;color:#201f1e}
.empty{color:#8a8886}
dl.profile{display:grid;grid-template-columns:120px 1fr;gap:4px 14px;background:#fff;border:1px solid #e1dfdd;border-radius:4px;padding:12px 16px;max-width:900px;margin:0 0 16px}
dl.profile dt{color:#605e5c}
dl.profile dd{margin:0}
article.doc{background:#fff;border:1px solid #e1dfdd;border-radius:4px;padding:28px 36px;max-width:900px}
article.doc p{margin:0 0 8px}
.table-wrap{overflow-x:auto;margin:6px 0 14px}
article.doc table{border-collapse:collapse;font-size:13px}
article.doc th,article.doc td{border:1px solid #c8c6c4;padding:5px 8px;vertical-align:top;text-align:left}
article.doc th{background:#f3f2f1;font-weight:600}
.back{font-weight:600}
.mock-badge{position:fixed;right:16px;bottom:16px;z-index:10;display:flex;flex-direction:column;align-items:flex-end;background:#d13438;color:#fff;border-radius:8px;padding:6px 12px;box-shadow:0 4px 14px rgba(0,0,0,.2);font-size:12px;line-height:1.35}
.mock-badge .mb-top{font-weight:700;letter-spacing:.06em}
.mock-badge .mb-sub{opacity:.92}
@media (max-width:800px){.tree{display:none}main{padding:14px 14px 120px}}
"""
