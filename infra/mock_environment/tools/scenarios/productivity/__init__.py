"""Productivity scenario tenant seed data (Verdantis Aurora launch, vendor slip).

Source: docs/scenarios/productivity/scenario.md
(Ignite_Lab_Productivity_Module_Smartsheet_Notion_Intranet.docx).

The doc asks the M365 tenant for:

- Lab users: the launch lead, Sam (Retail Ops lead) and Riley (Contoso
  Retail). The unnamed "Aurora core team" is not seeded.
- Riley's email to the launch lead asking for the POS kit ETA (doc 6.1). The
  doc gives only its gist; the wording here is authored.
- Verdantis Hub intranet pages (doc 6.3), seeded as COEP intranetwebsite items
  so the synced Enterprise Websites connector has content to ground on.

Notion data is served by the mock MCP server, not the tenant.

One lab account plays every domain, so the launch lead is Marcus Hollowell
(defined by the legal module, which is already in the tenant) instead of the
doc's Avery, and Zava becomes Verdantis. The doc's Jordan is renamed Riley so
it doesn't clash with finance's Jordan.

Dates: COEP rejects future timestamps, so the email and page stamps sit
before STORY_DATE. Nothing in the tenant names a story date: the Notion mock
computes those from the current week, and Riley's email refers only to "store
staff training". Surnames, titles, decoy page paths and the page author
identity are placeholders; see the README's assumptions.

The Hub is served by our own mock site (mock_mcp_servers/verdantis_hub), not
hub.verdantis.com, which belongs to an unrelated real company.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import date, datetime, time, timedelta, timezone
from html import escape
from zoneinfo import ZoneInfo

from ..legal import MARCUS, TEAMS_ONLY
from ..legal import _user as _verdantis_user

STORY_DATE = date(2026, 10, 12)  # reference for seeded timestamps only; story dates are relative

ET = ZoneInfo("America/New_York")  # Verdantis is in Stamford, CT

SAM, RILEY = "spatel", "rblake"

HUB = "https://mock-verdantis-hub.yellowsand-9530f5dc.eastus.azurecontainerapps.io"
HUB_AUTHOR = ("Verdantis Hub Content Team", "hubcontent@verdantis.com")


def utc(day_offset: int, hh: int, mm: int) -> str:
    local = datetime.combine(STORY_DATE + timedelta(days=day_offset), time(hh, mm), tzinfo=ET)
    return local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def users():
    return [
        _verdantis_user(SAM, "Sam", "Patel", "Retail Operations Lead", "Retail Operations", TEAMS_ONLY),
        {
            "MailNickName": RILEY,
            "DisplayName": "Riley Blake",
            "FirstName": "Riley",
            "LastName": "Blake",
            "JobTitle": "Partner Account Manager",
            "Department": "Partner Operations",
            "CompanyName": "Contoso Retail",
            "UsageLocation": "US",
            "Licenses": TEAMS_ONLY,
        },
    ]


RILEY_EMAIL = """<p>Hi Marcus,</p>
<p>Quick check on the Verdantis Aurora POS kits for our stores. What's the current ETA for delivery to Contoso Retail?</p>
<p>The stores need the complete kits (signage included) on site before our store staff training, so the teams can set up and train on the real displays.</p>
<p>Can you confirm the dates, or let me know if anything has changed?</p>
<p>Thanks,<br>Riley<br>Contoso Retail</p>"""


def emails():
    return [
        {
            "EmailId": "productivity-email-001",
            "EmailAction": "Send",
            "Sender": RILEY,
            "ToRecipients": [{"Recipient": MARCUS}],
            "Subject": "Aurora POS kits \u2013 ETA for our stores?",
            "Body": RILEY_EMAIL,
            "BodyType": "html",
            "Timestamp": utc(0, 7, 40),
        }
    ]


def chats():
    return []


def events():
    return []


def files():
    return []


# --- Verdantis Hub intranet pages (COEP intranetwebsite) -------------------------

def _page_html(crumbs, title, updated: date, body: str) -> str:
    items = "".join(f'<li><a href="{HUB}{href}">{escape(name)}</a></li>' for name, href in crumbs)
    nav = f'<nav aria-label="Breadcrumb"><ol><li><a href="{HUB}/">Home</a></li>{items}<li>{escape(title)}</li></ol></nav>'
    stamp = f"<p><em>Last updated: {updated:%B} {updated.day}, {updated.year}</em></p>"
    return f"{nav}\n<h1>{escape(title)}</h1>\n{stamp}\n{body.strip()}"


PAGES = [
    {
        "path": "/retail/launch-playbook",
        "crumbs": [("Retail", "/retail")],
        "title": "Retail Partner Launch Playbook",
        "description": (
            "The current rules every Verdantis launch team follows when shipping launch materials to retail partner stores. "
            "It covers POS kit timing against store staff training, when split shipments are allowed and who approves them, "
            "and how quickly partners must hear about changes."
        ),
        "keywords": ["Retail", "Launch", "POS kits", "Partners", "Split shipments"],
        "created": -220,
        "modified": -27,
        "body": """
