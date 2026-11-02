"""A small GitHub look-alike viewer for the seeded pull requests, so links in tool results open a real page.

Every page also exists under ``/v/{token}`` and shows one conversation's own changes (comments, reviews, labels, edits
and merges made with the write tools). Unscoped pages always show the original lab data."""

from __future__ import annotations

import hashlib
import html
import re
from contextvars import ContextVar
from datetime import datetime

from .store import COPILOT_REVIEWER, StateStore, Store
from .tools import comment_visible, parse, pr_matches, visible_reviews

e = html.escape

_HEADERS = {"Cache-Control": "no-store", "X-Robots-Tag": "noindex"}
_TOKEN = re.compile(r"[0-9a-f]{20}")
_LINK = re.compile(r'(href|action)="/(?!avatars/)')
_EXPIRED = ("No saved changes were found for this conversation (nothing was changed yet, or the changes expired after "
            "about 2 hours). Showing the original lab data.")
BADGE_SUB: ContextVar[str] = ContextVar("github_badge_sub", default="Original lab data")
NOTICE: ContextVar[str] = ContextVar("github_notice", default="")
_PALETTE = ["#0969da", "#8250df", "#bf3989", "#1a7f37", "#bc4c00", "#9a6700", "#cf222e", "#1b7c83"]


def when(iso: str | None) -> str:
    if not iso:
        return ""
    d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return f"{d.strftime('%b')} {d.day}, {d.year}"


def initials(name: str) -> str:
    parts = [p for p in re.split(r"[\s-]+", name) if p]
    return "".join(p[0] for p in parts[:2]).upper() or "?"


def avatar_svg(store: Store, login: str) -> str | None:
    if login == COPILOT_REVIEWER:
        return ('<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96">'
                '<circle cx="48" cy="48" r="48" fill="#1f2328"/><text x="48" y="58" text-anchor="middle" '
                'font-family="Segoe UI,Arial,sans-serif" font-size="30" font-weight="600" fill="#fff">CP</text></svg>')
    u = store.user(login)
    if u is None:
        return None
    color = _PALETTE[int(hashlib.sha256(u["login"].encode()).hexdigest(), 16) % len(_PALETTE)]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96">'
            f'<circle cx="48" cy="48" r="48" fill="{color}"/><text x="48" y="58" text-anchor="middle" '
            f'font-family="Segoe UI,Arial,sans-serif" font-size="36" font-weight="600" fill="#fff">'
            f'{e(initials(u["name"]))}</text></svg>')


def who(login: str) -> str:
    return "Copilot" if login == COPILOT_REVIEWER else login


def user_link(login: str) -> str:
    if login == COPILOT_REVIEWER:
        return "<strong>Copilot</strong>"
    return f'<a href="/{e(login)}"><strong>{e(login)}</strong></a>'


def av(login: str, size: int = 20) -> str:
    return (f'<img class="av" src="/avatars/{e(login)}.svg" width="{size}" height="{size}" alt="@{e(login)}">')


def text_color(hex6: str) -> str:
    r, g, b = (int(hex6[i:i + 2], 16) for i in (0, 2, 4))
    return "#1f2328" if (r * 299 + g * 587 + b * 114) / 1000 > 150 else "#ffffff"


def label_chip(repo: dict, name: str) -> str:
    lab = next((x for x in repo["labels"] if x["name"] == name), {"color": "ededed", "description": ""})
    q = f"is:pr label:{name}"
    return (f'<a class="lbl" href="/{repo["owner"]}/{repo["name"]}/pulls?q={e(q)}" title="{e(lab["description"])}" '
            f'style="background:#{lab["color"]};color:{text_color(lab["color"])}">{e(name)}</a>')


def markdown(text: str) -> str:
    out, items, para = [], [], []

    def flush():
        if para:
            out.append("<p>" + "<br>".join(e(x) for x in para) + "</p>")
            para.clear()
        if items:
            out.append("<ul>" + "".join(f"<li>{e(x)}</li>" for x in items) + "</ul>")
            items.clear()

    for line in (text or "").splitlines():
        s = line.strip()
        if not s:
            flush()
        elif s.startswith(("- ", "* ")):
            if para:
                flush()
            items.append(s[2:])
        else:
            if items:
                flush()
            para.append(s)
    flush()
    return "".join(out) or '<p class="muted"><em>No description provided.</em></p>'


