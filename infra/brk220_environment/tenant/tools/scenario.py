"""BRK220 tenant seed: Microsoft 365 content for the Contoso Ltd renewal (scenario.md, "Microsoft 365 seed").

Megan Bowen (Northwind Ltd) is the Copilot user. This module seeds what Copilot reads from Microsoft 365:

- Q3 QBR with Contoso (Tue Sep 29): a recorded Teams meeting with a transcript. Contoso is price-sensitive
  (CFO wants flat vendor pricing; order volumes down), Fabrikam quoted about 15% under the current price, and
  Lidia asks for a written SSO roadmap commitment.
- Megan's QBR notes (Word, OneDrive), the current order form (the "older contract") and the renewal order form
  template that the skill fills in.
- Renewal pricing thread with Daniel (Oct 6-8): Megan won't match Fabrikam; they agree on Oct 8 to cap the
  renewal uplift at 5% and Daniel asks for a formal proposal with the SSO commitment in writing.
- Teams group chat "Contoso escalation" (Wed Nov 4): the CIO escalated EU latency (symptoms match INC-40211 and
  INC-40302 in the Rovo mock), and Fabrikam has raised its offer to 20% off plus free migration.

Jira, Confluence and Salesforce data live in the mock MCP servers, not here.

Date rule: COEP rejects future timestamps, so every item is dated on or before EVIDENCE_CUTOFF. Move dates with the
constants below if the tenant is built later.
"""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
CET = ZoneInfo("Europe/Berlin")
EVIDENCE_CUTOFF = datetime(2026, 11, 6, tzinfo=timezone.utc)

TEAMS_ONLY = ["Microsoft Teams Enterprise", "Office 365 E5 (no Teams)"]
COPILOT_USER = ["Microsoft 365 Copilot", *TEAMS_ONLY]

MEGAN, ALEX, ISAIAH, ARJUN, ROSA = "megan", "alex", "isaiah", "arjun", "rosa"
LIDIA, DANIEL = "lidia", "daniel"


def at(month: int, day: int, hh: int, mm: int, tz=ET, year: int = 2026) -> str:
    local = datetime(year, month, day, hh, mm, tzinfo=tz)
    return local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _user(nick, first, last, title, dept, company, city, country, licenses, usage="US"):
    return {
        "MailNickName": nick,
        "DisplayName": f"{first} {last}",
        "FirstName": first,
        "LastName": last,
        "JobTitle": title,
        "Department": dept,
        "CompanyName": company,
        "UsageLocation": usage,
        "OfficeLocation": f"{city}, {country}",
        "Licenses": licenses,
    }


def _northwind(nick, first, last, title, dept, licenses=TEAMS_ONLY, city="New York", usage="US"):
    return _user(nick, first, last, title, dept, "Northwind Ltd", city, "USA" if usage == "US" else "Ireland",
                 licenses, usage)


def _contoso(nick, first, last, title, dept):
    return _user(nick, first, last, title, dept, "Contoso Ltd", "Munich", "Germany", TEAMS_ONLY, "DE")


def users():
    megan = _northwind(MEGAN, "Megan", "Bowen", "Account Executive", "Sales", COPILOT_USER)
    megan["Manager"] = ALEX
    return [
        megan,
        _northwind(ALEX, "Alex", "Wilber", "Regional Sales Director", "Sales"),
        _northwind(ISAIAH, "Isaiah", "Langer", "Customer Success Manager", "Customer Success"),
        _northwind(ARJUN, "Arjun", "Kumar", "Senior Support Engineer, EU Platform", "Support", city="Dublin",
                   usage="IE"),
        _northwind(ROSA, "Rosa", "Diaz", "Support Engineer", "Support"),
        _contoso(LIDIA, "Lidia", "Holloway", "Chief Information Officer", "IT"),
        _contoso(DANIEL, "Daniel", "Okafor", "Head of Procurement", "Procurement"),
    ]


# --- Renewal pricing thread (Oct 6-8) ----------------------------------------------------------------------------