<p>This playbook applies to every Verdantis product launch that ships point-of-sale (POS) kits, signage or other launch materials to retail partner stores. It replaces the <a href="/retail/launch-playbook-2025">2025 playbook</a>, which is archived and no longer in force.</p>
<h2>Who this is for</h2>
<p>Launch program managers, Retail Operations, and anyone who commits dates to a retail partner. If you are unsure whether a rule applies, ask Retail Operations before you promise anything to a partner.</p>
<h2>POS kit timing</h2>
<p>Every POS kit wave must be in partner stores at least <strong>3 days before store staff training</strong>. A wave counts as delivered only when everything planned for that wave, including signage, is on site at the partner's stores.</p>
<table><thead><tr><th>Milestone</th><th>Rule</th></tr></thead><tbody>
<tr><td>Store staff training</td><td>Date agreed with the partner; treat it as fixed once confirmed.</td></tr>
<tr><td>Each POS kit wave in stores</td><td>At least 3 days before store staff training.</td></tr>
<tr><td>Partner informed of any change</td><td>Within 1 business day of the change.</td></tr>
</tbody></table>
<h2>Split shipments</h2>
<p>Split shipments are allowed with approval from the Retail Ops lead (Sam Patel). Each split must be logged in the Launch Decision Log before it ships, with the reason, the waves and their dates. Every wave still has to meet the 3-day rule.</p>
<blockquote><strong>Note:</strong> A split shipment is a change to a partner commitment, so the partner must also be told within 1 business day.</blockquote>
<h2>Changes to partner commitments</h2>
<p>Any change to a date or deliverable promised to a partner must be communicated to the partner within <strong>1 business day</strong>, following the <a href="/comms/partner-updates">Partner Communication Guidelines</a>. Copy Retail Operations on the update.</p>
<h2>Vendors</h2>
<p>Print and signage must come from an approved vendor. See <a href="/procurement/approved-vendors/print">Approved Vendors – Print</a> for the primary and backup vendors and their rush terms.</p>
<h2>Frequently asked questions</h2>
<dl>
<dt>Can we ship kits without signage and send the signage later?</dt><dd>Only as an approved split shipment, and only if every wave, including the signage wave, is in stores at least 3 days before staff training.</dd>
<dt>Who approves a split shipment?</dt><dd>The Retail Ops lead, Sam Patel.</dd>
<dt>Where do decisions get recorded?</dt><dd>In the Launch Decision Log for the launch.</dd>
</dl>
<h2>Contacts</h2>
<p>Retail Operations: Sam Patel, Retail Operations Lead.</p>
""",
    },
    {
        "path": "/procurement/approved-vendors/print",
        "crumbs": [("Procurement", "/procurement"), ("Approved Vendors", "/procurement/approved-vendors")],
        "title": "Approved Vendors \u2013 Print",
        "description": (
            "The approved print vendors for brochures, in-store signage and other retail collateral. "
            "It names the primary and backup vendors, the backup vendor's rush turnaround and surcharge, "
            "and when Procurement approval is needed."
        ),
        "keywords": ["Procurement", "Vendors", "Print", "Signage", "Brochures"],
        "created": -300,
        "modified": -60,
        "body": """
