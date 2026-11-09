"""Read-only Jira Cloud look-alike for the mock site.

Routes (served next to /mcp); every page also exists under ``/v/{token}`` for one conversation's own changes:

* ``/`` and ``/jira/projects``: redirect to the Aurora board.
* ``/jira/software/projects/AUR/boards/57``: the active sprint board. ``.../backlog`` and ``/jira/software/projects/AUR/list``
  show the backlog and a list of every work item.
* ``/browse/{key}``: the work item view. An unscoped link to an item that a live conversation created redirects to
  that conversation's view.
* ``/ex/jira/{cloudId}/rest/api/3/issue/{idOrKey}``: REST ``self`` links in tool results redirect to the browse page.
* ``/wiki/spaces/AUR/pages/{id}/{slug}``: a Confluence page with its comments; ``/wiki`` and ``/wiki/spaces/AUR``
  open the space home page. ``/wiki/rest/api/content/{id}`` and ``/wiki/x/{tiny}`` redirect to the page.
* Icon URLs used in tool results (issue types, priorities, project avatar) return SVGs.
"""

from __future__ import annotations

import html as _html
import re
from datetime import datetime, timedelta, timezone

from . import render
from .store import Site, StateStore

_TOKEN = re.compile(r"[0-9a-f]{20}")
_HEADERS = {"Cache-Control": "no-store", "X-Robots-Tag": "noindex, nofollow"}
_EXPIRED = ("No saved changes were found for this conversation (nothing was changed yet, or the changes expired after "
            "about 2 hours). Showing the original Jira data.")
_AVATAR_COLORS = ("#1D7AFC", "#22A06B", "#E56910", "#8270DB", "#C9372C", "#2898BD", "#B38600")
_LOZENGE = {2: ("#DCDFE4", "#44546F"), 4: ("#CCE0FF", "#0055CC"), 3: ("#BAF3DB", "#216E4E")}


def e(value) -> str:
    return _html.escape("" if value is None else str(value), quote=True)


# --- time ----------------------------------------------------------------------------------------------------------

def _nth_sunday(year: int, month: int, n: int) -> datetime:
    first = datetime(year, month, 1)
    return first + timedelta(days=(6 - first.weekday()) % 7 + 7 * (n - 1))


def to_et(moment: datetime) -> datetime:
    """US Eastern wall time (the site's time zone)."""
    utc = moment.astimezone(timezone.utc).replace(tzinfo=None)
    start = _nth_sunday(utc.year, 3, 2) + timedelta(hours=7)
    end = _nth_sunday(utc.year, 11, 1) + timedelta(hours=6)
    return utc + timedelta(hours=-4 if start <= utc < end else -5)


def parse(stamp: str | None) -> datetime | None:
    if not stamp:
        return None
    text = stamp.replace("Z", "+00:00")
    if len(text) >= 5 and text[-5] in "+-" and text[-3] != ":":
        text = text[:-2] + ":" + text[-2:]
    try:
        value = datetime.fromisoformat(text)
    except ValueError:
        return None
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _clock(local: datetime) -> str:
    return f"{local.hour % 12 or 12}:{local.minute:02d} {'AM' if local.hour < 12 else 'PM'}"


def full_date(stamp: str | None) -> str:
    moment = parse(stamp)
    if moment is None:
        return ""
    local = to_et(moment)
    return f"{local:%B} {local.day}, {local.year} at {_clock(local)}"


def short_date(stamp: str | None) -> str:
    moment = parse(stamp)
    if moment is None:
        return ""
    local = to_et(moment)
    return f"{local.day} {local:%b}"


def ago(stamp: str | None, now: datetime) -> str:
    moment = parse(stamp)
    if moment is None:
        return ""
    seconds = (now - moment).total_seconds()
    if seconds < 0 or seconds >= 7 * 86400:
        return full_date(stamp)
    if seconds < 60:
        return "just now"
    for size, unit in ((86400, "day"), (3600, "hour"), (60, "minute")):
        if seconds >= size:
            n = int(seconds // size)
            return f"{n} {unit}{'s' if n != 1 else ''} ago"
    return "just now"


# --- markdown ------------------------------------------------------------------------------------------------------

def _inline(text: str, site: "View") -> str:
    out = e(text)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", out)
    out = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', out)

    def key(m: re.Match) -> str:
        found = site.site.issue(m.group(0))
        return f'<a href="{site.browse(found["key"])}">{m.group(0)}</a>' if found else m.group(0)

    # Link work item keys that aren't already inside a tag.
    parts = re.split(r"(<[^>]+>)", out)
    return "".join(p if p.startswith("<") else re.sub(r"\b[A-Z][A-Z0-9]+-\d+\b", key, p) for p in parts)


def markdown(text: str | None, site: "View") -> str:
    if not text or not text.strip():
        return '<p class="placeholder">Add a description...</p>'
    lines = text.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.lstrip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            rows = [r for r in rows if not all(re.fullmatch(r":?-{2,}:?", c) for c in r if c)]
            head, body = rows[0], rows[1:]
            out.append('<table class="md"><thead><tr>' + "".join(f"<th>{_inline(c, site)}</th>" for c in head)
                       + "</tr></thead><tbody>" + "".join(
                           "<tr>" + "".join(f"<td>{_inline(c, site)}</td>" for c in r) + "</tr>" for r in body)
                       + "</tbody></table>")
            continue
        heading = re.match(r"(#{1,6})\s+(.*)", line)
        if heading:
            level = min(len(heading.group(1)) + 2, 6)
            out.append(f"<h{level}>{_inline(heading.group(2), site)}</h{level}>")
            i += 1
            continue
        if re.match(r"\s*([-*]|\d+\.)\s+", line):
            ordered = bool(re.match(r"\s*\d+\.", line))
            items = []
            while i < len(lines) and re.match(r"\s*([-*]|\d+\.)\s+", lines[i]):
                items.append(re.sub(r"\s*([-*]|\d+\.)\s+", "", lines[i], count=1))
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{_inline(x, site)}</li>" for x in items) + f"</{tag}>")
            continue
        para = []
        while i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith("|") \
                and not re.match(r"(#{1,6})\s|\s*([-*]|\d+\.)\s+", lines[i]):
            para.append(lines[i].strip())
            i += 1
        out.append("<p>" + "<br>".join(_inline(p, site) for p in para) + "</p>")
    return "".join(out)


# --- icons ---------------------------------------------------------------------------------------------------------

def _svg(body: str, size: int = 16) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 16 16">'
            f"{body}</svg>")


