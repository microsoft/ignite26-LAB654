"""Engineering scenario tenant seed data (Aurora offline-status fix).

Source: docs/scenarios/engineering/scenario.md, Appendices A, C and D. Jira data
(AUR-142, AUR-145, Sprint 24) lives in the Test_Jira mock server and GitHub data
(PR #287) in the Test_GitHub mock server, not here.
This module seeds:

- E1: Atul's "Aurora pilot - offline status still wrong" thread with Emil
- T1: Aurora Engineering team, Platform Migration channel, cutover thread
- T2: the Engineering channel and the "Aurora Engineering LT" group chat

All seeded evidence is dated on or before Oct 30, 2026; the Nov 20 cutover and
Nov 23 expansion appear only as future dates in message text.
"""

from __future__ import annotations

import json

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
            "Content": "Bring a scope proposal before we move sprint work. LT needs to approve any deferral; Tama "
                       "needs to confirm platform review availability. We have not committed a release date to "
                       "Lakeshore Retail.",
            "SentDateTime": at(10, 29, 8, 30),
        },
    ]
