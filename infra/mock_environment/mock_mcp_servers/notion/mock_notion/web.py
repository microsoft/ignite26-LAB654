"""Browsable, read-only HTML pages for the mock workspace, styled like Notion's light theme.

Routes (served next to /mcp):
* ``/p/{ref}``: the original (seed) workspace.
* ``/v/{token}/p/{ref}``: the workspace as one conversation left it. ``token`` is the store's view token
  for that conversation (see ``StateStore.view_token``); tool results link here when ``PUBLIC_BASE_URL``
  is set. Unknown or expired tokens fall back to the seed with a notice.
* ``/`` and ``/v/{token}/``: redirect to the workspace's top page.
"""

from __future__ import annotations

import html
import re
from datetime import datetime

from .common import parse_ref, rewrite_links
from .store import StateStore, Workspace

_TOKEN = re.compile(r"[0-9a-f]{20}")

# Notion light-theme select colours: (background, text).
COLORS = {
    "default": ("rgba(227,226,224,0.5)", "rgb(50,48,44)"),
    "gray": ("rgb(227,226,224)", "rgb(50,48,44)"),
    "brown": ("rgb(238,224,218)", "rgb(68,42,30)"),
    "orange": ("rgb(250,222,201)", "rgb(73,41,14)"),
    "yellow": ("rgb(253,236,200)", "rgb(64,44,27)"),
    "green": ("rgb(219,237,219)", "rgb(28,56,41)"),
    "blue": ("rgb(211,229,239)", "rgb(24,51,71)"),
    "purple": ("rgb(232,222,238)", "rgb(65,36,84)"),
    "pink": ("rgb(245,224,233)", "rgb(76,35,55)"),
    "red": ("rgb(255,226,221)", "rgb(93,23,21)"),
}

_ICON_PAGE = (
    '<svg viewBox="0 0 16 16" class="ico"><path d="M4.35 1.5h4.9l3.25 3.25v8.4c0 .75-.6 1.35-1.35 1.35h-6.8'
    'c-.75 0-1.35-.6-1.35-1.35V2.85c0-.75.6-1.35 1.35-1.35z" fill="none" stroke="currentColor" stroke-width="1.1"/>'
    '<path d="M9 1.7v3.3h3.3M5.5 8h5M5.5 10.3h5M5.5 12.5h3" fill="none" stroke="currentColor" stroke-width="1.1"/></svg>'
)
_ICON_DB = (
    '<svg viewBox="0 0 16 16" class="ico"><rect x="1.8" y="2.3" width="12.4" height="11.4" rx="1.6" fill="none" '
    'stroke="currentColor" stroke-width="1.1"/><path d="M1.8 6h12.4M1.8 9.8h12.4M6.2 6v7.7" stroke="currentColor" '
    'stroke-width="1.1"/></svg>'
)
_TEXT_ICON = "\u2261"
PROP_ICONS = {"title": "Aa", "text": "\u2261", "select": "\u2304", "date": "\u25a6", "number": "#",
              "person": "\u263a", "checkbox": "\u2611", "url": "\u29c9"}