TYPE_SVGS = {
    "Task": _svg('<rect width="16" height="16" rx="3" fill="#4688EC"/><path d="M4.5 8.2l2.3 2.3 4.7-5" '
                 'stroke="#fff" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'),
    "Bug": _svg('<rect width="16" height="16" rx="3" fill="#E2483D"/><circle cx="8" cy="8" r="3.2" fill="#fff"/>'),
    "Story": _svg('<rect width="16" height="16" rx="3" fill="#82B536"/><path d="M5 3.8h6v8.6l-3-2.2-3 2.2z" '
                  'fill="#fff"/>'),
    "Epic": _svg('<rect width="16" height="16" rx="3" fill="#BF63F3"/><path d="M9.2 2.8L4.6 9h3l-.8 4.2L11.4 7h-3z" '
                 'fill="#fff"/>'),
    "Subtask": _svg('<rect width="16" height="16" rx="3" fill="#4688EC"/><rect x="3.5" y="3.5" width="5" height="5" '
                    'rx="1" fill="none" stroke="#fff" stroke-width="1.4"/><rect x="7.5" y="7.5" width="5" height="5" '
                    'rx="1" fill="#fff"/>'),
}
_UP = '<path d="M3.5 {y}l4.5-3.5 4.5 3.5" stroke="{c}" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
_DOWN = '<path d="M3.5 {y}l4.5 3.5 4.5-3.5" stroke="{c}" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
PRIORITY_SVGS = {
    "Highest": _svg(_UP.format(y=8, c="#C9372C") + _UP.format(y=12, c="#C9372C")),
    "High": _svg(_UP.format(y=10, c="#E2483D")),
    "Medium": _svg('<path d="M3 6h10M3 10h10" stroke="#E2B203" stroke-width="1.8" stroke-linecap="round"/>'),
    "Low": _svg(_DOWN.format(y=6, c="#1D7AFC")),
    "Lowest": _svg(_DOWN.format(y=4, c="#1D7AFC") + _DOWN.format(y=8, c="#1D7AFC")),
}
PROJECT_SVG = _svg('<rect width="16" height="16" rx="3" fill="#1D7AFC"/><circle cx="8" cy="8" r="4.2" fill="none" '
                   'stroke="#fff" stroke-width="1.4"/><path d="M8 3.8v8.4M3.8 8h8.4" stroke="#fff" '
                   'stroke-width="1.1"/>', 16)
JIRA_LOGO = ('<svg width="24" height="24" viewBox="0 0 24 24"><defs><linearGradient id="jl" x1="1" y1="0" x2="0" '
             'y2="1"><stop offset="0" stop-color="#0052CC"/><stop offset="1" stop-color="#2684FF"/></linearGradient>'
             '</defs><rect width="24" height="24" rx="6" fill="#1868DB"/><path d="M17.8 5.5H11.6a2.8 2.8 0 0 0 2.8 '
             '2.8h1.1v1.1a2.8 2.8 0 0 0 2.8 2.8V6a.5.5 0 0 0-.5-.5zM14.7 8.6H8.5a2.8 2.8 0 0 0 2.8 2.8h1.1v1.1a2.8 '
             '2.8 0 0 0 2.8 2.8V9.1a.5.5 0 0 0-.5-.5zM11.6 11.7H5.4a2.8 2.8 0 0 0 2.8 2.8h1.1v1.1a2.8 2.8 0 0 0 2.8 '
             '2.8v-6.2a.5.5 0 0 0-.5-.5z" fill="#fff"/></svg>')


def svg_for_avatar(site: Site, avatar_id: str) -> str | None:
    for t in site.data["issueTypes"]:
        if str(t["avatarId"]) == avatar_id:
            return TYPE_SVGS.get(t["name"], TYPE_SVGS["Task"])
    if str(site.project["avatarId"]) == avatar_id:
        return PROJECT_SVG
    return None


def svg_for_priority(site: Site, file: str) -> str | None:
    for p in site.data["priorities"]:
        if p["icon"] == file:
            return PRIORITY_SVGS.get(p["name"])
    return None


def type_icon(name: str) -> str:
    return f'<span class="ti" title="{e(name)}">{TYPE_SVGS.get(name, TYPE_SVGS["Task"])}</span>'


def priority_icon(name: str | None) -> str:
    if not name or name not in PRIORITY_SVGS:
        return ""
    return f'<span class="pi" title="{e(name)}">{PRIORITY_SVGS[name]}</span>'


def avatar(user: dict | None, size: int = 24) -> str:
    if user is None:
        return (f'<span class="av un" style="width:{size}px;height:{size}px" title="Unassigned">'
                '<svg viewBox="0 0 16 16" width="60%" height="60%"><circle cx="8" cy="5.5" r="3" fill="#626F86"/>'
                '<path d="M2.5 14c.6-3 2.8-4.6 5.5-4.6s4.9 1.6 5.5 4.6z" fill="#626F86"/></svg></span>')
    color = _AVATAR_COLORS[sum(map(ord, user["key"])) % len(_AVATAR_COLORS)]
    font = max(int(size * 0.42), 9)
    return (f'<span class="av" style="width:{size}px;height:{size}px;background:{color};font-size:{font}px" '
            f'title="{e(user["displayName"])}">{e(user["initials"])}</span>')


def lozenge(site: Site, status: str) -> str:
    category = site.statuses[status]["category"]
    bg, fg = _LOZENGE.get(category, _LOZENGE[2])
    return f'<span class="lz" style="background:{bg};color:{fg}">{e(status.upper())}</span>'


def estimate(issue: dict) -> str:
    hours = issue.get("estimateHours")
    return "" if hours is None else render.format_duration(int(hours * 3600))


# --- page model ----------------------------------------------------------------------------------------------------

class View:
    def __init__(self, site: Site, prefix: str, now: datetime, notice: str | None) -> None:
        self.site = site
        self.prefix = prefix
        self.now = now
        self.notice = notice
        p = site.project
        self.project_base = f"{prefix}/jira/software/projects/{p['key']}"

    def board(self) -> str:
        return f"{self.project_base}/boards/{self.site.project['boardId']}"

    def backlog(self) -> str:
        return self.board() + "/backlog"

    def list(self) -> str:
        return f"{self.project_base}/list"

    def browse(self, key: str) -> str:
        return f"{self.prefix}/browse/{key}"

    def user(self, key: str | None) -> dict | None:
        return self.site.users.get(key or "")

    def wiki_page(self, page: dict) -> str:
        return f"{self.prefix}/wiki{render.page_path(self.site, page)}"

    def wiki_home(self) -> str:
        space = self.site.data["confluence"]["spaces"][0]
        home = self.site.pages.get(space.get("homepageId") or "")
        return self.wiki_page(home) if home else f"{self.prefix}/wiki/spaces/{space['key']}"

    def active_sprint(self) -> dict | None:
        return next((s for s in self.site.data["sprints"] if s["state"] == "active"), None)

    def sprint_issues(self, sprint_id) -> list[dict]:
        return [i for i in self.site.data["issues"] if i.get("sprint") == sprint_id]