def _html(*paragraphs: str) -> str:
    return "".join(f"<p>{p}</p>" for p in paragraphs)


SUBJECT = "Contoso renewal \u2013 pricing options"
EMAIL_IDS = ("brk220-email-001", "brk220-email-002", "brk220-email-003", "brk220-email-004")


def emails():
    e1, e2, e3, e4 = EMAIL_IDS
    return [
        {
            "EmailId": e1, "EmailAction": "Send", "Sender": MEGAN,
            "ToRecipients": [{"Recipient": DANIEL}], "CcRecipients": [{"Recipient": ISAIAH}],
            "Subject": SUBJECT, "BodyType": "html", "Timestamp": at(10, 6, 10, 12),
            "Body": _html(
                "Hi Daniel,",
                "Thanks again for the candid conversation at the QBR. As promised, here is where I've landed on "
                "pricing for the FY27 renewal.",
                "Your current order form allows an uplift of up to 7% at renewal. Given the market conditions you "
                "described, I'm proposing to <strong>cap the uplift at 5%</strong> for the renewal term. Everything "
                "else stays as it is today: all 14 subsidiaries, EU data residency and our 1-hour P1 response.",
                "I'm also working with our Product team on the SSO roadmap commitment Lidia asked for, so we can put "
                "it in writing in the formal proposal.",
                "Best,<br>Megan",
                "Megan Bowen<br>Account Executive, Northwind Ltd"),
        },
        {
            "EmailId": e2, "EmailAction": "Reply", "ReferenceEmailId": e1, "Sender": DANIEL,
            "ToRecipients": [{"Recipient": MEGAN}], "CcRecipients": [{"Recipient": ISAIAH}],
            "Subject": f"RE: {SUBJECT}", "BodyType": "html", "Timestamp": at(10, 7, 10, 40, tz=CET),
            "Body": _html(
                "Hi Megan,",
                "Thanks for this. I have to be honest: Fabrikam's offer is about 15% below what we pay you today, "
                "and our CFO has seen it. Any increase is a hard sell while our order volumes are down.",
                "Is there more room here?",
                "Daniel"),
        },
        {
            "EmailId": e3, "EmailAction": "Reply", "ReferenceEmailId": e2, "Sender": MEGAN,
            "ToRecipients": [{"Recipient": DANIEL}], "CcRecipients": [{"Recipient": ISAIAH}],
            "Subject": f"RE: {SUBJECT}", "BodyType": "html", "Timestamp": at(10, 8, 9, 5),
            "Body": _html(
                "Hi Daniel,",
                "I understand the pressure. I can't match a discount, and I don't think a like-for-like comparison "
                "gets you there: Fabrikam's headline number doesn't include EU data residency or a 1-hour P1 "
                "response, and moving 14 subsidiaries is a long migration.",
                "What I can do is hold the cap at <strong>5%</strong>, below the 7% in the contract, and put the "
                "SSO roadmap commitment in writing in the proposal. Can we agree on that?",
                "Best,<br>Megan"),
        },
        {
            "EmailId": e4, "EmailAction": "Reply", "ReferenceEmailId": e3, "Sender": DANIEL,
            "ToRecipients": [{"Recipient": MEGAN}], "CcRecipients": [{"Recipient": ISAIAH}],
            "Subject": f"RE: {SUBJECT}", "BodyType": "html", "Timestamp": at(10, 8, 18, 30, tz=CET),
            "Body": _html(
                "Megan,",
                "Agreed: we can work with a <strong>5% cap</strong> on the renewal uplift. Please send the formal "
                "renewal proposal before the end of November, with the SSO roadmap commitment in writing, and I'll "
                "take it to our CFO.",
                "Daniel"),
        },
    ]


# --- Teams chat "Contoso escalation" (Wed Nov 4) -----------------------------------------------------------------

def _msg(i, sender, text, sent):
    return {"ChatMessageId": str(i), "From": sender, "ContentType": "text", "Content": text, "SentDateTime": sent}