OPEN_SVG = ('<svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor"><path d="M1.5 3.25a2.25 2.25 0 1 1 3 '
            '2.122v5.256a2.251 2.251 0 1 1-1.5 0V5.372A2.25 2.25 0 0 1 1.5 3.25Zm5.677-.177L9.573.677A.25.25 0 0 1 10 '
            '.854V2.5h1A2.5 2.5 0 0 1 13.5 5v5.628a2.251 2.251 0 1 1-1.5 0V5a1 1 0 0 0-1-1h-1v1.646a.25.25 0 0 1-.427'
            '.177L7.177 3.427a.25.25 0 0 1 0-.354ZM3.75 2.5a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Zm0 9.5a.75.75 0 1 0 '
            '0 1.5.75.75 0 0 0 0-1.5Zm8.25.75a.75.75 0 1 0 1.5 0 .75.75 0 0 0-1.5 0Z"/></svg>')
MERGED_SVG = ('<svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor"><path d="M5.45 5.154A4.25 4.25 0 0 0 '
              '9.25 7.5h1.378a2.251 2.251 0 1 1 0 1.5H9.25A5.734 5.734 0 0 1 5 7.123v3.505a2.25 2.25 0 1 1-1.5 0V5.372'
              'a2.25 2.25 0 1 1 1.95-.218ZM4.25 13.5a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm8.5-4.5a.75.75 0 1 0 0-1.5'
              '.75.75 0 0 0 0 1.5ZM5 3.25a.75.75 0 1 0 0 .005V3.25Z"/></svg>')
GH_SVG = ('<svg viewBox="0 0 16 16" width="32" height="32" fill="#fff"><path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 '
          '1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 '
          '0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 '
          '.27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-'
          '.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 '
          '1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"/>'
          '</svg>')


def state_badge(pr: dict) -> str:
    if pr["merged"]:
        return f'<span class="st merged">{MERGED_SVG} Merged</span>'
    if pr["state"] == "open":
        return f'<span class="st open">{OPEN_SVG} Open</span>'
    return f'<span class="st closed">{OPEN_SVG} Closed</span>'


def shell(store: Store, title: str, body: str, repo: dict | None = None, tab: str = "") -> str:
    me = store.me["login"]
    nav = ""
    if repo:
        n_open = sum(1 for p in repo["pulls"] if p["state"] == "open")
        base = f'/{repo["owner"]}/{repo["name"]}'
        tabs = [("code", "Code", base, ""), ("pulls", "Pull requests", base + "/pulls", str(n_open)),
                ("labels", "Labels", base + "/labels", "")]
        links = "".join(f'<a class="rt{" on" if k == tab else ""}" href="{h}">{t}'
                        f'{f"<span class=cnt>{c}</span>" if c else ""}</a>' for k, t, h, c in tabs)
        nav = (f'<div class="rh"><div class="rn"><a href="/{e(repo["owner"])}">{e(repo["owner"])}</a> / '
               f'<a href="{base}"><strong>{e(repo["name"])}</strong></a><span class="vis">'
               f'{"Private" if repo["private"] else "Public"}</span></div><nav class="rtabs">{links}</nav></div>')
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{e(title)} · GitHub</title>
<meta name="viewport" content="width=device-width,initial-scale=1"><style>{CSS}{_BADGE_CSS}</style></head><body>
<header class="top"><a class="logo" href="/" aria-label="Home">{GH_SVG}</a><span class="crumb">
{f'<a href="/{e(repo["owner"])}">{e(repo["owner"])}</a> / <a href="/{e(repo["owner"])}/{e(repo["name"])}">{e(repo["name"])}</a>' if repo else ""}
</span><form class="search" action="/{e(store.org["login"])}/{e(store.repos[0]["name"])}/pulls"><input name="q"
placeholder="Type / to search" aria-label="Search pull requests"></form><a href="/{e(me)}">{av(me, 32)}</a></header>
{nav}<main>{_notice()}{body}<footer>Mock environment for Microsoft Ignite lab LAB654. Not affiliated with GitHub. Data is
fictitious.</footer></main>{_mock_badge()}</body></html>"""


_BADGE_CSS = (".mock-badge{position:fixed;right:16px;bottom:16px;z-index:1000;display:flex;flex-direction:column;"
              "align-items:flex-end;background:#d13438;color:#fff;border-radius:8px;padding:6px 12px;"
              "box-shadow:0 4px 14px rgba(0,0,0,.2);font:12px/1.35 'Segoe UI',system-ui,sans-serif}"
              ".mock-badge .mb-top{font-weight:700;letter-spacing:.06em}.mock-badge .mb-sub{opacity:.92}")


def _mock_badge() -> str:
    return ('<div class="mock-badge" title="This is a mock GitHub page served by a mock MCP server. '
            'It is not GitHub."><span class="mb-top">MOCK GITHUB</span>'
            f'<span class="mb-sub">{e(BADGE_SUB.get())}</span></div>')


def _notice() -> str:
    text = NOTICE.get()
    return f'<div class="notice">{e(text)}</div>' if text else ""


def review_states(store: Store, pr: dict) -> dict[str, str]:
    """Latest decisive review state per reviewer; a later COMMENTED review doesn't clear an earlier verdict."""
    out: dict[str, str] = {}
    for r in sorted(visible_reviews(store, pr), key=lambda x: x.get("submitted_at") or ""):
        if r["state"] == "PENDING":
            continue
        if r["state"] in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED") or r["user"] not in out:
            out[r["user"]] = r["state"]
    return out