def _e(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _date(value: str | None, with_time: bool = False) -> str:
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    text = f"{dt.strftime('%B')} {dt.day}, {dt.year}"
    if with_time and "T" in value:
        text += " " + dt.strftime("%I:%M %p").lstrip("0")
    return text


def _short_date(value: str | None) -> str:
    try:
        dt = datetime.fromisoformat((value or "").replace("Z", "+00:00"))
    except ValueError:
        return ""
    return f"{dt.strftime('%b')} {dt.day}, {dt.year}"


# --- markdown ---------------------------------------------------------------------------------------------------

_INLINE = re.compile(
    r"`(?P<code>[^`]+)`"
    r"|\[(?P<ltext>[^\]]+)\]\((?P<lurl>[^)\s]+)\)"
    r"|\*\*(?P<bold>.+?)\*\*"
    r"|~~(?P<strike>.+?)~~"
    r"|(?<![\w*])\*(?P<ital>[^*\s][^*]*?)\*(?![\w*])"
)
_TAG_LINK = re.compile(r'^<(page|database)\s+url="\{*([^"}]+)\}*"[^>]*>(.*?)</\1>$')


def _href(url: str, prefix: str) -> tuple[str, bool]:
    local = rewrite_links(url, prefix)
    if local != url:
        return local, False
    if re.match(r"(?i)^(https?:|mailto:)", url):
        return url, True
    return "#", False


def inline(text: str, prefix: str) -> str:
    out, pos = [], 0
    for m in _INLINE.finditer(text):
        out.append(_e(text[pos:m.start()]))
        if m.group("code") is not None:
            out.append(f"<code>{_e(m.group('code'))}</code>")
        elif m.group("ltext") is not None:
            href, external = _href(m.group("lurl"), prefix)
            target = ' target="_blank" rel="noopener noreferrer"' if external else ""
            out.append(f'<a class="link" href="{_e(href)}"{target}>{inline(m.group("ltext"), prefix)}</a>')
        elif m.group("bold") is not None:
            out.append(f"<strong>{inline(m.group('bold'), prefix)}</strong>")
        elif m.group("strike") is not None:
            out.append(f"<s>{inline(m.group('strike'), prefix)}</s>")
        else:
            out.append(f"<em>{inline(m.group('ital'), prefix)}</em>")
        pos = m.end()
    out.append(_e(text[pos:]))
    return "".join(out)


def markdown(text: str, prefix: str, titles: dict[str, str] | None = None) -> str:
    """Notion-flavoured markdown subset -> HTML blocks. Everything is escaped; unknown tags show as text."""
    blocks: list[str] = []
    lines = text.replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        indent = (len(raw.expandtabs(4)) - len(raw.expandtabs(4).lstrip(" "))) // 2
        style = f' style="margin-left:{indent * 1.5}em"' if indent else ""
        i += 1
        if not line:
            continue
        if line.startswith("```"):
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            blocks.append(f'<pre class="code">{_e(chr(10).join(code))}</pre>')
        elif m := re.match(r"^(#{1,3})\s+(.*)$", line):
            level = len(m.group(1))
            blocks.append(f'<h{level + 1} class="h{level}">{inline(m.group(2), prefix)}</h{level + 1}>')
        elif re.fullmatch(r"-{3,}|\*{3,}", line):
            blocks.append('<div class="divider"></div>')
        elif line.startswith(">"):
            blocks.append(f'<blockquote{style}>{inline(line.lstrip("> "), prefix)}</blockquote>')
        elif m := re.match(r"^[-*]\s+\[( |x|X)\]\s+(.*)$", line):
            done = m.group(1).lower() == "x"
            blocks.append(f'<div class="todo{" done" if done else ""}"{style}><span class="box">'
                          f'{"&#10003;" if done else ""}</span><span>{inline(m.group(2), prefix)}</span></div>')
        elif m := re.match(r"^[-*+]\s+(.*)$", line):
            blocks.append(f'<div class="bullet"{style}><span class="dot">\u2022</span>'
                          f'<span>{inline(m.group(1), prefix)}</span></div>')
        elif m := re.match(r"^(\d+)[.)]\s+(.*)$", line):
            blocks.append(f'<div class="bullet"{style}><span class="num">{m.group(1)}.</span>'
                          f'<span>{inline(m.group(2), prefix)}</span></div>')
        elif m := _TAG_LINK.match(line):
            href, _ = _href(m.group(2), prefix)
            icon = _ICON_DB if m.group(1) == "database" else _ICON_PAGE
            blocks.append(f'<a class="child" href="{_e(href)}">{icon}<span>{_e(m.group(3))}</span></a>')
        else:
            blocks.append(f'<p{style}>{inline(line, prefix)}</p>')
    return "\n".join(blocks)


# --- views ------------------------------------------------------------------------------------------------------


def _title_of_row(db: dict, row: dict) -> str:
    return next((row["properties"].get(p["name"]) for p in db["schema"] if p["type"] == "title"), "") or "Untitled"


def _pill(prop: dict, value: str | None) -> str:
    if not value:
        return ""
    color = next((o.get("color", "default") for o in prop.get("options", []) if o["name"] == value), "default")
    bg, fg = COLORS.get(color, COLORS["default"])
    return f'<span class="pill" style="background:{bg};color:{fg}">{_e(value)}</span>'


def _value(prop: dict, value) -> str:
    t = prop["type"]
    if t == "select":
        return _pill(prop, value)
    if t == "date":
        if not value or not value.get("start"):
            return ""
        dt = bool(value.get("is_datetime"))
        text = _date(value["start"], dt)
        if value.get("end"):
            text += " \u2192 " + _date(value["end"], dt)
        return _e(text)
    if t == "number":
        if value is None:
            return ""
        return _e(int(value) if float(value).is_integer() else value)
    return _e(value)


def _plain(prop: dict, value) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", _value(prop, value)))


class Site:
    def __init__(self, ws: Workspace, prefix: str) -> None:
        self.ws = ws
        self.prefix = prefix

    def link(self, oid: str) -> str:
        return self.prefix + oid.replace("-", "")

    def roots(self) -> list[dict]:
        return [p for p in self.ws.pages if not p.get("parent_id")]

    def children(self, parent_id: str) -> list[tuple[str, dict]]:
        kids = [("page", p) for p in self.ws.pages if p.get("parent_id") == parent_id]
        kids += [("database", d) for d in self.ws.databases if d.get("parent_id") == parent_id]
        return kids

    def sidebar(self, current: set[str]) -> str:
        def tree(kind: str, obj: dict, depth: int) -> str:
            active = " active" if obj["id"] in current else ""
            icon = _ICON_DB if kind == "database" else _ICON_PAGE
            item = (f'<a class="nav{active}" style="padding-left:{8 + depth * 14}px" href="{self.link(obj["id"])}">'
                    f'{icon}<span>{_e(obj["title"])}</span></a>')
            if kind == "page":
                item += "".join(tree(k, o, depth + 1) for k, o in self.children(obj["id"]))
            return item

        return "".join(tree("page", p, 0) for p in self.roots())

    def crumbs(self, parent_id: str | None, tail: list[tuple[str, str | None]]) -> str:
        parts = [(a["obj"]["title"], self.link(a["obj"]["id"])) for a in reversed(self.ws.ancestors(parent_id))]
        parts += tail
        out = []
        for i, (title, href) in enumerate(parts):
            label = _e(title)
            out.append(f'<a href="{href}">{label}</a>' if href and i < len(parts) - 1 else f"<span>{label}</span>")
        return '<span class="sep">/</span>'.join(out)

    def child_blocks(self, page: dict) -> str:
        content = page.get("content", "")
        blocks = []
        for kind, obj in self.children(page["id"]):
            if obj["id"].replace("-", "") in content:
                continue
            icon = _ICON_DB if kind == "database" else _ICON_PAGE
            blocks.append(f'<a class="child" href="{self.link(obj["id"])}">{icon}<span>{_e(obj["title"])}</span></a>')
        return "\n".join(blocks)

    def page_body(self, page: dict) -> str:
        content = page.get("content", "")
        first, _, rest = content.lstrip().partition("\n")
        if first.strip() == f"# {page['title']}":
            content = rest
        return markdown(content, self.prefix) + self.child_blocks(page)

    def table(self, db: dict) -> str:
        props = {p["name"]: p for p in db["schema"]}
        cols = [props[n] for n in db.get("view") or [p["name"] for p in db["schema"]] if n in props]
        head = "".join(
            f'<th class="{"title-col" if p["type"] == "title" else ""}"><span class="pi">'
            f'{PROP_ICONS.get(p["type"], _TEXT_ICON)}</span>{_e(p["name"])}</th>'
            for p in cols
        )
        body = []
        for row in db["rows"]:
            cells = []
            for p in cols:
                value = row["properties"].get(p["name"])
                if p["type"] == "title":
                    cells.append(f'<td class="title-col"><a href="{self.link(row["id"])}">{_ICON_PAGE}'
                                 f'<span>{_e(value or "Untitled")}</span><span class="open">OPEN</span></a></td>')
                else:
                    cells.append(f'<td title="{_e(_plain(p, value))}">{_value(p, value)}</td>')
            body.append("<tr>" + "".join(cells) + "</tr>")
        return (
            f'<div class="views"><span class="view active">{_ICON_DB}Show All</span></div>'
            f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table>'
            f'<div class="count">COUNT <b>{len(db["rows"])}</b></div></div>'
        )

    def row_properties(self, db: dict, row: dict) -> str:
        out = []
        for p in db["schema"]:
            if p["type"] == "title":
                continue
            value = _value(p, row["properties"].get(p["name"])) or '<span class="empty">Empty</span>'
            out.append(f'<div class="prop"><div class="pname"><span class="pi">{PROP_ICONS.get(p["type"], _TEXT_ICON)}'
                       f'</span>{_e(p["name"])}</div><div class="pval">{value}</div></div>')
        return '<div class="props">' + "".join(out) + "</div>"


def _shell(site: Site, *, title: str, crumbs: str, edited: str | None, current: set[str], body: str,
           wide: bool, scoped: bool, notice: str | None, icon: str) -> str:
    state = "Showing this conversation's changes" if scoped else "Showing the original workspace data"
    notice_html = f'<div class="notice">{_e(notice)}</div>' if notice else ""
    edited_html = f'<span class="edited">Edited {_e(_short_date(edited))}</span>' if edited else ""
    workspace = _e(site.ws.data.get("workspace", {}).get("name", "Workspace"))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{_e(title)} | Mock Notion</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23fff' stroke='%23000' stroke-width='3'/%3E%3Ctext x='16' y='23' font-size='19' font-family='Georgia,serif' font-weight='700' text-anchor='middle'%3EN%3C/text%3E%3C/svg%3E">
<style>{CSS}</style></head>
<body>
<aside class="sidebar">
  <div class="ws"><span class="ws-icon">{workspace[:1]}</span><span>{workspace}</span></div>
  <div class="nav-label">Workspace</div>
  {site.sidebar(current)}
</aside>
<main>
  <header class="topbar"><div class="crumbs">{crumbs}</div>{edited_html}</header>
  <div class="scroller">
    {notice_html}
    <div class="page{' wide' if wide else ''}">
      <div class="page-icon">{icon}</div>
      <h1 class="title">{_e(title)}</h1>
      {body}
    </div>
  </div>
</main>
<div class="mock-badge" title="This is a mock Notion page served by the LAB654 mock MCP server. It is not a real Notion workspace.">
  <span class="mb-top">MOCK NOTION &middot; LAB654</span><span class="mb-sub">{state}</span>
</div>
</body></html>"""


def render(ws: Workspace, ref: str, prefix: str, scoped: bool, notice: str | None) -> str | None:
    parsed = parse_ref(ref)
    if not parsed or parsed[0] != "page":
        return None
    oid = parsed[1]
    site = Site(ws, prefix)
    page = ws.page(oid)
    if page:
        return _shell(site, title=page["title"], crumbs=site.crumbs(page.get("parent_id"), [(page["title"], None)]),
                      edited=page.get("edited"), current={oid}, body=site.page_body(page), wide=False,
                      scoped=scoped, notice=notice, icon=_ICON_PAGE)
    db = ws.database(oid)
    if db:
        return _shell(site, title=db["title"], crumbs=site.crumbs(db.get("parent_id"), [(db["title"], None)]),
                      edited=db.get("edited"), current={oid}, body=site.table(db), wide=True, scoped=scoped,
                      notice=notice, icon=_ICON_DB)
    db, row = ws.row(oid)
    if row:
        title = _title_of_row(db, row)
        crumbs = site.crumbs(db.get("parent_id"), [(db["title"], site.link(db["id"])), (title, None)])
        body = site.row_properties(db, row) + '<div class="divider"></div>' + markdown(row.get("content", ""), prefix)
        return _shell(site, title=title, crumbs=crumbs, edited=row.get("edited"), current={db["id"]}, body=body,
                      wide=False, scoped=scoped, notice=notice, icon=_ICON_PAGE)
    return None


def not_found_page(ws: Workspace, prefix: str, scoped: bool, notice: str | None) -> str:
    site = Site(ws, prefix)
    home = site.roots()[0]["id"] if site.roots() else ""
    body = (f'<p>This page doesn\u2019t exist in this workspace, or it was created in a conversation whose changes '
            f'aren\u2019t available here.</p><a class="child" href="{site.link(home)}">{_ICON_PAGE}'
            f'<span>Back to the workspace</span></a>')
    return _shell(site, title="Page not found", crumbs="<span>Page not found</span>", edited=None, current=set(),
                  body=body, wide=False, scoped=scoped, notice=notice, icon=_ICON_PAGE)


def build_routes(store: StateStore) -> list:
    from starlette.responses import HTMLResponse, RedirectResponse
    from starlette.routing import Route

    def resolve(request) -> tuple[Workspace, str, bool, str | None] | None:
        token = request.path_params.get("token")
        if token is None:
            ws, _ = store.read_by_token(None)
            return ws, "/p/", False, None
        if not _TOKEN.fullmatch(token):
            return None
        ws, scoped = store.read_by_token(token)
        notice = None if scoped else (
            "No saved changes were found for this conversation (nothing was changed yet, or the changes expired "
            "after about 2 hours). Showing the original workspace data.")
        return ws, f"/v/{token}/p/", scoped, notice

    headers = {"Cache-Control": "no-store", "X-Robots-Tag": "noindex, nofollow"}

    async def page(request):
        found = resolve(request)
        if found is None:
            ws, _ = store.read_by_token(None)
            return HTMLResponse(not_found_page(ws, "/p/", False, None), status_code=404, headers=headers)
        ws, prefix, scoped, notice = found
        text = render(ws, request.path_params["ref"], prefix, scoped, notice)
        if text is None:
            return HTMLResponse(not_found_page(ws, prefix, scoped, notice), status_code=404, headers=headers)
        return HTMLResponse(text, headers=headers)

    async def home(request):
        found = resolve(request)
        if found is None:
            return RedirectResponse("/", status_code=302)
        ws, prefix, _, _ = found
        roots = [p for p in ws.pages if not p.get("parent_id")]
        target = prefix + roots[0]["id"].replace("-", "") if roots else "/healthz"
        return RedirectResponse(target, status_code=302)

    return [
        Route("/", home),
        Route("/p/{ref}", page),
        Route("/v/{token}", home),
        Route("/v/{token}/", home),
        Route("/v/{token}/p/{ref}", page),
    ]


CSS = """
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{display:flex;font-family:ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI Variable Display","Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif;color:rgb(55,53,47);background:#fff;-webkit-font-smoothing:antialiased;font-size:16px;line-height:1.5}
a{color:inherit;text-decoration:none}
.ico{width:18px;height:18px;flex:none;color:rgba(55,53,47,.65)}
.sidebar{width:240px;flex:none;background:rgb(247,247,245);height:100vh;overflow:auto;padding:8px 6px;border-right:1px solid rgba(55,53,47,.09);font-size:14px;color:rgba(55,53,47,.85)}
.ws{display:flex;align-items:center;gap:8px;padding:6px 8px;font-weight:600;color:rgb(55,53,47)}
.ws-icon{width:22px;height:22px;border-radius:4px;background:rgb(55,53,47);color:#fff;font-size:12px;display:flex;align-items:center;justify-content:center}
.nav-label{font-size:12px;font-weight:500;color:rgba(55,53,47,.5);padding:14px 8px 4px}
.nav{display:flex;align-items:center;gap:6px;min-height:28px;border-radius:6px;padding-right:8px;white-space:nowrap;overflow:hidden}
.nav span{overflow:hidden;text-overflow:ellipsis}
.nav:hover{background:rgba(55,53,47,.06)}
.nav.active{background:rgba(55,53,47,.08);color:rgb(55,53,47);font-weight:500}
main{flex:1;display:flex;flex-direction:column;height:100vh;min-width:0}
.topbar{height:45px;flex:none;display:flex;align-items:center;justify-content:space-between;padding:0 14px;font-size:14px}
.crumbs{display:flex;align-items:center;gap:2px;overflow:hidden;white-space:nowrap;min-width:0;flex:1;margin-right:12px}
.crumbs>*{overflow:hidden;text-overflow:ellipsis;flex:none;max-width:240px}
.crumbs a,.crumbs span{padding:2px 6px;border-radius:4px}
.crumbs a:hover{background:rgba(55,53,47,.06)}
.crumbs .sep{color:rgba(55,53,47,.4);padding:0 1px}
.edited{color:rgba(55,53,47,.5);font-size:14px;white-space:nowrap;flex:none}
.scroller{flex:1;overflow:auto}
.notice{max-width:900px;margin:12px auto 0;background:rgb(251,243,219);color:rgb(64,44,27);border-radius:6px;padding:10px 14px;font-size:14px}
.page{max-width:708px;margin:0 auto;padding:60px 24px 160px}
.page.wide{max-width:1100px}
.page-icon .ico{width:56px;height:56px;color:rgba(55,53,47,.55)}
h1.title{font-size:40px;line-height:1.2;font-weight:700;margin:8px 0 18px;letter-spacing:-.01em}
h2.h1{font-size:1.875em;font-weight:600;margin:1.4em 0 .2em;line-height:1.3}
h3.h2{font-size:1.5em;font-weight:600;margin:1.1em 0 .1em;line-height:1.3}
h4.h3{font-size:1.25em;font-weight:600;margin:1em 0 .1em;line-height:1.3}
p{margin:2px 0;padding:3px 2px;min-height:1.5em}
.bullet,.todo{display:flex;gap:6px;padding:3px 2px}
.bullet .dot{width:20px;text-align:center;flex:none}
.bullet .num{min-width:20px;text-align:right;padding-right:2px;flex:none}
.todo .box{width:16px;height:16px;margin:4px 4px 0 2px;border:1.5px solid rgb(55,53,47);border-radius:2px;font-size:12px;line-height:13px;text-align:center;flex:none}
.todo.done .box{background:rgb(35,131,226);border-color:rgb(35,131,226);color:#fff}
.todo.done span:last-child{text-decoration:line-through;color:rgba(55,53,47,.5)}
blockquote{margin:6px 0;padding:3px 14px;border-left:3px solid currentColor}
.divider{border-top:1px solid rgba(55,53,47,.16);margin:14px 0}
code{font-family:"SFMono-Regular",Menlo,Consolas,monospace;background:rgba(135,131,120,.15);color:#eb5757;border-radius:4px;font-size:85%;padding:.2em .4em}
pre.code{background:rgb(247,246,243);border-radius:4px;padding:28px 24px;font-family:"SFMono-Regular",Menlo,Consolas,monospace;font-size:85%;overflow:auto}
a.link{color:inherit;text-decoration:underline;text-decoration-color:rgba(55,53,47,.4);text-underline-offset:2px}
a.link:hover{text-decoration-color:rgb(55,53,47)}
.child{display:flex;align-items:center;gap:8px;padding:4px 2px;border-radius:4px;font-weight:500;text-decoration:underline;text-decoration-color:rgba(55,53,47,.25);text-underline-offset:3px;margin:2px 0}
.child:hover{background:rgba(55,53,47,.06)}
.views{display:flex;gap:4px;border-bottom:1px solid rgba(55,53,47,.09);margin:6px 0 0;font-size:14px}
.view{display:flex;align-items:center;gap:6px;padding:6px 8px;color:rgba(55,53,47,.65)}
.view.active{color:rgb(55,53,47);font-weight:500;box-shadow:inset 0 -2px 0 rgb(55,53,47)}
.view .ico{width:15px;height:15px}
.table-wrap{overflow-x:auto}
table{border-collapse:collapse;font-size:14px;width:100%;min-width:760px}
th{font-weight:400;color:rgba(55,53,47,.65);text-align:left;padding:7px 8px;border-bottom:1px solid rgba(55,53,47,.09);border-right:1px solid rgba(55,53,47,.09);white-space:nowrap}
td{padding:7px 8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:280px;border-bottom:1px solid rgba(55,53,47,.09);border-right:1px solid rgba(55,53,47,.09);vertical-align:top}
th:last-child,td:last-child{border-right:none}
th .pi,.pname .pi{display:inline-block;width:18px;margin-right:4px;color:rgba(55,53,47,.45);text-align:center;font-size:13px}
td.title-col{font-weight:500;min-width:260px;max-width:340px}
td.title-col a{display:flex;align-items:center;gap:6px;min-width:0}
td.title-col a span:not(.open){overflow:hidden;text-overflow:ellipsis}
td.title-col .ico{width:16px;height:16px}
td.title-col .open{margin-left:auto;font-size:11px;font-weight:500;color:rgba(55,53,47,.65);border:1px solid rgba(55,53,47,.16);border-radius:4px;padding:0 5px;visibility:hidden;background:#fff}
tr:hover td.title-col .open{visibility:visible}
tr:hover td{background:rgba(55,53,47,.02)}
.pill{display:inline-block;border-radius:4px;padding:0 6px;font-size:14px;line-height:20px;white-space:nowrap}
.count{font-size:12px;color:rgba(55,53,47,.5);padding:8px;letter-spacing:.03em}
.count b{color:rgb(55,53,47);font-weight:500;margin-left:4px}
.props{margin:4px 0 10px;font-size:14px}
.prop{display:flex;min-height:34px;align-items:flex-start}
.pname{width:160px;flex:none;color:rgba(55,53,47,.65);padding:6px 6px}
.pval{padding:6px 8px;flex:1;min-width:0}
.empty{color:rgba(55,53,47,.35)}
.mock-badge{position:fixed;right:16px;bottom:16px;z-index:10;display:flex;flex-direction:column;align-items:flex-end;background:rgb(235,87,87);color:#fff;border-radius:8px;padding:6px 12px;box-shadow:0 4px 14px rgba(15,15,15,.18);font-size:12px;line-height:1.35;pointer-events:auto}
.mock-badge .mb-top{font-weight:700;letter-spacing:.06em}
.mock-badge .mb-sub{opacity:.92}
@media (max-width:800px){.sidebar{display:none}.page{padding:40px 18px 140px}}
"""
