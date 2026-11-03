"""Engineering scenario tenant seed data (Aurora offline-status fix).

Source: docs/scenarios/engineering/scenario.md. The Atlassian data (Jira project
AUR, Sprint 24, the Confluence space AUR) comes from the Rovo mock server's seed
file, so the synced connectors here and the Test_Rovo MCP tools return the same
records. GitHub data (PR #287) lives only in the Test_GitHub mock server.
This module seeds:

- Jira synced connector: the six Sprint 24 work items, AUR-142 the one at risk
- Confluence synced connector: the five pages in the Aurora Engineering space

- E1: Atul's "Aurora pilot - offline status still wrong" thread with Emil
- T1: Aurora Engineering team, Platform Migration channel, cutover thread
- T2: the Engineering channel and the "Aurora Engineering LT" group chat

All seeded evidence is dated on or before Oct 30, 2026; the Nov 20 cutover and
Nov 23 expansion appear only as future dates in message text.
"""

from __future__ import annotations

import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from ..legal import EMIL, TEAMS_ONLY, _msg, _user
from ..productivity import ATUL, at

TRIIN, MARIA, KERRY, TAMA = "triin", "maria", "kerry", "tama"


def users():
    return [
        _user(TRIIN, "Triin", "Lepp", "Senior Software Engineer", "Engineering", TEAMS_ONLY),
        _user(MARIA, "Maria", "Oliva", "Senior QA Engineer", "Engineering", TEAMS_ONLY),
        _user(KERRY, "Kerry", "Allen", "Engineering Lead, Aurora", "Engineering", TEAMS_ONLY),
        _user(TAMA, "Tama", "Surya", "Platform Lead", "Engineering", TEAMS_ONLY),
    ]


E1_SUBJECT = "Aurora pilot - offline status still wrong"


def _email(eid, action, sender, to, subject, body, ts, ref=None):
    e = {
        "EmailId": eid,
        "EmailAction": action,
        "Sender": sender,
        "ToRecipients": [{"Recipient": to}],
        "CcRecipients": [],
        "Subject": subject,
        "Body": body,
        "BodyType": "html",
        "Timestamp": ts,
    }
    if ref:
        e["ReferenceEmailId"] = ref
    return e


def emails():
    return [
        _email("eng-email-001", "Send", ATUL, EMIL, E1_SUBJECT,
               "<p>Hi Emil,</p><p>Some of our Aurora pilot stores are seeing hubs stay marked offline in the "
               "dashboard after they reconnect to the network. Could your team take a look?</p><p>Thanks,<br>Atul</p>",
               at(10, 23, 11, 5)),
        _email("eng-email-002", "Reply", EMIL, ATUL, f"RE: {E1_SUBJECT}",
               "<p>Thanks for flagging the reconnect issue. Engineering is working on a fix, and I will share an "
               "update once we have confirmed the validation plan.</p><p>Emil</p>",
               at(10, 26, 14, 0), ref="eng-email-001"),
        _email("eng-email-003", "Reply", ATUL, EMIL, f"RE: {E1_SUBJECT}",
               "<p>Hi Emil, our pilot stores are still seeing Aurora hubs marked offline after they reconnect. "
               "Staff keep restarting devices that are actually working. You mentioned a fix was being worked on. "
               "Can we expect it before Monday, November 23, when we expand the pilot? I need to brief our store "
               "managers before then. Thanks, Atul.</p>",
               at(10, 29, 8, 15), ref="eng-email-002"),
    ]


def chats():
    return [
        {
            "ChatId": "eng-chat-lt",
            "ChatType": "Group",
            "ChatName": "Aurora Engineering LT",
            "Members": [KERRY, TAMA, EMIL],
            "CreatedDateTime": at(9, 14, 9, 0),
            "ChatMessages": [
                _msg(1, KERRY, "Setting up this group for Aurora engineering leadership. Sprint scope changes "
                                "come here for approval.", at(9, 14, 9, 2)),
            ],
        }
    ]


def events():
    return []


def files():
    return []


# --- Teams: Aurora Engineering team ------------------------------------------

TEAM_ID = "eng-team-aurora"
CH_MIGRATION, CH_ENGINEERING = "eng-ch-platform-migration", "eng-ch-engineering"
MEMBERS = [TRIIN, MARIA, KERRY, TAMA]
T1_ROOT = "eng-msg-t1"