def reactions_html(items: list[dict]) -> str:
    emoji = {"+1": "&#128077;", "-1": "&#128078;", "laugh": "&#128516;", "confused": "&#128533;",
             "heart": "&#10084;&#65039;", "hooray": "&#127881;", "rocket": "&#128640;", "eyes": "&#128064;"}
    counts: dict[str, int] = {}
    for r in items or []:
        counts[r["content"]] = counts.get(r["content"], 0) + 1
    chips = "".join(f'<span class="rx">{emoji.get(k, e(k))} {n}</span>' for k, n in counts.items())
    return f'<div class="rxs">{chips}</div>' if chips else ""


def pr_row(store: Store, repo: dict, pr: dict) -> str:
    base = f'/{repo["owner"]}/{repo["name"]}'
    icon = MERGED_SVG if pr["merged"] else OPEN_SVG
    cls = "merged" if pr["merged"] else pr["state"]
    states = list(review_states(store, pr).values())
    review = ""
    if "CHANGES_REQUESTED" in states:
        review = '<span class="rv cr">Changes requested</span>'
    elif "APPROVED" in states:
        review = '<span class="rv ok">Approved</span>'
    if pr["merged"]:
        meta = f'by <a href="/{pr["user"]}">{e(pr["user"])}</a> was merged on {when(pr["merged_at"])}'
    else:
        meta = f'opened on {when(pr["created_at"])} by <a href="/{pr["user"]}">{e(pr["user"])}</a>'
    labels = " ".join(label_chip(repo, n) for n in pr["labels"])
    ms = f' <span class="ms">{e(pr["milestone"])}</span>' if pr.get("milestone") else ""
    who = "".join(av(a) for a in pr["assignees"])
    return (f'<div class="row"><span class="ic {cls}">{icon}</span><div class="rb"><a class="rtitle" '
            f'href="{base}/pull/{pr["number"]}">{e(pr["title"])}</a> {labels}<div class="meta">#{pr["number"]} '
            f'{meta}{" · " + review if review else ""}{ms}</div></div><div class="ra">{who}</div></div>')


def pulls_page(store: Store, repo: dict, q: str) -> str:
    q = q.strip() or "is:pr is:open"
    quals, words = parse(q if "is:pr" in q else "is:pr " + q)
    base = f'/{repo["owner"]}/{repo["name"]}'
    hits = sorted((p for p in repo["pulls"] if pr_matches(store, repo, p, quals, words)),
                  key=lambda p: p["created_at"], reverse=True)
    n_open = sum(1 for p in repo["pulls"] if p["state"] == "open")
    n_closed = len(repo["pulls"]) - n_open
    is_open = "is:open" in q
    is_closed = "is:closed" in q or "is:merged" in q
    rows = "".join(pr_row(store, repo, p) for p in hits) or '<div class="blank">No results matched your search.</div>'
    body = f"""<div class="bar"><form action="{base}/pulls" class="filter"><input name="q" value="{e(q)}"
aria-label="Search all pull requests"></form><a class="btn" href="{base}/labels">Labels</a></div>
<div class="box"><div class="bh"><a class="{'on' if is_open else ''}" href="{base}/pulls?q=is%3Apr+is%3Aopen">{OPEN_SVG}
{n_open} Open</a><a class="{'on' if is_closed else ''}" href="{base}/pulls?q=is%3Apr+is%3Aclosed">&#10003; {n_closed}
Closed</a></div>{rows}</div>"""
    return shell(store, f"Pull requests · {repo['owner']}/{repo['name']}", body, repo, "pulls")


