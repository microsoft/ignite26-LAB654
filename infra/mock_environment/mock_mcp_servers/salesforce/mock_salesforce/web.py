"""Read-only Lightning Experience look-alike for the mock org.

Routes (served next to /mcp); every page also exists under ``/v/{token}`` for a conversation's own changes:
* ``/`` and ``/lightning``: redirect to ``/lightning/page/home``.
* ``/lightning/page/home``: Sales home (quarterly performance, key deals, today's events and tasks).
* ``/lightning/o/{Object}/list`` and ``/lightning/o/{Object}/home``: list views.
* ``/lightning/r/{Object}/{id}/view``: record pages (``?tab=activity`` for the activity timeline).
* ``/lightning/o/Dashboard/home`` and ``/lightning/r/Dashboard/{id}/view``: the pipeline dashboard.
* ``/lightning/search?q=``: global search results.
* ``/img/icon/t4v35/standard/{name}.svg``: object icons (the ``iconUrl`` the search API returns).
Unknown or expired tokens fall back to the seed org with a notice.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timezone

from .ids import seed_id
from .lightning_css import CSS
from .lightning_ui import (COLORS, column_chart, compact, donut, e, gauge, icon, icon_file, label, legend, line_chart,
                           money, plain, record_name)
from .schema import OBJECTS, STAGES, field as schema_field
from .store import Org, StateStore
from .timeutil import display_date, display_datetime, et_date, parse_date, parse_dt

_TOKEN = re.compile(r"[0-9a-f]{20}")
_HEADERS = {"Cache-Control": "no-store", "X-Robots-Tag": "noindex, nofollow"}
DASHBOARD_ID = seed_id("01Z", 1)
DASHBOARD_NAME = "Aurora Sales Pipeline"
LIST_OBJECTS = ("Opportunity", "Account", "Contact", "Lead", "Task", "Event", "User")
_TABS = [("Home", "home", None), ("Opportunities", "Opportunity", "Opportunity"), ("Leads", "Lead", "Lead"),
         ("Tasks", "Task", "Task"), ("Accounts", "Account", "Account"), ("Contacts", "Contact", "Contact"),
         ("Calendar", "Event", "Event"), ("Dashboards", "Dashboard", None)]
_COLUMNS = {
    "Opportunity": ["Name", "AccountId", "Amount", "CloseDate", "StageName", "OwnerId"],
    "Account": ["Name", "Type", "Industry", "BillingCity", "Phone", "OwnerId"],
    "Contact": ["Name", "AccountId", "Title", "Phone", "Email", "OwnerId"],
    "Lead": ["Name", "Title", "Company", "Phone", "Email", "Status", "OwnerId"],
    "Task": ["Subject", "WhoId", "WhatId", "ActivityDate", "Status", "Priority", "OwnerId"],
    "Event": ["Subject", "WhoId", "WhatId", "StartDateTime", "EndDateTime", "Location", "OwnerId"],
    "User": ["Name", "Title", "Email", "Department"],
}
_HIGHLIGHTS = {
    "Opportunity": ["AccountId", "CloseDate", "Amount", "OwnerId"],
    "Account": ["Type", "Phone", "Website", "OwnerId", "Industry"],
    "Contact": ["Title", "AccountId", "Phone", "Email", "OwnerId"],
    "Lead": ["Title", "Company", "Phone", "Email", "Status"],
    "Task": ["ActivityDate", "Status", "Priority", "OwnerId"],
    "Event": ["StartDateTime", "EndDateTime", "Location", "OwnerId"],
    "User": ["Title", "Department", "Email", "Phone"],
}
_SECTIONS = {
    "Opportunity": [("Opportunity Information", ["OwnerId", "Amount", "Name", "CloseDate", "AccountId", "NextStep",
                                                 "Type", "StageName", "LeadSource", "Probability", "ContactId",
                                                 "ExpectedRevenue", "Competitor__c", "ForecastCategoryName",
                                                 "Loss_Reason__c"]),
                    ("Description Information", ["Description"]),
                    ("System Information", ["CreatedById", "LastModifiedById"])],
    "Account": [("Account Information", ["OwnerId", "Phone", "Name", "Website", "ParentId", "Type", "Industry",
                                         "NumberOfEmployees", "AnnualRevenue", "AccountSource"]),
                ("Address Information", ["BillingStreet", "BillingCity", "BillingState", "BillingPostalCode",
                                         "BillingCountry"]),
                ("Description Information", ["Description"]),
                ("System Information", ["CreatedById", "LastModifiedById"])],
    "Contact": [("Contact Information", ["OwnerId", "Phone", "Name", "MobilePhone", "AccountId", "Email", "Title",
                                         "ReportsToId", "Department", "LeadSource"]),
                ("Address Information", ["MailingCity", "MailingState", "MailingCountry"]),
                ("Description Information", ["Description"]),
                ("System Information", ["CreatedById", "LastModifiedById"])],
    "Lead": [("Lead Information", ["OwnerId", "Phone", "Name", "Email", "Company", "Status", "Title", "LeadSource",
                                   "Industry", "IsConverted"]),
             ("System Information", ["CreatedById", "LastModifiedById"])],
    "Task": [("Task Information", ["Subject", "OwnerId", "ActivityDate", "Status", "WhoId", "Priority", "WhatId",
                                   "Type", "Description"]),
             ("System Information", ["CreatedById", "LastModifiedById"])],
    "Event": [("Calendar Details", ["OwnerId", "Subject", "StartDateTime", "Location", "EndDateTime", "IsAllDayEvent",
                                    "WhoId", "ShowAs", "WhatId", "Type", "Description"]),
              ("System Information", ["CreatedById", "LastModifiedById"])],
    "User": [("About", ["Name", "Title", "Department", "CompanyName", "Email", "Phone", "ManagerId", "Username",
                        "IsActive", "TimeZoneSidKey"])],
}
_WIDE = {"Description", "BillingStreet"}


class Site:
    """Org, link prefix and clock for one request."""

    def __init__(self, org: Org, prefix: str, now: datetime) -> None:
        self.org, self.prefix, self.now = org, prefix, now

    @property
    def today(self) -> date:
        return et_date(self.now.isoformat()) or self.now.date()

    def home(self) -> str:
        return f"{self.prefix}/lightning/page/home"

    def lst(self, obj: str) -> str:
        if obj == "Dashboard":
            return f"{self.prefix}/lightning/o/Dashboard/home"
        return f"{self.prefix}/lightning/o/{obj}/list"

    def rec(self, obj: str, rid: str, tab: str | None = None) -> str:
        return f"{self.prefix}/lightning/r/{obj}/{rid}/view" + (f"?tab={tab}" if tab else "")

    def ref(self, rid: str | None) -> str:
        """Link to a referenced record by name, or empty."""
        hit = self.org.get(rid)
        if not hit:
            return e(rid or "")
        obj, rec = hit
        return f'<a href="{self.rec(obj, rec["Id"])}">{e(record_name(obj, rec))}</a>'

    def ref_name(self, rid: str | None) -> str:
        hit = self.org.get(rid)
        return record_name(*hit) if hit else ""

    def value(self, obj: str, api: str, rec: dict) -> str:
        raw = rec.get(api)
        meta = schema_field(obj, api)
        kind = meta[2] if meta else ""
        if kind == "BOOLEAN":
            return f'<span class="chk">{"&#10003;" if raw else ""}</span>'
        if raw is None or raw == "":
            return ""
        if kind == "REFERENCE":
            link = self.ref(raw)
            if api in ("CreatedById", "LastModifiedById"):
                stamp = rec.get("CreatedDate" if api == "CreatedById" else "LastModifiedDate")
                return f'{link}, {e(display_datetime(stamp))}' if stamp else link
            return link
        if kind == "URL":
            href = raw if str(raw).startswith("http") else f"https://{raw}"
            return f'<a href="{e(href)}" target="_blank" rel="noopener">{e(raw)}</a>'
        if kind == "EMAIL":
            return f'<a href="mailto:{e(raw)}">{e(raw)}</a>'
        if kind == "PHONE":
            return f'<a href="tel:{e(raw)}">{e(raw)}</a>'
        if kind == "TEXTAREA":
            return e(raw).replace("\n", "<br>")
        if api == "Name" or (obj in ("Task", "Event") and api == "Subject"):
            return e(raw)
        return e(plain(obj, api, rec))


def _avatar(org: Org) -> str:
    user = org.user(org.current_user_id) or {}
    letters = (user.get("FirstName", "")[:1] + user.get("LastName", "")[:1]).upper() or "U"
    return f'<span class="avatar" title="{e(user.get("Name", ""))}">{e(letters)}</span>'


_CLOUD = ('<svg width="52" height="36" viewBox="0 0 52 36" aria-label="Home"><g fill="#0b5cab"><circle cx="14" cy="21" '
          'r="10"/><circle cx="24" cy="13" r="11"/><circle cx="36" cy="15" r="9.5"/><circle cx="42" cy="23" r="8"/>'
          '<rect x="14" y="20" width="28" height="11"/></g></svg>')
_SEARCH_ICON = ('<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true"><path fill="#747474" d="M10 3a7 7 '
                '0 0 1 5.6 11.2l5.6 5.6-1.4 1.4-5.6-5.6A7 7 0 1 1 10 3zm0 2a5 5 0 1 0 0 10 5 5 0 0 0 0-10z"/></svg>')
_UTIL = [("Favorites", "M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"),
         ("Global Actions", "M11 4h2v7h7v2h-7v7h-2v-7H4v-2h7z"),
         ("Help", "M12 3a9 9 0 1 1 0 18 9 9 0 0 1 0-18zm0 12.6a1.2 1.2 0 1 0 0 2.4 1.2 1.2 0 0 0 0-2.4zM12 6.5c-2 0-3.5 "
                  "1.3-3.6 3.2h2c.1-.8.7-1.3 1.6-1.3s1.6.6 1.6 1.3c0 1.6-2.6 1.5-2.6 4.3h2c0-2 2.6-2.2 2.6-4.4 0-1.8-1.5-"
                  "3.1-3.6-3.1z"),
         ("Setup", "M13.6 3l.4 2.3 1.5.7 2-1.3 2.2 2.2-1.3 2 .7 1.5 2.3.4v3.2l-2.3.4-.7 1.5 1.3 2-2.2 2.2-2-1.3-1.5.7-"
                   ".4 2.3h-3.2l-.4-2.3-1.5-.7-2 1.3-2.2-2.2 1.3-2-.7-1.5L3 13.6v-3.2l2.3-.4.7-1.5-1.3-2 2.2-2.2 2 1.3 "
                   "1.5-.7.4-2.3zM12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6z"),
         ("Notifications", "M12 3a6 6 0 0 1 6 6v4.5l2 2.5v1H4v-1l2-2.5V9a6 6 0 0 1 6-6zm-2 15h4a2 2 0 1 1-4 0z")]


def shell(site: Site, *, title: str, active: str, body: str, notice: str | None, q: str = "") -> str:
    tabs = []
    for text, key, chev in _TABS:
        href = site.home() if key == "home" else site.lst(key)
        caret = '<span class="chev">&#9660;</span>' if chev else ""
        tabs.append(f'<a class="tab{" on" if key == active else ""}" href="{href}">{e(text)}{caret}</a>')
    utils = "".join(f'<span class="gh-ico" title="{e(t)}"><svg width="18" height="18" viewBox="0 0 24 24">'
                    f'<path fill="#747474" d="{p}"/></svg></span>' for t, p in _UTIL)
    banner = f'<div class="notice">&#9888; {e(notice)}</div>' if notice else ""
    org_name = next((o.get("Name") for o in site.org.records("Organization")), "Salesforce")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">
<title>{e(title)} | Salesforce</title><style>{CSS}</style></head><body>
<header class="gh"><div class="gh-top"><a class="logo" href="{site.home()}" title="{e(org_name)}">{_CLOUD}</a>
<form class="search" action="{site.prefix}/lightning/search" method="get">{_SEARCH_ICON}
<input name="q" value="{e(q)}" placeholder="Search..." aria-label="Search"></form>
<div class="gh-icons">{utils}{_avatar(site.org)}</div></div>
<nav class="ctx"><span class="waffle" title="App Launcher"><i>{"<b></b>" * 9}</i></span>
<span class="appname">Sales</span>{"".join(tabs)}</nav></header>{banner}
<main>{body}</main><footer>Mock environment for Microsoft Ignite lab LAB654. Not affiliated with Salesforce. Data is
fictitious and read-only.</footer></body></html>"""


