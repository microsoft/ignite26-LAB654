"""Bring-your-own-app (Zava Expense) tenant seed data.

Email bodies come from the provided receipt .eml files (receipt_emails/). Dates follow the lab calendar: Emil's Seattle trip runs
Mon Oct 26 - Thu Oct 29, 2026, with the airfare booked Oct 19 and the submission
reminder on Oct 30.

Receipt senders are tenant users so the emails pass schema checks; their display
names are the merchant names. Hannes Niemi (manager) and Ebere Ibeabuchi (Finance
Operations) are Zava users referenced by the expense mock.
"""

from __future__ import annotations

from pathlib import Path

from ..legal import EMIL, TEAMS_ONLY, _user
from ..productivity import at, ext_user

HANNES, EBERE = "hannes", "ebere"
ALASKA, YELLOWCAB, CANLIS, DTF, WESTIN, UBER, EXPENSE = (
    "alaskareceipts", "yellowcabreceipts", "canlisreservations", "dintaifungreceipts",
    "westinfolio", "uberreceipts", "zavaexpense",
)


def _vendor(nick, name, city, state):
    u = ext_user(nick, name, "Receipts", "Receipts", "Billing", name, city, state)
    u["DisplayName"] = name
    return u


def users():
    expense = _user(EXPENSE, "Zava", "Expense", "Expense notifications", "Finance", TEAMS_ONLY)
    expense["DisplayName"] = "Zava Expense"
    return [
        _user(HANNES, "Hannes", "Niemi", "Vice President, Product", "Product", TEAMS_ONLY),
        _user(EBERE, "Ebere", "Ibeabuchi", "Finance Operations Lead", "Finance", TEAMS_ONLY),
        expense,
        _vendor(ALASKA, "Alaska Airlines", "Seattle", "WA"),
        _vendor(YELLOWCAB, "Seattle Yellow Cab", "Seattle", "WA"),
        _vendor(CANLIS, "Canlis", "Seattle", "WA"),
        _vendor(DTF, "Din Tai Fung", "Seattle", "WA"),
        _vendor(WESTIN, "The Westin Seattle", "Seattle", "WA"),
        _vendor(UBER, "Uber Receipts", "San Francisco", "CA"),
    ]


BODIES = Path(__file__).with_name("receipt_emails")

# (sender, subject, body file, Eastern send time). Bodies are the HTML from the
# provided receipt .eml files, stored in receipt_emails/.
RECEIPTS = [
    (ALASKA, "Your receipt: Seattle (SEA) round trip, confirmation KXQ4TZ", "1.html", at(10, 19, 18, 12)),
    (YELLOWCAB, "Seattle Yellow Cab — trip receipt", "2.html", at(10, 26, 16, 48)),
    (CANLIS, "Your receipt from Canlis — party of 5", "3.html", at(10, 27, 23, 55)),
    (DTF, "Your Din Tai Fung receipt", "4.html", at(10, 28, 22, 10)),
    (WESTIN, "Your folio from The Westin Seattle", "5.html", at(10, 29, 9, 30)),
    (UBER, "Your Thursday morning trip with Uber", "6.html", at(10, 29, 10, 25)),
    (EXPENSE, "Reminder: submit your Seattle trip expenses by Friday, November 20", "7.html", at(10, 30, 8, 0)),
]


def emails():
    return [
        {
            "EmailId": f"exp-email-{i:03d}-v2",
            "EmailAction": "Send",
            "Sender": sender,
            "ToRecipients": [{"Recipient": EMIL}],
            "CcRecipients": [],
            "Subject": subject,
            "Body": (BODIES / body).read_text(encoding="utf-8").strip(),
            "BodyType": "html",
            "Timestamp": ts,
        }
        for i, (sender, subject, body, ts) in enumerate(RECEIPTS, 1)
    ]


def chats():
    return []


def events():
    return []


def files():
    return []
