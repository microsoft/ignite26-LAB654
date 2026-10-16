"""Finance scenario tenant seed data (NVIDIA investment committee).

Source: src/scenarios/finance/scenario.md (LAB654_Finance_Track_OnePager.docx).
The one-pager asks for only one piece of M365 data:

- Trigger 1:1 chat, Jordan to Marcus, Friday 4:00 PM: "Committee wants a view
  on NVIDIA Monday. Should we add more? Bring a short memo."

Everything else (earnings, consensus, peer margins, credit ratings) comes from
the LSEG, FactSet and Moody's connectors, and the workbook and memo are created
during the lab, so there are no emails, events or files.

One lab account plays every domain, so the driver is Marcus Hollowell (defined
by the legal module, which is already in the tenant) instead of the one-pager's
Alex. The asset manager becomes the Verdantis Investment Office, which invests
the insurer's reserves. Jordan's surname is a placeholder.

ASK_DATE is the Friday of Jordan's message. It must be in the past for COEP.
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

from ..legal import MARCUS, TEAMS_ONLY, _user

ASK_DATE = date(2026, 10, 9)  # Friday; Monday's committee is ASK_DATE + 3

ET = ZoneInfo("America/New_York")

JORDAN = "jreyes"


def utc(hh: int, mm: int) -> str:
    local = datetime.combine(ASK_DATE, time(hh, mm), tzinfo=ET)
    return local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def users():
    return [
        _user(JORDAN, "Jordan", "Reyes", "Portfolio Manager", "Investment Office", TEAMS_ONLY),
    ]


def emails():
    return []


def chats():
    return [
        {
            "ChatId": "finance-chat-001",
            "ChatType": "OneOnOne",
            "Members": [JORDAN, MARCUS],
            "CreatedDateTime": utc(15, 59),
            "ChatMessages": [
                {
                    "ChatMessageId": "1",
                    "From": JORDAN,
                    "ContentType": "text",
                    "Content": "Committee wants a view on NVIDIA Monday. Should we add more? Bring a short memo.",
                    "SentDateTime": utc(16, 0),
                }
            ],
        }
    ]


def events():
    return []


def files():
    return []