# --- List views ---------------------------------------------------------------------------------------------------
def _col_label(obj: str, api: str) -> str:
    if api == "Name" and obj not in ("Opportunity", "Account"):
        return "Name"
    if api == "OwnerId" and obj not in ("Task", "Event"):
        return "Owner"
    return label(obj, api)


def _sort_key(obj: str, rec: dict):
    return record_name(obj, rec).lower()


def list_page(site: Site, obj: str, notice: str | None) -> str:
    meta = OBJECTS[obj]
    rows = sorted(site.org.records(obj), key=lambda r: _sort_key(obj, r))
    cols = _COLUMNS[obj]
    name_api = meta["name"][0]
    head = "".join(
        f'<th class="{"num" if (schema_field(obj, c) or (0, 0, ""))[2] == "CURRENCY" else ""}">{e(_col_label(obj, c))}'
        f'{"<span class=ar>&#9650;</span>" if c == name_api else ""}</th>' for c in cols)
    body = []
    for n, rec in enumerate(rows, 1):
        cells = []
        for c in cols:
            if c == name_api:
                cells.append(f'<td><a href="{site.rec(obj, rec["Id"])}">{e(record_name(obj, rec))}</a></td>')
                continue
            kind = (schema_field(obj, c) or (0, 0, ""))[2]
            cells.append(f'<td class="{"num" if kind == "CURRENCY" else ""}">{site.value(obj, c, rec)}</td>')
        body.append(f'<tr><td class="rn">{n}</td><td class="ck"><span class="cb"></span></td>{"".join(cells)}'
                    f'<td class="ck"><span class="rowact">&#9660;</span></td></tr>')
    if not rows:
        body.append(f'<tr><td colspan="{len(cols) + 3}" class="empty" style="text-align:center;padding:40px">'
                    f'No items to display.</td></tr>')
    plural = meta["plural"]
    view = "All Open Leads" if obj == "Lead" else ("My Tasks" if obj == "Task" else
                                                  ("Active Users" if obj == "User" else f"All {plural}"))
    count = f'{len(rows)} item{"" if len(rows) == 1 else "s"}'
    html = f"""<div class="card lv"><div class="ph"><div class="ph-row">{icon(obj, 32)}
<div class="ph-t"><small>{e(plural)}</small><h1>{e(view)}<span class="dd">&#9660;</span></h1></div>
<div class="btngrp"><span class="btn">New</span><span class="btn">Import</span><span class="btn">Printable View</span>
</div></div><div class="ph-meta">{count} &bull; Sorted by {e(_col_label(obj, name_api))} &bull; Filtered by All
{e(plural.lower())} &bull; Updated a few seconds ago</div></div>
<div style="overflow-x:auto"><table class="dt"><thead><tr><th></th><th class="ck"><span class="cb"></span></th>{head}
<th class="ck"></th></tr></thead><tbody>{"".join(body)}</tbody></table></div></div>"""
    active = obj if any(k == obj for _, k, _ in _TABS) else ""
    return shell(site, title=plural, active=active, body=html, notice=notice)