<p>Use only the vendors on this page for printed launch materials: brochures, in-store signage, shelf talkers and packaging inserts. Using an unapproved vendor requires an exception from Procurement.</p>
<h2>Approved print vendors</h2>
<table><thead><tr><th>Vendor</th><th>Role</th><th>Terms</th></tr></thead><tbody>
<tr><td>Northwind Print</td><td>Primary</td><td>Standard production schedule per purchase order.</td></tr>
<tr><td>Litware Print</td><td>Backup</td><td>3-business-day rush available, +15% surcharge. Procurement approval is needed for a PO change.</td></tr>
</tbody></table>
<h2>When to use the backup vendor</h2>
<p>Use the primary vendor unless it cannot meet a committed date. Before switching, check whether the primary vendor can split or expedite the order, because switching vendors needs a PO change and adds the rush surcharge.</p>
<h2>How to request a PO change</h2>
<ol>
<li>Confirm the quantities, artwork files and delivery addresses with the launch team.</li>
<li>Get a written quote and delivery date from the vendor.</li>
<li>Submit the PO change to Procurement with the reason and the quote. Procurement approves or rejects it.</li>
<li>Record the change in the launch's decision log.</li>
</ol>
<blockquote><strong>Tip:</strong> Rush turnaround is counted in business days from approved artwork, not from the PO change request.</blockquote>
<h2>Quality and delivery</h2>
<p>All vendors ship to the addresses on the PO and provide tracking. Report damaged or incorrect deliveries to Procurement within 2 business days so the vendor can reprint.</p>
<h2>Contacts</h2>
<p>Procurement: procurement@verdantis.com. Include the launch name and PO number in the subject line.</p>
""",
    },
    {
        "path": "/comms/partner-updates",
        "crumbs": [("Communications", "/comms")],
        "title": "Partner Communication Guidelines",
        "description": (
            "How to write updates to retail partners when plans change. It sets out the five-part structure every partner "
            "update should follow, the 1-business-day timing rule, and tone and review tips so partners get clear, actionable messages."
        ),
        "keywords": ["Communications", "Partners", "Updates", "Email"],
        "created": -250,
        "modified": -45,
        "body": """
<p>Partners plan their stores, staff and promotions around the dates we give them. When something changes, they need to hear it from us quickly and clearly. These guidelines apply to email and chat updates sent to any retail partner.</p>
<h2>Timing</h2>
<p>Send the update within <strong>1 business day</strong> of the change, even if some details are still being confirmed. Say what is still open and when you will follow up.</p>
<h2>Structure</h2>
<p>Every partner update uses these five parts, in this order:</p>
<ol>
<li><strong>What changed</strong>: one or two sentences, in plain language.</li>
<li><strong>Impact on you</strong>: what it means for the partner's stores and teams.</li>
<li><strong>New dates</strong>: the revised dates, listed clearly.</li>
<li><strong>What we need from you</strong>: any action or confirmation, with a deadline.</li>
<li><strong>Contact</strong>: who to reach with questions.</li>
</ol>
<h2>Tone</h2>
<ul>
<li>Lead with the facts; don't bury the change under background.</li>
<li>Take ownership. Don't blame a vendor or another team by name.</li>
<li>Be specific: dates, quantities and locations, not "soon" or "shortly".</li>
<li>Keep it short. Link to details rather than pasting them.</li>
</ul>
<h2>Who to include</h2>
<p>Send to the partner's main contact and copy the internal launch core team. For changes to POS kits or signage, also copy Retail Operations.</p>
<h2>Example subject lines</h2>
<ul>
<li>"Updated delivery dates for launch materials"</li>
<li>"Change to your POS kit shipment"</li>
</ul>
<blockquote><strong>Note:</strong> If the change needs an internal approval, say so and give the date you expect a decision.</blockquote>
<h2>Before you send</h2>
<p>Check the dates against the launch tracker, make sure every action you ask of the partner has a deadline, and have a second person on the launch team read the update if it changes a store-facing date.</p>
""",
    },
    {
        "path": "/retail/launch-playbook-2025",
        "crumbs": [("Retail", "/retail"), ("Archive", "/retail/archive")],
        "title": "Retail Partner Launch Playbook (2025, archived)",
        "description": (
            "The archived 2025 version of the retail partner launch playbook, kept for reference only. "
            "It has been superseded by the current Retail Partner Launch Playbook, and its timing and shipment rules "
            "no longer apply to current launches."
        ),
        "keywords": ["Retail", "Launch", "Archive", "2025"],
        "created": -650,
        "modified": -400,
        "body": """
