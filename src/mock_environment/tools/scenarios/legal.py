"""Legal scenario seed data (Verdantis x Cognivault).

Source: src/scenarios/legal.md. All dates are relative to ``anchor``, the
Monday morning on which Tomás pings Marcus ("today" in the scenario).
The negotiation session is anchor + 7 days and go-live is anchor + 10 days,
so with the default anchor (Mon 2026-10-05) they land on the 12th and 15th
as written in the scenario doc.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

# Verdantis is in Stamford, CT (US Eastern). Z timestamps are UTC.
ET_OFFSET = timedelta(hours=-4)  # EDT; adjust if anchoring outside daylight time
EVENT_TZ = "Eastern Standard Time"

LICENSES = ["Microsoft 365 Copilot", "Microsoft Teams Enterprise", "Office 365 E5 (no Teams)"]

AGREEMENT_FILE = "Cognivault AI Vendor Agreement v4.2.docx"
AGREEMENT_FILE_ID = "legal-file-001"
AGREEMENT_LINK_ID = "legal-link-001"


def ordinal(d: date) -> str:
    n = d.day
    suffix = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def utc(day: date, hh: int, mm: int, ss: int = 0) -> str:
    """Eastern wall-clock time on ``day`` -> UTC ISO string with Z."""
    local_dt = datetime.combine(day, time(hh, mm, ss), tzinfo=timezone(ET_OFFSET))
    return local_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def local(day: date, hh: int, mm: int) -> str:
    return datetime.combine(day, time(hh, mm)).strftime("%Y-%m-%dT%H:%M:%S")


def _user(nick, first, last, title, dept, manager, phone):
    return {
        "MailNickName": nick,
        "DisplayName": f"{first} {last}",
        "FirstName": first,
        "LastName": last,
        "JobTitle": title,
        "Department": dept,
        "CompanyName": "Verdantis",
        "Manager": manager,
        "PhoneNumber": phone,
        "UsageLocation": "US",
        "OfficeLocation": "Stamford, CT",
        "Address": {
            "Street": "400 Atlantic St",
            "City": "Stamford",
            "State": "CT",
            "PostalCode": "06901",
            "Country": "USA",
        },
        "Licenses": LICENSES,
        "MailboxSettings": {
            "WorkingHours": {
                "DaysOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "StartTime": "08:30",
                "EndTime": "17:30",
                "TimeZone": "America/New_York",
            }
        },
    }


def users():
    return [
        _user("eleanor.vance", "Eleanor", "Vance", "General Counsel", "Legal", None, "+1 203 555 0101"),
        _user("marcus.hollowell", "Marcus", "Hollowell", "Associate General Counsel, Technology",
              "Legal - Technology Transactions", "eleanor.vance", "+1 203 555 0102"),
        _user("grace.lindqvist", "Grace", "Lindqvist", "Senior Paralegal, Technology Transactions",
              "Legal - Technology Transactions", "marcus.hollowell", "+1 203 555 0103"),
        _user("nathan.osei", "Nathan", "Osei", "Senior Counsel, Legal Knowledge and Innovation",
              "Legal - Knowledge and Innovation", "eleanor.vance", "+1 203 555 0104"),
        _user("tomas.aguilar", "Tomás", "Aguilar", "Chief Underwriting Officer", "Underwriting",
              None, "+1 203 555 0105"),
        _user("daniel.brandt", "Daniel", "Brandt", "Director, Underwriting Analytics", "Underwriting",
              "tomas.aguilar", "+1 203 555 0106"),
        _user("radhika.sengupta", "Radhika", "Sengupta", "SVP, Procurement", "Procurement",
              None, "+1 203 555 0107"),
        _user("olivia.park", "Olivia", "Park", "Procurement Manager, Technology Sourcing", "Procurement",
              "radhika.sengupta", "+1 203 555 0108"),
    ]


def _to(*nicks):
    return [{"Recipient": n} for n in nicks]


def emails(anchor: date):
    neg = anchor + timedelta(days=7)
    golive = anchor + timedelta(days=10)
    d_minus_14 = anchor - timedelta(days=14)
    d_minus_13 = anchor - timedelta(days=13)

    subj = "Cognivault Nexus: what the business needs from the contract (ranked)"
    radhika_body = f"""Hi Marcus,