# --- Record pages -------------------------------------------------------------------------------------------------
def _path(site: Site, opp: dict) -> str:
    stage = opp.get("StageName") or ""
    open_stages = [s for s, _, _ in STAGES if not s.startswith("Closed")]
    history = [h for h in site.org.records("OpportunityHistory") if h.get("OpportunityId") == opp["Id"]]
    reached = {h.get("StageName") for h in history} | {stage}
    steps = []
    if stage == "Closed Won":
        steps = [(s, "done") for s in open_stages] + [("Closed Won", "won")]
    elif stage == "Closed Lost":
        last = max((open_stages.index(s) for s in reached if s in open_stages), default=-1)
        steps = [(s, "done" if i <= last else "") for i, s in enumerate(open_stages)] + [("Closed Lost", "lost")]
    else:
        cur = open_stages.index(stage) if stage in open_stages else -1
        steps = [(s, "done" if i < cur else ("cur" if i == cur else "")) for i, s in enumerate(open_stages)]
        steps.append(("Closed", ""))
    items = "".join(f'<li class="{c}" title="{e(s)}"><span>{"&#10003; " if c == "done" else ""}{e(s)}</span></li>'
                    for s, c in steps)
    action = "Change Closed Stage" if stage.startswith("Closed") else "&#10003; Mark Stage as Complete"
    return (f'<div class="card"><div class="path"><span class="btn icn" title="Show more">&#8964;</span><ol>{items}'
            f'</ol><span class="btn brand">{action}</span></div></div>')


def _highlights(site: Site, obj: str, rec: dict) -> str:
    buttons = {"Opportunity": ["+ Follow", "New Event", "New Task", "Edit", "Delete"],
               "Account": ["+ Follow", "New Contact", "New Opportunity", "Edit"],
               "Contact": ["+ Follow", "New Event", "New Task", "Edit"],
               "Task": ["Edit Comments", "Change Date", "Create Follow-Up Task", "Edit"],
               "Event": ["Edit", "Delete", "Clone"], "Lead": ["+ Follow", "Convert", "Edit"],
               "User": ["Edit"]}[obj]
    btns = "".join(f'<span class="btn">{e(b)}</span>' for b in buttons) + '<span class="btn icn">&#9660;</span>'
    fields = "".join(f'<div><dt>{e(label(obj, api))}</dt><dd>{site.value(obj, api, rec) or "&nbsp;"}</dd></div>'
                     for api in _HIGHLIGHTS[obj])
    sub = OBJECTS[obj]["label"]
    return (f'<div class="card"><div class="ph"><div class="ph-row">{icon(obj, 32)}<div class="ph-t"><small>{e(sub)}'
            f'</small><h1>{e(record_name(obj, rec))}</h1></div><div class="btngrp">{btns}</div></div>'
            f'<dl class="hl">{fields}</dl></div></div>')


