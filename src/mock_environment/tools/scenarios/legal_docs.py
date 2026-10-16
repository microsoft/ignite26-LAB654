"""Synthetic stand-in for the Cognivault AI Vendor Agreement v4.2 (vendor first draft).

The scenario's source agreement is an HLAB (Harvey LAB) file that isn't in this
repo. This generates a stand-in whose terms match the scenario brief
("What's wrong with their draft"): Cognivault owns models fine-tuned on
customer data, 15 days' notice of model changes, a 6-month-fees liability cap,
and no audit / bias-testing / regulator-cooperation rights. Replace with the
HLAB file if it becomes available.
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

TITLE = "COGNIVAULT AI VENDOR AGREEMENT"
VERSION = "Version 4.2 | Cognivault standard form | Vendor draft for discussion"

SECTIONS: list[tuple[str, list[str]]] = [
    ("1. Definitions", [
        "1.1 \"Customer Data\" means data submitted by or on behalf of Customer to the Platform, including policy, claims and underwriting data.",
        "1.2 \"Platform\" means Cognivault Nexus, Cognivault's AI underwriting platform, including the Models, APIs, dashboards and Documentation.",
        "1.3 \"Model\" means any machine learning model made available through the Platform, including any version, update or replacement.",
        "1.4 \"Derived Model\" means any Model, weights, parameters, embeddings or other artifact that is trained, fine-tuned or otherwise improved using Customer Data.",
        "1.5 \"Decision\" means a single underwriting recommendation (eligibility, tier or price) returned by the Platform in response to an API call.",
        "1.6 \"Fees\" means the fees set out in Exhibit B.",
    ]),
    ("2. Services", [
        "2.1 Cognivault will make the Platform available to Customer during the Term for Customer's internal underwriting of personal auto and homeowners insurance policies, up to the volume set out in Exhibit B.",
        "2.2 Cognivault will provide the Platform in accordance with the service levels in Exhibit A.",
        "2.3 Customer is responsible for all underwriting decisions it makes, whether or not it relies on any Decision.",
    ]),
    ("3. Models and model changes", [
        "3.1 Cognivault may modify, update, replace or retire any Model at any time upon fifteen (15) days' prior notice to Customer, which may be given by email or through the Platform dashboard.",
        "3.2 Cognivault is not required to obtain Customer's consent to any Model change and is not required to maintain any retired Model.",
        "3.3 Cognivault may make emergency changes to any Model without prior notice where Cognivault determines it is necessary to protect the Platform.",
    ]),
    ("4. Customer Data", [
        "4.1 As between the parties, Customer owns Customer Data.",
        "4.2 Customer grants Cognivault a worldwide, royalty-free licence to use Customer Data to provide the Platform and to train, fine-tune and improve Cognivault's Models and services, including for other customers, provided such data is used in de-identified or aggregated form.",
        "4.3 Customer represents that it has all rights and consents needed to provide Customer Data to Cognivault.",
    ]),
    ("5. Intellectual property", [
        "5.1 Cognivault and its licensors own all right, title and interest in and to the Platform, the Models and all Derived Models, including all improvements, regardless of whether they were developed using Customer Data.",
        "5.2 Customer receives a non-exclusive, non-transferable right to use Decisions and Platform outputs for its internal business purposes during the Term.",
        "5.3 Nothing in this Agreement transfers ownership of any Derived Model to Customer.",
    ]),
    ("6. Fees and payment", [
        "6.1 Customer will pay the Fees set out in Exhibit B annually in advance.",
        "6.2 Fees are non-cancellable and non-refundable except as expressly stated in this Agreement.",
    ]),
    ("7. Security and compliance", [
        "7.1 Cognivault will maintain the security measures described in Exhibit C.",
        "7.2 Upon written request, no more than once per year, Cognivault will provide Customer with a copy of its most recent SOC 2 Type II report. This is Customer's sole means of verifying Cognivault's compliance with this Agreement.",
        "7.3 Model documentation, testing results and methodology are Cognivault Confidential Information and will not be provided to Customer or any third party.",
    ]),
    ("8. Confidentiality", [
        "8.1 Each party will protect the other party's Confidential Information using at least reasonable care and will use it only to perform under this Agreement.",
        "8.2 A party may disclose Confidential Information where required by law, after giving the other party prompt notice where legally permitted.",
    ]),
    ("9. Warranties and disclaimers", [
        "9.1 Cognivault warrants that the Platform will perform materially in accordance with the Documentation.",
        "9.2 EXCEPT AS EXPRESSLY STATED, THE PLATFORM, MODELS AND DECISIONS ARE PROVIDED \"AS IS\". COGNIVAULT DOES NOT WARRANT THAT ANY DECISION WILL BE ACCURATE, FAIR, UNBIASED OR COMPLIANT WITH ANY LAW OR REGULATION APPLICABLE TO CUSTOMER.",
    ]),
    ("10. Indemnification", [
        "10.1 Cognivault will defend Customer against third-party claims that the Platform infringes a US patent, copyright or trademark.",
        "10.2 Customer will defend Cognivault against claims arising from Customer Data or Customer's underwriting decisions, including any regulatory inquiry or action.",
    ]),
    ("11. Limitation of liability", [
        "11.1 EACH PARTY'S TOTAL AGGREGATE LIABILITY ARISING OUT OF OR RELATING TO THIS AGREEMENT WILL NOT EXCEED THE FEES PAID OR PAYABLE BY CUSTOMER IN THE SIX (6) MONTHS PRECEDING THE EVENT GIVING RISE TO THE CLAIM.",
        "11.2 NEITHER PARTY WILL BE LIABLE FOR ANY INDIRECT, CONSEQUENTIAL, SPECIAL OR PUNITIVE DAMAGES, OR FOR LOST PROFITS, REVENUE OR PREMIUM, OR REGULATORY FINES OR PENALTIES.",
    ]),
    ("12. Term and termination", [
        "12.1 This Agreement starts on the Effective Date and continues for five (5) years (the \"Term\").",
        "12.2 Either party may terminate for the other party's material breach that remains uncured thirty (30) days after written notice. Customer may not terminate for convenience.",
        "12.3 On expiry or termination, Customer may download Customer Data in Cognivault's then-standard export format for thirty (30) days, after which Cognivault may delete it. Cognivault has no obligation to provide transition assistance.",
    ]),
    ("13. Governing law and disputes", [
        "13.1 This Agreement is governed by the laws of the State of Texas, without regard to conflict-of-laws principles.",
        "13.2 Any dispute will be resolved by binding arbitration administered by the American Arbitration Association in Austin, Texas, before a single arbitrator.",
    ]),
    ("14. General", [
        "14.1 Cognivault may assign this Agreement without consent in connection with a merger, acquisition or sale of assets.",
        "14.2 This Agreement, including Exhibits A to D, is the entire agreement between the parties.",
    ]),
]

EXHIBITS: list[tuple[str, list[str]]] = [
    ("Exhibit A: Service levels", [
        "A.1 Platform availability: 99.5% per calendar month, excluding scheduled maintenance and emergency Model changes.",
        "A.2 Decision API latency: 95% of Decisions returned within 800 ms.",
        "A.3 Service credits: 2% of the monthly Fees for each full 0.5% below the availability target, capped at 10% of monthly Fees. Service credits are Customer's sole remedy for service level failures.",
    ]),
    ("Exhibit B: Fees", [
        "B.1 Annual platform fee: US$2,950,000, payable annually in advance for each year of the five-year Term (total US$14,750,000).",
        "B.2 Included volume: up to 4,000,000 Decisions per month.",
        "B.3 Overage: US$0.02 per Decision above the included volume, invoiced monthly in arrears.",
        "B.4 Cognivault may increase Fees by up to 7% at each anniversary of the Effective Date.",
    ]),
    ("Exhibit C: Security", [
        "C.1 Cognivault maintains a SOC 2 Type II certified information security program.",
        "C.2 Customer Data is encrypted in transit (TLS 1.2+) and at rest (AES-256) and hosted in US data centers.",
        "C.3 Cognivault will notify Customer of a confirmed security incident affecting Customer Data within seventy-two (72) hours.",
    ]),
    ("Exhibit D: Acceptable use", [
        "D.1 Customer will not use the Platform to make Decisions outside personal auto and homeowners insurance underwriting.",
        "D.2 Customer will not reverse engineer, probe or test the Models, including for bias or explainability, without Cognivault's prior written consent.",
        "D.3 Customer will not disclose Decisions, Model outputs or Platform documentation to any third party, including regulators, except as required by law and after notice to Cognivault.",
    ]),
]


def write_agreement(path: Path) -> None:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10.5)

    t = doc.add_heading(TITLE, level=0)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph(VERSION)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph(
        "This AI Vendor Agreement (the \"Agreement\") is entered into as of [Effective Date] between "
        "Cognivault Systems, Inc., a Delaware corporation with offices in Austin, Texas (\"Cognivault\"), and "
        "Verdantis Insurance Company, with offices in Stamford, Connecticut (\"Customer\")."
    )

    for heading, clauses in SECTIONS:
        doc.add_heading(heading, level=1)
        for c in clauses:
            doc.add_paragraph(c)

    doc.add_heading("Signatures", level=1)
    table = doc.add_table(rows=4, cols=2)
    table.style = "Table Grid"
    for i, (a, b) in enumerate([
        ("COGNIVAULT SYSTEMS, INC.", "VERDANTIS INSURANCE COMPANY"),
        ("By: ______________________", "By: ______________________"),
        ("Name:", "Name:"),
        ("Title:", "Title:"),
    ]):
        table.cell(i, 0).text = a
        table.cell(i, 1).text = b

    for heading, clauses in EXHIBITS:
        doc.add_page_break()
        doc.add_heading(heading, level=1)
        for c in clauses:
            doc.add_paragraph(c)

    footer = doc.sections[0].footer.paragraphs[0]
    footer.text = "Cognivault Confidential | v4.2 vendor draft | Fictional parties for Microsoft Ignite LAB654. Not legal advice."
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.core_properties.title = "Cognivault AI Vendor Agreement v4.2"
    doc.core_properties.author = "Cognivault Legal"
    doc.save(str(path))
