"""Engineering scenario tenant seed data (Aurora offline-status fix).

Source: docs/scenarios/engineering/scenario.md, Appendices A, C and D. Jira data
(AUR-142, AUR-145, Sprint 24) lives in the Test_Jira mock server, not here.
This module seeds:

- E1: Riley's "Aurora pilot - offline status still wrong" thread with Marcus
- T1: Aurora Engineering team, Platform Migration channel, cutover thread
- T2: the Engineering channel and the "Aurora Engineering LT" group chat
- G1/G2: Test_GitHub synced connector (customconnectors) with PR #287, Sam's
  changes-requested review in its content, and merged decoy PRs on the same repo

All seeded evidence is dated on or before Oct 30, 2026; the Nov 20 cutover and
Nov 23 expansion appear only as future dates in message text.
"""

from __future__ import annotations

import json

from ..legal import MARCUS, TEAMS_ONLY, _msg, _user
from ..productivity import RILEY, at

NINA, ELENA, TAYLOR, SAM = "nchen", "eruiz", "tmorgan", "spatel"


def users():
    return [
        _user(NINA, "Nina", "Chen", "Senior Software Engineer", "Engineering", TEAMS_ONLY),
        _user(ELENA, "Elena", "Ruiz", "Senior QA Engineer", "Engineering", TEAMS_ONLY),
        _user(TAYLOR, "Taylor", "Morgan", "Engineering Lead, Aurora", "Engineering", TEAMS_ONLY),
        _user(SAM, "Sam", "Patel", "Platform Lead", "Engineering", TEAMS_ONLY),
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
        _email("eng-email-001", "Send", RILEY, MARCUS, E1_SUBJECT,
               "<p>Hi Marcus,</p><p>Some of our Aurora pilot stores are seeing hubs stay marked offline in the "
               "dashboard after they reconnect to the network. Could your team take a look?</p><p>Thanks,<br>Riley</p>",
               at(10, 23, 11, 5)),
        _email("eng-email-002", "Reply", MARCUS, RILEY, f"RE: {E1_SUBJECT}",
               "<p>Thanks for flagging the reconnect issue. Engineering is working on a fix, and I will share an "
               "update once we have confirmed the validation plan.</p><p>Marcus</p>",
               at(10, 26, 14, 0), ref="eng-email-001"),
        _email("eng-email-003", "Reply", RILEY, MARCUS, f"RE: {E1_SUBJECT}",
               "<p>Hi Marcus, our pilot stores are still seeing Aurora hubs marked offline after they reconnect. "
               "Staff keep restarting devices that are actually working. You mentioned a fix was being worked on. "
               "Can we expect it before Monday, November 23, when we expand the pilot? I need to brief our store "
               "managers before then. Thanks, Riley.</p>",
               at(10, 29, 8, 15), ref="eng-email-002"),
    ]


