# BRK220 Copilot Connectors: Contoso renewal scenario (mock environment)

Revised from *BRK220 Copilot Connectors - Demo Outline* (Word) and its review comments. This is the version the mock environment in this folder implements. Only Demos 1 and 2 are in scope.

## What changed from the outline

| Outline | Here | Why |
|---|---|---|
| Megan's company "Contoso", customer "Contoso" | Megan Bowen is the Account Executive at **Northwind Ltd**; the customer is **Contoso Ltd** | Review comment: both companies were named Contoso |
| ServiceNow (ITSM) incidents | **Jira through Rovo** (Rovo mock). Same ticket numbers: INC-40211, INC-40188, INC-40302 in the Northwind Support (INC) project | Review comment: ServiceNow is IT helpdesk; Rovo partner approval secured |
| Confluence (sync connector) | **Confluence connector.** The CS and PROD pages (open SSO ask, approved roadmap dates) are seeded in the graphc-test.atlassian.net site and indexed by the Confluence connector; the skill reads them through Microsoft 365 search, and Rovo only for Jira. The Rovo mock still serves the same pages as a fallback | Review comment: Confluence might be missing; seeded Nov 12 |
| "Compete insights on meeting notes {TBD}" | **The twist:** Fabrikam quoted about 15% under Contoso's current price (QBR, Sep 29), then raised it to 20% off plus free migration (Teams escalation, Nov 4). Salesforce win/loss against Fabrikam shows that holding price and fixing service won, while discounting late lost | Same pattern as the LAB654 productivity scenario (Boulder Innovations, 20% under list) |
| Pricing approval risk | Alex Wilber (Regional Sales Director) says in the escalation chat: hold the agreed cap; anything lower needs his approval. The renewal template has the same rule | Review comment: risks are open escalations and pricing approvals |
| Older contract "sitting somewhere" | The current order form (NW-OF-2025-0142) and a renewal order form template are in Megan's OneDrive | Review comment; SharePoint needs a site in COEP, so OneDrive for v1 |
| QBR notes source | Recorded Teams meeting with transcript **and** Megan's Word notes | Review comment: either works |
| Renewal-prep skill + contract-drafting skill; MCP App widget | One **renewal-prep** skill does both demos (brief, then close-out with approvals, including the contract draft). No custom MCP App widget for now; the brief uses tables | Product direction for this iteration |
| "INC-40211: P0" in one table, "three P1s" elsewhere | Jira's default priorities: INC-40211 (EU latency) and INC-40188 (SSO) are **Highest**, given the CIO's escalation; INC-40302 is **High** | Review feedback; Jira has no P0 by default |

## Cast

| Person | Company | Role in the story | Where they appear |
|---|---|---|---|
| **Megan Bowen** | Northwind Ltd | Account Executive, the Copilot user. Owns Contoso Ltd | Everywhere |
| Alex Wilber | Northwind Ltd | Regional Sales Director, Megan's manager, approves pricing below the agreed cap | Teams chat, Salesforce |
| Isaiah Langer | Northwind Ltd | Customer Success Manager for Contoso | QBR, email cc, Teams chat, Jira reporter |
| Arjun Kumar | Northwind Ltd | Senior Support Engineer, EU Platform. Resolved Contoso's two earlier EU latency incidents | Jira |
| Rosa Diaz | Northwind Ltd | Support Engineer, owns INC-40188 | Jira |
| Lidia Holloway | Contoso Ltd | CIO, executive sponsor. Wants the SSO roadmap in writing; escalated EU latency | QBR, Salesforce contact |
| Daniel Okafor | Contoso Ltd | Head of Procurement, the renewal buyer. Agreed the 5% cap on Oct 8 | QBR, email, Salesforce contact |
| Fabrikam | Competitor | 15% under current price (QBR) → 20% off plus free migration (Nov 4) | QBR, Teams chat, Salesforce |

## Story

Contoso Ltd's $2.4M-a-year Northwind Platform contract renews on **December 31, 2026**, about six weeks after Ignite.