_NAV_ICON = {
    "summary": '<path d="M2 3h12v2H2zM2 7h8v2H2zM2 11h10v2H2z" fill="currentColor"/>',
    "board": '<path d="M2 2h3.5v12H2zM6.25 2h3.5v8h-3.5zM10.5 2H14v10h-3.5z" fill="currentColor"/>',
    "backlog": '<path d="M2 3h12v2H2zM2 7h12v2H2zM2 11h12v2H2z" fill="currentColor"/>',
    "list": '<path d="M2 3h2v2H2zM6 3h8v2H6zM2 7h2v2H2zM6 7h8v2H6zM2 11h2v2H2zM6 11h8v2H6z" fill="currentColor"/>',
    "timeline": '<path d="M2 3h7v2H2zM5 7h9v2H5zM3 11h6v2H3z" fill="currentColor"/>',
    "foryou": '<circle cx="8" cy="5.5" r="3" fill="currentColor"/><path d="M2.5 14c.6-3 2.8-4.6 5.5-4.6s4.9 1.6 '
              '5.5 4.6z" fill="currentColor"/>',
    "recent": '<circle cx="8" cy="8" r="5.6" stroke="currentColor" stroke-width="1.5" fill="none"/><path '
              'd="M8 4.8V8l2.2 1.6" stroke="currentColor" stroke-width="1.5" fill="none"/>',
    "starred": '<path d="M8 2l1.8 3.8 4.1.5-3 2.9.8 4.1L8 11.3l-3.7 2 .8-4.1-3-2.9 4.1-.5z" stroke="currentColor" '
               'stroke-width="1.3" fill="none" stroke-linejoin="round"/>',
    "spaces": '<rect x="2" y="2" width="5" height="5" rx="1" fill="currentColor"/><rect x="9" y="2" width="5" '
              'height="5" rx="1" fill="currentColor"/><rect x="2" y="9" width="5" height="5" rx="1" '
              'fill="currentColor"/><rect x="9" y="9" width="5" height="5" rx="1" fill="currentColor"/>',
}


def _nav_icon(name: str) -> str:
    return f'<svg width="16" height="16" viewBox="0 0 16 16">{_NAV_ICON[name]}</svg>'


def shell(view: View, *, title: str, active: str, body: str) -> str:
    p = view.site.project
    me = view.site.current_user
    items = [("board", "Board", view.board()), ("backlog", "Backlog", view.backlog()), ("list", "List", view.list())]
    nav = "".join(
        f'<a class="nv sub{" on" if key == active else ""}" href="{href}">{_nav_icon(key)}<span>{label}</span></a>'
        for key, label, href in items)
    notice = f'<div class="notice">{e(view.notice)}</div>' if view.notice else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport"
