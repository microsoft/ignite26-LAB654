"""Productivity scenario tenant seed data (sales pitch prep, Lakeshore Retail).

Source: docs/scenarios/productivity/scenario.md section 5. Salesforce data lives
in the Salesforce_Lab mock server, not here. This module seeds:

- Atul's pre-pitch email to Emil (Nanami is not cc'd: she has no email history)
- The pitch meeting (Fri Nov 20, 2026), busy blocks Nov 23-25 and out of office
  Nov 26-27 (Thanksgiving), so "next week" slots look real during Ignite week
- The recorded "Lakeshore Retail - Aurora pilot review" Teams meeting: a past event,
  an onlinemeetings item and its .vtt transcript

Date rule: seeded evidence is dated on or before Fri Oct 30, 2026 (the tenant is
ingested once, around Nov 1). Upcoming items are on or after Fri Nov 20, after
the last lab day (Nov 19).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ..legal import ET, EMIL, TEAMS_ONLY, _user

ATUL, JAHIDI, NANAMI, ZOE = "atul", "jahidi", "nanami", "zoe"


def at(month: int, day: int, hh: int, mm: int, year: int = 2026) -> str:
    """Eastern wall-clock time as a UTC timestamp."""
    local = datetime(year, month, day, hh, mm, tzinfo=ET)
    return local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ext_user(nick, first, last, title, dept, company, city, state):
    """A user from another company. Tenant users so they can attend Teams meetings."""
    return {
        "MailNickName": nick,
        "DisplayName": f"{first} {last}",
        "FirstName": first,
        "LastName": last,
        "JobTitle": title,
        "Department": dept,
        "CompanyName": company,
        "UsageLocation": "US",
        "OfficeLocation": f"{city}, {state}",
        "Licenses": TEAMS_ONLY,
    }


def lakeshore(nick, first, last, title, dept):
    return ext_user(nick, first, last, title, dept, "Lakeshore Retail", "Minneapolis", "MN")


def users():
    return [
        lakeshore(ATUL, "Atul", "Manohar", "Director of Store Operations", "Store Operations"),
        lakeshore(JAHIDI, "Jahidi", "Juma", "IT Security Lead", "Information Technology"),
        lakeshore(NANAMI, "Nanami", "Nakayama", "Chief Financial Officer", "Finance"),
        _user(ZOE, "Zoe", "Armstrong", "Director of Retail Sales", "Sales", TEAMS_ONLY),
    ]


ATUL_EMAIL = """<p>Hi Emil,</p>
<p>Quick heads-up before our expansion pitch on November 20.</p>
<p>Our CFO, Nanami Nakayama, will join the call. She wants to see the all-in cost of rolling Aurora out to all 400 stores, not just the per-hub price, so please come ready with that number.</p>
<p>Jahidi Juma from IT has also asked for Zava's security documentation before anything goes to 400 stores. He'll want to walk through it with your team beforehand.</p>
<p>The pilot stores have been happy so far. Looking forward to it.</p>
<p>Thanks,<br>Atul</p>
<p>Atul Manohar<br>Director of Store Operations, Lakeshore Retail</p>"""


def emails():
    return [
        {
            "EmailId": "prod-email-001",
            "EmailAction": "Send",
            "Sender": ATUL,
            "ToRecipients": [{"Recipient": EMIL}],
            "CcRecipients": [],
            "Subject": "Aurora expansion pitch \u2013 Nanami joining, security docs",
            "Body": ATUL_EMAIL,
            "BodyType": "html",
            "Timestamp": at(10, 28, 9, 40),
        }
    ]


def chats():
    return []


PILOT_REVIEW_EVENT = "prod-event-pilot-review"


def _event(eid, subject, start, end, body, attendees=(), show_as="busy", online=False):
    e = {
        "EventId": eid,
        "Subject": subject,
        "Body": body,
        "StartDateTime": start,
        "EndDateTime": end,
        "Sender": EMIL,
        "TimeZone": "UTC",
        "ShowAs": show_as,
        "RequiredAttendees": [{"Email": a, "Operation": "Accepted"} for a in attendees],
    }
    if online:
        e |= {"IsOnlineMeeting": True, "OnlineMeetingProvider": "teamsForBusiness"}
    return e


def events():
    return [
        _event(
            PILOT_REVIEW_EVENT,
            "Lakeshore Retail \u2013 Aurora pilot review",
            at(10, 22, 14, 0), at(10, 22, 14, 15),
            "Review of the six-week, 50-store Aurora pilot with Lakeshore Retail and next steps toward the 400-store rollout.",
            [ATUL, JAHIDI], online=True,
        ),
        _event(
            "prod-event-pitch",
            "Lakeshore Retail \u2013 Aurora expansion pitch",
            at(11, 20, 10, 0), at(11, 20, 11, 0),
            "Aurora 400-store rollout proposal for Lakeshore Retail.<br>Attendees: Atul Manohar (Director of Store Operations), "
            "Nanami Nakayama (CFO), Jahidi Juma (IT Security Lead).",
            [ATUL, NANAMI, JAHIDI], online=True,
        ),
        _event("prod-event-busy-1", "Q4 retail forecast review", at(11, 23, 9, 0), at(11, 23, 11, 0),
               "Quarterly forecast review with the retail sales team.", [ZOE], online=True),
        _event("prod-event-busy-2", "Aurora launch event planning", at(11, 23, 14, 0), at(11, 23, 15, 30),
               "Run-of-show for the Dec 8 Aurora launch event."),
        _event("prod-event-busy-3", "Retail sales pipeline sync", at(11, 24, 10, 0), at(11, 24, 11, 0),
               "Weekly pipeline review.", [ZOE], online=True),
        _event("prod-event-busy-4", "Partner enablement workshop", at(11, 24, 13, 0), at(11, 24, 16, 0),
               "Aurora partner enablement session (in person)."),
        _event("prod-event-busy-5", "1:1 with Zoe", at(11, 25, 11, 0), at(11, 25, 11, 30),
               "Weekly 1:1.", [ZOE], online=True),
        _event("prod-event-ooo", "Out of office \u2013 Thanksgiving", at(11, 26, 0, 0), at(11, 28, 0, 0),
               "Out of office for Thanksgiving.", show_as="outOfOffice"),
    ]


def files():
    return []


# --- Recorded pilot review call (Teams meeting + transcript) -------------------

TRANSCRIPT_FILE = "transcripts/lakeshore-pilot-review.vtt"

_CUES = [
    ("Emil Vanggaard", "Thanks for making time, Atul, Jahidi. I'd like to walk through how the pilot went and talk about what the full rollout could look like."),
    ("Atul Manohar", "Sure. Overall the stores have been really positive. Staff picked it up faster than we expected."),
    ("Emil Vanggaard", "Good to hear. On our side, the headline number is attach rate. Across the 50 pilot stores we're seeing a 9% attach-rate lift on smart-home bundles compared with the control stores."),
    ("Atul Manohar", "That matches what our store managers are telling me. The demo stations especially are pulling people in."),
    ("Emil Vanggaard", "So the proposal for next month is to take Aurora to all 400 stores ahead of the holiday season."),
    ("Atul Manohar", "That's where I need to be straight with you. We've had Boulder Innovations in as well, and they quoted about 20% under your list price."),
    ("Atul Manohar", "If you can get close to that we could sign this quarter. I'd rather stay with Aurora, the pilot has gone well, but price is going to come up."),
    ("Emil Vanggaard", "Understood. Is that 20% on the hub alone, or does it include install and support?"),
    ("Atul Manohar", "Honestly I'm not sure. I've only seen the per-store number, about $2,400."),
    ("Emil Vanggaard", "That's in line with what we've seen from Boulder at other retailers. The $2,400 is the hub only. Once their install and support are added, it usually lands around $3,250 per store all-in."),
    ("Emil Vanggaard", "So rather than match the 20%, here's what I can put forward: we hold the discount to 12%, that's $2,640 per store against our $3,000 list, and we bundle install at no extra cost."),
    ("Atul Manohar", "That's a better conversation than the sticker price. And Nanami will want the all-in cost. She's joining the pitch, and she'll look at the total for 400 stores, not the sticker price."),
    ("Emil Vanggaard", "That's helpful. I'll bring an all-in, per-store and total view for Nanami."),
    ("Jahidi Juma", "From the IT side, one thing before we go any further. We need a security review before the 400-store rollout. The pilot was a small footprint, so we let it through on a lighter check."),
    ("Jahidi Juma", "For 400 stores I need to see your security documentation, where the data is stored, and confirm nothing captures customer PII in store."),
    ("Emil Vanggaard", "Absolutely. We have a security and compliance FAQ, and I can set up a session with our team to walk through it with you."),
    ("Jahidi Juma", "That works. As long as it happens before anything is signed for the full rollout."),
    ("Atul Manohar", "One more thing from the stores: the reconnect issue we saw a couple of times. I'll send details separately, but it's not a blocker for this conversation."),
    ("Emil Vanggaard", "Noted. So next steps: I'll set up the security review with Jahidi, and I'll come to the pitch with the all-in cost for Nanami."),
    ("Atul Manohar", "Sounds good. Thanks, Emil."),
    ("Jahidi Juma", "Thanks."),
]


def _ts(seconds: int) -> str:
    return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}.000"


def transcripts():
    """{package-relative path: WebVTT text} for the onlinemeetings transcripts."""
    blocks, t = ["WEBVTT"], 4
    for i, (speaker, text) in enumerate(_CUES, 1):
        dur = max(8, len(text) // 6)
        blocks.append(f"{i}\n{_ts(t)} --> {_ts(t + dur)}\n<v {speaker}>{text}</v>")
        t += dur + 25  # pauses: the call runs about 10 minutes
    return {TRANSCRIPT_FILE: "\n\n".join(blocks) + "\n"}


def onlinemeetings():
    return [
        {
            "OnlineMeetingId": "prod-meeting-pilot-review",
            "OnlineMeetingType": "Event",
            "EventId": PILOT_REVIEW_EVENT,
            "StartDateTime": at(10, 22, 14, 0),
            "EndDateTime": at(10, 22, 14, 15),
            "Owner": EMIL,
            "Participants": [EMIL, ATUL, JAHIDI],
            "Transcripts": [{"LanguageTag": "en", "TranscriptFile": TRANSCRIPT_FILE}],
        }
    ]