def teams():
    return [
        {
            "TeamId": TEAM_ID,
            "Name": "Aurora Engineering",
            "Description": "Engineering team for the Zava Aurora smart-home hub platform.",
            "CreatedDateTime": at(3, 2, 9, 0),
            "TeamType": "Private",
            "Owners": [EMIL],
            "Members": MEMBERS,
        }
    ]


def channels():
    everyone = [EMIL, *MEMBERS]
    return [
        {
            "ChannelId": CH_MIGRATION,
            "TeamId": TEAM_ID,
            "Name": "Platform Migration",
            "Description": "Migration from the legacy polling status service to the event-driven status service.",
            "CreatedDateTime": at(6, 8, 10, 0),
            "ChannelType": "Standard",
            "Members": everyone,
        },
        {
            "ChannelId": CH_ENGINEERING,
            "TeamId": TEAM_ID,
            "Name": "Engineering",
            "Description": "Aurora engineering updates, sprint planning and decisions.",
            "CreatedDateTime": at(3, 2, 9, 5),
            "ChannelType": "Standard",
            "Members": everyone,
        },
    ]


def channelmessages():
    return [
        {
            "ChannelMessageId": T1_ROOT,
            "ChannelId": CH_MIGRATION,
            "From": TAMA,
            "Subject": "Aurora status-service cutover - Lakeshore Retail pilot",
            "ContentType": "text",
            "Content": "The November 20 status-service cutover is still the plan. The Lakeshore Retail expansion on "
                       "November 23 will use the event-driven service. A fix confined to the legacy polling path "
                       "will not resolve that pilot's issue.",
            "SentDateTime": at(10, 28, 16, 0),
        },
        {
            "ChannelMessageId": "eng-msg-sprint24",
            "ChannelId": CH_ENGINEERING,
            "From": KERRY,
            "Subject": "Aurora Sprint 24 has started",
            "ContentType": "text",
            "Content": "Aurora Sprint 24 runs October 26 to November 20. The sprint board is in Jira. Raise any "
                       "scope change here and bring it to LT for approval.",
            "SentDateTime": at(10, 26, 9, 30),
        },
    ]


def channelmessagereplies():
    return [
        {
            "ChannelMessageReplyId": "eng-reply-t1-1",
            "ChannelMessageId": T1_ROOT,
            "From": MARIA,
            "ContentType": "text",
            "Content": "We need reconnect coverage on the new path and the rollout regression checks. Passing the "
                       "old-service tests is not enough to call this ready.",
            "SentDateTime": at(10, 28, 16, 10),
        },
        {
            "ChannelMessageReplyId": "eng-reply-t1-2",
            "ChannelMessageId": T1_ROOT,
            "From": EMIL,
            "ContentType": "text",
            "Content": "Bring a scope proposal before we move sprint work. LT needs to approve any deferral. We "
                       "have not committed a release date to Lakeshore Retail.",
            "SentDateTime": at(10, 29, 8, 30),
        },
    ]


# --- Synced connectors: Jira and Confluence ----------------------------------
# Built from the Rovo mock's seed so the synced copies match what Test_Rovo returns. Links point at the mock's
# browse and wiki viewers so citations open.

ROVO_DIR = Path(__file__).resolve().parents[3] / "mock_mcp_servers" / "atlassian"
ROVO_URL = "https://mock-atlassian.yellowsand-9530f5dc.eastus.azurecontainerapps.io"
ATLASSIAN_SITE = "https://zava-online.atlassian.net"


def _seed() -> dict:
    return json.loads((ROVO_DIR / "seed_files" / "seed.json").read_text(encoding="utf-8"))


def _render():
    for d in (ROVO_DIR, ROVO_DIR.parent / "_framework"):
        if str(d) not in sys.path:
            sys.path.insert(0, str(d))
    from mock_atlassian import render
    return render