def _details(site: Site, obj: str, rec: dict) -> str:
    out = []
    for title, apis in _SECTIONS[obj]:
        cells = []
        for api in apis:
            if schema_field(obj, api) is None:
                continue
            wide = " wide" if api in _WIDE else ""
            cells.append(f'<div class="fld{wide}"><label>{e(label(obj, api))}</label>'
                         f'<div class="v">{site.value(obj, api, rec)}</div></div>')
        out.append(f'<div class="sec"><div class="sec-h">{e(title)}</div><div class="form">{"".join(cells)}</div></div>')
    return "".join(out) + '<div style="height:12px"></div>'


def _activities(site: Site, obj: str, rec: dict) -> list[tuple[str, dict]]:
    rid = rec["Id"]
    keys = {"Account": ("AccountId", "WhatId"), "Contact": ("WhoId",), "Lead": ("WhoId",),
            "Opportunity": ("WhatId",), "User": ("OwnerId",)}.get(obj, ())
    found = []
    for kind in ("Task", "Event"):
        for act in site.org.records(kind):
            if any(act.get(k) == rid for k in keys):
                found.append((kind, act))
    return found


def _act_when(kind: str, act: dict) -> datetime | None:
    if kind == "Event":
        return parse_dt(act.get("StartDateTime"))
    day = parse_date(act.get("ActivityDate"))
    return datetime(day.year, day.month, day.day, 12, tzinfo=timezone.utc) if day else None


def _timeline_item(site: Site, kind: str, act: dict, upcoming: bool) -> str:
    who = site.ref(act.get("WhoId")) if act.get("WhoId") else ""
    what = site.ref(act.get("WhatId")) if act.get("WhatId") else ""
    is_call = kind == "Task" and (act.get("Type") == "Call" or act.get("TaskSubtype") == "Call")
    glyph = "Call" if is_call else kind
    if is_call:
        line = "You logged a call"
    elif kind == "Event":
        line = "You have an upcoming event" if upcoming else "You had an event"
    else:
        line = "You have an upcoming task" if upcoming else "You had a task"
    if who:
        line += f" with {who}"
    if what:
        line += f" about {what}"
    if kind == "Event":
        when = display_datetime(act.get("StartDateTime") or "")
    else:
        day = parse_date(act.get("ActivityDate"))
        when = display_date(day) if day else "No due date"
    status = ""
    if kind == "Task":
        status = f'<span class="chk">{"&#10003;" if act.get("IsClosed") else ""}</span> '
    desc = f'<div class="desc">{e(act.get("Description"))}</div>' if act.get("Description") else ""
    return (f'<li>{icon(glyph, 24, round_=False)}<div class="tx"><div class="ttl"><span>{status}'
            f'<a href="{site.rec(kind, act["Id"])}">{e(record_name(kind, act))}</a></span><span class="dt2">{e(when)}'
            f'</span></div><div class="sub">{line}</div>{desc}</div></li>')


def _timeline(site: Site, obj: str, rec: dict) -> str:
    acts = _activities(site, obj, rec)
    upcoming, past = [], []
    for kind, act in acts:
        when = _act_when(kind, act)
        is_open = (kind == "Task" and not act.get("IsClosed")) or (kind == "Event" and when and when >= site.now)
        (upcoming if is_open else past).append((when, kind, act))
    upcoming.sort(key=lambda t: t[0] or site.now)
    past.sort(key=lambda t: t[0] or site.now, reverse=True)
    parts = ['<div class="composer">' + "".join(f'<span class="btn">{b}</span>' for b in
                                                ("Log a Call", "New Task", "New Event", "Email")) + "</div>",
             '<div class="filters"><span>Filters: All time &bull; All activities &bull; All types</span>'
             '<span><a>Refresh</a> &bull; <a>Expand All</a> &bull; <a>View All</a></span></div>',
             '<div style="padding:0 16px 14px">', '<div class="tl-g">Upcoming &amp; Overdue</div>']
    if upcoming:
        parts.append('<ul class="tl">' + "".join(_timeline_item(site, k, a, True) for _, k, a in upcoming) + "</ul>")
    else:
        parts.append('<div class="empty">No activities to show.<br>Get started by sending an email, scheduling a '
                     'task, and more.</div>')
    groups: dict[str, list] = {}
    for when, kind, act in past:
        key = when.strftime("%B &bull; %Y") if when else "No date"
        groups.setdefault(key, []).append((kind, act))
    for key, items in groups.items():
        parts.append(f'<div class="tl-g">{key}</div><ul class="tl">' +
                     "".join(_timeline_item(site, k, a, False) for k, a in items) + "</ul>")
    if not past:
        parts.append('<div class="empty" style="margin-top:12px">No past activity. Past meetings and tasks marked '
                     'as done show up here.</div>')
    parts.append("</div>")
    return "".join(parts)


def _tile(site: Site, obj: str, rec: dict, apis: list[str], extra: str = "") -> str:
    rows = "".join(f'<dt>{e(label(obj, a))}:</dt><dd>{site.value(obj, a, rec) or "&nbsp;"}</dd>' for a in apis)
    return (f'<div class="tile"><div style="min-width:0;flex:1"><a class="nm" href="{site.rec(obj, rec["Id"])}">'
            f'{e(record_name(obj, rec))}</a>{extra}<dl>{rows}</dl></div><span class="rowact">&#9660;</span></div>')


def _related_card(kind: str, title: str, tiles: list[str], view_all: str | None = None, new: bool = True,
                  empty: str = "") -> str:
    body = "".join(tiles) if tiles else ""
    btn = '<span class="btn" style="height:28px;padding:0 12px">New</span>' if new else ""
    foot = f'<div class="card-f"><a href="{view_all}">View All</a></div>' if tiles and view_all else ""
    inner = f'<div class="card-b">{body or empty}</div>' if tiles or empty else ""
    return (f'<div class="card rl"><div class="card-h">{icon(kind, 24)}<h2><a>{e(title)} ({len(tiles)})</a></h2>'
            f'{btn}</div>{inner}{foot}</div>')


