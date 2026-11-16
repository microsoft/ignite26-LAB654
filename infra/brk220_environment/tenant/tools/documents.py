"""Word documents for Megan's OneDrive: the Q3 QBR notes, the current order form (the contract being renewed) and
the renewal order form template the renewal-prep skill fills in. Built with python-docx so the content stays in
reviewable source."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.shared import Pt

COMMENT = "BRK220 demo seed. Fictitious data."


def _doc(title: str, author: str = "Megan Bowen") -> Document:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    doc.core_properties.author = author
    doc.core_properties.title = title
    doc.core_properties.comments = COMMENT
    doc.add_heading(title, level=0)
    return doc


def _bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        doc.add_paragraph(item, style="List Bullet")


def _table(doc: Document, rows: list[tuple[str, str]]) -> None:
    table = doc.add_table(rows=0, cols=2)
    table.style = "Light Grid Accent 1"
    for left, right in rows:
        cells = table.add_row().cells
        cells[0].text, cells[1].text = left, right


def stamp(path: Path, created: str, modified: str) -> Path:
    """Set the core created/modified dates; python-docx's default template carries 2013 dates otherwise."""
    from datetime import datetime

    doc = Document(path)
    doc.core_properties.created = datetime.fromisoformat(created.replace("Z", "+00:00"))
    doc.core_properties.modified = datetime.fromisoformat(modified.replace("Z", "+00:00"))
    doc.core_properties.last_modified_by = doc.core_properties.author
    doc.save(path)
    return path


def build_qbr_notes(path: Path) -> Path:
    doc = _doc("Contoso Ltd \u2013 Q3 QBR notes")
    doc.add_paragraph("Tuesday, September 29, 2026 \u00b7 Microsoft Teams \u00b7 Notes by Megan Bowen")
    doc.add_heading("Attendees", level=1)
    _bullets(doc, [
        "Contoso Ltd: Lidia Holloway (CIO, executive sponsor), Daniel Okafor (Head of Procurement, renewal buyer)",
        "Northwind Ltd: Megan Bowen (Account Executive), Isaiah Langer (Customer Success Manager)",
    ])
    doc.add_heading("Summary", level=1)
    _bullets(doc, [
        "Usage up 22% year over year. EU West carries about 60% of Contoso's traffic (Frankfurt workloads).",
        "Lidia is happy with the platform but needs identity work for the 2027 Entra conditional access rollout.",
        "Renewal is due December 31, 2026. Current contract: $2.4M a year.",
    ])
    doc.add_heading("Customer asks", level=1)
    _bullets(doc, [
        "SSO roadmap commitment, in writing, before renewal: SCIM provisioning and per-subsidiary conditional "
        "access for all 14 subsidiaries (Lidia).",
        "Support responsiveness: no P1 incident should sit without an owner (Lidia).",
    ])
    doc.add_heading("Commercial and competition", level=1)
    _bullets(doc, [
        "Contoso is price-sensitive given current market conditions: order volumes are down, energy costs are "
        "up, and their CFO has asked every vendor for flat or lower pricing in 2027.",
        "Competitor: Fabrikam quoted about 15% under Contoso's current price on a three-year term. Daniel has "
        "seen only the headline number; scope (EU data residency, P1 response) is unknown.",
        "The order form allows up to a 7% uplift at renewal. Daniel: \u201cSeven won't fly.\u201d",
        "Lidia doesn't want to migrate 14 subsidiaries, but slow P1 response is what would make her listen to "
        "Fabrikam.",
    ])
    doc.add_heading("Next steps", level=1)
    _bullets(doc, [
        "Megan: send renewal pricing options to Daniel in early October.",
        "Megan with Product: written SSO roadmap commitment for the renewal proposal.",
        "Isaiah: keep the monthly EU usage report going.",
    ])
    doc.save(path)
    return path