def thread_html(store: Store, pr: dict, t: dict) -> str:
    items = [c for c in t["comments"] if comment_visible(store, pr, c)]
    if not items:
        return ""
    first = items[0]
    where = e(first["path"]) + (f' line {first["line"]}' if first.get("line") else "")
    resolved = '<span class="rv ok">Resolved</span>' if t["is_resolved"] else ""
    rows = "".join(f"""<div class="tc" id="discussion_r{c["id"]}">{av(c["user"])} {user_link(c["user"])}
<span class="muted">{when(c["created_at"])}</span><div class="md">{markdown(c["body"])}</div>
{reactions_html(c.get("reactions"))}</div>""" for c in items)
    return f'<div class="th"><div class="thh"><code>{where}</code>{resolved}</div>{rows}</div>'


def pr_page(store: Store, repo: dict, pr: dict) -> str:
    u = pr["user"]
    if pr["merged"]:
        sub = (f'{user_link(pr["merged_by"])} merged this pull request on {when(pr["merged_at"])}')
    else:
        sub = f'{user_link(u)} opened this pull request on {when(pr["created_at"])}'
    events: list[tuple[str, str]] = [(pr["created_at"], f"""<div class="tl"><a href="/{u}">{av(u, 40)}</a><div
class="cm"><div class="ch">{user_link(u)} commented on {when(pr["created_at"])}<span class="role">Member</span><span
class="role">Author</span></div><div class="cb md">{markdown(pr["body"])}</div>{reactions_html(pr.get("reactions"))}
</div></div>""")]
    by_review: dict[int, list[str]] = {}
    for t in pr["threads"]:
        block = thread_html(store, pr, t)
        if not block:
            continue
        rid = t["comments"][0].get("review_id")
        if rid is not None and any(r["id"] == rid for r in pr["reviews"]):
            by_review.setdefault(rid, []).append(block)
        else:
            events.append((t["comments"][0]["created_at"], f'<div class="tl solo">{block}</div>'))
    for r in pr["reviews"]:
        if r["state"] == "PENDING":
            continue
        verb, cls = {"APPROVED": ("approved these changes", "ok"), "CHANGES_REQUESTED": ("requested changes", "cr"),
                     "DISMISSED": ("reviewed (dismissed)", "cm2")}.get(r["state"], ("reviewed", "cm2"))
        body = f'<div class="cb md">{markdown(r["body"])}</div>' if r.get("body") else ""
        events.append((r.get("submitted_at") or "", f"""<div class="tl" id="pullrequestreview-{r["id"]}">
{av(r["user"], 40)}<div class="cm {cls}"><div class="ch">{user_link(r["user"])} {verb} on {when(r.get("submitted_at"))}
<span class="role">{"Bot" if r["user"] == COPILOT_REVIEWER else "Member"}</span></div>{body}
{"".join(by_review.get(r["id"], []))}</div></div>"""))
    for c in pr["comments"]:
        events.append((c["created_at"], f"""<div class="tl" id="issuecomment-{c["id"]}"><a href="/{c["user"]}">
{av(c["user"], 40)}</a><div class="cm"><div class="ch">{user_link(c["user"])} commented on {when(c["created_at"])}
<span class="role">Member</span></div><div class="cb md">{markdown(c["body"])}</div>{reactions_html(c.get("reactions"))}
</div></div>"""))
    if pr["merged"]:
        events.append((pr["merged_at"], f'<div class="ev"><span class="ic merged">{MERGED_SVG}</span>'
                       f'{user_link(pr["merged_by"])} merged this pull request on {when(pr["merged_at"])}</div>'))
    elif pr["state"] == "closed" and pr.get("closed_at"):
        events.append((pr["closed_at"], f'<div class="ev"><span class="ic closed">{OPEN_SVG}</span>'
                       f'This pull request was closed on {when(pr["closed_at"])}</div>'))
    events.sort(key=lambda x: x[0] or "")
    states = review_states(store, pr)
    label = {"APPROVED": ("ok", "Approved"), "CHANGES_REQUESTED": ("cr", "Changes requested"),
             "COMMENTED": ("cm2", "Commented"), "DISMISSED": ("cm2", "Dismissed")}
    rows = []
    for login in pr["requested_reviewers"]:
        rows.append(f'<div class="si">{av(login)} {user_link(login)}<span class="rv pend">Awaiting review</span></div>')
    for login, st in states.items():
        if login in pr["requested_reviewers"]:
            continue
        cls, text = label.get(st, ("cm2", st.title()))
        rows.append(f'<div class="si">{av(login)} {user_link(login)}<span class="rv {cls}">{text}</span></div>')
    reviewers = "".join(rows) or '<div class="muted">No reviews</div>'
    assignees = "".join(f'<div class="si">{av(a)} <a href="/{a}">{e(a)}</a></div>' for a in pr["assignees"]) \
        or '<div class="muted">No one assigned</div>'
    labels = " ".join(label_chip(repo, n) for n in pr["labels"]) or '<div class="muted">None yet</div>'
    ms = e(pr["milestone"]) if pr.get("milestone") else '<span class="muted">No milestone</span>'
    n_conv = len(pr["comments"]) + sum(1 for r in pr["reviews"] if r["state"] != "PENDING")
    body = f"""<div class="ph"><h1>{e(pr["title"])} <span class="num">#{pr["number"]}</span></h1>
<div class="phs">{state_badge(pr)} <span>{sub}</span></div></div><nav class="ptabs"><a class="on">Conversation
<span class="cnt">{n_conv}</span></a></nav><div class="pw"><div class="pl">{"".join(x for _, x in events)}</div>
<aside class="ps"><div class="sb"><h3>Reviewers</h3>{reviewers}</div><div class="sb"><h3>Assignees</h3>{assignees}
</div><div class="sb"><h3>Labels</h3>{labels}</div><div class="sb"><h3>Milestone</h3>{ms}</div></aside></div>"""
    return shell(store, f"{pr['title']} by {u} · Pull Request #{pr['number']} · {repo['owner']}/{repo['name']}",
                 body, repo, "pulls")