<blockquote><strong>Archived.</strong> This page is superseded by the current <a href="/retail/launch-playbook">Retail Partner Launch Playbook</a> and is kept for reference only. Do not use these rules for current launches.</blockquote>
<p>This playbook applied to Verdantis product launches in 2025 that shipped launch materials to retail partner stores.</p>
<h2>POS kit timing</h2>
<p>POS kits must arrive in partner stores at least <strong>5 days</strong> before store staff training.</p>
<h2>Split shipments</h2>
<p>Split shipments are not permitted. Each partner receives one complete POS kit shipment.</p>
<h2>Changes to partner commitments</h2>
<p>Changes must be communicated to the partner within 2 business days by the launch program manager.</p>
<h2>Vendors</h2>
<p>All printed materials were produced by Northwind Print under the 2025 master agreement.</p>
<h2>Checklist</h2>
<ul>
<li>Confirm training dates with each partner at least 6 weeks before launch.</li>
<li>Lock artwork 4 weeks before the kit ship date.</li>
<li>Confirm delivery addresses with partner store operations.</li>
<li>Send tracking details to each partner when kits ship.</li>
</ul>
<h2>Frequently asked questions</h2>
<dl>
<dt>Can we ship signage separately?</dt><dd>No. Under this playbook, kits ship complete or not at all.</dd>
<dt>Who signs off on kit contents?</dt><dd>The launch program manager.</dd>
</dl>
<p>For current rules, including the 3-day timing rule and approved split shipments, see the <a href="/retail/launch-playbook">current playbook</a>.</p>
<h2>Why this was replaced</h2>
<p>The 2025 rules proved too rigid when vendors slipped. The current playbook shortens the lead time and allows approved split shipments with a logged decision.</p>
""",
    },
    {
        "path": "/customer-service/holiday-returns",
        "crumbs": [("Customer Service", "/customer-service")],
        "title": "Holiday Returns Policy",
        "description": (
            "The extended return window for Verdantis products bought during the holiday season. "
            "It explains which purchases qualify, the return deadline, the condition products must be in, "
            "and how store and online customers return items."
        ),
        "keywords": ["Customer Service", "Returns", "Holiday"],
        "created": -380,
        "modified": -30,
        "body": """
<p>To make holiday gifting easier, Verdantis extends the standard 30-day return window for purchases made during the holiday season. This policy applies to Verdantis products bought directly from Verdantis and from participating retail partners.</p>
<h2>Eligible purchases</h2>
<p>Products bought between <strong>November 1 and December 31</strong> can be returned until <strong>January 31</strong> of the following year with proof of purchase.</p>
<h2>Condition of returned products</h2>
<ul>
<li>Opened devices must include all accessories, cables and packaging.</li>
<li>Devices must be reset to factory settings and removed from the customer's Verdantis account.</li>
<li>Products with physical damage not caused by a defect are not eligible.</li>
</ul>
<h2>How to return</h2>
<table><thead><tr><th>Bought from</th><th>Return to</th></tr></thead><tbody>
<tr><td>Verdantis online store</td><td>Start a return from the order page; a prepaid label is emailed.</td></tr>
<tr><td>Retail partner</td><td>The partner store where it was bought, under the partner's process.</td></tr>
</tbody></table>
<h2>Refunds</h2>
<p>Refunds go back to the original payment method within 10 business days of receiving the return. Gift receipts are refunded as store credit.</p>
<h2>Frequently asked questions</h2>
<dl>
<dt>Does this extend the warranty?</dt><dd>No. The product warranty is unchanged.</dd>
<dt>Can a customer exchange instead of return?</dt><dd>Yes, for the same product in a different color, subject to stock.</dd>
</dl>
<p>Questions: contact Customer Service through the support portal.</p>
<h2>For store and support staff</h2>
<p>Check the purchase date on the receipt or order before accepting a return under this policy. Outside the holiday window, the standard 30-day return policy applies.</p>
""",
    },
    {
        "path": "/products/verdantis-lumen/launch-faq",
        "crumbs": [("Products", "/products"), ("Verdantis Lumen", "/products/verdantis-lumen")],
        "title": "Verdantis Lumen Launch FAQ",
        "description": (
            "Frequently asked questions about the Verdantis Lumen smart lighting launch for internal teams. "
            "It covers who owns the launch, where its tracker and materials live, and how to raise questions. "
            "It does not cover the Verdantis Aurora launch."
        ),
        "keywords": ["Verdantis Lumen", "Launch", "FAQ"],
        "created": -120,
        "modified": -20,
        "body": """