content="width=device-width,initial-scale=1"><title>{e(title)} - Jira</title><style>{CSS}{_BADGE_CSS}</style></head><body>
<header class="top"><div class="tl"><span class="grid" title="Switch apps"><svg width="20" height="20"
viewBox="0 0 20 20"><g fill="#44546F"><rect x="3" y="3" width="4" height="4" rx="1"/><rect x="8" y="3" width="4"
height="4" rx="1"/><rect x="13" y="3" width="4" height="4" rx="1"/><rect x="3" y="8" width="4" height="4" rx="1"/>
<rect x="8" y="8" width="4" height="4" rx="1"/><rect x="13" y="8" width="4" height="4" rx="1"/><rect x="3" y="13"
width="4" height="4" rx="1"/><rect x="8" y="13" width="4" height="4" rx="1"/><rect x="13" y="13" width="4" height="4"
rx="1"/></g></svg></span><a class="logo" href="{view.board()}">{JIRA_LOGO}<span>Jira</span></a></div>
<form class="search" action="{view.list()}" method="get"><svg width="16" height="16" viewBox="0 0 16 16"><circle
cx="7" cy="7" r="4.6" stroke="#626F86" stroke-width="1.6" fill="none"/><path d="M10.5 10.5l3 3" stroke="#626F86"
stroke-width="1.6" stroke-linecap="round"/></svg><input name="text" placeholder="Search" aria-label="Search"></form>
<div class="tr"><span class="create">+ Create</span>{avatar(me, 28)}</div></header>
<div class="wrap"><nav class="side">
<a class="nv" href="{view.board()}">{_nav_icon("foryou")}<span>For you</span></a>
<a class="nv" href="{view.board()}">{_nav_icon("recent")}<span>Recent</span></a>
<a class="nv" href="{view.board()}">{_nav_icon("starred")}<span>Starred</span></a>
<a class="nv" href="{view.list()}">{_nav_icon("spaces")}<span>Spaces</span></a>
<div class="sh">Recent</div>
<a class="nv proj" href="{view.board()}"><span class="pa">{PROJECT_SVG}</span><span>{e(p["name"])}</span></a>
{nav}
</nav><main>{notice}{body}<footer>Mock environment for Microsoft Ignite lab LAB654. Not affiliated with Atlassian.
Data is fictitious.</footer></main></div>{_mock_badge(view.prefix.startswith("/v/") and not view.notice)}</body></html>"""


_BADGE_CSS = (".mock-badge{position:fixed;right:16px;bottom:16px;z-index:1000;display:flex;flex-direction:column;"
              "align-items:flex-end;background:#d13438;color:#fff;border-radius:8px;padding:6px 12px;"
              "box-shadow:0 4px 14px rgba(0,0,0,.2);font:12px/1.35 'Segoe UI',system-ui,sans-serif}"
              ".mock-badge .mb-top{font-weight:700;letter-spacing:.06em}.mock-badge .mb-sub{opacity:.92}")


def _mock_badge(scoped: bool, product: str = "Jira") -> str:
    state = "Showing this conversation's changes" if scoped else "Showing the original site data"
    return (f'<div class="mock-badge" title="This is a mock Atlassian {product} page served by a mock MCP server. '
            f'It is not a real Atlassian site."><span class="mb-top">MOCK ATLASSIAN · {product.upper()}</span>'
            f'<span class="mb-sub">{state}</span></div>')


def _crumbs(view: View, *extra: str) -> str:
    p = view.site.project
    parts = [f'<a href="{view.list()}">Spaces</a>', f'<a href="{view.board()}">{e(p["name"])}</a>', *extra]
    return '<div class="crumbs">' + '<span class="sep">/</span>'.join(parts) + "</div>"


def _card(view: View, issue: dict) -> str:
    labels = "".join(f'<span class="tag">{e(x)}</span>' for x in issue.get("labels", [])[:2])
    est = estimate(issue)
    est_html = f'<span class="est" title="Original estimate">{e(est)}</span>' if est else ""
    return (f'<a class="card" href="{view.browse(issue["key"])}"><div class="ct">{e(issue["summary"])}</div>'
            f'<div class="tags">{labels}</div><div class="cf"><span class="ck">{type_icon(issue["type"])}'
            f'<span class="key{" done" if view.site.statuses[issue["status"]]["category"] == 3 else ""}">'
            f'{e(issue["key"])}</span></span><span class="cr">{est_html}{priority_icon(issue.get("priority"))}'
            f'{avatar(view.user(issue.get("assignee")), 24)}</span></div></a>')


def board_page(view: View) -> str:
    sprint = view.active_sprint()
    issues = view.sprint_issues(sprint["id"]) if sprint else []
    columns = []
    for status in view.site.data["statuses"]:
        hits = [i for i in issues if i["status"] == status["name"]]
        tick = " ✓" if status["category"] == 3 else ""
        columns.append(f'<section class="col"><div class="ch">{e(status["name"].upper())} <span class="n">'
                       f'{len(hits)}</span>{tick}</div>' + "".join(_card(view, i) for i in hits) + "</section>")
    header = "Board"
    bar = goal = ""
    if sprint:
        header = sprint["name"]
        end = parse(sprint.get("endDate"))
        if end:
            days = max((to_et(end).date() - to_et(view.now).date()).days, 0)
            bar = f'<span class="days">{days} day{"s" if days != 1 else ""} remaining</span>'
        bar = f'<div class="sprintbar">{bar}<span class="btn">Complete sprint</span></div>'
        if sprint.get("goal"):
            goal = f'<p class="goal"><strong>Sprint goal:</strong> {e(sprint["goal"])}</p>'
    people = "".join(avatar(u, 30) for u in view.site.data["users"])
    body = (f'{_crumbs(view)}<div class="ph"><h1>{e(header)}</h1>{bar}</div>{goal}<div class="toolbar"><span class="fs">'
            f'<svg width="14" height="14" viewBox="0 0 16 16"><circle cx="7" cy="7" r="4.6" stroke="#626F86" '
            f'stroke-width="1.6" fill="none"/></svg>Search board</span><span class="people">{people}</span>'
            f'<span class="btn sub">Epic</span><span class="btn sub">Type</span></div>'
            f'<div class="board">{"".join(columns)}</div>')
    return shell(view, title=f"{view.site.project['key']} board", active="board", body=body)


def _row(view: View, issue: dict, extra: str = "") -> str:
    return (f'<a class="row" href="{view.browse(issue["key"])}">{type_icon(issue["type"])}'
            f'<span class="key">{e(issue["key"])}</span><span class="sum">{e(issue["summary"])}</span>'
            + "".join(f'<span class="tag">{e(x)}</span>' for x in issue.get("labels", [])[:2])
            + f'{extra}<span class="rs">{lozenge(view.site, issue["status"])}'
            f'<span class="est">{e(estimate(issue)) or "-"}</span>{priority_icon(issue.get("priority"))}'
            f'{avatar(view.user(issue.get("assignee")), 24)}</span></a>')


def _totals(view: View, issues: list[dict]) -> str:
    chips = []
    for category, title in ((2, "To Do"), (4, "In progress"), (3, "Done")):
        hours = sum(i.get("estimateHours") or 0 for i in issues
                    if view.site.statuses[i["status"]]["category"] == category)
        bg, fg = _LOZENGE[category]
        label = render.format_duration(int(hours * 3600)) if hours else "0m"
        chips.append(f'<span class="chip" style="background:{bg};color:{fg}" title="{title}: {label}">{label}</span>')
    return "".join(chips)


def backlog_page(view: View) -> str:
    blocks = []
    for sprint in view.site.data["sprints"]:
        if sprint["state"] == "closed":
            continue
        issues = view.sprint_issues(sprint["id"])
        dates = ""
        if sprint.get("startDate") and sprint.get("endDate"):
            dates = f'{short_date(sprint["startDate"])} – {short_date(sprint["endDate"])}'
        blocks.append(
            f'<section class="bl"><div class="bh"><span class="chev">▾</span><strong>{e(sprint["name"])}</strong>'
            f'<span class="dim">{e(dates)} ({len(issues)} work item{"s" if len(issues) != 1 else ""})</span>'
            f'<span class="grow"></span>{_totals(view, issues)}<span class="btn sub">'
            f'{"Complete sprint" if sprint["state"] == "active" else "Start sprint"}</span></div>'
            + (f'<p class="goal in">{e(sprint.get("goal"))}</p>' if sprint.get("goal") else "")
            + "".join(_row(view, i) for i in issues) + "</section>")
    rest = [i for i in view.site.data["issues"] if i.get("sprint") is None]
    blocks.append(
        f'<section class="bl"><div class="bh"><span class="chev">▾</span><strong>Backlog</strong>'
        f'<span class="dim">({len(rest)} work item{"s" if len(rest) != 1 else ""})</span><span class="grow"></span>'
        f'{_totals(view, rest)}<span class="btn sub">Create sprint</span></div>'
        + ("".join(_row(view, i) for i in rest) or '<p class="empty">Your backlog is empty.</p>')
        + '<div class="add">+ Create</div></section>')
    body = f'{_crumbs(view)}<div class="ph"><h1>Backlog</h1></div>{"".join(blocks)}'
    return shell(view, title=f"{view.site.project['key']} backlog", active="backlog", body=body)


def list_page(view: View, text: str) -> str:
    issues = list(view.site.data["issues"])
    if text.strip():
        needle = text.strip().lower()
        issues = [i for i in issues if needle in f"{i['key']} {i['summary']} {i.get('description') or ''}".lower()]
    head = ("<tr><th>Type</th><th>Key</th><th>Summary</th><th>Status</th><th>Assignee</th><th>Priority</th>"
            "<th>Sprint</th><th>Original estimate</th><th>Created</th><th>Updated</th></tr>")
    rows = []
    for i in sorted(issues, key=lambda x: -int(x["id"])):
        sprint = view.site.sprints.get(i.get("sprint"))
        assignee = view.user(i.get("assignee"))
        rows.append(
            f'<tr><td>{type_icon(i["type"])}</td><td><a href="{view.browse(i["key"])}">{e(i["key"])}</a></td>'
            f'<td><a class="plain" href="{view.browse(i["key"])}">{e(i["summary"])}</a></td>'
            f'<td>{lozenge(view.site, i["status"])}</td><td><span class="who">{avatar(assignee, 20)}'
            f'{e(assignee["displayName"]) if assignee else "Unassigned"}</span></td>'
            f'<td><span class="who">{priority_icon(i.get("priority"))}{e(i.get("priority"))}</span></td>'
            f'<td>{e(sprint["name"]) if sprint else ""}</td><td>{e(estimate(i))}</td>'
            f'<td>{e(short_date(i["created"]))}</td><td>{e(short_date(i["updated"]))}</td></tr>')
    search = (f'<form class="lsearch" method="get"><input name="text" value="{e(text)}" placeholder="Search list">'
              "</form>")
    table = (f'<table class="grid">{head}{"".join(rows)}</table>' if rows
             else '<p class="empty">No work items match your search.</p>')
    body = f'{_crumbs(view)}<div class="ph"><h1>List</h1></div>{search}{table}'
    return shell(view, title=f"{view.site.project['key']} list", active="list", body=body)


def _field(label: str, value: str) -> str:
    return f'<div class="fl"><div class="fn">{e(label)}</div><div class="fv">{value}</div></div>'


def _who(user: dict | None) -> str:
    return f'<span class="who">{avatar(user, 24)}{e(user["displayName"]) if user else "Unassigned"}</span>'


def _time_tracking(issue: dict) -> str:
    tt = render.timetracking(issue)
    spent = tt.get("timeSpentSeconds", 0)
    remaining = tt.get("remainingEstimateSeconds", 0)
    total = spent + remaining
    if not total:
        return '<span class="none">No time logged</span>'
    pct = int(round(100 * spent / total))
    return (f'<div class="tt"><div class="bar"><span style="width:{pct}%"></span></div><div class="ttl">'
            f'<span>{e(tt.get("timeSpent", "0m"))} logged</span><span>{e(tt.get("remainingEstimate", "0m"))} '
            "remaining</span></div></div>")


def _links(view: View, issue: dict) -> str:
    groups: dict[str, list[str]] = {}
    for link in render.issue_links(view.site, issue):
        if "outwardIssue" in link:
            phrase, other = link["type"]["outward"], link["outwardIssue"]
        else:
            phrase, other = link["type"]["inward"], link["inwardIssue"]
        target = view.site.issue(other["key"])
        groups.setdefault(phrase, []).append(
            f'<a class="li" href="{view.browse(target["key"])}">{type_icon(target["type"])}<span class="key">'
            f'{e(target["key"])}</span><span class="sum">{e(target["summary"])}</span><span class="rs">'
            f'{priority_icon(target.get("priority"))}{avatar(view.user(target.get("assignee")), 20)}'
            f'{lozenge(view.site, target["status"])}</span></a>')
    remote = view.site.data["remoteLinks"].get(issue["key"], [])
    if not groups and not remote:
        return ""
    out = '<h2>Linked work items</h2><div class="links">'
    for phrase, items in groups.items():
        out += f'<div class="lg">{e(phrase)}</div>' + "".join(items)
    out += "</div>"
    if remote:
        out += "<h2>Web links</h2><ul>" + "".join(
            f'<li><a href="{e((r.get("object") or {}).get("url"))}">{e((r.get("object") or {}).get("title"))}</a></li>'
            for r in remote) + "</ul>"
    return out


def _activity(view: View, issue: dict, tab: str) -> str:
    tabs = [("all", "All"), ("comments", "Comments"), ("worklog", "Work log")]
    bar = "".join(f'<a class="tab{" on" if key == tab else ""}" href="?activity={key}">{label}</a>'
                  for key, label in tabs)
    entries: list[tuple[str, str]] = []
    if tab in ("all", "comments"):
        for c in issue.get("comments", []):
            who = view.user(c.get("author"))
            entries.append((c["created"],
                            f'<div class="act">{avatar(who, 32)}<div class="ab"><div class="ah"><strong>'
                            f'{e(who["displayName"] if who else "Unknown")}</strong><span class="dim">'
                            f'{e(ago(c["created"], view.now))}</span></div><div class="md-body">'
                            f'{markdown(c.get("body"), view)}</div></div></div>'))
    if tab in ("all", "worklog"):
        for w in issue.get("worklogs", []):
            who = view.user(w.get("author"))
            note = f'<div class="md-body">{markdown(w["comment"], view)}</div>' if w.get("comment") else ""
            entries.append((w["created"],
                            f'<div class="act">{avatar(who, 32)}<div class="ab"><div class="ah"><strong>'
                            f'{e(who["displayName"] if who else "Unknown")}</strong> logged <strong>'
                            f'{e(render.format_duration(w["timeSpentSeconds"]))}</strong><span class="dim">'
                            f'{e(full_date(w["started"]))}</span></div>{note}</div></div>'))
    entries.sort(key=lambda x: x[0], reverse=True)
    me = view.site.current_user
    composer = (f'<div class="act">{avatar(me, 32)}<div class="composer">Add a comment...</div></div>'
                if tab != "worklog" else "")
    listing = "".join(x for _, x in entries) or '<p class="empty">Nothing here yet.</p>'
    return f'<h2>Activity</h2><div class="tabs">{bar}</div>{composer}{listing}'


def issue_page(view: View, issue: dict, tab: str) -> str:
    site = view.site
    sprint = site.sprints.get(issue.get("sprint"))
    parent = site.issue(issue["parent"]) if issue.get("parent") else None
    category = site.statuses[issue["status"]]["category"]
    bg, fg = _LOZENGE.get(category, _LOZENGE[2])
    status_btn = (f'<span class="status" style="background:{bg};color:{fg}">{e(issue["status"])} '
                  '<svg width="12" height="12" viewBox="0 0 16 16"><path d="M4 6l4 4 4-4" stroke="currentColor" '
                  'stroke-width="1.8" fill="none"/></svg></span>')
    labels = "".join(f'<span class="tag">{e(x)}</span>' for x in issue.get("labels", [])) or '<span class="none">None'\
        '</span>'
    details = "".join([
        _field("Assignee", _who(view.user(issue.get("assignee")))),
        _field("Labels", labels),
        _field("Parent", f'<a href="{view.browse(parent["key"])}">{type_icon(parent["type"])} {e(parent["key"])} '
                         f'{e(parent["summary"])}</a>' if parent else '<span class="none">None</span>'),
        _field("Sprint", f'<a href="{view.board()}">{e(sprint["name"])}</a>' if sprint
               else '<span class="none">None</span>'),
        _field("Priority", f'<span class="who">{priority_icon(issue.get("priority"))}{e(issue.get("priority"))}</span>'),
        _field("Original estimate", e(estimate(issue)) or '<span class="none">None</span>'),
        _field("Time tracking", _time_tracking(issue)),
        _field("Components", ", ".join(e(c) for c in issue.get("components", [])) or '<span class="none">None</span>'),
        _field("Reporter", _who(view.user(issue.get("reporter")))),
    ])
    resolution = issue.get("resolution")
    resolved = f'<div class="res">Resolution: <strong>{e(resolution["name"])}</strong></div>' if resolution else ""
    crumbs = _crumbs(view, f'<a href="{view.browse(issue["key"])}">{type_icon(issue["type"])} {e(issue["key"])}</a>')
    body = f"""{crumbs}<div class="issue"><div class="il"><h1 class="title">{e(issue["summary"])}</h1>