def repo_page(store: Store, repo: dict) -> str:
    base = f'/{repo["owner"]}/{repo["name"]}'
    recent = "".join(pr_row(store, repo, p) for p in sorted(repo["pulls"], key=lambda p: p["updated_at"],
                                                             reverse=True))
    body = f"""<div class="pw"><div class="pl"><div class="box"><div class="bh"><strong>Recent pull requests</strong>
<a class="more" href="{base}/pulls?q=is%3Apr">View all</a></div>{recent}</div><p class="muted">Source files aren't part
of this mock. It serves pull requests, reviews and labels only.</p></div><aside class="ps"><div class="sb"><h3>About
</h3><p>{e(repo["description"])}</p><p class="muted">Default branch: {e(repo["default_branch"])}</p></div>
<div class="sb"><h3>Labels</h3>{" ".join(label_chip(repo, x["name"]) for x in repo["labels"])}</div></aside></div>"""
    return shell(store, f"{repo['owner']}/{repo['name']}: {repo['description']}", body, repo, "code")


def labels_page(store: Store, repo: dict) -> str:
    rows = "".join(
        f'<div class="row"><div class="lc">{label_chip(repo, x["name"])}</div><div class="rb muted">'
        f'{e(x["description"])}</div><div class="ra muted">{sum(x["name"] in p["labels"] for p in repo["pulls"])} '
        f'pull requests</div></div>' for x in repo["labels"])
    body = f'<div class="box"><div class="bh"><strong>{len(repo["labels"])} labels</strong></div>{rows}</div>'
    return shell(store, f"Labels · {repo['owner']}/{repo['name']}", body, repo, "labels")


def org_page(store: Store) -> str:
    org = store.org
    rows = "".join(f'<div class="row"><div class="rb"><a class="rtitle" href="/{r["owner"]}/{r["name"]}">'
                   f'{e(r["name"])}</a> <span class="vis">{"Private" if r["private"] else "Public"}</span>'
                   f'<div class="meta">{e(r["description"])} · Updated {when(max(p["updated_at"] for p in r["pulls"]))}'
                   f'</div></div></div>' for r in store.repos)
    people = "".join(f'<a href="/{u["login"]}" title="{e(u["name"])}">{av(u["login"], 32)}</a>'
                     for u in store.users.values())
    body = f"""<div class="org"><div class="oav">{initials(org["name"])}</div><div><h1>{e(org["name"])}</h1>
<p class="muted">{e(org["description"])}</p></div></div><div class="pw"><div class="pl"><div class="box"><div class="bh">
<strong>Repositories</strong></div>{rows}</div></div><aside class="ps"><div class="sb"><h3>People</h3><div
class="people">{people}</div></div></aside></div>"""
    return shell(store, org["name"], body)