<p>Verdantis Lumen is our smart lighting line. This FAQ answers common internal questions about its launch. For other launches, check that product's own pages.</p>
<h2>Who owns the Verdantis Lumen launch?</h2>
<p>The Lumen launch team in Product Marketing owns the launch plan, partner communication and launch event.</p>
<h2>Where is the launch tracker?</h2>
<p>In Notion, under "Verdantis Lumen Launch Tracker". Ask the Lumen launch team for access.</p>
<h2>Which retail partners are carrying Lumen?</h2>
<p>Lumen launches online first. Retail partners will be confirmed later; until then, don't commit dates or materials to any partner.</p>
<h2>Are there POS kits for Lumen?</h2>
<p>Not for the online launch. If retail is added, POS kits will follow the current <a href="/retail/launch-playbook">Retail Partner Launch Playbook</a>.</p>
<h2>Where are the product images and messaging?</h2>
<p>In the Lumen brand folder, linked from the launch tracker. Use only approved assets.</p>
<h2>Who do I ask about pricing?</h2>
<p>The Commercial team. Don't share pricing outside Verdantis before the launch date.</p>
<h2>How do I raise a question that isn't answered here?</h2>
<p>Post it in the Lumen launch channel, or contact the Lumen launch team directly. We update this FAQ weekly during the launch period.</p>
<h2>Is there a launch event?</h2>
<p>An online launch stream is planned. Details will be posted here when confirmed.</p>
<h2>Can I share Lumen details with partners or press?</h2>
<p>Not yet. All external communication about Lumen goes through the Lumen launch team and PR until the launch date.</p>
<h2>Where do Lumen launch decisions get recorded?</h2>
<p>In the Lumen launch team's own decision log, linked from the Lumen launch tracker.</p>
""",
    },
    {
        "path": "/finance/travel-expense-policy",
        "crumbs": [("Finance", "/finance")],
        "title": "Travel & Expense Policy",
        "description": (
            "The rules for booking business travel and claiming business expenses at Verdantis. "
            "It covers booking channels, approval requirements, travel classes, meals and lodging limits, "
            "and the deadline and receipts needed to submit an expense claim."
        ),
        "keywords": ["Finance", "Travel", "Expenses"],
        "created": -500,
        "modified": -90,
        "body": """