- **Sep 29, Q3 QBR (Teams, recorded).** Lidia asks for a written SSO roadmap commitment (SCIM provisioning and per-subsidiary conditional access) before renewal. Daniel says Contoso is price-sensitive: order volumes are down, their CFO wants flat vendor pricing, and **Fabrikam quoted about 15% under** what they pay today. The contract allows up to a 7% uplift; "seven won't fly." Lidia: slow P1 response is what would make her listen to Fabrikam.
- **Oct 6 to 8, email.** Megan proposes capping the uplift at 5%. Daniel pushes back with the Fabrikam number. Megan won't match a discount but holds the cap at 5% and promises the SSO commitment in writing. **Oct 8: Daniel agrees to the 5% cap** and asks for a formal proposal before the end of November.
- **Nov 4, Teams chat "Contoso escalation".** Isaiah: Lidia escalated **EU latency** (Frankfurt API calls 4 to 6 s, morning export batch timing out) and said she'd back Daniel on Fabrikam if it isn't owned and fixed. **Fabrikam is now at 20% off plus free migration.** Alex: don't chase their number (remember Adatum), hold the agreed cap, anything lower needs his approval.
- **Now, in Jira:** three open incidents for Contoso: two Highest (INC-40211, INC-40188) and one High (INC-40302). INC-40211 (EU latency, 9 days) and INC-40302 (EU export timeouts, 4 days) are **unassigned**; INC-40188 (SSO login failures, 12 days) is with Rosa Diaz. Arjun Kumar fixed Contoso's two earlier EU latency incidents.
- **In Confluence:** the SSO ask is still open with no committed date, but the Product roadmap now has committable dates: SCIM 2.0 GA by March 31, 2027 and per-subsidiary conditional access in Q2 2027.
- **In Salesforce:** the renewal is open at $2.4M with Fabrikam as competitor. Win/loss: **Tailwind Traders** renewed against Fabrikam's 25% off by holding a 4% uplift, putting a named engineer on open P1s and committing a roadmap item in writing; **Adatum** was lost after matching 15% in the final week with P1s unassigned.

The point: the renewal risk isn't the price gap. It's unowned incidents and an unanswered SSO ask, and the evidence says to fix those and hold the 5% cap.

## Demo 1: "Prep me for my Contoso renewal"

Surface: Microsoft 365 Copilot Chat. Skill: **renewal-prep** (BRIEF).

| Do | Say |
|---|---|
| Fresh Chat session. | Every seller knows this moment: a big renewal is coming and the context is scattered everywhere. |
| Type **Prep me for my Contoso renewal.** Let it stream. Hover the source chips. | One answer: the contract from Salesforce, live incidents from Jira through Rovo, the open SSO ask and roadmap from Confluence, and from Microsoft 365 my pricing agreement in email, the QBR and the Teams escalation. |
| Point to the KPI row and the ticket table. | The numbers are exact: $2.4M, December 31, three open incidents, two of them Highest priority, two unassigned. |
| Point to **What's at risk → Service**. | Copilot links the CIO's Teams escalation to INC-40211 and INC-40302. Neither system could tell me that on its own. |
| Point to **What's at risk → Price**. | Here's the twist. Fabrikam went from 15% to 20% off. But my own win/loss history says matching a discount late lost Adatum, and holding price while fixing service kept Tailwind. So I hold the 5% we agreed. |
| Pause on the full brief. | Now I have the full picture. A picture doesn't renew a contract. Let's close the gaps. |