def _related(site: Site, obj: str, rec: dict) -> str:
    rid, org, cards = rec["Id"], site.org, []
    if obj == "Account":
        contacts = [c for c in org.records("Contact") if c.get("AccountId") == rid]
        cards.append(_related_card("Contact", "Contacts", [_tile(site, "Contact", c, ["Title", "Email", "Phone"])
                                                            for c in contacts], site.lst("Contact")))
        opps = sorted((o for o in org.records("Opportunity") if o.get("AccountId") == rid),
                      key=lambda o: o.get("CloseDate") or "", reverse=True)
        cards.append(_related_card("Opportunity", "Opportunities",
                                   [_tile(site, "Opportunity", o, ["StageName", "Amount", "CloseDate"]) for o in opps],
                                   site.lst("Opportunity")))
    elif obj == "Contact":
        opps = [o for o in org.records("Opportunity") if o.get("ContactId") == rid]
        cards.append(_related_card("Opportunity", "Opportunities",
                                   [_tile(site, "Opportunity", o, ["StageName", "Amount", "CloseDate"]) for o in opps],
                                   site.lst("Opportunity")))
    elif obj == "Opportunity":
        hit = org.get(rec.get("ContactId"))
        roles = []
        if hit and hit[0] == "Contact":
            roles.append(_tile(site, "Contact", hit[1], ["Title", "Email"],
                               ' <span style="font-size:11px;color:#444;margin-left:6px">Primary</span>'))
        cards.append(_related_card("Contact", "Contact Roles", roles, None))
        history = sorted((h for h in org.records("OpportunityHistory") if h.get("OpportunityId") == rid),
                         key=lambda h: h.get("CreatedDate") or "", reverse=True)
        tiles = []
        for h in history:
            rows = "".join(f'<dt>{e(t)}:</dt><dd>{v or "&nbsp;"}</dd>' for t, v in (
                ("Amount", e(plain("OpportunityHistory", "Amount", h))),
                ("Probability (%)", e(plain("OpportunityHistory", "Probability", h))),
                ("Close Date", e(plain("OpportunityHistory", "CloseDate", h))),
                ("Last Modified", e(plain("OpportunityHistory", "CreatedDate", h)))))
            tiles.append(f'<div class="tile"><div style="min-width:0;flex:1"><span class="nm">{e(h.get("StageName"))}'
                         f'</span><dl>{rows}</dl></div></div>')
        cards.append(_related_card("OpportunityHistory", "Stage History", tiles, None, new=False))
    elif obj == "User":
        reports = [u for u in org.records("User") if u.get("ManagerId") == rid]
        cards.append(_related_card("User", "Direct Reports", [_tile(site, "User", u, ["Title", "Email"])
                                                               for u in reports], site.lst("User"), new=False))
    if obj in ("Account", "Contact", "Opportunity", "Lead"):
        cards.append(_related_card("Dashboard", "Files", [], None, new=False, empty=(
            '<div class="empty" style="text-align:center;border:1px dashed #c9c9c9;border-radius:4px;padding:14px">'
            '&#8679; Upload Files<br><small>Or drop files</small></div>')))
    return '<div class="stack">' + "".join(cards) + "</div>"


def record_page(site: Site, obj: str, rec: dict, tab: str | None, notice: str | None) -> str:
    has_timeline = obj in ("Opportunity", "Account", "Contact", "Lead")
    tab = tab if tab in ("details", "activity") and has_timeline else "details"
    path = _path(site, rec) if obj == "Opportunity" else ""
    tabs = ""
    if has_timeline:
        tabs = '<div class="tabs">' + "".join(
            f'<a class="{"on" if t == tab else ""}" href="{site.rec(obj, rec["Id"], t)}">{n}</a>'
            for t, n in (("activity", "Activity"), ("details", "Details"))) + "</div>"
    main = _timeline(site, obj, rec) if tab == "activity" else _details(site, obj, rec)
    side = _related(site, obj, rec)
    layout = "cols" if side != '<div class="stack"></div>' else "cols full"
    body = (f'{_highlights(site, obj, rec)}{path and "<div style=margin-top:12px>" + path + "</div>"}'
            f'<div class="{layout}"><div class="card">{tabs}{main}</div>'
            f'{side if layout == "cols" else ""}</div>')
    active = obj if any(k == obj for _, k, _ in _TABS) else ""
    return shell(site, title=record_name(obj, rec), active=active, body=body, notice=notice)


# --- Home ---------------------------------------------------------------------------------------------------------
def _quarter(day: date) -> tuple[date, date, int]:
    q = (day.month - 1) // 3
    start = date(day.year, q * 3 + 1, 1)
    end = date(day.year + 1, 1, 1) if q == 3 else date(day.year, q * 3 + 4, 1)
    return start, end, q + 1


def _mine(site: Site, obj: str) -> list[dict]:
    uid = site.org.current_user_id
    return [r for r in site.org.records(obj) if r.get("OwnerId") == uid]


