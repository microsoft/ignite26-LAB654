"""Browsable, read-only HTML pages for the mock matter, styled after the iManage Work web client.

Routes (served next to /mcp), matching the links tool results return:
* ``/work/link/w/{id}``, ``/work/link/f/{id}``, ``/work/link/d/{id}``: workspace, folder and document pages for the
  original (seed) matter.
* ``/v/{token}/work/link/...``: the same pages as one conversation left the matter (uploads, new folders). ``token``
  is the store's view token for that conversation. Unknown or expired tokens fall back to the seed with a notice.
* ``/`` and ``/v/{token}/``: redirect to the workspace page.

The chrome (top bar, left navigation, toolbar, filters, column sets and the Properties pane) mirrors the real web
client's layout. Navigation entries, search, upload and filter controls are decorative: the mock is read-only.
"""

from __future__ import annotations

import html
import re
from datetime import datetime

from .common import DOC_ID, doc_id, full_file_name, size_label
from .store import Matter, StateStore

_TOKEN = re.compile(r"[0-9a-f]{20}")
_TYPE_CODES = {"docx": "WORDX", "doc": "WORD", "xlsx": "EXCELX", "xls": "EXCEL", "pptx": "PPTX", "pdf": "ACROBAT",
               "txt": "ANSI", "md": "ANSI"}
_SIGNED_IN = "EMIL"

_SVG_FOLDER = ('<svg class="ico" viewBox="0 0 24 20" aria-hidden="true"><path d="M1.5 3.5h7l2 2.2h12v12.8h-21z" '
               'fill="#fbe7a8" stroke="#c9a227" stroke-width="1.2"/><path d="M1.5 7.5h21" stroke="#c9a227" '
               'stroke-width="1.2"/></svg>')
_SVG_MATTER = ('<svg class="ico" viewBox="0 0 28 22" aria-hidden="true"><rect x="1" y="5" width="26" height="16" rx="1.5" '
               'fill="#e9b996" stroke="#9c5a32" stroke-width="1.2"/><path d="M10 5V2.5h8V5" fill="none" stroke="#9c5a32" '
               'stroke-width="1.2"/><path d="M1 11.5h26" stroke="#9c5a32" stroke-width="1.2"/><rect x="12.5" y="10" '
               'width="3" height="3.5" fill="#9c5a32"/></svg>')
_SVG_LIBRARY = ('<svg class="ico sm" viewBox="0 0 16 16" aria-hidden="true"><ellipse cx="8" cy="3.5" rx="6" ry="2.2" '
                'fill="none" stroke="#605e5c"/><path d="M2 3.5v9c0 1.2 2.7 2.2 6 2.2s6-1 6-2.2v-9M2 8c0 1.2 2.7 2.2 6 '
                '2.2s6-1 6-2.2" fill="none" stroke="#605e5c"/></svg>')
_SVG_BACK = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M14 8H3M7 3.5 2.5 8 7 12.5" fill="none" '
             'stroke="currentColor" stroke-width="1.4"/></svg>')
_SVG_REFRESH = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M13.5 8A5.5 5.5 0 1 1 11.6 3.8M13 1.5v3h-3" '
                'fill="none" stroke="#2f59d8" stroke-width="1.5"/></svg>')
_SVG_SHIELD = ('<svg viewBox="0 0 16 18" aria-hidden="true"><path d="M8 1 2 3.5V8c0 4 2.7 7.2 6 8.5 3.3-1.3 6-4.5 '
               '6-8.5V3.5z" fill="#2f59d8"/><path d="M8 4.5v8" stroke="#fff" stroke-width="2"/></svg>')
_SVG_LOCK = ('<svg viewBox="0 0 16 16" aria-hidden="true"><rect x="3" y="7" width="10" height="7" rx="1" fill="none" '
             'stroke="#605e5c"/><path d="M5 7V5a3 3 0 0 1 6 0v2" fill="none" stroke="#605e5c"/></svg>')