<p>This policy applies to all Verdantis employees and contractors who travel or spend money on Verdantis's behalf. It helps you spend responsibly and get reimbursed quickly.</p>
<h2>Booking travel</h2>
<ul>
<li>Book flights, hotels and rental cars through the corporate travel tool.</li>
<li>Get manager approval before booking any trip.</li>
<li>International travel also needs approval from your department head.</li>
</ul>
<h2>Travel class</h2>
<table><thead><tr><th>Trip</th><th>Class</th></tr></thead><tbody>
<tr><td>Flights under 6 hours</td><td>Economy</td></tr>
<tr><td>Flights of 6 hours or more</td><td>Premium economy</td></tr>
<tr><td>Rail</td><td>Standard class</td></tr>
</tbody></table>
<h2>Lodging and meals</h2>
<p>Use hotels from the corporate travel tool where available. Meal costs should be reasonable for the location; alcohol is not reimbursed except at approved client events.</p>
<h2>Submitting expenses</h2>
<p>Submit expense claims within <strong>30 days</strong> with itemized receipts. Claims older than 90 days are not reimbursed without Finance approval.</p>
<h2>Non-reimbursable expenses</h2>
<ul>
<li>Personal entertainment and upgrades you choose for yourself.</li>
<li>Traffic and parking fines.</li>
<li>Expenses for people who aren't on Verdantis business.</li>
</ul>
<h2>Frequently asked questions</h2>
<dl>
<dt>What if I lose a receipt?</dt><dd>Submit a missing-receipt declaration with the claim. Repeated missing receipts are reviewed by Finance.</dd>
<dt>Who approves my expense claim?</dt><dd>Your manager, then Finance for amounts over the department limit.</dd>
<dt>Can I book travel outside the travel tool?</dt><dd>Only if the tool has no suitable option. Keep the booking confirmation and note the reason on your claim.</dd>
</dl>
""",
    },
]


def _performer():
    name, email = HUB_AUTHOR
    return {
        "ExternalId": str(uuid.uuid5(uuid.NAMESPACE_URL, f"mailto:{email}")),
        "Email": email,
        "ExternalName": name,
        "PrincipalType": "user",
        "id": email,
        "identitySourceProperties": {"email": email},
        "identitySource": "azureActiveDirectory",
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


def _intranet_item(i: int, p: dict) -> dict:
    url = HUB + p["path"]
    created, modified = utc(p["created"], 10, 0), utc(p["modified"], 14, 30)
    updated = STORY_DATE + timedelta(days=p["modified"])
    return {
        "id": hashlib.sha512(url.encode("utf-16-le")).hexdigest().upper(),
        "displayName": url,
        "contentDomainCategoryName": "knowledgeBase",
        "accessControlList": [EVERYONE_ACL],
        "activityList": [
            {"ActivityType": "created", "ActivityPerformer": _performer(), "ActivityDateTime": created, "id": f"activity-hub{i:02d}-created"},
            {"ActivityType": "modified", "ActivityPerformer": _performer(), "ActivityDateTime": modified, "id": f"activity-hub{i:02d}-1"},
        ],
        "isContainer": False,
        "containerId": None,
        "itemVersion": None,
        "skipAssociatedItems": False,
        "isAssociatedItem": False,
        "UniversalAccessControlBlock": None,
        "contentEnrichmentData": None,
        "associatedItemsMetadata": None,
        "shouldHashId": False,
        "hashedId": None,
        "dataSourceResponse": None,
        "content": {
            "parsedData": _page_html(p["crumbs"], p["title"], updated, p["body"]),
            "type": "html",
            "annotation": None,
            "semanticContent": None,
        },
        "properties": {
            "FileType": "html",
            "URL": url,
            "Title": p["title"],
            "IconUrl": "/assets/icons/verdantis-hub.svg",
            "Keywords": p["keywords"],
            "Authors": [HUB_AUTHOR[0]],
            "LastModifiedBy": HUB_AUTHOR[0],
            "CreatedDateTime": created,
            "LastModifiedDateTime": modified,
            "Description": p["description"],
        },
    }


def hub_pages():
    """Page data for the hosted Verdantis Hub site (verdantis_hub/export_pages.py)."""
    out = []
    for p in PAGES:
        updated = STORY_DATE + timedelta(days=p["modified"])
        out.append({
            "path": p["path"],
            "title": p["title"],
            "crumbs": [[name, href] for name, href in p["crumbs"]],
            "description": p["description"],
            "keywords": p["keywords"],
            "updated": updated.isoformat(),
            "html": _page_html(p["crumbs"], p["title"], updated, p["body"]),
        })
    return out


def intranetpages():
    return [_intranet_item(i, p) for i, p in enumerate(PAGES, 1)]