def chats():
    return [
        {
            "ChatId": "brk220-chat-escalation",
            "ChatType": "Group",
            "ChatName": "Contoso escalation",
            "Members": [ISAIAH, MEGAN, ALEX],
            "CreatedDateTime": at(11, 4, 9, 57),
            "ChatMessages": [
                _msg(1, ISAIAH,
                     "Heads-up: Lidia (Contoso's CIO) called me this morning to escalate latency in the EU region. "
                     "Their Frankfurt workloads are seeing API calls take 4 to 6 seconds during business hours, and "
                     "their morning export batch is failing with gateway timeouts. It's been going on for about "
                     "a week.", at(11, 4, 9, 58)),
                _msg(2, ISAIAH,
                     "She was blunt: if this isn't owned and fixed before the renewal, she'll back Daniel on "
                     "looking at Fabrikam. Fabrikam went back to them last week with 20% off and free migration.",
                     at(11, 4, 10, 1)),
                _msg(3, ALEX, "Six weeks to renewal. Megan, who's on this?", at(11, 4, 10, 6)),
                _msg(4, MEGAN,
                     "Not sure yet. I'll check what Support has open, get owners on it and pull the renewal plan "
                     "together.", at(11, 4, 10, 9)),
                _msg(5, ALEX,
                     "Good. Don't chase Fabrikam's number. Remember Adatum: we matched a discount in the last week "
                     "with P1s sitting unassigned and lost them anyway. Hold the cap you agreed with Daniel; "
                     "anything below it needs my approval.", at(11, 4, 10, 12)),
                _msg(6, ISAIAH,
                     "I'll ask Contoso's ops team to file the export timeouts as their own ticket so Support can "
                     "triage both.", at(11, 4, 10, 15)),
            ],
        },
    ]


# --- Q3 QBR (Tue Sep 29): Teams meeting with transcript ----------------------------------------------------------

QBR_EVENT = "brk220-event-qbr"
QBR_START, QBR_END = at(9, 29, 9, 0), at(9, 29, 9, 45)
TRANSCRIPT_FILE = "transcripts/contoso-q3-qbr.vtt"

_CUES = [
    ("Megan Bowen", "Thanks for joining, everyone. Today: Q3 usage, support, your 2027 plans and the renewal timeline."),
    ("Isaiah Langer", "Usage is up 22% year over year. EU West now carries about 60% of your traffic, mostly the Frankfurt workloads."),
    ("Lidia Holloway", "The platform has been solid this year. My one big ask is identity. We're rolling out Entra conditional access across all 14 subsidiaries in the first half of next year."),
    ("Lidia Holloway", "For that we need SCIM provisioning and per-subsidiary conditional access from Northwind. Before we renew, I need a roadmap commitment for both, in writing."),
    ("Megan Bowen", "Understood. I'll take that to our Product team and come back with dates we can commit to."),
    ("Daniel Okafor", "On the renewal, I'll be direct. Our CFO has asked every vendor for flat or lower pricing next year. Market conditions are tough: our order volumes are down and energy costs are up."),
    ("Daniel Okafor", "And Fabrikam came in last month. They quoted about 15% under what we pay you today, on a three-year term."),
    ("Megan Bowen", "Is that like for like? Does it include EU data residency and a one-hour P1 response?"),
    ("Daniel Okafor", "I'm not sure. I've only seen the headline number. But our CFO has seen it too."),
    ("Lidia Holloway", "For me, switching isn't attractive. Migrating 14 subsidiaries is a year of pain. But I need the platform to stay fast, and I need the SSO piece delivered."),
    ("Daniel Okafor", "Your contract allows up to a 7% uplift. Seven won't fly. Anything above flat needs a good story for our CFO."),
    ("Megan Bowen", "I won't promise a discount today. Let me come back in early October with options. What matters most to you: price, or the SSO commitment and service?"),
    ("Daniel Okafor", "Both. Price gets it past my CFO. Lidia's SSO commitment gets it past IT."),
    ("Lidia Holloway", "And support responsiveness. If P1s sit without an owner, that's what will make me listen to Fabrikam."),
    ("Megan Bowen", "Noted. Next steps: I'll send pricing options early October and work on the SSO commitment, and Isaiah will keep the monthly EU usage report coming."),
    ("Daniel Okafor", "Sounds good. Thanks, Megan."),
]