_SVG_PAGE = ('<svg viewBox="0 0 14 16" aria-hidden="true"><path d="M1.5 1h7l4 4v10h-11z M8.5 1v4h4" fill="none" '
             'stroke="#605e5c"/></svg>')
_SVG_GEAR = ('<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="2.4" fill="none" stroke="#201f1e" '
             'stroke-width="1.6"/><path d="M8 1v2.2M8 12.8V15M1 8h2.2M12.8 8H15M3 3l1.6 1.6M11.4 11.4 13 13M3 13l1.6-'
             '1.6M11.4 4.6 13 3" stroke="#201f1e" stroke-width="2"/></svg>')
_KEBAB = '<span class="kebab" aria-hidden="true">&#8942;</span>'
_NAV = [("Documents", "M4 1.5h6l3 3v10H4z"), ("Emails", "M1.5 4h13v9h-13z M1.5 4l6.5 5 6.5-5"),
        ("Folders", "M1.5 3.5h5l1.5 1.5h6.5v8.5h-13z"), ("Clients", "M2 5h12v8.5H2z M6 5V3h4v2"),
        ("Recent Matters", "M2 3h12v10H2z M5 6h6M5 9h4"), ("My Matters", "M2 3h12v10H2z M8 6.5a1.5 1.5 0 1 1 0 .1"),
        ("My Favorites", "M8 1.5l1.9 4.1 4.4.5-3.3 3 .9 4.4L8 11.3 4.1 13.5l.9-4.4-3.3-3 4.4-.5z")]


