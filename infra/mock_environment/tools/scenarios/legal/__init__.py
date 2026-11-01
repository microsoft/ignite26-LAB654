"""Legal scenario tenant seed data (Verdantis x Cognivault).

Source: the "legal v1 seed kit" (see docs/scenarios/legal/seed_kit.md). Only
what the kit asks to load into Outlook and Teams goes into the tenant:

- Radhika's business-priorities email to Marcus, cc Tomás (lab date - 14 days)
- Group chat "Cognivault deal" with 3 messages (lab date - 6 days, a Tuesday)
- Trigger 1:1 chat, Tomás to Marcus (lab date, 8:07 AM ET)

The kit's documents (agreement, exhibits, playbook) live only in iManage, so
they're under mock_mcp_servers/imanage/seed_files, not in the tenant. The kit
needs no calendar items.

LAB_DATE is the Monday of Tomás's trigger chat. Every tenant item is dated on
or before it, so it must be before the tenant is ingested. NEGOTIATION_DATE
(a Thursday) and go-live / contract effective date (NEGOTIATION_DATE + 3, a
Sunday) are still to come, so they must be after the last lab day.
The iManage documents and the scenario docs contain the same dates, so don't
edit these by hand: run redate.py in this folder, which rewrites all of them.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

CONTENT = Path(__file__).resolve().parent / "content"

LAB_DATE = date(2026, 10, 26)
NEGOTIATION_DATE = date(2026, 12, 10)
GO_LIVE_DATE = NEGOTIATION_DATE + timedelta(days=3)

ET = ZoneInfo("America/New_York")  # Verdantis is in Stamford, CT

TEAMS_ONLY = ["Microsoft Teams Enterprise", "Office 365 E5 (no Teams)"]
COPILOT_USER = ["Microsoft 365 Copilot", *TEAMS_ONLY]


def utc(days: int, hh: int, mm: int) -> str:
    """Eastern wall-clock time on LAB_DATE + days, as a UTC timestamp."""
    local = datetime.combine(LAB_DATE + timedelta(days=days), time(hh, mm), tzinfo=ET)
    return local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ordinal(d: date) -> str:
    n = d.day
    return f"{n}{'th' if 11 <= n <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def _user(nick, first, last, title, dept, licenses):
    return {
        "MailNickName": nick,
        "DisplayName": f"{first} {last}",
        "FirstName": first,
        "LastName": last,
        "JobTitle": title,
        "Department": dept,
        "CompanyName": "Verdantis Technologies, Inc.",
        "UsageLocation": "US",
        "OfficeLocation": "Stamford, CT",
        "Address": {
            "Street": "200 Harborview Drive, Suite 1400",
            "City": "Stamford",
            "State": "CT",
            "PostalCode": "06902",
            "Country": "USA",
        },
        "Licenses": licenses,
    }


# Aliases match the kit's .eml addresses (mhollowell@, rsengupta@, taguilar@).
MARCUS, RADHIKA, TOMAS = "mhollowell", "rsengupta", "taguilar"


def users():
    return [
        _user(MARCUS, "Marcus", "Hollowell", "Associate General Counsel, Technology Transactions",
              "Legal", COPILOT_USER),
        _user(RADHIKA, "Radhika", "Sengupta", "SVP, Strategic Procurement & Vendor Management",
              "Procurement", TEAMS_ONLY),
        _user(TOMAS, "Tomás", "Aguilar", "Chief Underwriting Officer", "Underwriting", TEAMS_ONLY),
    ]


def emails():
    return [
        {
            "EmailId": "legal-email-001",
            "EmailAction": "Send",
            "Sender": RADHIKA,
            "ToRecipients": [{"Recipient": MARCUS}],
            "CcRecipients": [{"Recipient": TOMAS}],
            "Subject": "Cognivault Nexus \u2013 Business Requirements & Negotiation Priorities",
            "Body": (CONTENT / "radhika_email_body.html").read_text(encoding="utf-8").strip(),
            "BodyType": "html",
            "Timestamp": utc(-14, 9, 12),
        }
    ]


def _msg(i, sender, text, sent):
    return {"ChatMessageId": str(i), "From": sender, "ContentType": "text", "Content": text, "SentDateTime": sent}


def chats():
    return [
        {
            "ChatId": "legal-chat-001",
            "ChatType": "Group",
            "ChatName": "Cognivault deal",
            "Members": [TOMAS, RADHIKA, MARCUS],
            "CreatedDateTime": utc(-6, 10, 13),
            "ChatMessages": [
                _msg(1, TOMAS,
                     "Quick one on Cognivault. Our last vendor retired its model on 2 weeks' notice and we "
                     "couldn't quote for a week. Can't happen again.",
                     utc(-6, 10, 14)),
                _msg(2, RADHIKA,
                     "Agreed. And we don't go to the table without owning the fine-tuned model.",
                     utc(-6, 10, 20)),
                _msg(3, MARCUS,
                     "Understood. Their paper came in on Friday and it's in the matter. I'll review it against "
                     f"the playbook before the session on the {ordinal(NEGOTIATION_DATE)}.",
                     utc(-6, 10, 31)),
            ],
        },
        {
            "ChatId": "legal-chat-002",
            "ChatType": "OneOnOne",
            "Members": [TOMAS, MARCUS],
            "CreatedDateTime": utc(0, 8, 6),
            "ChatMessages": [
                _msg(1, TOMAS,
                     "Morning Marcus. Have you had a chance to look at Cognivault's contract? We'd like to sign "
                     f"at the session with them on the {ordinal(NEGOTIATION_DATE)} so we can go live on the "
                     f"{ordinal(GO_LIVE_DATE)}. Anything you need from me?",
                     utc(0, 8, 7)),
            ],
        },
    ]


def events():
    return []


def files():
    return []