Ahead of Cognivault sending over their paper, here is what the business needs from the Nexus contract, in priority order. Tomás and I are aligned on this list.

1. We own the fine-tuned model. Nexus will be fine-tuned on our claims and underwriting data. Whatever gets built from our data (the fine-tuned model and its outputs) has to belong to Verdantis. This one is not negotiable.

2. Control over model changes. We need real advance notice, and a say, before Cognivault changes or retires the model that prices our policies.

3. Explainability for regulators. Colorado and New York examiners are scrutinising AI underwriting. We have to be able to explain how Nexus reaches a decision and show that we are overseeing the vendor.

4. A clean exit. If this doesn't work out, we need our data back in a usable format and enough runway to transition without a gap in quoting.

5. Liability that matches the deal size. This is $14.75M over five years ($2.95M a year), with up to 4 million underwriting decisions a month. The cap has to reflect that.

6. Delaware law and Delaware courts, not the vendor's arbitration.

On timing: the session on the {ordinal(neg)} is a negotiation session with Cognivault's counsel, not a signing. Tomás would like to go live on the {ordinal(golive)}, but nothing gets signed until you've been through their contract against the playbook.

Shout if any of this conflicts with the AI procurement playbook.

Thanks,
Radhika

Radhika Sengupta
SVP, Procurement | Verdantis"""

    tomas_reply = """Thanks Radhika, agree with the order.

Marcus, #2 is the one I care about most from the underwriting side. Let me know what you need from my team.

Tomás"""

    marcus_reply = """Thanks both, this is helpful.

These line up with our AI procurement playbook. I'll review Cognivault's contract against the playbook and this list as soon as their paper lands, and flag anything that needs a business call.

Marcus

Marcus Hollowell
Associate General Counsel, Technology | Verdantis Legal"""

    return [
        {
            "EmailId": "legal-email-001",
            "EmailAction": "Send",
            "Sender": "radhika.sengupta",
            "ToRecipients": _to("marcus.hollowell"),
            "CcRecipients": _to("tomas.aguilar"),
            "Subject": subj,
            "Body": radhika_body,
            "BodyType": "text",
            "Importance": "High",
            "Timestamp": utc(d_minus_14, 10, 12),
        },
        {
            "EmailId": "legal-email-002",
            "ReferenceEmailId": "legal-email-001",
            "EmailAction": "ReplyAll",
            "Sender": "tomas.aguilar",
            "ToRecipients": _to("radhika.sengupta", "marcus.hollowell"),
            "Subject": f"RE: {subj}",
            "Body": tomas_reply,
            "BodyType": "text",
            "Timestamp": utc(d_minus_14, 11, 40),
        },
        {
            "EmailId": "legal-email-003",
            "ReferenceEmailId": "legal-email-002",
            "EmailAction": "ReplyAll",
            "Sender": "marcus.hollowell",
            "ToRecipients": _to("tomas.aguilar", "radhika.sengupta"),
            "Subject": f"RE: {subj}",
            "Body": marcus_reply,
            "BodyType": "text",
            "Timestamp": utc(d_minus_13, 9, 5),
        },
        # Background mail so Marcus's mailbox isn't single-topic.
        {
            "EmailId": "legal-email-004",
            "EmailAction": "Send",
            "Sender": "eleanor.vance",
            "ToRecipients": _to("marcus.hollowell", "nathan.osei", "grace.lindqvist"),
            "Subject": "Legal ops: Q4 matter intake and outside counsel budgets",
            "Body": """Team,

Quick reminder that Q4 outside counsel budget requests are due Friday. Please make sure every open matter has a current status and owner in the matter list, and that any matter expected to exceed its budget is flagged.

Thanks,
Eleanor""",
            "BodyType": "text",
            "Timestamp": utc(anchor - timedelta(days=10), 16, 20),
        },
        {
            "EmailId": "legal-email-005",
            "EmailAction": "Send",
            "Sender": "olivia.park",
            "ToRecipients": _to("marcus.hollowell"),
            "CcRecipients": _to("grace.lindqvist"),
            "Subject": "NDA review: Halvorsen Telematics data pilot",
            "Body": """Hi Marcus,