def _e(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _parse(value: str | None) -> datetime | None:
    try:
        return datetime.fromisoformat((value or "").replace("Z", "+00:00"))
    except ValueError:
        return None


def _date(value: str | None) -> str:
    dt = _parse(value)
    if dt is None:
        return value or ""
    return f"{dt.strftime('%b')} {dt.day}, {dt.year}, {dt.strftime('%I:%M %p').lstrip('0')}"


def _short_date(value: str | None) -> str:
    dt = _parse(value)
    if dt is None:
        return value or ""
    return f"{dt.month}/{dt.day}/{dt.year} {dt.strftime('%I:%M %p').lstrip('0')}"


def _updated(value: str | None) -> str:
    dt = _parse(value)
    if dt is None:
        return value or ""
    return f"{dt.strftime('%b')} {dt.day}, {dt.strftime('%I:%M %p').lstrip('0')}"


def _initials(name: str) -> str:
    parts = [p for p in re.split(r"\s+", name.strip()) if p]
    return "".join(p[0] for p in parts[:2]).upper() or "?"


def _doc_icon(ext: str) -> str:
    code = {"docx": "DOC", "doc": "DOC", "xlsx": "XLS", "xls": "XLS", "pptx": "PPT", "pdf": "PDF"}.get(ext, "TXT")
    color = {"DOC": "#2f59d8", "XLS": "#217346", "PPT": "#b7472a", "PDF": "#c4314b"}.get(code, "#605e5c")
    return (f'<svg class="ico" viewBox="0 0 20 22" aria-hidden="true"><path d="M3 1h10l4 4v16H3z" fill="#fff" '
            f'stroke="#a19f9d"/><rect x="1" y="7" width="15" height="7" rx="1" fill="{color}"/><text x="8.5" y="12.4" '
            f'font-size="5.2" font-weight="700" text-anchor="middle" fill="#fff" font-family="Segoe UI,Arial">'
            f"{code}</text></svg>")


def _type_label(doc: dict) -> str:
    ext = doc.get("extension", "")
    return f"{_TYPE_CODES.get(ext, ext.upper())} | {doc.get('type_description', '')}".strip(" |")


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

    @property
    def library_label(self) -> str:
        return str(self.m.library).title()

    def ws_link(self) -> str:
        return f"{self.prefix}w/{self.m.workspace['id']}"

    def folder_link(self, fid: str) -> str:
        return f"{self.prefix}f/{fid}"

    def doc_link(self, doc: dict) -> str:
        return f"{self.prefix}d/{doc_id(self.m, doc)}"

    def container_link(self, cid: str | None) -> str | None:
        if not cid:
            return None
        if cid.lower() == self.m.workspace["id"].lower():
            return self.ws_link()
        return self.folder_link(cid)

    def container_name(self, cid: str | None) -> str:
        if cid and cid.lower() == self.m.workspace["id"].lower():
            return self.m.workspace["name"]
        folder = self.m.folder(cid) if cid else None
        return folder["name"] if folder else ""

    def person(self, uid: str) -> str:
        user = self.m.user(uid) or {}
        name = user.get("full_name", uid)
        return (f'<span class="person"><span class="avatar">{_e(_initials(name))}</span>'
                f"<span>{_e(name)}</span></span>")

    def last_updated(self, container_id: str, own: str | None) -> str:
        dates = [own] + [f["edit_date"] for f in self.m.subfolders(container_id)] + \
                [d["edit_date"] for d in self.m.documents_in(container_id)]
        parsed = [p for p in (_parse(d) for d in dates) if p]
        return max(parsed).isoformat() if parsed else (own or "")

    def listing(self, container_id: str, selected: str | None = None) -> tuple[int, str]:
        folders = sorted(self.m.subfolders(container_id), key=lambda f: f["name"].lower())
        docs = sorted(self.m.documents_in(container_id), key=lambda d: d["name"].lower())
        count = len(folders) + len(docs)
        if not count:
            return 0, '<div class="empty">There are no items to display.</div>'
        ws_name = self.m.workspace["name"]
        if not docs:
            head = ('<th class="c-chk"></th><th class="c-ico">' + _SVG_PAGE + '</th><th>Name <span class="sort">'
                    '&#8593;</span></th><th>Workspace Name</th><th>Owner</th><th class="c-gear">' + _SVG_GEAR + "</th>")
            rows = [f'<tr class="{"sel" if selected == f["id"] else ""}"><td class="c-chk"><span class="chk"></span>'
                    f'</td><td class="c-ico">{_SVG_FOLDER}</td><td class="c-name"><a href="{self.folder_link(f["id"])}">'
                    f'{_e(f["name"])}</a></td><td>{_e(ws_name)}</td><td>{_e(f["owner"])}</td><td class="c-gear">'
                    f"{_KEBAB}</td></tr>" for f in folders]
        else:
            head = ('<th class="c-chk"></th><th class="c-ico">' + _SVG_PAGE + '</th><th class="c-lock">' + _SVG_LOCK +
                    "</th><th>Title</th><th>Version</th><th>Doc. Number</th><th>Edit Date</th><th>File Size</th>"
                    '<th class="c-gear">' + _SVG_GEAR + "</th>")
            rows = [f'<tr><td class="c-chk"><span class="chk"></span></td><td class="c-ico">{_SVG_FOLDER}</td>'
                    f'<td class="c-lock"></td><td class="c-name"><a href="{self.folder_link(f["id"])}">{_e(f["name"])}'
                    f'</a></td><td></td><td></td><td>{_e(_short_date(f["edit_date"]))}</td><td></td>'
                    f'<td class="c-gear">{_KEBAB}</td></tr>' for f in folders]
            rows += [f'<tr><td class="c-chk"><span class="chk"></span></td><td class="c-ico">{_doc_icon(d["extension"])}'
                     f'</td><td class="c-lock"></td><td class="c-name"><a href="{self.doc_link(d)}" title="'
                     f'{_e(d["name"])}">{_e(d["name"])}</a></td><td>{d["version"]}</td><td>{d["number"]:,}</td>'
                     f'<td>{_e(_short_date(d["edit_date"]))}</td><td>{_e(size_label(d["size"]))}</td>'
                     f'<td class="c-gear">{_KEBAB}</td></tr>' for d in docs]
        return count, f'<table class="list"><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def _field(label: str, value_html: str, required: bool = False) -> str:
    star = '<span class="req">*</span>' if required else ""
    return f'<div class="field"><div class="label">{_e(label)}{star}</div><div class="value">{value_html}</div></div>'


def _security_field() -> str:
    return _field("Default Security", f'<span class="security">{_SVG_SHIELD}<span>Private</span></span>')


def _pane(tabs: list[tuple[str, str]]) -> str:
    heads = "".join(f'<button type="button" class="tab{" on" if i == 0 else ""}" data-tab="t{i}">{_e(name)}</button>'
                    for i, (name, _) in enumerate(tabs))
    bodies = "".join(f'<div class="tabbody{" on" if i == 0 else ""}" id="t{i}">{body}</div>'
                     for i, (_, body) in enumerate(tabs))
    return f'<aside class="pane"><div class="tabs">{heads}</div>{bodies}</aside>'


def _container_pane(site: Site, *, name: str, icon: str, owner: str, description: str, extra: str = "") -> str:
    props = (f'<div class="ptitle">{icon}<span>{_e(name)}</span></div>' + _security_field()
             + _field("Owner", site.person(owner), required=True)
             + _field("Description", _e(description)) + extra
             + _field("Class", "") + _field("Subclass", ""))
    security = (_security_field() + _field("Access", f'{site.person(owner)}<span class="muted"> Full Access</span>'))
    return _pane([("Properties", props), ("Security", security)])


def _doc_pane(site: Site, doc: dict) -> str:
    author = site.m.user(doc["author"]) or {}
    meta = " | ".join([f"v{doc['version']}", f"#{doc['number']:,}", _date(doc["edit_date"]), size_label(doc["size"]),
                       author.get("full_name", doc["author"])])
    props = (f'<div class="ptitle">{_doc_icon(doc["extension"])}<span>{_e(doc["name"])}</span></div>'
             f'<div class="pmeta">{_e(meta)}</div>' + _security_field()
             + _field("Author", site.person(doc["author"]), required=True)
             + _field("Comments", _e(doc.get("comment", "")))
             + _field("Type", _e(_type_label(doc)), required=True)
             + _field("Class", "DOC | Document", required=True)
             + _field("Subclass", _e(doc.get("doc_type", "")))
             + _field("Create Date", _e(_date(doc["create_date"])))
             + _field("Edit Date", _e(_date(doc["edit_date"]))))
    security = _security_field() + _field("Access", f'{site.person(doc["author"])}<span class="muted"> Full Access'
                                                    "</span>")
    versions = ('<table class="versions"><thead><tr><th>Version</th><th>Author</th><th>Edit Date</th><th>Size</th>'
                f'</tr></thead><tbody><tr><td>{doc["version"]}</td><td>{_e(author.get("full_name", doc["author"]))}'
                f'</td><td>{_e(_short_date(doc["edit_date"]))}</td><td>{_e(size_label(doc["size"]))}</td></tr>'
                "</tbody></table>")
    return _pane([("Properties", props), ("Security", security), ("Versions", versions)])


def _shell(site: Site, *, page_title: str, crumb: str, back: str | None, icon: str, heading: str, updated: str,
           action: str, toolbar: str, content: str, pane: str, scoped: bool, notice: str | None,
           search_scope: str) -> str:
    state = "Showing this conversation's changes" if scoped else "Showing the original matter data"
    notice_html = f'<div class="notice">{_e(notice)}</div>' if notice else ""
    me = site.m.user(_SIGNED_IN) or {"full_name": _SIGNED_IN}
    back_html = (f'<a class="backbtn" href="{back}" title="Back">{_SVG_BACK}</a>' if back
                 else f'<span class="backbtn off">{_SVG_BACK}</span>')
    nav = "".join(
        f'<a class="navitem{" caret" if label.startswith(("Recent", "My")) else ""}" '
        f'href="{site.ws_link() if label in ("Recent Matters", "My Matters") else "#"}">'
        f'<svg viewBox="0 0 16 16" aria-hidden="true"><path d="{path}" fill="none" stroke="#fff"/></svg>'
        f"<span>{_e(label)}</span></a>" for label, path in _NAV)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{_e(page_title)} | Mock iManage Work</title>
<style>{CSS}</style></head>
<body>
<header class="top">
  <span class="burger" aria-hidden="true"><i></i><i></i><i></i></span>
  <a class="logo" href="{site.ws_link()}"><span class="mark">m</span><span class="word"><small>iManage</small>Work</span></a>
  <div class="search"><span class="scope">{_SVG_PAGE}<span>Documents</span><b>&#8964;</b></span>
    <input type="text" disabled placeholder="Title: Search the names of Documents within {_e(search_scope)}">
    <span class="go" aria-hidden="true"><svg viewBox="0 0 16 16" width="16" height="16"><circle cx="6.5" cy="6.5" r="4.5" fill="none" stroke="#605e5c" stroke-width="1.4"/><path d="M10 10l4.5 4.5" stroke="#605e5c" stroke-width="1.6"/></svg></span></div>
  <div class="me"><span class="bell" aria-hidden="true">&#128276;</span>
    <span class="avatar lg">{_e(_initials(me["full_name"]))}</span>
    <span class="who">{_e(_SIGNED_IN)} |<br>{_e(me["full_name"])}</span><b>&#9662;</b><span class="help">?</span></div>
</header>
<div class="banner"><span>&#10515;</span><b>Want to edit, take files offline, and use desktop applications with iManage Work?</b>
  <span class="dl">Download iManage Work for Windows</span></div>
<div class="layout">
<nav class="nav">{nav}</nav>
<main>
  <div class="head">
    <div class="crumb">{crumb}</div>
    <div class="titlerow">{back_html}{icon}<h1>{_e(heading)}</h1></div>
    <div class="updated">{_SVG_REFRESH}<span>Last Updated {_e(_updated(updated))}</span></div>
    <div class="actions"><span>{action}</span>{_KEBAB}</div>
  </div>
  {notice_html}
  <div class="split">
    <section class="content">
      {toolbar}
      {content}
    </section>
    {pane}
  </div>
</main>
</div>
<div class="mock-badge" title="This is a mock iManage Work page served by a mock MCP server. It is not a real iManage library.">
  <span class="mb-top">MOCK IMANAGE</span><span class="mb-sub">{state}</span>
</div>
<script>
document.querySelectorAll('.tab').forEach(function(t){{t.addEventListener('click',function(){{
  document.querySelectorAll('.tab,.tabbody').forEach(function(n){{n.classList.remove('on')}});
  t.classList.add('on');document.getElementById(t.dataset.tab).classList.add('on');}})}});
</script>
</body></html>"""


def _toolbar(count: int) -> str:
    label = f"{count} item" + ("" if count == 1 else "s")
    return (f'<div class="toolbar"><span class="chk"></span><span>{label}</span><span class="tools">'
            '<span class="tbtn">&#9638; &#8964;</span><span class="tbtn info">i</span></span></div>'
            '<div class="filters"><span>No active filters</span><span class="fbtn">&#9663; Filters</span></div>')


def render(matter: Matter, kind: str, ident: str, prefix: str, scoped: bool, notice: str | None) -> str | None:
    site = Site(matter, prefix)
    ws = matter.workspace
    if kind == "w":
        if ident.lower() != ws["id"].lower():
            return None
        count, table = site.listing(ws["id"])
        pane = _container_pane(site, name=ws["name"], icon=_SVG_MATTER, owner=ws["owner"],
                               description=ws.get("description", ""),
                               extra=_field("Client", _e(ws.get("client", ""))))
        return _shell(site, page_title=ws["name"], crumb=f"{_SVG_LIBRARY}<span>{_e(site.library_label)}</span>",
                      back=None, icon=_SVG_MATTER, heading=ws["name"],
                      updated=site.last_updated(ws["id"], ws.get("edit_date")), action="&#128193; Folder Upload",
                      toolbar=_toolbar(count), content=table, pane=pane, scoped=scoped, notice=notice,
                      search_scope=ws["name"])
    if kind == "f":
        folder = matter.folder(ident)
        if folder is None:
            return None
        parent = folder["parent_id"]
        count, table = site.listing(folder["id"])
        pane = _container_pane(site, name=folder["name"], icon=_SVG_FOLDER, owner=folder["owner"],
                               description=folder.get("description", ""))
        crumb = (f'<span class="tri">&#9656;</span><a href="{site.container_link(parent)}">{_e(site.container_name(parent))}'
                 "</a>")
        return _shell(site, page_title=folder["name"], crumb=crumb, back=site.container_link(parent), icon=_SVG_FOLDER,
                      heading=folder["name"], updated=site.last_updated(folder["id"], folder.get("edit_date")),
                      action="&#8679; Upload File", toolbar=_toolbar(count), content=table, pane=pane, scoped=scoped,
                      notice=notice, search_scope=folder["name"])
    if kind == "d":
        match = DOC_ID.match(ident)
        doc = matter.document(int(match.group(2))) if match else None
        if doc is None or match.group(1).upper() != matter.library or int(match.group(3)) != doc["version"]:
            return None
        parent = doc["folder_id"]
        crumb = (f'<span class="tri">&#9656;</span><a href="{site.container_link(parent)}">{_e(site.container_name(parent))}'
                 "</a>")
        content = (f'<div class="toolbar"><span>Preview</span><span class="tools"><span class="muted">'
                   f'{_e(full_file_name(doc))}</span></span></div>'
                   f'<div class="preview"><article class="doc">{document_body(doc["text"])}</article></div>')
        return _shell(site, page_title=full_file_name(doc), crumb=crumb, back=site.container_link(parent),
                      icon=_doc_icon(doc["extension"]), heading=doc["name"], updated=doc["edit_date"],
                      action="&#9998; Check Out", toolbar="", content=content, pane=_doc_pane(site, doc),
                      scoped=scoped, notice=notice, search_scope=site.container_name(parent))
    return None


def not_found_page(matter: Matter, prefix: str, scoped: bool, notice: str | None) -> str:
    site = Site(matter, prefix)
    content = ('<div class="empty"><p>This item doesn\u2019t exist in this library, or it was created in a conversation '
               f'whose changes aren\u2019t available here.</p><p><a class="backlink" href="{site.ws_link()}">Back to the '
               "workspace</a></p></div>")
    return _shell(site, page_title="Item not found", crumb=f"{_SVG_LIBRARY}<span>{_e(site.library_label)}</span>",
                  back=site.ws_link(), icon="", heading="Item not found", updated="", action="", toolbar="",
                  content=content, pane="", scoped=scoped, notice=notice, search_scope=matter.workspace["name"])


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
body{font-family:"Segoe UI","Noto Sans",-apple-system,Roboto,Helvetica,Arial,sans-serif;color:#201f1e;background:#fff;font-size:14px;line-height:1.4;display:flex;flex-direction:column}
a{color:#2f59d8;text-decoration:none}
a:hover{text-decoration:underline}
svg{display:block}
.top{height:80px;flex:none;display:flex;align-items:center;gap:22px;padding:0 16px;background:#fff;border-bottom:1px solid #e1dfdd}
.burger{display:flex;flex-direction:column;gap:4px;width:18px}
.burger i{display:block;height:2px;background:#323130}
.logo{display:flex;align-items:center;gap:8px;color:#201f1e;text-decoration:none!important;margin-right:40px}
.logo .mark{width:58px;height:46px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#4b7bff,#2534d9 60%,#1fa4f0);color:#fff;font-weight:700;font-size:28px;display:flex;align-items:center;justify-content:center;font-family:Arial,sans-serif}
.logo .word{display:flex;flex-direction:column;font-size:26px;line-height:1;color:#3b3a39}
.logo .word small{font-size:15px;font-weight:600}
.search{display:flex;align-items:stretch;border:1px solid #c8c6c4;height:36px;width:690px;max-width:48vw}
.search .scope{display:flex;align-items:center;gap:8px;padding:0 12px;background:#f3f2f1;border-right:1px solid #c8c6c4;white-space:nowrap}
.search .scope svg{width:14px;height:16px}
.search .scope b{font-weight:400;margin-left:14px}
.search input{flex:1;border:0;padding:0 12px;font:inherit;background:#fff;color:#605e5c;min-width:0}
.search .go{width:40px;border-left:1px solid #c8c6c4;display:flex;align-items:center;justify-content:center}
.me{margin-left:auto;display:flex;align-items:center;gap:12px;font-size:11px;color:#323130}
.bell{font-size:20px;filter:grayscale(1)}
.avatar{width:22px;height:22px;border-radius:50%;border:1px solid #a19f9d;display:inline-flex;align-items:center;justify-content:center;font-size:10px;color:#605e5c;background:#fff;flex:none}
.avatar.lg{width:32px;height:32px;font-size:12px}
.who{line-height:1.35;min-width:110px}
.help{font-size:20px;margin-left:16px}
.banner{flex:none;display:flex;align-items:center;gap:16px;padding:7px 18px;background:#fdf6d8;border-bottom:3px solid #f2c94c;font-size:14px}
.banner b{font-weight:600}
.banner .dl{border:1px solid #c8c6c4;background:#fff;padding:5px 12px}
.layout{flex:1;display:flex;min-height:0}
.nav{width:200px;flex:none;background:#0a0a6b;color:#fff;overflow:auto}
.navitem{display:flex;align-items:center;gap:10px;padding:0 16px 0 32px;height:53px;color:#fff;border-bottom:1px solid #2b2b86;font-size:13px;position:relative}
.navitem:hover{background:#1a1a80;text-decoration:none}
.navitem svg{width:18px;height:18px}
.navitem.caret:before{content:"";position:absolute;left:14px;border:4px solid transparent;border-left:5px solid #fff}
main{flex:1;display:flex;flex-direction:column;min-width:0;min-height:0}
.head{position:relative;padding:10px 12px 8px;border-bottom:1px solid #e1dfdd}
.crumb{display:flex;align-items:center;gap:6px;color:#605e5c;font-size:14px;margin-left:2px}
.crumb a{color:#605e5c}
.crumb .tri{font-size:12px;color:#323130;margin-right:8px}
.ico{width:26px;height:22px;flex:none}
.ico.sm{width:14px;height:14px}
.titlerow{display:flex;align-items:center;gap:14px;margin-top:6px}
.backbtn{width:28px;height:28px;border:1px solid #c8c6c4;display:flex;align-items:center;justify-content:center;color:#323130;background:#fff}
.backbtn svg{width:14px;height:14px}
.backbtn.off{opacity:.45}
h1{font-size:19px;font-weight:400;margin:0}
.updated{display:flex;align-items:center;gap:8px;font-size:12px;margin:8px 0 0 44px}
.updated svg{width:15px;height:15px}
.actions{position:absolute;right:14px;top:52px;display:flex;align-items:center;gap:22px;color:#323130}
.kebab{font-size:20px;font-weight:700;color:#201f1e;line-height:1}
.notice{background:#fff4ce;color:#3b2f00;padding:9px 14px;border-bottom:1px solid #f2c94c}
.split{flex:1;display:flex;min-height:0}
.content{flex:1;min-width:0;overflow:auto;padding-bottom:110px}
.toolbar{display:flex;align-items:center;gap:12px;height:40px;padding:0 14px;background:#f3f2f1;border-bottom:1px solid #e1dfdd;color:#605e5c;font-size:13px}
.toolbar .tools{margin-left:auto;display:flex;gap:0}
.tbtn{border:1px solid #c8c6c4;background:#fff;padding:4px 10px;color:#323130}
.tbtn.info{color:#fff;background:#2f59d8;border-radius:50%;width:16px;height:16px;padding:0;font-size:10px;font-weight:700;display:flex;align-items:center;justify-content:center;margin:4px 8px}
.filters{display:flex;align-items:center;justify-content:space-between;height:42px;padding:0 12px;border-bottom:1px solid #e1dfdd;color:#605e5c}
.fbtn{border:1px solid #c8c6c4;padding:4px 12px;font-size:12px}
.chk{display:inline-block;width:15px;height:15px;border:1.5px solid #605e5c;border-radius:2px;background:#fff}
.toolbar .chk{border-color:#c8c6c4}
table.list{border-collapse:collapse;width:100%}
table.list th{text-align:left;font-weight:600;font-size:12px;padding:10px 8px;border-bottom:1px solid #e1dfdd;white-space:nowrap}
table.list th+th:not(.c-gear):not(.c-ico):not(.c-lock){border-left:0}
table.list td{padding:0 8px;height:48px;border-bottom:1px solid #e1dfdd;white-space:nowrap;max-width:320px;overflow:hidden;text-overflow:ellipsis}
table.list tr:hover td{background:#f3f2f1}
table.list tr.sel td{background:#edebe9}
.c-chk{width:42px;text-align:center}
.c-ico,.c-lock{width:40px}
.c-ico svg,.c-lock svg{width:16px;height:18px}
td.c-ico svg{width:22px;height:20px}
.c-gear{width:40px;text-align:center}
.c-gear svg{width:16px;height:16px;margin:auto}
.c-name a{color:#201f1e}
.sort{font-weight:400}
.empty{padding:28px 18px;color:#605e5c}
.pane{width:340px;flex:none;border-left:1px solid #e1dfdd;overflow:auto;padding-bottom:110px}
.tabs{display:flex;border-bottom:1px solid #e1dfdd}
.tab{flex:1;background:none;border:0;border-bottom:3px solid transparent;padding:12px 6px 10px;font:inherit;font-size:14px;color:#323130;cursor:pointer}
.tab.on{border-bottom-color:#2f59d8;font-weight:600}
.tabbody{display:none;padding:14px 12px}
.tabbody.on{display:block}
.ptitle{display:flex;align-items:flex-start;gap:12px;font-size:16px;font-weight:600;color:#323130;margin-bottom:8px}
.ptitle .ico{margin-top:2px}
.pmeta{font-size:12px;color:#323130;margin:0 0 16px 6px;line-height:1.8}
.field{margin:0 0 22px}
.field .label{font-size:12px;font-weight:600;margin-bottom:8px}
.field .value{min-height:16px;padding-left:2px;color:#323130}
.req{color:#c4314b;margin-left:2px}
.security{display:flex;align-items:center;gap:10px;color:#2f59d8;padding-left:8px}
.security svg{width:16px;height:18px}
.person{display:inline-flex;align-items:center;gap:8px}
.muted{color:#8a8886}
table.versions{border-collapse:collapse;width:100%;font-size:12px}
table.versions th,table.versions td{text-align:left;padding:6px 4px;border-bottom:1px solid #e1dfdd}
.preview{padding:18px;background:#f3f2f1;min-height:100%}
article.doc{background:#fff;border:1px solid #e1dfdd;padding:36px 44px;max-width:860px;margin:0 auto;box-shadow:0 1px 3px rgba(0,0,0,.08)}
article.doc p{margin:0 0 8px}
.table-wrap{overflow-x:auto;margin:6px 0 14px}
article.doc table{border-collapse:collapse;font-size:13px}
article.doc th,article.doc td{border:1px solid #c8c6c4;padding:5px 8px;vertical-align:top;text-align:left}
article.doc th{background:#f3f2f1;font-weight:600}
.backlink{font-weight:600}
.mock-badge{position:fixed;right:16px;bottom:16px;z-index:10;display:flex;flex-direction:column;align-items:flex-end;background:#d13438;color:#fff;border-radius:8px;padding:6px 12px;box-shadow:0 4px 14px rgba(0,0,0,.2);font-size:12px;line-height:1.35}
.mock-badge .mb-top{font-weight:700;letter-spacing:.06em}
.mock-badge .mb-sub{opacity:.92}
@media (max-width:1100px){.pane{display:none}.search{display:none}}
@media (max-width:800px){.nav{display:none}.banner{display:none}}
"""
