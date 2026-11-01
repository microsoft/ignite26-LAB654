"""Productivity scenario tenant seed data (sales pitch prep, Lakeshore Retail).

Source: docs/scenarios/productivity/scenario.md section 5. Salesforce data lives
in the Test_Salesforce mock server, not here. This module seeds:

- Atul's pre-pitch email to Emil (Nanami is not cc'd: she has no email history)
- The pitch meeting (Fri Nov 20, 2026), busy blocks Nov 23-25 and out of office
  Nov 26-27 (Thanksgiving), so "next week" slots look real during Ignite week
- The recorded "Lakeshore Retail - Aurora pilot review" Teams meeting: a past event,
  an onlinemeetings item and its .vtt transcript (replaces Zoom)
- Test_Confluence pages in the "Zava Sales" space

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
    ("Atul Manohar", "Honestly I'm not sure. I've only seen the per-store number."),
    ("Atul Manohar", "And Nanami will want the all-in cost. She's joining the pitch, and she'll look at the total for 400 stores, not the sticker price."),
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


# --- Test_Confluence (space "Zava Sales") -------------------------------

SITE = "https://zava-online.atlassian.net"
SPACE = {
    "SpaceName": "Zava Sales",
    "SpaceKey": "VSALES",
    "SpaceId": "884213307",
    "SpaceURL": f"{SITE}/wiki/rest/api/space/VSALES",
    "SpaceDescription": "Zava retail sales playbooks: pricing and discount policy, competitive battlecards, "
                        "security and compliance answers for customers, and customer case studies.",
    "SpaceStatus": "current",
    "SpaceType": "global",
    "SpaceLabels": ["sales", "retail", "aurora", "pricing", "enablement"],
}

EVERYONE_ACL = {
    "principal": {
        "type": "everyone",
        "value": "EVERYONE",
        "identitySource": None,
        "identitySourceEnum": "azureActiveDirectory",
        "identityType": 3,
        "identitySourceProperties": None,
        "metadata": None,
        "displayName": None,
    },
    "ruleNode": None,
    "accessType": "grant",
    "transformedIdentity": None,
}


def _person(name: str, email: str) -> dict:
    return {
        "ExternalId": str(uuid.uuid5(uuid.NAMESPACE_URL, f"mailto:{email}")),
        "Email": email,
        "ExternalName": name,
        "PrincipalType": "user",
        "id": email,
    }


P_ZOE = ("Zoe Armstrong", "zoe@zava-online.com")
P_DEALDESK = ("Gerko Peterson", "gerko@zava-online.com")
P_SECURITY = ("Selma Pakarinen", "selma@zava-online.com")
P_MARKETING = ("Alice Pena", "alice@zava-online.com")

PRICING_POLICY = """<h1>Aurora Retail Pricing &amp; Discount Policy</h1>
<p><strong>Status:</strong> Current. Effective for all Aurora retail deals from September 1, 2026. Supersedes the 2025 Aurora retail pricing policy (archived).</p>
<h2>List price</h2>
<p>Aurora retail list price is <strong>$3,000 per store</strong>. This includes the in-store Aurora hub kit and 3-year support.</p>
<h2>Volume discounts and approvals</h2>
<table>
<tr><th>Discount off list</th><th>Eligibility</th><th>Approval</th></tr>
<tr><td>Up to 12%</td><td>250+ stores</td><td>None required</td></tr>
<tr><td>Over 12% and up to 15%</td><td>250+ stores</td><td>Zoe Armstrong, Director of Retail Sales</td></tr>
<tr><td>Over 15%</td><td>Any</td><td>VP Sales and Deal Desk</td></tr>
</table>
<p>Do not quote a discount that needs approval until it has been approved.</p>
<h2>Value-add items</h2>
<p>In-store installation and staff training are normally <strong>$300 per store</strong>. They can be bundled at no charge as value-add on deals of 250+ stores. Value-add items <strong>do not count as discount</strong> toward the tiers above.</p>
<h2>Worked example</h2>
<p>400 stores at 12% off: $2,640 per store, about <strong>$1.06M</strong> total, with installation and training bundled as value-add.</p>"""

BATTLECARD = """<h1>Competitive Battlecard: Boulder Innovations</h1>
<h2>Positioning</h2>
<p>Boulder Innovations leads with a low sticker price: about <strong>$2,400 per store</strong>, roughly 20% under Aurora's $3,000 list. The sticker price <strong>excludes</strong> installation and 3-year support, which Aurora includes or bundles.</p>
<h2>All-in cost per store (3 years)</h2>
<table>
<tr><th>Item</th><th>Boulder Innovations</th><th>Zava Aurora (12% volume discount)</th></tr>
<tr><td>Hub kit</td><td>$2,400</td><td>$2,640 (includes 3-year support)</td></tr>
<tr><td>In-store installation</td><td>about $350</td><td>Included (value-add)</td></tr>
<tr><td>3-year support</td><td>about $500</td><td>Included</td></tr>
<tr><td><strong>All-in per store</strong></td><td><strong>about $3,250</strong></td><td><strong>$2,640</strong></td></tr>
</table>
<p>For 400 stores, Aurora at 12% is about $1.06M all-in.</p>
<h2>How to win</h2>
<ul>
<li><strong>Don't lead with discount.</strong> Lead with all-in cost (TCO) and pilot results.</li>
<li>Bundle installation and staff training as value-add instead of going past the 12% tier.</li>
<li>Bring finance stakeholders the per-store and total all-in numbers.</li>
</ul>"""

SECURITY_FAQ = """<h1>Aurora Security &amp; Compliance FAQ</h1>
<h2>Certifications</h2>
<p>The Aurora cloud service is <strong>SOC 2 Type II</strong> certified. The current report is available to customers under NDA.</p>
<h2>Where is data stored?</h2>
<p>Aurora supports <strong>regional data residency</strong>. US customers' device and store data is stored in US data centers.</p>
<h2>Does Aurora capture customer data in store?</h2>
<p>No. Aurora hubs have <strong>no in-store cameras</strong> and do not collect shopper <strong>PII</strong>. Hubs report device status and anonymous demo-station usage only.</p>
<h2>Security review</h2>
<p>For rollouts over 100 stores, Zava offers a security review session with the customer's IT security team covering this FAQ, data residency and the rollout plan.</p>"""