Halvorsen Telematics sent their mutual NDA for the 90-day telematics data pilot with Personal Auto. It's their standard form. Could someone on your team take a look this week? No rush beyond that.

Thanks,
Olivia""",
            "BodyType": "text",
            "Timestamp": utc(anchor - timedelta(days=6), 14, 3),
        },
        {
            "EmailId": "legal-email-006",
            "ReferenceEmailId": "legal-email-005",
            "EmailAction": "ReplyAll",
            "Sender": "grace.lindqvist",
            "ToRecipients": _to("olivia.park"),
            "CcRecipients": _to("marcus.hollowell"),
            "Subject": "RE: NDA review: Halvorsen Telematics data pilot",
            "Body": """Hi Olivia,

I'll pick this up and run it against our NDA checklist. I'll come back to you by Thursday.

Grace""",
            "BodyType": "text",
            "Timestamp": utc(anchor - timedelta(days=6), 15, 30),
        },
    ]


def chats(anchor: date):
    neg = anchor + timedelta(days=7)
    golive = anchor + timedelta(days=10)
    last_week = anchor - timedelta(days=5)  # Wednesday of last week
    return [
        {
            "ChatId": "legal-chat-001",
            "ChatType": "Group",
            "ChatName": "Cognivault Nexus deal",
            "Members": ["marcus.hollowell", "tomas.aguilar", "radhika.sengupta"],
            "CreatedDateTime": utc(anchor - timedelta(days=13), 13, 0),
            "ChatMessages": [
                {
                    "ChatMessageId": "1",
                    "From": "tomas.aguilar",
                    "ContentType": "text",
                    "Content": "Our last vendor retired its model on 2 weeks' notice and we couldn't quote for a week. Can't happen again.",
                    "SentDateTime": utc(last_week, 15, 2),
                },
                {
                    "ChatMessageId": "2",
                    "From": "radhika.sengupta",
                    "ContentType": "text",
                    "Content": "Agreed. And we don't go to the table without owning the fine-tuned model.",
                    "SentDateTime": utc(last_week, 15, 6),
                },
                {
                    "ChatMessageId": "3",
                    "From": "marcus.hollowell",
                    "ContentType": "text",
                    "Content": "Understood. I'll review Cognivault's paper against the playbook as soon as it lands.",
                    "SentDateTime": utc(last_week, 15, 11),
                },
            ],
        },
        {
            "ChatId": "legal-chat-002",
            "ChatType": "OneOnOne",
            "Members": ["tomas.aguilar", "marcus.hollowell"],
            "CreatedDateTime": utc(anchor, 8, 45),
            "ChatMessages": [
                {
                    "ChatMessageId": "1",
                    "From": "tomas.aguilar",
                    "ContentType": "html",
                    "Content": (
                        "<p>Marcus, Cognivault sent over their contract (attached). "
                        f"We'd like to sign at the session with them on the {ordinal(neg)} so we can go live on the "
                        f"{ordinal(golive)}. Anything you need from me?</p><p>{{placeholder:1}}</p>"
                    ),
                    "SentDateTime": utc(anchor, 8, 47),
                    "Importance": "normal",
                    "Placeholders": [
                        {
                            "PlaceholderId": "1",
                            "Type": "attachment",
                            "HyperLinkContent": {
                                "DisplayText": AGREEMENT_FILE,
                                "FileId": AGREEMENT_FILE_ID,
                                "SharedLinkId": AGREEMENT_LINK_ID,
                                "FileOwner": "tomas.aguilar",
                            },
                        }
                    ],
                }
            ],
        },
    ]


def events(anchor: date):
    neg = anchor + timedelta(days=7)
    golive = anchor + timedelta(days=10)
    weekly_start = anchor - timedelta(days=28)
    return [
        {
            "EventId": "legal-event-001",
            "Sender": "radhika.sengupta",
            "Subject": "Cognivault Nexus: negotiation session with Cognivault counsel",
            "Body": (
                "Negotiation session on the Cognivault AI Vendor Agreement (Nexus underwriting platform). "
                "Cognivault's counsel, Priya Ramasubramanian, will join via the Teams link. "
                "This is a negotiation session, not a signing.\n\n"
                "Agenda:\n1. Verdantis position on Cognivault's draft (Marcus)\n"
                "2. Business priorities (Radhika, Tomás)\n3. Open points and next steps"
            ),
            "BodyType": "text",
            "StartDateTime": local(neg, 10, 0),
            "EndDateTime": local(neg, 12, 0),
            "TimeZone": EVENT_TZ,
            "Locations": ["Stamford HQ, Conference Room 4B"],
            "IsOnlineMeeting": True,
            "OnlineMeetingProvider": "teamsForBusiness",
            "ShowAs": "busy",
            "Importance": "high",
            "RequiredAttendees": [
                {"Email": "marcus.hollowell", "Operation": "Accepted"},
                {"Email": "tomas.aguilar", "Operation": "Accepted"},
            ],
            "OptionalAttendees": [{"Email": "olivia.park", "Operation": "TentativelyAccept"}],
        },
        {
            "EventId": "legal-event-002",
            "Sender": "tomas.aguilar",
            "Subject": "Nexus go-live readiness check",
            "Body": "Target go-live for Cognivault Nexus in Personal Auto and Homeowners underwriting. Readiness check: integration, model validation sign-off, contract status.",
            "BodyType": "text",
            "StartDateTime": local(golive, 9, 0),
            "EndDateTime": local(golive, 9, 45),
            "TimeZone": EVENT_TZ,
            "IsOnlineMeeting": True,
            "OnlineMeetingProvider": "teamsForBusiness",
            "ShowAs": "busy",
            "RequiredAttendees": [{"Email": "daniel.brandt", "Operation": "Accepted"}],
            "OptionalAttendees": [
                {"Email": "marcus.hollowell", "Operation": ""},
                {"Email": "radhika.sengupta", "Operation": "Accepted"},
            ],
        },
        {
            "EventId": "legal-event-003",
            "Sender": "eleanor.vance",
            "Subject": "Legal leadership weekly",
            "Body": "Weekly legal leadership sync: matter updates, staffing, outside counsel spend.",
            "BodyType": "text",
            "StartDateTime": local(weekly_start, 14, 0),
            "EndDateTime": local(weekly_start, 14, 30),
            "TimeZone": EVENT_TZ,
            "IsOnlineMeeting": True,
            "OnlineMeetingProvider": "teamsForBusiness",
            "ShowAs": "busy",
            "RequiredAttendees": [
                {"Email": "marcus.hollowell", "Operation": "Accepted"},
                {"Email": "nathan.osei", "Operation": "Accepted"},
            ],
            "Recurrence": {
                "RecurrencePattern": {"Type": "weekly", "Interval": 1, "DaysOfWeek": ["Monday"]},
                "RecurrenceRange": {"Type": "noEnd", "StartDate": weekly_start.isoformat()},
            },
        },
    ]


def files(anchor: date):
    return [
        {
            "FileId": AGREEMENT_FILE_ID,
            "FileName": f"Microsoft Teams Chat Files/{AGREEMENT_FILE}",
            "FileLocation": f"files/legal/{AGREEMENT_FILE}",
            "Owner": "tomas.aguilar",
            "DestinationType": "onedrive",
            "CreatedDate": utc(anchor, 8, 44),
            "LastModifiedDate": utc(anchor, 8, 46),
            "SharedWith": [{"Email": "marcus.hollowell", "PermissionLevel": "edit"}],
            "FileSharedLinks": [{"SharedLinkId": AGREEMENT_LINK_ID, "Type": "edit", "Scope": "users"}],
        }
    ]


def build_documents(files_dir):
    """Create binary files referenced by files(). Returns written paths."""
    from .legal_docs import write_agreement

    out = files_dir / "legal" / AGREEMENT_FILE
    out.parent.mkdir(parents=True, exist_ok=True)
    write_agreement(out)
    return [out]