def build_order_form(path: Path) -> Path:
    doc = _doc("Order Form NW-OF-2025-0142", author="Alex Wilber")
    doc.add_paragraph("Under the Northwind Master Subscription Agreement between Northwind Ltd (\u201cNorthwind\u201d) "
                      "and Contoso Ltd (\u201cCustomer\u201d) dated December 16, 2024.")
    doc.add_heading("1. Subscription", level=1)
    _table(doc, [
        ("Service", "Northwind Platform, Enterprise edition"),
        ("Scope", "All 14 Contoso Ltd subsidiaries"),
        ("Regions", "EU West (Frankfurt) and US East"),
        ("Term", "January 1, 2025 to December 31, 2026 (24 months)"),
        ("Annual subscription fee", "$2,400,000, invoiced annually in advance, payable net 30"),
    ])
    doc.add_heading("2. Renewal", level=1)
    doc.add_paragraph("This Order Form renews for successive 12-month terms unless either party gives notice of "
                      "non-renewal at least 60 days before the end of the current term. Fees for a renewal term "
                      "may increase by up to 7% over the fees for the prior term.")
    doc.add_heading("3. Service levels", level=1)
    _bullets(doc, [
        "Monthly availability of 99.9%.",
        "P1 incidents: response within 1 hour, 24 hours a day, 7 days a week.",
        "Service credit of 5% of the monthly fee for each 0.1% of availability below the target, up to 25%.",
    ])
    doc.add_heading("4. Data residency and identity", level=1)
    _bullets(doc, [
        "Customer data for EU subsidiaries is stored and processed in EU West.",
        "SAML 2.0 single sign-on is included. SCIM provisioning is not included in this Order Form.",
    ])
    doc.add_heading("5. Signatures", level=1)
    _table(doc, [
        ("Northwind Ltd", "Alex Wilber, Regional Sales Director \u00b7 December 16, 2024"),
        ("Contoso Ltd", "Daniel Okafor, Head of Procurement \u00b7 December 16, 2024"),
    ])
    doc.save(path)
    return path


def build_template(path: Path) -> Path:
    doc = _doc("Northwind Renewal Order Form (template)", author="Alex Wilber")
    doc.add_paragraph("Replace every [bracketed] field. Keep section numbering. Mark the document DRAFT until Legal "
                      "has reviewed it.")
    doc.add_paragraph("Under the Northwind Master Subscription Agreement between Northwind Ltd (\u201cNorthwind\u201d) "
                      "and [Customer legal name] (\u201cCustomer\u201d) dated [MSA date]. This Order Form renews "
                      "Order Form [prior order form number].")
    doc.add_heading("1. Subscription", level=1)
    _table(doc, [
        ("Service", "[Service and edition]"),
        ("Scope", "[Entities and users covered]"),
        ("Regions", "[Regions]"),
        ("Renewal term", "[Start date] to [end date]"),
        ("Annual subscription fee", "[Fee], invoiced annually in advance, payable net 30"),
        ("Change from prior term", "[Uplift or discount, as a percentage and an amount]"),
    ])
    doc.add_heading("2. Renewal", level=1)
    doc.add_paragraph("[Carry over the renewal clause from the prior order form unless the proposal changed it.]")
    doc.add_heading("3. Service levels", level=1)
    doc.add_paragraph("[Carry over the service levels from the prior order form.]")
    doc.add_heading("4. Data residency and identity", level=1)
    doc.add_paragraph("[Carry over data residency and identity terms.]")
    doc.add_heading("5. Roadmap commitments", level=1)
    doc.add_paragraph("[Only capabilities and dates marked Committable in the Product Roadmap Confluence space, "
                      "using its approved wording. Leave this section out if there are none.]")
    doc.add_heading("6. Approvals", level=1)
    _bullets(doc, [
        "Any discount, or an uplift below the cap agreed in writing with the customer, needs Regional Sales "
        "Director approval before this Order Form is sent.",
        "Legal reviews every renewal Order Form before signature.",
    ])
    doc.add_heading("7. Signatures", level=1)
    _table(doc, [
        ("Northwind Ltd", "[Name, title, date]"),
        ("[Customer legal name]", "[Name, title, date]"),
    ])
    doc.save(path)
    return path