def home_page(site: Site, notice: str | None) -> str:
    today = site.today
    start, end, qn = _quarter(today)
    span = (end - start).days
    in_q = [(o, parse_date(o.get("CloseDate"))) for o in _mine(site, "Opportunity")]
    in_q = [(o, d) for o, d in in_q if d and start <= d < end]
    won = sorted(((d, o.get("Amount") or 0) for o, d in in_q if o.get("IsWon")), key=lambda t: t[0])
    hot = sorted(((d, o.get("Amount") or 0) for o, d in in_q
                  if not o.get("IsClosed") and (o.get("Probability") or 0) > 70), key=lambda t: t[0])
    closed_total, open_total = sum(a for _, a in won), sum(a for _, a in hot)

    def series(events: list[tuple[date, float]], stop: date) -> list[tuple[float, float]]:
        points, total = [(0.0, 0.0)], 0.0
        for d, amount in events:
            x = (d - start).days / span
            points.append((x, total))
            total += amount
            points.append((x, total))
        points.append(((stop - start).days / span, total))
        return points

    today_x = (today - start).days / span
    months = [date(start.year, start.month + i, 1).strftime("%b") for i in range(3)]
    chart = line_chart(months, [
        ("Closed", "#2e844a", series(won, today), False),
        ("Closed + Open (>70%)", "#0176d3", series(sorted(won + hot), end), True)],
        max(closed_total + open_total, 1), today=today_x)
    perf = f"""<div class="card"><div class="card-h">{icon("Home", 24)}<h2>Quarterly Performance</h2>
<span style="font-size:12px;color:#444">As of Today {e(display_datetime(site.now.isoformat()).split(", ")[1])}</span>
<span class="btn icn">&#8635;</span></div><div class="qp-sum"><div>CLOSED<b>{e(compact(closed_total))}</b></div>
<div>OPEN (&gt;70%)<b>{e(compact(open_total))}</b></div><div>GOAL<b>--</b></div>
<div style="margin-left:auto;align-self:flex-end">Q{qn} {start.strftime("%b")}&ndash;{months[-1]} {start.year}</div></div>
<div class="card-b">{chart}<div class="legend"><span><i style="background:#2e844a"></i>Closed</span>
<span><i style="background:#fe9339"></i>Goal</span><span><i style="background:#0176d3"></i>Closed + Open (&gt;70%)</span>
</div></div></div>"""

    deals = sorted(_mine(site, "Opportunity"), key=lambda o: o.get("LastModifiedDate") or "", reverse=True)[:5]
    deal_rows = "".join(
        f'<div class="deal">{icon("Opportunity", 24)}<div><a href="{site.rec("Opportunity", o["Id"])}">{e(o["Name"])}'
        f'</a><div class="m">{e(site.ref_name(o.get("AccountId")))} &bull; {e(plain("Opportunity", "CloseDate", o))}'
        f' &bull; {e(o.get("StageName"))}</div></div><div class="amt">{e(money(o.get("Amount")))}</div></div>'
        for o in deals)
    key_deals = (f'<div class="card"><div class="card-h">{icon("Opportunity", 24)}<h2>Key Deals - Recent '
                 f'Opportunities</h2></div><div class="card-b">{deal_rows or "<div class=empty>No deals yet.</div>"}'
                 f'</div><div class="card-f"><a href="{site.lst("Opportunity")}">View All Key Deals</a></div></div>')

    events_today = sorted((ev for ev in _mine(site, "Event") if et_date(ev.get("StartDateTime")) == today),
                          key=lambda ev: ev.get("StartDateTime") or "")
    tasks_today = [t for t in _mine(site, "Task") if not t.get("IsClosed") and parse_date(t.get("ActivityDate"))
                   and parse_date(t.get("ActivityDate")) <= today]
    ev_html = "".join(f'<div class="tile">{icon("Event", 24)}<div><a href="{site.rec("Event", ev["Id"])}">'
                      f'{e(ev.get("Subject"))}</a><div class="m" style="font-size:12px;color:#444">'
                      f'{e(display_datetime(ev.get("StartDateTime")))}</div></div></div>' for ev in events_today)
    tk_html = "".join(f'<div class="tile">{icon("Task", 24)}<div><a href="{site.rec("Task", t["Id"])}">'
                      f'{e(t.get("Subject"))}</a><div style="font-size:12px;color:#444">'
                      f'{e(plain("Task", "ActivityDate", t))}</div></div></div>' for t in tasks_today)
    free_ev = ('<div class="free">' + icon("Event", 40, True) + "<span>Looks like you\u2019re free and clear the rest "
               "of the day.</span></div>")
    free_tk = ('<div class="free">' + icon("Task", 40, True) + "<span>Nothing due today. Be a go-getter, and check back "
               "soon.</span></div>")
    today_cards = (f'<div class="card"><div class="card-h">{icon("Event", 24)}<h2>Today\u2019s Events</h2></div>'
                   f'<div class="card-b">{ev_html or free_ev}</div><div class="card-f"><a href="{site.lst("Event")}">'
                   f'View Calendar</a></div></div>'
                   f'<div class="card"><div class="card-h">{icon("Task", 24)}<h2>Today\u2019s Tasks</h2>'
                   f'<span class="btn icn">&#9660;</span></div><div class="card-b">{tk_html or free_tk}</div>'
                   f'<div class="card-f"><a href="{site.lst("Task")}">View All</a></div></div>')

    insights = []
    for ev in sorted(_mine(site, "Event"), key=lambda x: x.get("StartDateTime") or ""):
        when = parse_dt(ev.get("StartDateTime"))
        if when and site.now <= when and (when - site.now).days < 7:
            insights.append((icon("Event", 24), f'Upcoming meeting: <a href="{site.rec("Event", ev["Id"])}">'
                             f'{e(ev.get("Subject"))}</a>', display_datetime(ev.get("StartDateTime"))))
    for opp in _mine(site, "Opportunity"):
        if opp.get("IsClosed"):
            continue
        close = parse_date(opp.get("CloseDate"))
        link = f'<a href="{site.rec("Opportunity", opp["Id"])}">{e(opp["Name"])}</a>'
        if close and 0 <= (close - today).days <= 60:
            insights.append((icon("Opportunity", 24), f"Closing in {(close - today).days} days: {link}",
                             f'{opp.get("StageName")} \u2022 {money(opp.get("Amount"), False)}'))
        done = [_act_when(k, a) for k, a in _activities(site, "Opportunity", opp)
                if (k == "Task" and a.get("IsClosed")) or (k == "Event" and _act_when(k, a)
                                                          and _act_when(k, a) < site.now)]
        last = max((d for d in done if d), default=None)
        if last is None or (site.now - last).days > 30:
            insights.append((icon("Task", 24), f"No activity in 30 days: {link}",
                             "Log a call or schedule a meeting to keep the deal moving."))
    assist_html = "".join(f'<div class="assist">{ic}<div><div>{text}</div><div style="font-size:12px;color:#444">'
                          f'{e(sub)}</div></div></div>' for ic, text, sub in insights) or \
        '<div class="empty">Nothing needs your attention right now.</div>'
    assistant = (f'<div class="card"><div class="card-h">{icon("Lead", 24)}<h2>Assistant</h2></div>'
                 f'<div class="card-b">{assist_html}</div></div>')

    recent = []
    for obj in ("Opportunity", "Account", "Contact", "Event", "Task"):
        recent += [(r.get("LastModifiedDate") or "", obj, r) for r in site.org.records(obj)]
    recent.sort(key=lambda t: t[0], reverse=True)
    rec_html = "".join(f'<div class="tile">{icon(obj, 24)}<div style="min-width:0"><a href="{site.rec(obj, r["Id"])}">'
                       f'{e(record_name(obj, r))}</a><div style="font-size:12px;color:#444">{e(OBJECTS[obj]["label"])}'
                       f'</div></div></div>' for _, obj, r in recent[:6])
    recent_card = (f'<div class="card"><div class="card-h">{icon("Account", 24)}<h2>Recent Records</h2></div>'
                   f'<div class="card-b">{rec_html}</div></div>')
    body = (f'<div class="home"><div class="stack">{perf}{key_deals}{recent_card}</div>'
            f'<div class="stack">{assistant}{today_cards}</div></div>')
    return shell(site, title="Home", active="home", body=body, notice=notice)