<div class="actions"><span class="btn sub">+ Add</span><span class="btn sub">Link work item</span></div>
<h2>Description</h2><div class="md-body">{markdown(issue.get("description"), view)}</div>
{_links(view, issue)}{_activity(view, issue, tab)}</div>
<aside class="ir"><div class="sr">{status_btn}{resolved}</div><div class="det"><div class="dh">Details</div>{details}
</div><div class="stamps"><div>Created {e(full_date(issue["created"]))}</div><div>Updated
{e(full_date(issue["updated"]))}</div></div></aside></div>"""
    return shell(view, title=f"[{issue['key']}] {issue['summary']}", active="", body=body)


def not_found_page(view: View, what: str = "this page") -> str:
    body = (f'<div class="nf"><h1>We can\'t find {e(what)}</h1><p>It may have been deleted, or the link may belong '
            f'to a different conversation.</p><p><a href="{view.board()}">Go to the {e(view.site.project["name"])} '
            "board</a></p></div>")
    return shell(view, title="Not found", active="", body=body)


# --- Confluence ----------------------------------------------------------------------------------------------------

CONFLUENCE_LOGO = ('<svg width="24" height="24" viewBox="0 0 24 24"><path d="M3.2 16.6c-.3.4-.6 1-.8 1.3a.7.7 0 0 0 '
                   '.2 1l3.6 2.2a.7.7 0 0 0 1-.2c.2-.3.5-.9.9-1.5 2.5-4.1 5-3.6 9.6-1.4l3.6 1.7a.7.7 0 0 0 .9-.3l1.7-'
                   '3.9a.7.7 0 0 0-.3-.9c-.8-.4-2.3-1.1-3.7-1.8-5.4-2.6-10-2.4-16.7 3.8z" fill="#1868DB"/><path d="M20.8'
                   ' 7.4c.3-.4.6-1 .8-1.3a.7.7 0 0 0-.2-1L17.8 2.9a.7.7 0 0 0-1 .2c-.2.3-.5.9-.9 1.5-2.5 4.1-5 3.6-9.6 '
                   '1.4L2.7 4.3a.7.7 0 0 0-.9.3L.1 8.5a.7.7 0 0 0 .3.9c.8.4 2.3 1.1 3.7 1.8 5.4 2.6 10 2.4 16.7-3.8z" '
                   'fill="#1868DB"/></svg>')


def _tree(view: View, current: dict | None) -> str:
    pages = [p for p in view.site.data["confluence"]["pages"] if p["status"] == "current"]

    def branch(parent_id, depth: int) -> str:
        out = ""
        for page in sorted((p for p in pages if p.get("parentId") == parent_id), key=lambda p: int(p["id"])):
            on = " on" if current and page["id"] == current["id"] else ""
            out += (f'<a class="nv{on}" style="padding-left:{8 + depth * 16}px" href="{view.wiki_page(page)}">'
                    f'{_nav_icon("summary")}<span>{e(page["title"])}</span></a>') + branch(page["id"], depth + 1)
        return out

    return branch(None, 0)


def wiki_shell(view: View, *, title: str, current: dict | None, body: str) -> str:
    space = view.site.data["confluence"]["spaces"][0]
    me = view.site.current_user
    notice = f'<div class="notice">{e(view.notice)}</div>' if view.notice else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport"
content="width=device-width,initial-scale=1"><title>{e(title)} - {e(space["name"])} - Confluence</title>
<style>{CSS}{_BADGE_CSS}</style></head><body>
<header class="top"><div class="tl"><a class="logo" href="{view.wiki_home()}">{CONFLUENCE_LOGO}<span>Confluence</span>
</a><a class="nv" href="{view.board()}">Jira</a></div><div class="tr">{avatar(me, 28)}</div></header>
<div class="wrap"><nav class="side"><div class="sh">Space</div><a class="nv proj" href="{view.wiki_home()}">
<span class="pa">{PROJECT_SVG}</span><span>{e(space["name"])}</span></a><div class="sh">Content</div>
{_tree(view, current)}</nav><main>{notice}{body}<footer>Mock environment for Microsoft Ignite lab LAB654. Not
affiliated with Atlassian. Data is fictitious.</footer></main></div>{_wiki_badge(view)}</body></html>"""


