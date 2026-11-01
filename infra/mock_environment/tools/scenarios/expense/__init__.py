"""Bring-your-own-app (Zava Expense) tenant seed data.

Source: the expense trial's "seattle_trip" receipt emails, with dates fixed to the lab calendar: Emil's Seattle trip runs
Mon Oct 26 - Thu Oct 29, 2026, with the airfare booked Oct 19 and the submission
reminder on Oct 30.

Receipt senders are tenant users so the emails pass schema checks; their display
names are the merchant names. Hannes Niemi (manager) and Ebere Ibeabuchi (Finance
Operations) are Zava users referenced by the expense mock.
"""

from __future__ import annotations

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


D0, D1, D2, D3 = "October 26", "October 27", "October 28", "October 29"

RECEIPTS = [
    (ALASKA, "Your receipt: Seattle (SEA) round trip, confirmation KXQ4TZ",
     f"Passenger: Emil Vanggaard. JFK–SEA {D0}, SEA–JFK {D3}. Economy. Total charged to card ending 4417: $486.40.",
     at(10, 19, 18, 12)),
    (YELLOWCAB, "Seattle Yellow Cab — trip receipt",
     f"SEA airport to The Westin Seattle, {D0}. Fare $48.75, tip $10.00. Total $58.75.",
     at(10, 26, 16, 48)),
    (CANLIS, "Your receipt from Canlis — party of 5",
     f"Dinner for 5 on {D1}. Food $392.00, beverages $64.00, tax $46.00, gratuity $38.00. Total $540.00.",
     at(10, 27, 23, 55)),
    (DTF, "Your Din Tai Fung receipt",
     f"Table for 1 on {D2}. Total $48.20.",
     at(10, 28, 22, 10)),
    (WESTIN, "Your folio from The Westin Seattle",
     f"Guest: Emil Vanggaard. Arrive {D0}, depart {D3}. Room rate: {D0} $239.00, {D1} $239.00, {D2} $389.00 "
     "(city-wide convention rate). Total $867.00.",
     at(10, 29, 9, 30)),
    (UBER, "Your Thursday morning trip with Uber",
     f"The Westin Seattle to SEA airport, {D3}. Total $52.30.",
     at(10, 29, 10, 25)),
    (EXPENSE, "Reminder: submit your Seattle trip expenses by Friday, November 20",
     f"Hi Emil, you have 8 unreported card charges from October 5 to {D3}. Please submit them in Zava "
     "Expense by Friday, November 20.",
     at(10, 30, 8, 0)),
]


def emails():
    return [
        {
            "EmailId": f"exp-email-{i:03d}",
            "EmailAction": "Send",
            "Sender": sender,
            "ToRecipients": [{"Recipient": EMIL}],
            "CcRecipients": [],
            "Subject": subject,
            "Body": f"<p>{body}</p>",
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