# --- Dashboard ----------------------------------------------------------------------------------------------------
def _comp(title: str, body: str, foot: str = "View Report (Opportunities)", span: str = "") -> str:
    return (f'<div class="card comp {span}"><div class="card-h"><h2>{e(title)}</h2><span class="btn icn">&#10530;</span>'
            f'</div><div class="card-b">{body}</div><div class="card-f"><a>{e(foot)}</a></div></div>')


def dashboard_page(site: Site, notice: str | None) -> str:
    opps = site.org.records("Opportunity")
    open_opps = [o for o in opps if not o.get("IsClosed")]
    won = [o for o in opps if o.get("IsWon")]
    lost = [o for o in opps if o.get("IsClosed") and not o.get("IsWon")]
    pipeline = sum(o.get("Amount") or 0 for o in open_opps)
    won_total = sum(o.get("Amount") or 0 for o in won)
    rate = 100 * len(won) / (len(won) + len(lost)) if won or lost else 0.0
    stages = [s for s, _, _ in STAGES if any(o.get("StageName") == s for o in opps)]
    by_stage = column_chart(stages, [("Amount", [sum(o.get("Amount") or 0 for o in opps if o.get("StageName") == s)
                                                 for s in stages])], x_title="Stage")
    accounts: dict[str, float] = {}
    for o in won:
        accounts[site.ref_name(o.get("AccountId")) or "Unknown"] = \
            accounts.get(site.ref_name(o.get("AccountId")) or "Unknown", 0) + (o.get("Amount") or 0)
    donut_html = (f'<div style="display:flex;justify-content:center">{donut(list(accounts.items()), "Closed Won")}'
                  f'</div>{legend(list(accounts))}')
    closed = sorted((parse_date(o.get("CloseDate")), o) for o in won + lost if parse_date(o.get("CloseDate")))
    months = []
    for d, _ in closed:
        key = d.strftime("%b %Y")
        if key not in months:
            months.append(key)
    won_s = [sum(o.get("Amount") or 0 for d, o in closed if d.strftime("%b %Y") == m and o.get("IsWon"))
             for m in months]
    lost_s = [sum(o.get("Amount") or 0 for d, o in closed if d.strftime("%b %Y") == m and not o.get("IsWon"))
              for m in months]
    by_month = column_chart(months, [("Closed Won", won_s), ("Closed Lost", lost_s)], x_title="Close Month") + \
        legend(["Closed Won", "Closed Lost"])
    rows = "".join(f'<tr><td><a href="{site.rec("Opportunity", o["Id"])}">{e(o["Name"])}</a></td>'
                   f'<td>{site.ref(o.get("AccountId"))}</td><td>{e(o.get("StageName"))}</td>'
                   f'<td class="num">{e(money(o.get("Amount")))}</td><td>{e(plain("Opportunity", "CloseDate", o))}</td>'
                   f'</tr>' for o in sorted(open_opps, key=lambda o: o.get("CloseDate") or ""))
    table = (f'<table class="dt"><thead><tr><th>Opportunity Name</th><th>Account Name</th><th>Stage</th>'
             f'<th class="num">Amount</th><th>Close Date</th></tr></thead><tbody>{rows or ""}</tbody></table>')
    user = site.org.user(site.org.current_user_id) or {}
    header = (f'<div class="card"><div class="ph"><div class="ph-row">{icon("Dashboard", 32)}<div class="ph-t">'
              f'<small>Dashboard</small><h1>{e(DASHBOARD_NAME)}</h1></div><div class="btngrp"><span class="btn">'
              f'Refresh</span><span class="btn">Edit</span><span class="btn">Subscribe</span><span class="btn icn">'
              f'&#9660;</span></div></div><div class="ph-meta">As of {e(display_datetime(site.now.isoformat()))} '
              f'&bull; Viewing as {e(user.get("Name", ""))}</div></div></div>')
    comps = "".join([
        _comp("Open Pipeline", f'<div class="metric">{e(compact(pipeline))}<small>Sum of Amount</small></div>'),
        _comp("Closed Won", f'<div class="metric">{e(compact(won_total))}<small>Sum of Amount</small></div>'),
        _comp("Win Rate", f'<div class="gauge">{gauge(rate)}</div>'),
        _comp("Opportunities by Stage", by_stage, span="span2"),
        _comp("Closed Won by Account", donut_html),
        _comp("Won vs. Lost by Close Month", by_month),
        _comp("Open Opportunities", table, span="span2"),
    ])
    body = f'{header}<div class="dash">{comps}</div>'
    return shell(site, title=DASHBOARD_NAME, active="Dashboard", body=body, notice=notice)


def dashboards_page(site: Site, notice: str | None) -> str:
    user = site.org.user(site.org.current_user_id) or {}
    body = (f'<div class="card lv"><div class="ph"><div class="ph-row">{icon("Dashboard", 32)}<div class="ph-t">'
            f'<small>Dashboards</small><h1>All Dashboards</h1></div><div class="btngrp"><span class="btn">New '
            f'Dashboard</span><span class="btn">New Folder</span></div></div><div class="ph-meta">1 item</div></div>'
            f'<table class="dt"><thead><tr><th>Dashboard Name</th><th>Description</th><th>Folder</th>'
            f'<th>Created By</th><th>Created On</th></tr></thead><tbody><tr><td><a href="{site.prefix}/lightning/r/'
            f'Dashboard/{DASHBOARD_ID}/view">{e(DASHBOARD_NAME)}</a></td><td>Pipeline, win rate and closed business '
            f'for Aurora deals</td><td>Sales Dashboards</td><td>{e(user.get("Name", ""))}</td>'
            f'<td>{e(display_date(site.today))}</td></tr></tbody></table></div>')
    return shell(site, title="Dashboards", active="Dashboard", body=body, notice=notice)