def _wiki_badge(view: View) -> str:
    return _mock_badge(view.prefix.startswith("/v/") and not view.notice, "Confluence")


def _wiki_comment(view: View, c: dict, replies: list[dict]) -> str:
    who = view.user(c["author"])
    quote = (f'<blockquote class="dim">"{e(c["selection"])}"</blockquote>' if c.get("selection") else "")
    nested = "".join(_wiki_comment(view, r, []) for r in replies)
    return (f'<div class="act" id="comment-{e(c["id"])}">{avatar(who, 32)}<div class="ab"><div class="ah"><strong>'
            f'{e(who["displayName"] if who else "Unknown")}</strong><span class="dim">{e(ago(c["created"], view.now))}'
            f'</span></div>{quote}<div class="md-body">{markdown(c["body"], view)}</div>'
            f'<div style="margin-left:8px">{nested}</div></div></div>')


def wiki_page_view(view: View, page: dict) -> str:
    site = view.site
    author, editor = view.user(page["author"]), view.user(page.get("updatedBy") or page["author"])
    labels = "".join(f'<span class="tag">{e(x)}</span>' for x in page.get("labels", []))
    comments = [c for c in site.data["confluence"]["comments"] if c["pageId"] == page["id"]]
    tops = sorted((c for c in comments if not c.get("parentId")), key=lambda c: c["created"])
    thread = "".join(_wiki_comment(view, c, [r for r in comments if r.get("parentId") == c["id"]]) for c in tops)
    crumbs, cur = [], site.pages.get(page.get("parentId") or "")
    while cur:
        crumbs.insert(0, f'<a href="{view.wiki_page(cur)}">{e(cur["title"])}</a>')
        cur = site.pages.get(cur.get("parentId") or "")
    space = site.spaces.get(page["spaceId"]) or {}
    trail = '<span class="sep">/</span>'.join([f'<a href="{view.wiki_home()}">{e(space.get("name", ""))}</a>', *crumbs])
    body = f"""<div class="crumbs">{trail}</div><h1 class="title">{e(page["title"])}</h1>
<div class="ah">{avatar(author, 24)}<span>Owned by <strong>{e(author["displayName"] if author else "")}</strong></span>
<span class="dim">Last updated {e(full_date(page["updated"]))} by {e(editor["displayName"] if editor else "")} -
version {page["version"]}</span></div><div class="md-body" style="margin-top:16px">{markdown(page.get("body"), view)}
</div><div style="margin:16px 0">{labels}</div><h2>Comments</h2>{thread or '<p class="empty">No comments yet.</p>'}"""
    return wiki_shell(view, title=page["title"], current=page, body=body)


def wiki_not_found(view: View) -> str:
    body = ('<div class="nf"><h1>We can\'t find this page</h1><p>It may have been deleted, or the link may belong to '
            f'a different conversation.</p><p><a href="{view.wiki_home()}">Go to the space home</a></p></div>')
    return wiki_shell(view, title="Not found", current=None, body=body)


def tiny_to_id(tiny: str) -> str | None:
    import base64
    try:
        return str(int.from_bytes(base64.urlsafe_b64decode(tiny + "=" * (-len(tiny) % 4)), "little"))
    except (ValueError, TypeError):
        return None


# --- routes --------------------------------------------------------------------------------------------------------