def _ts(seconds: int) -> str:
    return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}.000"


def transcripts():
    blocks, t = ["WEBVTT"], 4
    for i, (speaker, text) in enumerate(_CUES, 1):
        dur = max(8, len(text) // 6)
        blocks.append(f"{i}\n{_ts(t)} --> {_ts(t + dur)}\n<v {speaker}>{text}</v>")
        t += dur + 30
    return {TRANSCRIPT_FILE: "\n\n".join(blocks) + "\n"}


def events():
    return [
        {
            "EventId": QBR_EVENT,
            "Subject": "Contoso Ltd \u2013 Q3 QBR",
            "Body": "Quarterly business review with Contoso Ltd: Q3 usage, support, 2027 plans and the renewal "
                    "timeline.",
            "StartDateTime": QBR_START,
            "EndDateTime": QBR_END,
            "Sender": MEGAN,
            "TimeZone": "UTC",
            "ShowAs": "busy",
            "RequiredAttendees": [{"Email": a, "Operation": "Accepted"} for a in (ISAIAH, LIDIA, DANIEL)],
            "IsOnlineMeeting": True,
            "OnlineMeetingProvider": "teamsForBusiness",
        },
    ]


def onlinemeetings():
    return [
        {
            "OnlineMeetingId": "brk220-meeting-qbr",
            "OnlineMeetingType": "Event",
            "EventId": QBR_EVENT,
            "StartDateTime": QBR_START,
            "EndDateTime": QBR_END,
            "Owner": MEGAN,
            "Participants": [MEGAN, ISAIAH, LIDIA, DANIEL],
            "Transcripts": [{"LanguageTag": "en", "TranscriptFile": TRANSCRIPT_FILE}],
        }
    ]


# --- OneDrive documents ------------------------------------------------------------------------------------------

QBR_NOTES = "Contoso Ltd - Q3 QBR notes.docx"
ORDER_FORM = "Contoso Ltd - Order Form NW-OF-2025-0142.docx"
TEMPLATE = "Northwind Renewal Order Form template.docx"
DOCS = {
    QBR_NOTES: ("Contoso", at(9, 30, 9, 20), at(9, 30, 9, 41)),
    ORDER_FORM: ("Contoso", at(12, 16, 14, 0, year=2024), at(12, 16, 14, 5, year=2024)),
    TEMPLATE: ("Templates", at(3, 2, 11, 0), at(3, 2, 11, 30)),
}


def files():
    return [
        {
            "FileId": f"brk220-file-{i:03d}",
            "FileName": f"{folder}/{name}",
            "FileLocation": f"files/brk220/{name}",
            "Owner": MEGAN,
            "CreatedDate": created,
            "LastModifiedDate": modified,
            "DestinationType": "onedrive",
        }
        for i, (name, (folder, created, modified)) in enumerate(DOCS.items(), 1)
    ]


def build_documents(files_dir):
    from documents import build_order_form, build_qbr_notes, build_template, stamp

    out = files_dir / "brk220"
    out.mkdir(parents=True, exist_ok=True)
    built = {QBR_NOTES: build_qbr_notes, ORDER_FORM: build_order_form, TEMPLATE: build_template}
    return [stamp(fn(out / name), DOCS[name][1], DOCS[name][2]) for name, fn in built.items()]


def das_users():
    return [MEGAN]


def all_timestamps():
    """Every seeded timestamp, for the evidence cutoff check in build_tenant.py."""
    stamps = [e["Timestamp"] for e in emails()]
    stamps += [m["SentDateTime"] for c in chats() for m in c["ChatMessages"]]
    stamps += [QBR_START, QBR_END] + [d[2] for d in DOCS.values()]
    return stamps
