"""Turns the site data into the JSON shapes the Atlassian Rovo MCP server returns.

Shapes were captured from the live ``/v1/mcp`` endpoint. The real server mixes two URL bases: REST ``self`` links on
``api.atlassian.com/ex/jira/{cloudId}`` and browse links on the site host. The mock serves both from
``PUBLIC_BASE_URL``.
"""

from __future__ import annotations

import base64
import hashlib
import html as _html
import os
import re
from contextvars import ContextVar
from typing import Any
from urllib.parse import quote

from .store import Site

PRETTY_EXPAND = "renderedFields,names,schema,operations,editmeta,changelog,versionedRepresentations"
DEFAULT_FIELDS = ("summary", "issuetype", "components", "created", "description", "project", "reporter", "priority",
                  "resolution", "labels", "assignee", "updated", "status")
# Order used when a caller asks for more than the default fields.
ALL_FIELDS = ("summary", "issuetype", "parent", "timeestimate", "timeoriginalestimate", "customfield_10020",
              "components", "created", "description", "project", "reporter", "priority", "resolution", "labels",
              "assignee", "issuelinks", "updated", "status", "comment", "timetracking", "worklog")
FIELD_ALIASES = {"sprint": "customfield_10020", "type": "issuetype", "issuetype": "issuetype", "links": "issuelinks",
                 "comments": "comment"}
CATEGORIES = {
    2: {"key": "new", "colorName": "blue-gray", "name": "To Do", "graph": "BLUE_GRAY"},
    4: {"key": "indeterminate", "colorName": "yellow", "name": "In Progress", "graph": "YELLOW"},
    3: {"key": "done", "colorName": "green", "name": "Done", "graph": "GREEN"},
}
HOURS_PER_DAY = 8
DAYS_PER_WEEK = 5
# "/v/{token}" while a tool runs for a conversation, so browse links open that conversation's copy in the viewer.
VIEW_SCOPE: ContextVar[str] = ContextVar("jira_view_scope", default="")


def base_url() -> str:
    return os.environ.get("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")


def site_url() -> str:
    return base_url()


def api(site: Site) -> str:
    return f"{base_url()}/ex/jira/{site.data['site']['cloudId']}"


def browse_url(key: str) -> str:
    """Browse link for an issue; inside a tool call with a conversation it opens that conversation's view."""
    return f"{site_url()}{VIEW_SCOPE.get()}/browse/{key}"


# --- identifiers ---------------------------------------------------------------------------------------------------

def issue_ari(site: Site, issue: dict) -> str:
    return f"ari:cloud:jira:{site.data['site']['cloudId']}:issue/{issue['id']}"


def user_ari(user: dict) -> str:
    return f"ari:cloud:identity::user/{user['accountId']}"


def sprint_ari(site: Site, sprint_id: int | str) -> str:
    return f"ari:cloud:jira-software:{site.data['site']['cloudId']}:sprint/{sprint_id}"


def avatar(user: dict) -> str:
    digest = hashlib.md5(user["email"].lower().encode()).hexdigest()
    n = int(hashlib.md5(user["accountId"].encode()).hexdigest()[:2], 16) % 5 + 1
    fallback = quote(f"https://avatar-management--avatars.us-west-2.prod.public.atl-paas.net/initials/"
                     f"{user['initials']}-{n}.png", safe="")
    return f"https://secure.gravatar.com/avatar/{digest}?d={fallback}"


# --- text ----------------------------------------------------------------------------------------------------------

def plain_text(markdown: str | None) -> str:
    """Markdown with the emphasis removed and blank lines collapsed, as Teamwork Graph returns descriptions."""
    if not markdown:
        return ""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", markdown)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    return re.sub(r"\n{2,}", "\n", text).strip()


def snippet(markdown: str | None, limit: int = 150) -> str:
    text = re.sub(r"\s+", " ", plain_text(markdown)).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:.") + "..."