# --- Search and errors --------------------------------------------------------------------------------------------
def search_page(site: Site, q: str, notice: str | None) -> str:
    needle = q.strip().lower()
    sections, total = [], 0
    for obj in ("Opportunity", "Account", "Contact", "Lead", "Event", "Task", "User"):
        hits = [r for r in site.org.records(obj) if needle and needle in record_name(obj, r).lower()]
        if not hits:
            continue
        total += len(hits)
        cols = _COLUMNS[obj]
        name_api = OBJECTS[obj]["name"][0]
        rows = "".join("<tr>" + "".join(
            (f'<td><a href="{site.rec(obj, r["Id"])}">{e(record_name(obj, r))}</a></td>' if c == name_api
             else f'<td>{site.value(obj, c, r)}</td>') for c in cols) + "</tr>" for r in hits)
        sections.append(f'<div class="card"><div class="card-h">{icon(obj, 24)}<h2>{e(OBJECTS[obj]["plural"])} '
                        f'({len(hits)})</h2></div><table class="dt"><thead><tr>' +
                        "".join(f"<th>{e(_col_label(obj, c))}</th>" for c in cols) +
                        f"</tr></thead><tbody>{rows}</tbody></table></div>")
    if not sections:
        sections.append(f'<div class="card nf">{icon("Lead", 48, True)}<h1>Don\u2019t give up yet!</h1>'
                        f'<p>No results for \u201c{e(q)}\u201d. Check the spelling or try a different search.</p></div>')
    head = (f'<div class="card"><div class="ph"><div class="ph-row"><div class="ph-t"><small>Search Results</small>'
            f'<h1>\u201c{e(q)}\u201d</h1></div></div><div class="ph-meta">{total} results</div></div></div>')
    return shell(site, title=f"Search: {q}", active="", body=head + '<div class="stack" style="margin-top:12px">' +
                 "".join(sections) + "</div>", notice=notice, q=q)


def not_found_page(site: Site, notice: str | None) -> str:
    body = (f'<div class="card nf">{icon("Lead", 48, True)}<h1>Looks like there\u2019s a problem.</h1><p>This record '
            f'doesn\u2019t exist in this org, or it was created in a conversation whose changes aren\u2019t available '
            f'here.</p><p><a href="{site.home()}">Go to Home</a></p></div>')
    return shell(site, title="Not found", active="", body=body, notice=notice)


# --- Routes -------------------------------------------------------------------------------------------------------
_EXPIRED = ("No saved changes were found for this conversation (nothing was changed yet, or the changes expired after "
            "about 2 hours). Showing the original org data.")


def build_routes(store: StateStore, clock_factory=None) -> list:
    from starlette.responses import HTMLResponse, RedirectResponse, Response
    from starlette.routing import Route

    def now() -> datetime:
        if clock_factory is None:
            return datetime.now(timezone.utc)
        return clock_factory().now

    def resolve(request) -> tuple[Site, bool, str | None] | None:
        token = request.path_params.get("token")
        if token is None:
            org, _ = store.read_by_token(None)
            return Site(org, "", now()), False, None
        if not _TOKEN.fullmatch(token):
            return None
        org, scoped = store.read_by_token(token)
        return Site(org, f"/v/{token}", now()), scoped, None if scoped else _EXPIRED

    def html(text: str, status: int = 200) -> HTMLResponse:
        return HTMLResponse(text, status_code=status, headers=_HEADERS)

    def page(render):
        async def endpoint(request):
            found = resolve(request)
            if found is None:
                org, _ = store.read_by_token(None)
                return html(not_found_page(Site(org, "", now()), None), 404)
            site, scoped, notice = found
            return render(request, site, scoped, notice)
        return endpoint

    def home(request, site, scoped, notice):
        return html(home_page(site, notice))

    def to_home(request, site, scoped, notice):
        return RedirectResponse(site.home(), status_code=302)

    def obj_list(request, site, scoped, notice):
        obj = request.path_params["obj"]
        if obj == "Dashboard":
            return html(dashboards_page(site, notice))
        if obj not in LIST_OBJECTS:
            return html(not_found_page(site, notice), 404)
        return html(list_page(site, obj, notice))

    def record(request, site, scoped, notice):
        obj, rid = request.path_params["obj"], request.path_params["rid"]
        if obj == "Dashboard":
            if rid[:15] != DASHBOARD_ID[:15]:
                return html(not_found_page(site, notice), 404)
            return html(dashboard_page(site, notice))
        hit = site.org.get(rid)
        if hit is None:
            token = None if scoped else store.token_for_record(rid)
            if token:
                return RedirectResponse(f"/v/{token}/lightning/r/{obj}/{rid}/view", status_code=302)
            return html(not_found_page(site, notice), 404)
        real, rec = hit
        if real not in _SECTIONS:
            return html(not_found_page(site, notice), 404)
        if real != obj or rec["Id"] != rid:
            return RedirectResponse(site.rec(real, rec["Id"]), status_code=302)
        return html(record_page(site, real, rec, request.query_params.get("tab"), notice))

    def search(request, site, scoped, notice):
        return html(search_page(site, request.query_params.get("q", ""), notice))

    async def icon_svg(request):
        svg = icon_file(request.path_params["name"].removesuffix(".svg"))
        if svg is None:
            return Response("Not found", status_code=404)
        return Response(svg, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})

    routes = [Route("/img/icon/t4v35/standard/{name}", icon_svg)]
    for base in ("", "/v/{token}"):
        routes += [
            Route(base + "/" if base == "" else base, page(to_home)),
            Route(base + "/lightning", page(to_home)),
            Route(base + "/lightning/page/home", page(home)),
            Route(base + "/lightning/o/{obj}/list", page(obj_list)),
            Route(base + "/lightning/o/{obj}/home", page(obj_list)),
            Route(base + "/lightning/r/{obj}/{rid}/view", page(record)),
            Route(base + "/lightning/search", page(search)),
        ]
    routes.append(Route("/v/{token}/", page(to_home)))
    return routes