**Expected result** (layout can vary; content shouldn't):

- It picks **Contoso Ltd**, not Contoso Pharmaceuticals (Salesforce `USING SCOPE mine`; Jira label `customer-contoso`).
- KPI row: $2.4M a year · Dec 31, 2026 · days to renewal · 3 open incidents (2 Highest) · 2 unassigned.
- Tickets: INC-40211 (Highest, 9d, Unassigned, EU latency), INC-40188 (Highest, 12d, Rosa Diaz, SSO login failures), INC-40302 (High, 4d, Unassigned, EU export timeouts). INC-40211 and INC-40302 match the Nov 4 escalation.
- Price: 5% cap agreed Oct 8 (email); price-sensitive (QBR: volumes down, CFO wants flat pricing); Fabrikam 15% (QBR) → 20% + free migration (Teams); win/loss Tailwind (won) vs Adatum (lost) → hold the cap.
- Open ask: SSO roadmap commitment, open since the Sep 29 QBR, no committed date (Confluence); committable roadmap dates exist.
- Stakeholders: Lidia Holloway (CIO), Daniel Okafor (procurement); internal Alex, Isaiah.

**If it goes wrong:** if Copilot asks which Contoso, answer "Contoso Ltd". If it doesn't use the skill, ask "Use the renewal-prep skill."

## Demo 2: "Close out the Contoso risks before renewal"

Surface: Copilot Cowork (or Chat), plus Outlook and Word. Skill: **renewal-prep** (CLOSE-OUT). Same conversation as Demo 1 if possible; mock writes are kept per conversation.

Prompt: **Close out the Contoso risks before renewal: assign owners to the latency tickets, send Contoso the renewal proposal, and draft the renewal contract.**

| Step | System | Approval | Expected result |
|---|---|---|---|
| 1 · Assign latency tickets | Jira (Rovo) | Yes | Suggests **Arjun Kumar** (resolved INC-39412 and INC-39750 for Contoso). After yes: INC-40211 and INC-40302 assigned to Arjun with a work note. The issue links open the Jira viewer showing the change |
| 2 · Renewal proposal email | Outlook | Yes, before send | To Daniel, cc Lidia and Isaiah: $2,520,000 a year (5% uplift, below the 7% cap); acknowledges budget pressure; SCIM 2.0 GA by March 31, 2027 and per-subsidiary conditional access in Q2 2027; latency tickets now owned by Arjun. No discount, Fabrikam not named |
| 3 · Renewal contract | Word | No (draft only) | *Contoso Ltd - Renewal Order Form FY27 (DRAFT).docx* from the template and NW-OF-2025-0142: Jan 1 to Dec 31, 2027, $2,520,000, +5% (+$120,000), SLAs and EU residency carried over, roadmap section with the approved wording, no director approval needed |
| 4 · Update opportunity | Salesforce | Yes | Stage Value Proposition → Proposal/Price Quote, Amount $2.4M → $2.52M, Next Step updated, completed Email task logged. The record link shows the change |

**Say:** One instruction, three systems. Nothing is written to Jira or Salesforce, and nothing is sent, until I approve. Copilot suggests Arjun because he fixed Contoso's last two EU latency incidents. The proposal keeps the 5% we agreed, speaks to their budget pressure and answers the SSO ask with dates Product has approved.

**Optional beat (pricing approval):** "Should we just match Fabrikam's 20%?" The skill declines to put it in the proposal, cites Adatum and Tailwind, says it needs Alex Wilber's approval and offers to create an approval Task in Salesforce.

## Out of scope

Demos 3 to 5 from the outline aren't part of this environment. Demo 1 is read-only and Demo 2 writes within its own conversation, so the default per-conversation state is enough. `MOCK_SHARED_STATE=1` remains available if a later demo needs to see Demo 2's writes from another surface.

## Seed data

| Source | Where | What |
|---|---|---|
| Salesforce | `mock_mcp_servers/salesforce/mock_salesforce/seed.py` | See [Salesforce mock README](mock_mcp_servers/salesforce/README.md) |
| Jira and Confluence | `mock_mcp_servers/atlassian/seed_files/seed.json` | See [Rovo mock README](mock_mcp_servers/atlassian/README.md) |
| Microsoft 365 | `tenant/tools/scenario.py`, `tenant/tools/documents.py` | 7 users, 4 emails (Oct 6 to 8 thread), 1 group chat (Nov 4), 1 QBR event with online meeting and transcript (Sep 29), 3 OneDrive documents |

**One identity per person.** Megan, Alex, Isaiah, Arjun, Rosa, Lidia and Daniel are tenant users (Lidia and Daniel have mailbox and Teams only). The mocks use `TENANT_EMAIL_DOMAIN` so Salesforce contacts and Jira users match tenant emails.

**Dates.** Microsoft 365 items are dated on or before Nov 6, 2026 (COEP rejects future timestamps). Jira ticket ages are relative to the day you run the demo. The renewal date (Dec 31, 2026) is fixed.