def _iso(ts: str) -> str:
    """Seed timestamps (``+0000`` or ``Z``, with milliseconds) as UTC ISO 8601 with ``Z``."""
    dt = datetime.strptime(ts.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S.%f%z")
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _day(ts: str) -> str:
    d = datetime.fromisoformat(_iso(ts).replace("Z", "+00:00"))
    return f"{d:%A, %B} {d.day}, {d.year}"


def _prop(name, type_, description, labels=None, searchable=True, refinable=False):
    p = {"name": name, "type": type_, "description": description, "isSearchable": searchable,
         "isRetrievable": True, "isQueryable": True}
    if labels:
        p["labels"] = labels
    if refinable:
        p["isRefinable"] = True
        p["isSearchable"] = False
    return p


JIRA_PROPERTIES = [
    _prop("Key", "string", "Work item key, for example AUR-142.", ["secondaryId"]),
    _prop("Url", "string", "Link to the work item in Jira.", ["url"], searchable=False),
    _prop("Title", "string", "Work item summary.", ["title"]),
    _prop("Description", "string", "Work item description."),
    _prop("Type", "string", "Work item type: Story, Task or Bug.", ["itemType"], refinable=True),
    _prop("Status", "string", "Workflow status: To Do, In Progress or Done.", ["state"], refinable=True),
    _prop("Priority", "string", "Priority: Highest, High, Medium or Low.", refinable=True),
    _prop("Assignee", "stringCollection", "Person the work item is assigned to.", ["assignedToPeople"]),
    _prop("Reporter", "string", "Person who reported the work item.", ["createdBy"]),
    _prop("Labels", "stringCollection", "Labels on the work item.", ["tags"]),
    _prop("Sprint", "string", "Sprint the work item is planned in.", ["sprintName"], refinable=True),
    _prop("SprintGoal", "string", "Goal of the sprint the work item is planned in."),
    _prop("SprintDates", "string", "Start and end dates of the sprint."),
    _prop("OriginalEstimateHours", "double", "Original estimate in hours.", searchable=False),
    _prop("Comments", "stringCollection", "Comments on the work item, oldest first, as 'date - author: text'."),
    _prop("LinkedItems", "stringCollection", "Linked work items, as 'relationship KEY'."),
    _prop("Project", "string", "Jira project.", ["containerName"]),
    _prop("ProjectUrl", "string", "Link to the Jira project.", ["containerUrl"], searchable=False),
    _prop("CreatedAt", "dateTime", "When the work item was created.", ["createdDateTime"], refinable=True),
    _prop("UpdatedAt", "dateTime", "When the work item was last updated.", ["lastModifiedDateTime"],
          refinable=True),
    _prop("ResolvedAt", "dateTime", "When the work item was resolved.", ["closedDate"], refinable=True),
]


def _jira_item(issue, seed, names):
    sprint = next((s for s in seed["sprints"] if s["id"] == issue.get("sprint")), None)
    comments = [f"{c['created'][:10]} - {names[c['author']]}: {c['body']}" for c in issue.get("comments", [])]
    links = [f"{l.get('type', 'relates to')} {l.get('key') or l.get('outwardIssue') or l.get('inwardIssue')}"
             for l in issue.get("links", [])]
    props = {
        "Key": issue["key"],
        "Url": f"{ROVO_URL}/browse/{issue['key']}",
        "Title": issue["summary"],
        "Description": issue.get("description") or "",
        "Type": issue["type"],
        "Status": issue["status"],
        "Priority": issue["priority"],
        "Assignee": [names[issue["assignee"]]] if issue.get("assignee") else [],
        "Reporter": names[issue["reporter"]],
        "Labels": issue.get("labels", []),
        "Comments": comments,
        "LinkedItems": links,
        "Project": f"{seed['project']['name']} ({seed['project']['key']})",
        "ProjectUrl": f"{ROVO_URL}/jira/software/projects/{seed['project']['key']}/boards/{seed['project']['boardId']}",
        "CreatedAt": _iso(issue["created"]),
        "UpdatedAt": _iso(issue["updated"]),
    }
    if issue.get("estimateHours") is not None:
        props["OriginalEstimateHours"] = float(issue["estimateHours"])
    if sprint:
        props.update({"Sprint": sprint["name"], "SprintGoal": sprint.get("goal", ""),
                      "SprintDates": f"{_day(sprint['startDate'])} to {_day(sprint['endDate'])}"})
    if issue["status"] == "Done":
        props["ResolvedAt"] = _iso(issue["updated"])
    props = {k: v for k, v in props.items() if v not in ("", [])}
    text = [f"{issue['key']}: {issue['summary']}", f"Status: {issue['status']}. Priority: {issue['priority']}.",
            issue.get("description") or ""]
    if comments:
        text += ["Comments:", *comments]
    return {"id": re.sub(r"[^A-Za-z0-9]", "", issue["key"]).lower(), "properties": props,
            "content": "\n\n".join(t for t in text if t), "contentType": "text"}


def customconnectors():
    seed = _seed()
    names = {u["key"]: u["displayName"] for u in seed["users"]}
    return [
        {
            "ConnectionId": "jiraaurora",
            "ConnectionName": "Jira",
            "ConnectionDescription": "Jira work items from the Aurora (AUR) project at zava-online.atlassian.net, "
                                     "including sprints, status and comments.",
            "ContentCategory": "taskManagement",
            "Properties": JIRA_PROPERTIES,
            "Items": [_jira_item(i, seed, names) for i in seed["issues"]],
        }
    ]


EVERYONE_ACL = {
    "principal": {"type": "everyone", "value": "EVERYONE", "identitySource": None,
                  "identitySourceEnum": "azureActiveDirectory", "identityType": 3,
                  "identitySourceProperties": None, "metadata": None, "displayName": None},
    "ruleNode": None,
    "accessType": "grant",
    "transformedIdentity": None,
}


def _person(user: dict) -> dict:
    email = user["email"]
    return {"ExternalId": str(uuid.uuid5(uuid.NAMESPACE_URL, f"mailto:{email}")), "Email": email,
            "ExternalName": user["displayName"], "PrincipalType": "user", "id": email}


def _page_comment(c, users, render):
    who = _person(users[c["author"]])
    ts = _iso(c["created"])
    return {"entitySemanticType": "comment", "commentId": c["id"], "parentCommentId": c.get("parentId"),
            "creator": who, "modifier": who, "createdDateTime": ts, "modifiedDateTime": ts,
            "mentionedUsers": [], "reactions": [], "entityContent": render.to_html(c["body"]),
            "entityEncoding": "raw", "entityFormat": "html"}


def confluencepages():
    seed, render = _seed(), _render()
    users = {u["key"]: u for u in seed["users"]}
    conf = seed["confluence"]
    spaces = {s["id"]: s for s in conf["spaces"]}
    pages = {p["id"]: p for p in conf["pages"]}
    items = []
    for page in conf["pages"]:
        space = spaces[page["spaceId"]]
        tree, parent = [], pages.get(page.get("parentId"))
        while parent:
            tree.insert(0, parent["title"])
            parent = pages.get(parent.get("parentId"))
        editors = [page["author"]] + ([page["updatedBy"]] if page["updatedBy"] != page["author"] else [])
        comments = [c for c in conf["comments"] if c["pageId"] == page["id"]]
        items.append({
            "id": page["id"],
            "displayName": page["id"],
            "contentDomainCategoryName": "wikis",
            "isContainer": False,
            "containerId": None,
            "UniversalAccessControlBlock": None,
            "activityList": None,
            "contentEnrichmentData": None,
            "associatedItemsMetadata": None,
            "itemVersion": None,
            "isAssociatedItem": False,
            "accessControlList": [EVERYONE_ACL],
            "properties": {
                "Id": page["id"],
                "Title": page["title"],
                "Url": f"{ROVO_URL}/wiki/spaces/{space['key']}/pages/{page['id']}/{render.page_slug(page['title'])}",
                "Type": "page",
                "Status": page["status"],
                "PageTree": " > ".join([space["name"], *tree]),
                "ItemPath": "/" + "/".join([space["name"], *tree]),
                "Labels": page.get("labels", []),
                "Likes": 0,
                "IconUrl": f"{ROVO_URL}/wiki/download/attachments/{space['id']}/{space['key']}",
                "SpaceName": space["name"],
                "SpaceKey": space["key"],
                "SpaceId": space["id"],
                "SpaceURL": f"{ATLASSIAN_SITE}/wiki/rest/api/space/{space['key']}",
                "SpaceDescription": space["description"],
                "SpaceStatus": space["status"],
                "SpaceType": space["type"],
                "SpaceLabels": space.get("labels", []),
                "CreatedOn": _iso(page["created"]),
                "CreatedByEmail": users[page["author"]]["email"],
                "CreatedByName": _person(users[page["author"]]),
                "UpdatedOn": _iso(page["updated"]),
                "UpdatedByEmail": users[page["updatedBy"]]["email"],
                "UpdatedByName": _person(users[page["updatedBy"]]),
                "Authors": [_person(users[k]) for k in editors],
            },
            "content": {"parsedData": render.to_html(page["body"]), "type": "html", "annotation": None,
                        "semanticContent": None},
            **({"comments": [_page_comment(c, users, render) for c in comments]} if comments else {}),
        })
    return items