def build_routes(store: StateStore, clock_factory=None) -> list:
    from starlette.responses import HTMLResponse, RedirectResponse, Response
    from starlette.routing import Route

    def now() -> datetime:
        if clock_factory is None:
            return datetime.now(timezone.utc)
        return clock_factory().now

    def resolve(request) -> View | None:
        token = request.path_params.get("token")
        if token is None:
            site, _ = store.read_by_token(None)
            return View(site, "", now(), None)
        if not _TOKEN.fullmatch(token):
            return None
        site, scoped = store.read_by_token(token)
        return View(site, f"/v/{token}", now(), None if scoped else _EXPIRED)

    def html(text: str, status: int = 200) -> HTMLResponse:
        return HTMLResponse(text, status_code=status, headers=_HEADERS)

    def page(render_fn):
        async def endpoint(request):
            view = resolve(request)
            if view is None:
                site, _ = store.read_by_token(None)
                return html(not_found_page(View(site, "", now(), None)), 404)
            return render_fn(request, view)
        return endpoint

    def project_ok(request, view: View) -> bool:
        p = view.site.project
        key = request.path_params.get("key", p["key"]).upper()
        board = request.path_params.get("board", str(p["boardId"]))
        return key == p["key"] and board == str(p["boardId"])

    def to_board(request, view):
        return RedirectResponse(view.board(), status_code=302)

    def to_list(request, view):
        # Jira's /issues?jql=... search page; the mock viewer shows the project list instead.
        return RedirectResponse(view.list(), status_code=302)

    def board(request, view):
        if not project_ok(request, view):
            return html(not_found_page(view, "this board"), 404)
        return html(board_page(view))

    def backlog(request, view):
        if not project_ok(request, view):
            return html(not_found_page(view, "this board"), 404)
        return html(backlog_page(view))

    def listing(request, view):
        if not project_ok(request, view):
            return html(not_found_page(view, "this space"), 404)
        return html(list_page(view, request.query_params.get("text", "")))

    def browse(request, view):
        key = request.path_params["key"]
        issue = view.site.issue(key)
        if issue is None:
            token = None if view.prefix else store.token_for_issue(key)
            if token:
                return RedirectResponse(f"/v/{token}/browse/{key.upper()}", status_code=302)
            return html(not_found_page(view, "this work item"), 404)
        if issue["key"] != key:
            return RedirectResponse(view.browse(issue["key"]), status_code=302)
        tab = request.query_params.get("activity", "all")
        return html(issue_page(view, issue, tab if tab in ("all", "comments", "worklog") else "all"))

    def wiki_home(request, view):
        space = view.site.space(request.path_params.get("space", "AUR"))
        if space is None:
            return html(wiki_not_found(view), 404)
        return RedirectResponse(view.wiki_home(), status_code=302)

    def wiki_page(request, view):
        space = view.site.space(request.path_params["space"])
        page = view.site.pages.get(request.path_params["id"])
        if page is None and space is not None and not view.prefix:
            token = store.token_for_page(request.path_params["id"])
            if token:
                return RedirectResponse(f"/v/{token}{request.url.path}", status_code=302)
        if space is None or page is None or page["status"] != "current" or page["spaceId"] != space["id"]:
            return html(wiki_not_found(view), 404)
        return html(wiki_page_view(view, page))

    def wiki_by_id(request, view):
        ref = request.path_params.get("id") or tiny_to_id(request.path_params.get("tiny", ""))
        page = view.site.pages.get(ref or "")
        if page is None and ref and not view.prefix:
            token = store.token_for_page(ref)
            if token:
                return RedirectResponse(f"/v/{token}{request.url.path}", status_code=302)
        if page is None:
            return html(wiki_not_found(view), 404)
        return RedirectResponse(view.wiki_page(page), status_code=302)

    async def api_issue(request):
        site = store.seed
        if request.path_params["cid"] != site.data["site"]["cloudId"]:
            return Response('{"errorMessages":["Site not found."]}', status_code=404, media_type="application/json")
        key = request.path_params["ref"]
        found = site.issue(key)
        target = found["key"] if found else key.upper()
        if found is None and not store.token_for_issue(target):
            return Response('{"errorMessages":["Issue does not exist or you do not have permission to see it."]}',
                            status_code=404, media_type="application/json")
        return RedirectResponse(f"/browse/{target}", status_code=302)

    def svg(text: str | None) -> Response:
        if text is None:
            return Response("Not found", status_code=404)
        return Response(text, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})

    async def avatar_svg(request):
        return svg(svg_for_avatar(store.seed, request.path_params["aid"]))

    async def priority_svg(request):
        return svg(svg_for_priority(store.seed, request.path_params["name"]))

    routes = [
        Route("/images/icons/priorities/{name}", priority_svg),
        Route("/rest/api/{v}/universal_avatar/view/type/{kind}/avatar/{aid}", avatar_svg),
        Route("/ex/jira/{cid}/rest/api/{v}/universal_avatar/view/type/{kind}/avatar/{aid}", avatar_svg),
        Route("/ex/jira/{cid}/rest/api/{v}/issue/{ref}", api_issue),
    ]
    for base in ("", "/v/{token}"):
        routes += [
            Route(base + "/" if base == "" else base, page(to_board)),
            Route(base + "/jira", page(to_board)),
            Route(base + "/jira/projects", page(to_board)),
            Route(base + "/jira/software/projects/{key}/boards/{board}", page(board)),
            Route(base + "/jira/software/projects/{key}/boards/{board}/backlog", page(backlog)),
            Route(base + "/jira/software/projects/{key}/list", page(listing)),
            Route(base + "/issues", page(to_list)),
            Route(base + "/browse/{key}", page(browse)),
            Route(base + "/wiki", page(wiki_home)),
            Route(base + "/wiki/", page(wiki_home)),
            Route(base + "/wiki/spaces/{space}", page(wiki_home)),
            Route(base + "/wiki/spaces/{space}/overview", page(wiki_home)),
            Route(base + "/wiki/spaces/{space}/pages/{id}", page(wiki_page)),
            Route(base + "/wiki/spaces/{space}/pages/{id}/{slug}", page(wiki_page)),
            Route(base + "/wiki/rest/api/content/{id}", page(wiki_by_id)),
            Route(base + "/wiki/x/{tiny}", page(wiki_by_id)),
        ]
    routes.append(Route("/v/{token}/", page(to_board)))
    return routes