CASE_STUDY = """<h1>Case Study: Wide World Importers 320-store rollout</h1>
<h2>Summary</h2>
<p>Wide World Importers rolled Aurora out to 320 stores after a 40-store pilot. Boulder Innovations was also shortlisted.</p>
<h2>Timeline</h2>
<ul>
<li>Pilot: 40 stores, 6 weeks</li>
<li>Security review with WWI IT: 2 weeks before signature</li>
<li>Rollout: 320 stores in 10 weeks, in three regional waves</li>
</ul>
<h2>Outcome</h2>
<p>Zava won on all-in cost: a 12% volume discount with installation and staff training bundled as value-add, and no discount above 12%. WWI reported higher smart-home bundle attach rates in rollout stores in the first quarter after launch.</p>"""

ARCHIVED_PRICING = """<h1>Aurora Retail Pricing Policy (2025)</h1>
<p><strong>ARCHIVED.</strong> Superseded by the current Aurora Retail Pricing &amp; Discount Policy. Do not use for new deals.</p>
<p>List price $3,200 per store. Volume discounts up to 18% at 200+ stores with regional sales manager approval.</p>"""

ONBOARDING = """<h1>Aurora Retail Partner Onboarding Checklist</h1>
<ul>
<li>Sign partner agreement and data processing addendum</li>
<li>Schedule store-staff training sessions</li>
<li>Confirm demo-station placement per store layout</li>
<li>Set up the partner dashboard accounts</li>
</ul>"""

QBR = """<h1>Retail Sales QBR Template</h1>
<p>Use this template for quarterly business reviews with retail partners: pipeline, wins and losses, pilot results, next-quarter plan and asks.</p>"""

PAGES = [
    # (id, title, html, labels, created, updated, author, editor, status, likes)
    ("884213411", "Aurora Retail Pricing & Discount Policy", PRICING_POLICY, ["pricing", "discount-policy", "aurora"],
     at(8, 24, 10, 5), at(9, 1, 9, 30), P_ZOE, P_DEALDESK, "current", 14),
    ("884213452", "Competitive Battlecard: Boulder Innovations", BATTLECARD, ["battlecard", "competitive", "boulder-innovations"],
     at(9, 8, 11, 20), at(10, 14, 16, 45), P_MARKETING, P_ZOE, "current", 22),
    ("884213487", "Aurora Security & Compliance FAQ", SECURITY_FAQ, ["security", "compliance", "faq"],
     at(7, 15, 13, 0), at(10, 6, 10, 10), P_SECURITY, P_SECURITY, "current", 9),
    ("884213523", "Case Study: Wide World Importers 320-store rollout", CASE_STUDY, ["case-study", "aurora"],
     at(9, 29, 15, 40), at(9, 30, 9, 15), P_MARKETING, P_MARKETING, "current", 11),
    ("884212190", "Aurora Retail Pricing Policy (2025)", ARCHIVED_PRICING, ["pricing", "archived"],
     at(1, 12, 9, 0, year=2025), at(9, 1, 9, 35), P_DEALDESK, P_DEALDESK, "archived", 3),
    ("884213566", "Aurora Retail Partner Onboarding Checklist", ONBOARDING, ["onboarding", "partners"],
     at(6, 3, 14, 0), at(8, 19, 11, 0), P_ZOE, P_ZOE, "current", 5),
    ("884213598", "Retail Sales QBR Template", QBR, ["template", "qbr"],
     at(5, 11, 10, 30), at(5, 11, 10, 30), P_ZOE, P_ZOE, "current", 2),
]


def _confluence_item(pid, title, html, labels, created, updated, author, editor, status, likes):
    slug = "+".join(title.replace("&", "%26").replace(":", "").split())
    authors = [_person(*author)] + ([_person(*editor)] if editor != author else [])
    return {
        "id": pid,
        "displayName": pid,
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
            "Id": pid,
            "Title": title,
            "Url": f"{SITE}/wiki/spaces/{SPACE['SpaceKey']}/pages/{pid}/{slug}",
            "Type": "page",
            "Status": status,
            "PageTree": SPACE["SpaceName"],
            "ItemPath": f"/{SPACE['SpaceName']}",
            "Labels": labels,
            "Likes": likes,
            "IconUrl": f"{SITE}/wiki/download/thumbnails/{SPACE['SpaceId']}/space-icon.png",
            **SPACE,
            "CreatedOn": created,
            "CreatedByEmail": author[1],
            "CreatedByName": _person(*author),
            "UpdatedOn": updated,
            "UpdatedByEmail": editor[1],
            "UpdatedByName": _person(*editor),
            "Authors": authors,
        },
        "content": {"parsedData": html, "type": "html", "annotation": None, "semanticContent": None},
    }


def confluencepages():
    return [_confluence_item(*p) for p in PAGES]