def chats():
    return [
        {
            "ChatId": "eng-chat-lt",
            "ChatType": "Group",
            "ChatName": "Aurora Engineering LT",
            "Members": [TAYLOR, SAM, MARCUS],
            "CreatedDateTime": at(9, 14, 9, 0),
            "ChatMessages": [
                _msg(1, TAYLOR, "Setting up this group for Aurora engineering leadership. Sprint scope changes "
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
MEMBERS = [NINA, ELENA, TAYLOR, SAM]
T1_ROOT = "eng-msg-t1"


def teams():
    return [
        {
            "TeamId": TEAM_ID,
            "Name": "Aurora Engineering",
            "Description": "Engineering team for the Verdantis Aurora smart-home hub platform.",
            "CreatedDateTime": at(3, 2, 9, 0),
            "TeamType": "Private",
            "Owners": [MARCUS],
            "Members": MEMBERS,
        }
    ]


def channels():
    everyone = [MARCUS, *MEMBERS]
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
            "From": SAM,
            "Subject": "Aurora status-service cutover - Contoso pilot",
            "ContentType": "text",
            "Content": "The November 20 status-service cutover is still the plan. The Contoso expansion on "
                       "November 23 will use the event-driven service. A fix confined to the legacy polling path "
                       "will not resolve that pilot's issue.",
            "SentDateTime": at(10, 28, 16, 0),
        },
        {
            "ChannelMessageId": "eng-msg-sprint24",
            "ChannelId": CH_ENGINEERING,
            "From": TAYLOR,
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
            "From": ELENA,
            "ContentType": "text",
            "Content": "We need reconnect coverage on the new path and the rollout regression checks. Passing the "
                       "old-service tests is not enough to call this ready.",
            "SentDateTime": at(10, 28, 16, 10),
        },
        {
            "ChannelMessageReplyId": "eng-reply-t1-2",
            "ChannelMessageId": T1_ROOT,
            "From": MARCUS,
            "ContentType": "text",
            "Content": "Bring a scope proposal before we move sprint work. LT needs to approve any deferral; Sam "
                       "needs to confirm platform review availability. We have not committed a release date to "
                       "Contoso.",
            "SentDateTime": at(10, 29, 8, 30),
        },
    ]


# --- Test_GitHub (synced custom connector) -----------------------------------

ORG, REPO = "verdantis-lab", "aurora-status"
ORG_URL = f"https://github.com/{ORG}"
REPO_URL = f"{ORG_URL}/{REPO}"

PEOPLE = {NINA: "Nina Chen", ELENA: "Elena Ruiz", SAM: "Sam Patel", TAYLOR: "Taylor Morgan"}


def _prop(name, type_, description, labels=None, searchable=False, refinable=False):
    p = {"name": name, "type": type_, "description": description}
    if labels:
        p["labels"] = labels
    p |= {"isSearchable": searchable, "isRetrievable": True, "isQueryable": True}
    if refinable:
        p["isRefinable"] = True
    return p


GITHUB_PROPERTIES = [
    _prop("Id", "string", "Pull request number.", ["secondaryId"], searchable=True),
    _prop("Url", "string", "Link to the pull request on GitHub.", ["url"]),
    _prop("Title", "string", "Pull request title.", ["title"], searchable=True),
    _prop("Description", "string", "Pull request description.", searchable=True),
    _prop("CreatedBy", "string", "Author of the pull request.", ["createdBy"], searchable=True),
    _prop("CreatedAt", "dateTime", "When the pull request was opened.", ["createdDateTime"], refinable=True),
    _prop("LastModifiedAt", "dateTime", "When the pull request was last updated.", ["lastModifiedDateTime"], refinable=True),
    _prop("LastModifiedBy", "string", "Person who last updated the pull request.", ["lastModifiedBy"], searchable=True),
    _prop("MergedAt", "dateTime", "When the pull request was merged.", ["closedDate"], refinable=True),
    _prop("State", "string", "Pull request state: Open, Merged or Closed.", ["state"], refinable=True),
    _prop("Labels", "stringCollection", "Labels on the pull request.", ["tags"], searchable=True),
    _prop("Assignees", "stringCollection", "People assigned to the pull request.", searchable=True),
    _prop("Contributors", "stringCollection", "People who authored or reviewed the pull request.", ["authors"], searchable=True),
    _prop("RepositoryName", "string", "Repository name.", ["containerName"], searchable=True),
    _prop("RepositoryURL", "string", "Link to the repository.", ["containerUrl"]),
    _prop("RepositoryDescription", "string", "Repository description.", searchable=True),
    _prop("Type", "string", "Item type.", ["itemType"], refinable=True),
    _prop("ItemPath", "string", "Owner and repository of the pull request.", ["itemPath"]),
    _prop("OrganizationName", "string", "GitHub organization.", refinable=True),
    _prop("OrganizationUrl", "string", "Link to the GitHub organization."),
    _prop("Milestone", "string", "Milestone (sprint) of the pull request.", ["sprintName"], refinable=True),
]

PR287_BODY = """Fixes AUR-142: Aurora hubs remain offline after reconnect.

Updates the legacy polling status handler so a successful network reconnect clears the stale Offline state in the dashboard. Previously the handler kept the last Offline state until the next full poll cycle, so reconnected hubs stayed Offline even though telemetry had resumed.

Changes:
- Legacy polling status handler: clear Offline on reconnect heartbeat
- Legacy-path reconnect tests added

Checks: legacy-path checks pass as of October 28, 17:00.

Not yet covered: the event-driven status service. Event-driven reconnect coverage is not implemented in this PR."""

G2_REVIEW = ("The legacy-path fix looks reasonable, but Contoso moves to the event-driven status service with the "
             "November 20 cutover. Two things are needed: implement the equivalent reconnect correction in that "
             "path, and add/run the reconnect tests there. Once both are done, request another platform review. "
             "I am not approving this version for the pilot.")

# (number, title, body, author, created, modified, modified_by, merged, labels, assignees, contributors, milestone, comments)
PRS = [
    (287, "Fix stale offline state after reconnect", PR287_BODY, NINA,
     at(10, 27, 11, 30), at(10, 28, 17, 20), SAM, None, ["bug", "aurora-status"], [NINA], [NINA, SAM],
     "Aurora Sprint 24",
     [{"SubmittedAt": at(10, 28, 17, 20), "createdBy": SAM, "Content": G2_REVIEW, "State": "ChangesRequested"}]),
    (281, "Add retry backoff to status poller",
     "Adds exponential backoff to the legacy status poller when the device gateway returns 503, to reduce load "
     "during regional outages.",
     NINA, at(10, 13, 10, 0), at(10, 16, 15, 20), SAM, at(10, 16, 15, 20), ["enhancement", "aurora-status"],
     [NINA], [NINA, SAM], "Aurora Sprint 23",
     [{"SubmittedAt": at(10, 16, 14, 50), "createdBy": SAM, "Content": "Looks good. Approving.", "State": "Approved"}]),
    (276, "Event-driven status service: publish device heartbeat events",
     "First step of the status-service migration: device heartbeats are published as events on the new status "
     "bus. The dashboard still reads from the legacy poller until the cutover.",
     SAM, at(9, 28, 9, 15), at(10, 7, 11, 40), SAM, at(10, 7, 11, 40), ["migration", "aurora-status"],
     [SAM], [SAM, ELENA], "Aurora Sprint 23",
     [{"SubmittedAt": at(10, 7, 10, 5), "createdBy": ELENA, "Content": "Regression suite passes on staging. Approved.",
       "State": "Approved"}]),
    (269, "Rollout regression suite: add store-group targeting tests",
     "Adds regression tests for store-group targeting in staged rollouts.",
     ELENA, at(9, 15, 13, 0), at(9, 18, 16, 30), TAYLOR, at(9, 18, 16, 30), ["tests", "aurora-status"],
     [ELENA], [ELENA, TAYLOR], "Aurora Sprint 22",
     [{"SubmittedAt": at(9, 18, 16, 0), "createdBy": TAYLOR, "Content": "Approved.", "State": "Approved"}]),
]


def _pr_item(num, title, body, author, created, modified, modified_by, merged, labels, assignees,
             contributors, milestone, comments):
    props = {
        "Id": str(num),
        "Url": f"{REPO_URL}/pull/{num}",
        "Title": title,
        "Description": body,
        "CreatedBy": PEOPLE[author],
        "CreatedAt": created,
        "LastModifiedAt": modified,
        "LastModifiedBy": PEOPLE[modified_by],
        "State": "Merged" if merged else "Open",
        "Labels": labels,
        "Assignees": [PEOPLE[a] for a in assignees],
        "Contributors": [PEOPLE[c] for c in contributors],
        "RepositoryName": REPO,
        "RepositoryURL": REPO_URL,
        "RepositoryDescription": "Aurora hub status service",
        "Type": "Pull request",
        "ItemPath": f"{ORG}/{REPO}",
        "OrganizationName": ORG,
        "OrganizationUrl": ORG_URL,
        "Milestone": milestone,
    }
    if merged:
        props["MergedAt"] = merged
    review = {"comments": [{**c, "createdBy": PEOPLE[c["createdBy"]]} for c in comments]}
    return {
        "id": f"pr{num}",
        "properties": props,
        "content": f"{body}\n\n{json.dumps(review, ensure_ascii=False)}",
        "contentType": "text",
    }


def customconnectors():
    return [
        {
            "ConnectionId": "testgithub",
            "ConnectionName": "Test_GitHub",
            "ConnectionDescription": "GitHub pull requests from the verdantis-lab organization, including reviews.",
            "ContentCategory": "taskManagement",
            "Properties": GITHUB_PROPERTIES,
            "Items": [_pr_item(*pr) for pr in PRS],
        }
    ]