CSS = """
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Oxygen,Ubuntu,
"Fira Sans","Droid Sans","Helvetica Neue",sans-serif;font-size:14px;color:#172B4D;background:#fff;line-height:1.43}
a{color:#0C66E4;text-decoration:none}a:hover{text-decoration:underline}
.top{position:sticky;top:0;z-index:5;height:56px;display:flex;align-items:center;gap:12px;padding:0 12px;
background:#fff;border-bottom:1px solid #DCDFE4}
.tl{display:flex;align-items:center;gap:8px;width:228px}.grid{display:flex;padding:6px;border-radius:4px}
.grid:hover{background:#F1F2F4}.logo{display:flex;align-items:center;gap:8px;color:#172B4D;font-weight:600;
font-size:16px}.logo:hover{text-decoration:none}
.search{flex:1;max-width:780px;margin:0 auto;display:flex;align-items:center;gap:8px;height:36px;padding:0 10px;
border:1px solid #8590A2;border-radius:6px}.search input{border:0;outline:0;flex:1;font:inherit;color:#172B4D}
.tr{display:flex;align-items:center;gap:12px}.create{background:#0C66E4;color:#fff;font-weight:500;padding:6px 12px;
border-radius:4px}.mock{font-size:11px;font-weight:700;letter-spacing:.04em;color:#7F5F01;background:#F8E6A0;
padding:2px 6px;border-radius:3px}
.wrap{display:flex;min-height:calc(100vh - 56px)}
.side{width:240px;flex:none;border-right:1px solid #DCDFE4;padding:12px 8px;background:#fff}
.nv{display:flex;align-items:center;gap:10px;padding:6px 8px;border-radius:4px;color:#44546F;font-weight:500}
.nv:hover{background:#F1F2F4;text-decoration:none}.nv.on{background:#E9F2FF;color:#0C66E4}
.nv.sub{padding-left:32px}.sh{margin:16px 8px 6px;font-size:12px;font-weight:600;color:#626F86}
.proj{color:#172B4D}.pa{display:flex}
main{flex:1;min-width:0;padding:16px 32px 24px}
footer{margin-top:40px;color:#626F86;font-size:12px}
.notice{background:#FFF7D6;border:1px solid #F5CD47;padding:8px 12px;border-radius:4px;margin-bottom:12px}
.crumbs{color:#44546F;font-size:14px;display:flex;align-items:center;gap:6px}.crumbs a{color:#44546F}
.crumbs .sep{color:#8590A2}.crumbs a{display:inline-flex;align-items:center;gap:4px}
.ph{display:flex;align-items:center;gap:16px;margin:8px 0}.ph h1{font-size:24px;font-weight:600;margin:0;flex:1}
.sprintbar{display:flex;align-items:center;gap:12px}.days{color:#44546F}
.btn{display:inline-block;background:#0C66E4;color:#fff;padding:6px 12px;border-radius:4px;font-weight:500}
.btn.sub{background:#091E420F;color:#172B4D}.goal{color:#44546F;margin:0 0 12px;max-width:980px}
.goal.in{margin:0 12px 8px}
.toolbar{display:flex;align-items:center;gap:12px;margin:8px 0 16px}.fs{display:inline-flex;align-items:center;
gap:6px;border:1px solid #8590A2;border-radius:4px;padding:5px 10px;color:#626F86;width:180px}
.people{display:flex}.people .av{margin-left:-4px;border:2px solid #fff}
.board{display:flex;gap:8px;align-items:flex-start}.col{background:#F7F8F9;border-radius:6px;flex:0 1 272px;min-width:200px;
padding:8px;min-height:400px}.ch{font-size:12px;font-weight:600;color:#44546F;padding:6px 6px 10px}
.ch .n{margin-left:4px}
.card{display:block;background:#fff;border-radius:4px;box-shadow:0 1px 1px #091E4240,0 0 1px #091E424F;padding:12px;
margin-bottom:6px;color:#172B4D}.card:hover{background:#F7F8F9;text-decoration:none}.ct{margin-bottom:8px}
.tags{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px}.tags:empty{display:none}
.tag{display:inline-block;font-size:12px;border:1px solid #DCDFE4;border-radius:3px;padding:0 4px;color:#44546F;
background:#fff;margin-right:4px}
.cf{display:flex;align-items:center;justify-content:space-between}.ck,.cr{display:flex;align-items:center;gap:6px}
.key{font-size:12px;font-weight:600;color:#44546F}.key.done{text-decoration:line-through}
.est{font-size:12px;background:#DCDFE4;color:#172B4D;border-radius:8px;padding:0 6px;min-width:20px;
text-align:center}
.ti,.pi{display:inline-flex;vertical-align:middle}
.av{display:inline-flex;align-items:center;justify-content:center;border-radius:50%;color:#fff;font-weight:600;
flex:none}.av.un{background:#DCDFE4}
.lz{display:inline-block;font-size:11px;font-weight:700;padding:0 4px;border-radius:3px;line-height:16px;
white-space:nowrap}
.bl{background:#F7F8F9;border-radius:6px;padding:8px;margin-bottom:16px}
.bh{display:flex;align-items:center;gap:8px;padding:6px 4px 10px}.grow{flex:1}.dim{color:#626F86;font-size:13px}
.chev{color:#44546F}.chip{display:inline-block;font-size:12px;font-weight:600;border-radius:8px;padding:0 6px;
min-width:24px;text-align:center}
.row{display:flex;align-items:center;gap:10px;background:#fff;border:1px solid #DCDFE4;margin-top:-1px;padding:8px 10px;
color:#172B4D}.row:hover{background:#F1F2F4;text-decoration:none}.row .sum{flex:1;overflow:hidden;
text-overflow:ellipsis;white-space:nowrap}.rs{display:flex;align-items:center;gap:10px;margin-left:auto}
.add{padding:8px 10px;color:#44546F}.empty{color:#626F86;padding:8px 10px;margin:0}
.lsearch input{border:1px solid #8590A2;border-radius:4px;padding:6px 10px;font:inherit;width:240px;margin:8px 0 12px}
table.grid{border-collapse:collapse;width:100%}table.grid th{text-align:left;font-size:12px;color:#626F86;
font-weight:600;padding:8px;border-bottom:2px solid #DCDFE4}table.grid td{padding:8px;border-bottom:1px solid #DCDFE4;
vertical-align:middle}a.plain{color:#172B4D}.who{display:inline-flex;align-items:center;gap:8px}
.issue{display:flex;gap:32px;margin-top:12px}.il{flex:1;min-width:0;max-width:820px}.ir{width:360px;flex:none}
h1.title{font-size:24px;font-weight:600;margin:4px 0 12px}.actions{display:flex;gap:8px;margin-bottom:16px}
h2{font-size:16px;font-weight:600;margin:24px 0 8px}.md-body p{margin:0 0 10px}.md-body ul,.md-body ol{margin:0 0 10px;
padding-left:24px}.md-body code{background:#F1F2F4;padding:1px 4px;border-radius:3px;font-size:13px}
.placeholder{color:#626F86}
table.md{border-collapse:collapse;margin:4px 0 12px}table.md th,table.md td{border:1px solid #DCDFE4;padding:6px 10px;
text-align:left}table.md th{background:#F7F8F9;font-weight:600}
.links{border:1px solid #DCDFE4;border-radius:4px}.lg{font-size:12px;font-weight:600;color:#626F86;padding:8px 10px 4px}
.li{display:flex;align-items:center;gap:10px;padding:8px 10px;color:#172B4D;border-top:1px solid #F1F2F4}
.li:hover{background:#F7F8F9;text-decoration:none}.li .sum{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;
white-space:nowrap}.li .key,.li .rs{flex:none}
@media (max-width:1180px){.issue{flex-direction:column;gap:16px}.il{max-width:none}.ir{width:auto}}
.tabs{display:flex;gap:4px;margin-bottom:12px}.tab{padding:4px 10px;border-radius:4px;color:#44546F;font-weight:500}
.tab.on{background:#E9F2FF;color:#0C66E4}.tab:hover{text-decoration:none;background:#F1F2F4}
.act{display:flex;gap:12px;margin-bottom:16px}.ab{flex:1}.ah{display:flex;gap:8px;align-items:baseline;
margin-bottom:4px}.composer{flex:1;border:1px solid #DCDFE4;border-radius:4px;padding:8px 10px;color:#626F86}
.sr{display:flex;align-items:center;gap:12px;margin-bottom:16px}.status{display:inline-flex;align-items:center;gap:6px;
font-weight:600;padding:6px 12px;border-radius:4px}.res{color:#44546F}
.det{border:1px solid #DCDFE4;border-radius:6px}.dh{font-weight:600;padding:12px 16px;border-bottom:1px solid #DCDFE4}
.fl{display:flex;gap:12px;padding:8px 16px}.fn{width:130px;flex:none;color:#44546F;font-weight:600;font-size:13px;
padding-top:2px}.fv{flex:1;min-width:0}.none{color:#626F86}
.tt .bar{height:6px;background:#DCDFE4;border-radius:3px;overflow:hidden}.tt .bar span{display:block;height:100%;
background:#1D7AFC}.ttl{display:flex;justify-content:space-between;font-size:12px;color:#44546F;margin-top:4px}
.stamps{color:#626F86;font-size:12px;margin-top:12px;line-height:1.7}
.nf{padding:48px 0;text-align:center}
"""