def _inline(text: str) -> list[dict]:
    nodes: list[dict] = []
    for part in re.split(r"(\*\*[^*]+\*\*)", text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            nodes.append({"type": "text", "text": part[2:-2], "marks": [{"type": "strong"}]})
        else:
            nodes.append({"type": "text", "text": part})
    return nodes


def to_adf(markdown: str | None) -> dict | None:
    """A small markdown-to-ADF conversion: headings, bullet lists, tables and paragraphs."""
    if markdown is None:
        return None
    content: list[dict] = []
    for block in re.split(r"\n\s*\n", markdown.strip()):
        lines = [line for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        if all(line.lstrip().startswith(("- ", "* ")) for line in lines):
            items = [{"type": "listItem", "content": [{"type": "paragraph",
                                                        "content": _inline(line.lstrip()[2:])}]} for line in lines]
            content.append({"type": "bulletList", "content": items})
        elif all(re.match(r"\s*\d+\.\s", line) for line in lines):
            items = [{"type": "listItem", "content": [{"type": "paragraph", "content": _inline(
                re.sub(r"\s*\d+\.\s+", "", line, count=1))}]} for line in lines]
            content.append({"type": "orderedList", "attrs": {"order": 1}, "content": items})
        elif all(line.lstrip().startswith("|") for line in lines):
            rows = []
            for i, line in enumerate(lines):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                    continue
                cell_type = "tableHeader" if i == 0 else "tableCell"
                rows.append({"type": "tableRow", "content": [
                    {"type": cell_type, "content": [{"type": "paragraph", "content": _inline(c)}]} for c in cells]})
            content.append({"type": "table", "content": rows})
        elif re.match(r"#{1,6} ", lines[0]) and len(lines) == 1:
            level = len(lines[0].split(" ", 1)[0])
            content.append({"type": "heading", "attrs": {"level": level}, "content": _inline(lines[0][level + 1:])})
        else:
            nodes: list[dict] = []
            for i, line in enumerate(lines):
                if i:
                    nodes.append({"type": "hardBreak"})
                nodes.extend(_inline(line))
            content.append({"type": "paragraph", "content": nodes})
    return {"type": "doc", "version": 1, "content": content}


def from_adf(node: Any) -> str:
    """Flatten an ADF document (dict or JSON string) back to markdown-ish text."""
    if isinstance(node, str):
        return node
    if not isinstance(node, dict):
        return ""
    kind = node.get("type")
    children = node.get("content") or []
    if kind == "text":
        text = node.get("text", "")
        if any(m.get("type") == "strong" for m in node.get("marks") or []):
            text = f"**{text}**"
        return text
    if kind == "hardBreak":
        return "\n"
    inner = "".join(from_adf(c) for c in children)
    if kind == "doc":
        return "\n\n".join(from_adf(c) for c in children).strip()
    if kind == "bulletList":
        return "\n".join(f"- {from_adf(c).strip()}" for c in children)
    if kind == "orderedList":
        return "\n".join(f"{i}. {from_adf(c).strip()}" for i, c in enumerate(children, 1))
    if kind == "heading":
        return "#" * int((node.get("attrs") or {}).get("level", 1)) + " " + inner
    if kind == "listItem":
        return " ".join(from_adf(c) for c in children)
    return inner


def body(text: str | None, fmt: str | None) -> Any:
    return to_adf(text) if fmt == "adf" else text


# --- Confluence ----------------------------------------------------------------------------------------------------

def wiki_base() -> str:
    return f"{site_url()}/wiki"


def page_ari(site: Site, page: dict) -> str:
    return f"ari:cloud:confluence:{site.data['site']['cloudId']}:page/{page['id']}"


def page_slug(title: str) -> str:
    return "+".join(re.findall(r"[\w-]+", title)) or "page"


def page_path(site: Site, page: dict) -> str:
    """The page's web UI path below /wiki, as Confluence puts in ``_links.webui``."""
    space = site.spaces.get(page.get("spaceId"))
    return f"/spaces/{space['key'] if space else 'AUR'}/pages/{page['id']}/{page_slug(page['title'])}"


def page_url(site: Site, page: dict) -> str:
    """Browse link for a page; inside a tool call with a conversation it opens that conversation's view."""
    return f"{site_url()}{VIEW_SCOPE.get()}/wiki{page_path(site, page)}"


def _html_inline(text: str) -> str:
    out = _html.escape(text, quote=False)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', out)


def to_html(markdown: str | None) -> str:
    """Markdown to the structured HTML Confluence returns for ``contentFormat: html``."""
    out: list[str] = []
    for block in re.split(r"\n\s*\n", (markdown or "").strip()):
        lines = [line for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        if all(line.lstrip().startswith(("- ", "* ")) for line in lines):
            out.append("<ul>" + "".join(f"<li><p>{_html_inline(x.lstrip()[2:])}</p></li>" for x in lines) + "</ul>")
        elif all(re.match(r"\s*\d+\.\s", line) for line in lines):
            items = [_html_inline(re.sub(r"^\s*\d+\.\s+", "", x)) for x in lines]
            out.append("<ol>" + "".join(f"<li><p>{x}</p></li>" for x in items) + "</ol>")
        elif all(line.lstrip().startswith("|") for line in lines):
            rows = []
            for i, line in enumerate(lines):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                    continue
                tag = "th" if i == 0 else "td"
                rows.append("<tr>" + "".join(f"<{tag}><p>{_html_inline(c)}</p></{tag}>" for c in cells) + "</tr>")
            out.append("<table><tbody>" + "".join(rows) + "</tbody></table>")
        elif re.match(r"#{1,6} ", lines[0]) and len(lines) == 1:
            level = len(lines[0].split(" ", 1)[0])
            out.append(f"<h{level}>{_html_inline(lines[0][level + 1:])}</h{level}>")
        else:
            out.append("<p>" + "<br />".join(_html_inline(x) for x in lines) + "</p>")
    return "".join(out)


def from_html(text: str) -> str:
    """Structured HTML (as agents write page bodies) back to markdown for storage."""
    s = re.sub(r"\s*\n\s*", " ", text)
    s = re.sub(r"<(strong|b)>(.*?)</\1>", r"**\2**", s, flags=re.I | re.S)
    s = re.sub(r"<code>(.*?)</code>", r"`\1`", s, flags=re.I | re.S)
    s = re.sub(r'<a\s[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r"[\2](\1)", s, flags=re.I | re.S)
    s = re.sub(r"<h([1-6])[^>]*>(.*?)</h\1>", lambda m: "\n\n" + "#" * int(m.group(1)) + " " + m.group(2) + "\n\n",
               s, flags=re.I | re.S)

    def table(m: re.Match) -> str:
        rows = []
        for row in re.findall(r"<tr[^>]*>(.*?)</tr>", m.group(0), flags=re.I | re.S):
            cells = [re.sub(r"<[^>]+>", "", c).strip() for c in
                     re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, flags=re.I | re.S)]
            rows.append("| " + " | ".join(cells) + " |")
            if len(rows) == 1:
                rows.append("|" + "---|" * len(cells))
        return "\n\n" + "\n".join(rows) + "\n\n"

    s = re.sub(r"<table[^>]*>.*?</table>", table, s, flags=re.I | re.S)

    def listing(m: re.Match) -> str:
        items = re.findall(r"<li[^>]*>(.*?)</li>", m.group(2), flags=re.I | re.S)
        marks = [f"{i}." if m.group(1).lower() == "ol" else "-" for i in range(1, len(items) + 1)]
        return "\n\n" + "\n".join(f"{k} {re.sub(r'<[^>]+>', '', x).strip()}" for k, x in zip(marks, items)) + "\n\n"

    s = re.sub(r"<(ul|ol)[^>]*>(.*?)</\1>", listing, s, flags=re.I | re.S)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</p>|</div>", "\n\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = _html.unescape(s)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(line.strip() for line in s.splitlines())).strip()


# --- durations -----------------------------------------------------------------------------------------------------

def format_duration(seconds: int) -> str:
    minutes = seconds // 60
    parts = []
    for unit, size in (("w", 60 * HOURS_PER_DAY * DAYS_PER_WEEK), ("d", 60 * HOURS_PER_DAY), ("h", 60), ("m", 1)):
        if minutes >= size:
            parts.append(f"{minutes // size}{unit}")
            minutes %= size
    return " ".join(parts) or "0m"


def parse_duration(text: str) -> int | None:
    """Seconds in a Jira duration such as ``2h 30m`` or ``1d``; None if it isn't one."""
    sizes = {"w": 3600 * HOURS_PER_DAY * DAYS_PER_WEEK, "d": 3600 * HOURS_PER_DAY, "h": 3600, "m": 60}
    total = 0
    matched = False
    rest = text.strip().lower()
    for amount, unit in re.findall(r"(\d+(?:\.\d+)?)\s*([wdhm])", rest):
        total += int(float(amount) * sizes[unit])
        matched = True
    leftover = re.sub(r"(\d+(?:\.\d+)?)\s*([wdhm])", "", rest).strip()
    if not matched or leftover:
        return None
    return total


def logged_seconds(issue: dict) -> int:
    return sum(w["timeSpentSeconds"] for w in issue.get("worklogs", []))


# --- field objects -------------------------------------------------------------------------------------------------

def user_obj(site: Site, user: dict | None, full: bool = True) -> dict | None:
    if user is None:
        return None
    if not full:
        return {"accountId": user["accountId"], "displayName": user["displayName"]}
    pic = avatar(user)
    out: dict[str, Any] = {
        "self": f"{api(site)}/rest/api/3/user?accountId={quote(user['accountId'], safe='')}",
        "accountId": user["accountId"],
    }
    if user["key"] == site.data["currentUser"]:
        out["emailAddress"] = user["email"]
    out.update({
        "avatarUrls": {"48x48": pic, "24x24": pic, "16x16": pic, "32x32": pic},
        "displayName": user["displayName"],
        "active": True,
        "timeZone": "Etc/GMT",
        "accountType": "atlassian",
    })
    return out


def issuetype_obj(site: Site, t: dict, entity: bool = True) -> dict:
    out = {
        "self": f"{api(site)}/rest/api/3/issuetype/{t['id']}",
        "id": t["id"],
        "description": t["description"],
        "iconUrl": f"{api(site)}/rest/api/2/universal_avatar/view/type/issuetype/avatar/{t['avatarId']}?size=medium",
        "name": t["name"],
        "subtask": t["subtask"],
        "avatarId": t["avatarId"],
    }
    if entity:
        out["entityId"] = t["entityId"]
    out["hierarchyLevel"] = t["hierarchyLevel"]
    return out


def project_avatars(site: Site) -> dict:
    root = f"{api(site)}/rest/api/3/universal_avatar/view/type/project/avatar/{site.project['avatarId']}"
    return {"48x48": root, "24x24": f"{root}?size=small", "16x16": f"{root}?size=xsmall",
            "32x32": f"{root}?size=medium"}


def project_obj(site: Site) -> dict:
    p = site.project
    return {"self": f"{api(site)}/rest/api/3/project/{p['id']}", "id": p["id"], "key": p["key"], "name": p["name"],
            "projectTypeKey": p["projectTypeKey"], "simplified": p["simplified"], "avatarUrls": project_avatars(site)}


def priority_obj(site: Site, name: str | None) -> dict | None:
    p = site.priorities.get(name or "")
    if p is None:
        return None
    return {"self": f"{api(site)}/rest/api/3/priority/{p['id']}",
            "iconUrl": f"{site_url()}/images/icons/priorities/{p['icon']}", "name": p["name"], "id": p["id"]}


def category_obj(site: Site, category: int) -> dict:
    c = CATEGORIES[category]
    return {"self": f"{api(site)}/rest/api/3/statuscategory/{category}", "id": category, "key": c["key"],
            "colorName": c["colorName"], "name": c["name"]}


def status_obj(site: Site, name: str) -> dict:
    s = site.statuses[name]
    return {"self": f"{api(site)}/rest/api/3/status/{s['id']}", "description": "", "iconUrl": f"{api(site)}/",
            "name": s["name"], "id": s["id"], "statusCategory": category_obj(site, s["category"])}


def sprint_obj(site: Site, sprint_id: int | None) -> list[dict] | None:
    sprint = site.sprints.get(sprint_id) if sprint_id is not None else None
    if sprint is None:
        return None
    return [{k: sprint[k] for k in ("id", "name", "state", "boardId", "goal", "startDate", "endDate")}]


def comment_obj(site: Site, issue: dict, c: dict, fmt: str | None, full: bool = False) -> dict:
    author = site.users.get(c["author"])
    out: dict[str, Any] = {}
    if full:
        out["self"] = f"{api(site)}/rest/api/3/issue/{issue['id']}/comment/{c['id']}"
    out.update({"id": c["id"], "body": body(c["body"], fmt), "created": c["created"],
                "updated": c.get("updated", c["created"])})
    out["author"] = user_obj(site, author, full=full)
    if full:
        out["updateAuthor"] = out["author"]
        out["jsdPublic"] = True
    return out


def linked_issue(site: Site, issue: dict) -> dict:
    return {"id": issue["id"], "key": issue["key"], "self": f"{api(site)}/rest/api/3/issue/{issue['id']}",
            "fields": {"summary": issue["summary"], "status": status_obj(site, issue["status"]),
                       "priority": priority_obj(site, issue["priority"]),
                       "issuetype": issuetype_obj(site, site.types[issue["type"]])}}


def link_type_obj(site: Site, name: str) -> dict:
    t = site.link_types[name]
    return {"id": t["id"], "name": t["name"], "inward": t["inward"], "outward": t["outward"],
            "self": f"{api(site)}/rest/api/3/issueLinkType/{t['id']}"}


def issue_links(site: Site, issue: dict) -> list[dict]:
    """Links stored on this issue point outward; links stored on other issues that name it point inward."""
    out = []
    for link in issue.get("links", []):
        other = site.issue(link["outward"])
        if other:
            out.append({"id": link["id"], "self": f"{api(site)}/rest/api/3/issueLink/{link['id']}",
                        "type": link_type_obj(site, link["type"]), "outwardIssue": linked_issue(site, other)})
    for other in site.data["issues"]:
        for link in other.get("links", []):
            if link["outward"] == issue["key"]:
                out.append({"id": link["id"], "self": f"{api(site)}/rest/api/3/issueLink/{link['id']}",
                            "type": link_type_obj(site, link["type"]), "inwardIssue": linked_issue(site, other)})
    return sorted(out, key=lambda x: int(x["id"]))


def timetracking(issue: dict) -> dict:
    estimate = issue.get("estimateHours")
    spent = logged_seconds(issue)
    out: dict[str, Any] = {}
    if estimate is not None:
        original = int(estimate * 3600)
        remaining = max(original - spent, 0)
        out.update({"originalEstimate": format_duration(original), "remainingEstimate": format_duration(remaining)})
    if spent:
        out["timeSpent"] = format_duration(spent)
    if estimate is not None:
        out.update({"originalEstimateSeconds": original, "remainingEstimateSeconds": remaining})
    if spent:
        out["timeSpentSeconds"] = spent
    return out


def worklog_obj(site: Site, issue: dict, w: dict, fmt: str | None = None) -> dict:
    author = user_obj(site, site.users.get(w["author"]))
    out = {"self": f"{api(site)}/rest/api/3/issue/{issue['id']}/worklog/{w['id']}", "author": author,
           "updateAuthor": author}
    if w.get("comment"):
        out["comment"] = body(w["comment"], fmt)
    out.update({"created": w["created"], "updated": w.get("updated", w["created"]), "started": w["started"],
                "timeSpent": format_duration(w["timeSpentSeconds"]), "timeSpentSeconds": w["timeSpentSeconds"],
                "id": w["id"], "issueId": issue["id"]})
    return out


def field_value(site: Site, issue: dict, name: str, fmt: str | None) -> Any:
    if name == "summary":
        return issue["summary"]
    if name == "issuetype":
        return issuetype_obj(site, site.types[issue["type"]])
    if name == "components":
        return list(issue.get("components", []))
    if name == "created":
        return issue["created"]
    if name == "updated":
        return issue["updated"]
    if name == "description":
        return body(issue.get("description"), fmt)
    if name == "project":
        return project_obj(site)
    if name == "reporter":
        return user_obj(site, site.users.get(issue.get("reporter") or ""))
    if name == "assignee":
        return user_obj(site, site.users.get(issue.get("assignee") or ""))
    if name == "priority":
        return priority_obj(site, issue.get("priority"))
    if name == "resolution":
        return issue.get("resolution")
    if name == "labels":
        return list(issue.get("labels", []))
    if name == "status":
        return status_obj(site, issue["status"])
    if name == "comment":
        comments = [comment_obj(site, issue, c, fmt) for c in issue.get("comments", [])]
        return {"comments": comments, "self": f"{api(site)}/rest/api/3/issue/{issue['id']}/comment",
                "maxResults": len(comments), "total": len(comments), "startAt": 0}
    if name == "issuelinks":
        return issue_links(site, issue)
    if name == "timetracking":
        return timetracking(issue)
    if name == "timeoriginalestimate":
        est = issue.get("estimateHours")
        return int(est * 3600) if est is not None else None
    if name == "timeestimate":
        est = issue.get("estimateHours")
        return max(int(est * 3600) - logged_seconds(issue), 0) if est is not None else None
    if name == "customfield_10020":
        return sprint_obj(site, issue.get("sprint"))
    if name == "parent":
        parent = site.issue(issue.get("parent"))
        if parent is None:
            return None
        return {"id": parent["id"], "key": parent["key"], "self": f"{api(site)}/rest/api/3/issue/{parent['id']}",
                "fields": linked_issue(site, parent)["fields"]}
    if name == "worklog":
        logs = [worklog_obj(site, issue, w, fmt) for w in issue.get("worklogs", [])]
        return {"startAt": 0, "maxResults": 20, "total": len(logs), "worklogs": logs}
    raise KeyError(name)


def select_fields(requested: list[str] | None) -> tuple[str, ...]:
    if not requested:
        return DEFAULT_FIELDS
    wanted: set[str] = set()
    for raw in requested:
        name = str(raw).strip()
        low = name.lower()
        if low in ("*all", "*navigable"):
            wanted.update(ALL_FIELDS)
        elif low == "*none":
            continue
        elif name.startswith("-"):
            wanted.discard(FIELD_ALIASES.get(name[1:].lower(), name[1:]))
        else:
            wanted.add(FIELD_ALIASES.get(low, name))
    return tuple(f for f in ALL_FIELDS if f in wanted)


def issue_obj(site: Site, issue: dict, fields: list[str] | None = None, fmt: str | None = None,
              expand: str | None = None) -> dict:
    out: dict[str, Any] = {"expand": PRETTY_EXPAND, "id": issue["id"],
                           "self": f"{api(site)}/rest/api/3/issue/{issue['id']}", "key": issue["key"]}
    chosen = select_fields(fields)
    values: dict[str, Any] = {}
    for name in chosen:
        if name == "parent" and not issue.get("parent"):
            continue
        values[name] = field_value(site, issue, name, fmt)
    out["fields"] = values
    wanted = {e.strip().lower() for e in (expand or "").split(",") if e.strip()}
    if "transitions" in wanted:
        out["transitions"] = transitions_list(site)
    if "names" in wanted:
        out["names"] = {n: NAMES.get(n, n) for n in values}
    return out


NAMES = {"summary": "Summary", "issuetype": "Work type", "components": "Components", "created": "Created",
         "description": "Description", "project": "Space", "reporter": "Reporter", "priority": "Priority",
         "resolution": "Resolution", "labels": "Labels", "assignee": "Assignee", "updated": "Updated",
         "status": "Status", "comment": "Comment", "issuelinks": "Linked work items",
         "timetracking": "Time tracking", "timeestimate": "Remaining Estimate",
         "timeoriginalestimate": "Original estimate", "customfield_10020": "Sprint", "parent": "Parent",
         "worklog": "Log Work"}


def transitions_list(site: Site) -> list[dict]:
    out = []
    for t in site.data["transitions"]:
        status = site.statuses_by_id[t["to"]]
        out.append({"id": t["id"], "name": t["name"], "to": status_obj(site, status["name"]), "hasScreen": False,
                    "isGlobal": True, "isInitial": False, "isAvailable": True, "isConditional": False,
                    "isLooped": False})
    return out


def project_value(site: Site) -> dict:
    p = site.project
    types = [issuetype_obj(site, t, entity=False) for t in site.data["issueTypes"]]
    return {"expand": "description,lead,issueTypes,url,projectKeys,permissions,insight",
            "self": f"{api(site)}/rest/api/3/project/{p['id']}", "id": p["id"], "key": p["key"],
            "issueTypes": types, "name": p["name"], "avatarUrls": project_avatars(site),
            "projectTypeKey": p["projectTypeKey"], "simplified": p["simplified"], "style": p["style"],
            "isPrivate": False, "properties": {}, "entityId": p.get("entityId", ""), "uuid": p.get("uuid", "")}


# --- Teamwork Graph ------------------------------------------------------------------------------------------------

def graph_issue_raw(site: Site, issue: dict) -> dict:
    cid = site.data["site"]["cloudId"]
    t = site.types[issue["type"]]
    status = site.statuses[issue["status"]]
    category = CATEGORIES[status["category"]]
    icon = f"{site_url()}/rest/api/2/universal_avatar/view/type/issuetype/avatar/{t['avatarId']}"

    def person(key: str | None) -> dict | None:
        u = site.users.get(key or "")
        return {"id": user_ari(u), "name": u["displayName"]} if u else None

    return {
        "assignee": person(issue.get("assignee")),
        "createdAt": to_z(issue["created"]),
        "description": plain_text(issue.get("description")),
        "dueAt": None,
        "id": issue_ari(site, issue),
        "issueId": issue["id"],
        "issueType": {"avatar": {"large": icon, "medium": f"{icon}?size=medium", "small": f"{icon}?size=small",
                                 "xsmall": f"{icon}?size=xsmall"},
                      "description": t["description"], "id": f"ari:cloud:jira:{cid}:issue-type/{t['id']}",
                      "name": t["name"]},
        "key": issue["key"],
        "reporter": person(issue.get("reporter")),
        "resolvedAt": None,
        "startedAt": None,
        "jiraStatus": {
            "description": None,
            "id": f"ari:cloud:jira:{cid}:issue-status/activation/{site.data['site']['statusActivationId']}/"
                  f"{status['id']}",
            "name": status["name"],
            "statusCategory": {"colorName": category["graph"],
                               "id": base64.b64encode(f"JiraStatusCategory:{status['category']}".encode())
                               .decode().rstrip("="),
                               "key": category["key"], "name": category["name"],
                               "statusCategoryId": str(status["category"])},
            "statusId": status["id"],
        },
        "summary": issue["summary"],
        "webUrl": browse_url(issue["key"]),
    }


def to_z(stamp: str) -> str:
    """``2026-10-23T14:41:27.905+0000`` -> ``2026-10-23T14:41:27.905Z``."""
    return re.sub(r"\+0000$", "Z", stamp)