def user_page(store: Store, user: dict) -> str:
    authored = [(r, p) for r in store.repos for p in r["pulls"] if p["user"] == user["login"]]
    rows = "".join(pr_row(store, r, p) for r, p in authored) or '<div class="blank">No pull requests.</div>'
    body = f"""<div class="pw"><aside class="up"><img class="av big" src="/avatars/{user["login"]}.svg" width="260"
height="260" alt=""><h1>{e(user["name"])}</h1><div class="login">{e(user["login"])}</div><p>{e(user["bio"])}</p>
<p class="muted">{e(user["company"])}</p></aside><div class="pl"><div class="box"><div class="bh"><strong>Pull requests
</strong></div>{rows}</div></div></div>"""
    return shell(store, f"{user['login']} ({user['name']})", body)


def not_found_page(store: Store) -> str:
    body = ('<div class="nf"><h1>404</h1><p>This is not the web page you are looking for.</p>'
            f'<p><a href="/{store.org["login"]}">Go to {e(store.org["name"])}</a></p></div>')
    return shell(store, "Page not found", body)


# --- routes --------------------------------------------------------------------------------------------------------

def build_routes(state: StateStore, clock_factory=None) -> list:
    from starlette.responses import HTMLResponse, RedirectResponse, Response
    from starlette.routing import Route

    def resolve(request) -> tuple[Store, str, str, str] | None:
        """(store, link prefix, badge sub-line, notice) or None for a malformed token."""
        token = request.path_params.get("token")
        if token is None:
            return state.seed, "", "Original lab data", ""
        if not _TOKEN.fullmatch(token):
            return None
        store, scoped = state.read_by_token(token)
        if scoped:
            return store, f"/v/{token}", "This conversation's changes", ""
        return store, f"/v/{token}", "Original lab data", _EXPIRED

    def page(render):
        async def endpoint(request):
            found = resolve(request)
            if found is None:
                return HTMLResponse(not_found_page(state.seed), status_code=404, headers=_HEADERS)
            store, prefix, sub, notice = found
            t1, t2 = BADGE_SUB.set(sub), NOTICE.set(notice)
            try:
                result = render(request, store, prefix)
            finally:
                BADGE_SUB.reset(t1)
                NOTICE.reset(t2)
            if isinstance(result, tuple):
                text, status = result
                if prefix:
                    text = _LINK.sub(lambda m: f'{m.group(1)}="{prefix}/', text)
                return HTMLResponse(text, status_code=status, headers=_HEADERS)
            return result
        return endpoint

    def get_repo(request, store: Store) -> dict | None:
        return store.repo(request.path_params["owner"], request.path_params["repo"])

    def get_pr(request, store: Store) -> tuple[dict | None, dict | None]:
        repo = get_repo(request, store)
        num = request.path_params["number"]
        return repo, next((p for p in repo["pulls"] if str(p["number"]) == num), None) if repo else None

    def missing(store: Store):
        return not_found_page(store), 404

    def home(request, store, prefix):
        return RedirectResponse(f"{prefix}/{store.org['login']}", status_code=302)

    def owner(request, store, prefix):
        login = request.path_params["owner"]
        if login.lower() == store.org["login"].lower():
            return org_page(store), 200
        user = store.user(login)
        return (user_page(store, user), 200) if user else missing(store)

    def repo_home(request, store, prefix):
        repo = get_repo(request, store)
        return (repo_page(store, repo), 200) if repo else missing(store)

    def pulls(request, store, prefix):
        repo = get_repo(request, store)
        return (pulls_page(store, repo, request.query_params.get("q", "")), 200) if repo else missing(store)

    def pull(request, store, prefix):
        repo, pr = get_pr(request, store)
        return (pr_page(store, repo, pr), 200) if pr else missing(store)

    def issue(request, store, prefix):
        repo, pr = get_pr(request, store)
        if pr is None:
            return missing(store)
        return RedirectResponse(f"{prefix}/{repo['owner']}/{repo['name']}/pull/{pr['number']}", status_code=302)

    def labels(request, store, prefix):
        repo = get_repo(request, store)
        return (labels_page(store, repo), 200) if repo else missing(store)

    async def avatar(request):
        svg = avatar_svg(state.seed, request.path_params["login"])
        if svg is None:
            return Response("Not found", status_code=404)
        return Response(svg, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})

    routes = [Route("/avatars/{login}.svg", avatar), Route("/", page(home)), Route("/v/{token}", page(home)),
              Route("/v/{token}/", page(home))]
    for base in ("/v/{token}", ""):
        routes += [
            Route(base + "/{owner}", page(owner)),
            Route(base + "/{owner}/{repo}", page(repo_home)),
            Route(base + "/{owner}/{repo}/pulls", page(pulls)),
            Route(base + "/{owner}/{repo}/pull/{number}", page(pull)),
            Route(base + "/{owner}/{repo}/pull/{number}/{tab}", page(pull)),
            Route(base + "/{owner}/{repo}/issues/{number}", page(issue)),
            Route(base + "/{owner}/{repo}/labels", page(labels)),
        ]
    return routes

CSS = """
.notice{background:#fff8c5;border:1px solid #d4a72c66;border-radius:6px;padding:8px 12px;margin-bottom:16px}
.rxs{display:flex;gap:6px;padding:0 16px 10px}.rx{border:1px solid #d1d9e0;border-radius:999px;padding:0 8px;
font-size:12px;background:#f6f8fa}.th{border:1px solid #d1d9e0;border-radius:6px;margin:8px 16px 12px}
.thh{display:flex;gap:8px;align-items:center;padding:6px 10px;background:#f6f8fa;border-bottom:1px solid #d1d9e0}
.tc{padding:8px 10px;border-top:1px solid #eef1f4}.tc:first-of-type{border-top:0}.tc .md{margin-top:4px}
.tl.solo{display:block}.rv.pend{background:#fff8c5;color:#7d4e00}
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,
Arial,sans-serif;font-size:14px;line-height:1.5;color:#1f2328;background:#fff}a{color:#0969da;text-decoration:none}
a:hover{text-decoration:underline}.muted{color:#59636e}
.top{display:flex;align-items:center;gap:16px;padding:12px 24px;background:#f6f8fa;border-bottom:1px solid #d1d9e0}
.top .logo{display:flex;background:#1f2328;border-radius:50%;padding:2px}.crumb{font-size:14px;flex:1}
.crumb a{color:#1f2328}.search input{width:280px;border:1px solid #d1d9e0;border-radius:6px;padding:5px 10px;
font:inherit;background:#fff}.av{border-radius:50%;vertical-align:middle;background:#eee}
.rh{background:#f6f8fa;border-bottom:1px solid #d1d9e0;padding:16px 32px 0}.rn{font-size:20px;display:flex;
align-items:center;gap:6px}.rn a{color:#0969da}.vis{font-size:12px;border:1px solid #d1d9e0;border-radius:2em;
padding:0 7px;color:#59636e;font-weight:500}.rtabs{display:flex;gap:8px;margin-top:12px}.rt{padding:8px 12px;
color:#1f2328;border-bottom:2px solid transparent}.rt.on{border-bottom-color:#fd8c73;font-weight:600}
.rt:hover{text-decoration:none;background:#eaeef2;border-radius:6px 6px 0 0}.cnt{display:inline-block;min-width:20px;
margin-left:6px;padding:0 6px;font-size:12px;font-weight:500;background:#818b981f;border-radius:2em;text-align:center}
main{max-width:1280px;margin:0 auto;padding:24px 32px}footer{margin-top:48px;color:#59636e;font-size:12px;
border-top:1px solid #d1d9e0;padding-top:16px}
.bar{display:flex;gap:8px;margin-bottom:16px}.filter{flex:1}.filter input{width:100%;border:1px solid #d1d9e0;
border-radius:6px;padding:5px 12px;font:inherit;background:#f6f8fa}.btn{border:1px solid #d1d9e0;border-radius:6px;
padding:5px 16px;color:#1f2328;background:#f6f8fa;font-weight:500}
.box{border:1px solid #d1d9e0;border-radius:6px}.bh{display:flex;gap:16px;align-items:center;padding:12px 16px;
background:#f6f8fa;border-bottom:1px solid #d1d9e0;border-radius:6px 6px 0 0}.bh a{color:#59636e;display:flex;
align-items:center;gap:4px}.bh a.on{color:#1f2328;font-weight:600}.bh .more{margin-left:auto;color:#0969da}
.row{display:flex;gap:10px;padding:10px 16px;border-top:1px solid #d1d9e0}.bh+.row{border-top:0}
.row:hover{background:#f6f8fa}.rb{flex:1;min-width:0}.ra{display:flex;gap:4px;align-items:flex-start}
.rtitle{color:#1f2328;font-weight:600;font-size:16px}.rtitle:hover{color:#0969da}.meta{color:#59636e;font-size:12px;
margin-top:2px}.meta a{color:#59636e}.ms{margin-left:8px}.ic{padding-top:3px}.ic.open{color:#1a7f37}
.ic.merged{color:#8250df}.ic.closed{color:#cf222e}.blank{padding:32px;text-align:center;color:#59636e}
.lbl{display:inline-block;font-size:12px;font-weight:500;padding:0 7px;border-radius:2em;line-height:20px;
vertical-align:middle}.lbl:hover{text-decoration:none}.lc{width:200px}
.rv{font-size:12px;font-weight:500}.rv.cr{color:#cf222e}.rv.ok{color:#1a7f37}
.ph h1{font-size:32px;font-weight:400;margin:0 0 8px}.ph .num{color:#59636e;font-weight:300}.phs{display:flex;
align-items:center;gap:8px;color:#59636e;padding-bottom:16px;border-bottom:1px solid #d1d9e0}.phs a{color:#59636e}
.st{display:inline-flex;align-items:center;gap:4px;color:#fff;font-weight:500;padding:5px 12px;border-radius:2em}
.st.open{background:#1f883d}.st.merged{background:#8250df}.st.closed{background:#cf222e}
.ptabs{display:flex;margin:16px 0 0;border-bottom:1px solid #d1d9e0}.ptabs a{padding:8px 16px;border:1px solid
#d1d9e0;border-bottom:0;border-radius:6px 6px 0 0;margin-bottom:-1px;background:#fff;color:#1f2328}
.pw{display:flex;gap:24px;margin-top:16px}.pl{flex:1;min-width:0}.ps{width:296px;flex:none}
.sb{padding:16px 0;border-bottom:1px solid #d1d9e0}.sb:first-child{padding-top:0}.sb h3{font-size:12px;color:#59636e;
margin:0 0 8px;font-weight:600}.si{display:flex;align-items:center;gap:6px;margin:4px 0}.si a{color:#1f2328;
font-weight:600}.si .rv{margin-left:auto}
.tl{display:flex;gap:16px;margin-bottom:16px}.cm{flex:1;border:1px solid #d1d9e0;border-radius:6px}.ch{display:flex;
align-items:center;gap:6px;padding:8px 16px;background:#f6f8fa;border-bottom:1px solid #d1d9e0;color:#59636e;
border-radius:6px 6px 0 0}.ch a{color:#1f2328}.cm.ok{border-color:#1a7f37}.cm.ok .ch{background:#dafbe1}
.cm.cr{border-color:#cf222e}.cm.cr .ch{background:#ffebe9}.role{margin-left:auto;font-size:12px;border:1px solid
#d1d9e0;border-radius:2em;padding:0 7px}.role+.role{margin-left:0}.cb{padding:16px}.md p{margin:0 0 12px}
.md ul{margin:0 0 12px;padding-left:2em}.md>:last-child{margin-bottom:0}.ev{display:flex;align-items:center;gap:8px;
margin:0 0 16px 56px;color:#59636e}.ev a{color:#1f2328}
.org{display:flex;gap:24px;align-items:center;margin-bottom:24px}.org h1{margin:0;font-size:24px}.oav{width:100px;
height:100px;border-radius:12px;background:#1f2328;color:#fff;display:flex;align-items:center;justify-content:center;
font-size:36px;font-weight:600}.people{display:flex;flex-wrap:wrap;gap:6px}
.up{width:296px;flex:none}.up .big{width:100%;height:auto}.up h1{font-size:24px;margin:16px 0 0}.login{font-size:20px;
color:#59636e;font-weight:300}.nf{text-align:center;padding:64px 0}.nf h1{font-size:64px;margin:0}
@media (max-width:900px){.pw{flex-direction:column}.ps,.up{width:auto}}
"""
