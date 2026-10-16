# Lab seed kit: scenario #1, Verdantis × Cognivault

> Converted from `00_Seed_Kit_Guide.docx` in the "legal v1 seed kit". The seed data built from it lives in `src/mock_environment` (tenant: `tools/scenarios/legal/`; iManage: `mock_mcp_servers/imanage/seed_files`). All dates here, in the seed data and in the iManage documents have been moved from the kit's original lab date so that every seeded item is in the past. The current lab date is `LAB_DATE` in `tools/scenarios/legal/__init__.py`; to move it again, run `tools/scenarios/legal/redate.py`.

*AI underwriting platform contract  |  US  |  Data adapted from Harvey LAB (MIT License)*

Everything to load before the lab: who sends what to whom, when, and which files go into iManage. Assumed lab date: Monday, October 12, 2026. Every date inside the files has been shifted to fit that date (negotiation Thursday Oct 15, go-live Sunday Oct 18). If your lab is on another date, the build script can regenerate the kit.

## Kit folder layout

- `01_Outlook_Marcus_mailbox`: Radhika’s email (.eml to import, plus HTML/TXT body to paste)
- `02_Teams`: the exact Teams messages and who posts them
- `03_iManage_Cognivault-Nexus_matter`: 6 documents in 2 folders, plus 2 folders left empty for Copilot’s output
- `04_Answer_key_DO_NOT_SEED`: 83 grading criteria and an expert issue list, for checking Copilot’s output

## Story timeline

| Story date | What happens | Where it lives |
|---|---|---|
| Mon Sep 28, 2026 | Radhika emails Marcus (cc Tomás) the business’s ranked must-haves for the Cognivault deal. | Outlook (seed) |
| Fri Oct 2 | Cognivault sends its AI Vendor Agreement v4.2 + Exhibits A–D. Marcus files them in iManage. | iManage (seed) |
| Tue Oct 6 | Group chat: Tomás, Radhika and Marcus agree on two must-haves; Marcus says he’ll review before the 15th. | Teams (seed) |
| Mon Oct 12, 8:07 AM | TRIGGER: Tomás asks Marcus whether they can sign on the 15th. | Teams (lab morning) |
| Mon Oct 12 | The lab: steps 1–5. | Live |
| Thu Oct 15 | Negotiation session with Cognivault’s counsel. Mentioned in the email and chat only; no calendar item needed. | — |
| Sun Oct 18 | Target effective date / go-live. | In the contract |

## Demo accounts

| Persona | Role | Account needs |
|---|---|---|
| Marcus Hollowell (presenter) | Associate General Counsel, Technology Transactions, Verdantis | Microsoft 365 Copilot license; Copilot Cowork; Word Legal Agent (Frontier program + Anthropic enabled); Harvey license and agent; iManage Work account with access to the matter. Mailbox and Teams. |
| Radhika Sengupta | SVP, Strategic Procurement & Vendor Management, Verdantis | Mailbox and Teams only. |
| Tomás Aguilar | Chief Underwriting Officer, Verdantis | Mailbox and Teams only. (A co-presenter can sign in as Tomás to send the trigger live.) |
| Diane Xu, Priya Ramasubramanian | Cognivault sales lead and counsel | No accounts. Named in the documents only. |

Use these exact display names. Prompts refer to Radhika and Tomás by name, and Copilot matches on display names. The .eml uses @verdantis.com addresses; replace them with your tenant’s addresses.

## Seeding checklist

| # | Item | From → To / location | When | Kit file |
|---|---|---|---|---|
| 1 | Business priorities email (≈1,500 words). Subject: “Cognivault Nexus – Business Requirements & Negotiation Priorities” | Radhika → Marcus, cc Tomás | Ideally 2 weeks before the lab (at least 2 days, for indexing) | 01_Outlook…/Radhika_to_Marcus_email_BODY.html (or .eml) |
| 2 | Group chat “Cognivault deal”: 3 short messages | Tomás, Radhika, Marcus | The week before the lab | 02_Teams/Teams_messages_to_post.txt (part A) |
| 3 | iManage workspace and 6 documents | Client: Verdantis Technologies, Inc. · Matter: “Cognivault – Nexus AI Platform Agreement” | Any time before; check Marcus’s access | 03_iManage… (see section 4) |
| 4 | Trigger message | Tomás → Marcus, 1:1 chat | Lab morning, or live | 02_Teams/… (part B) |
| — | Answer key | Do not load anywhere Marcus can see | — | 04_Answer_key_DO_NOT_SEED |

### How to seed the email

- Option A (recommended): signed in as Radhika, open the BODY.html file in a browser, copy everything, paste into a new email to Marcus (cc Tomás) with the subject above, and send. It arrives from a real tenant user, but with the real send date.
- Option B (keeps the Sep 28 date): edit the From/To/Cc addresses in the .eml to your tenant users, then in Outlook desktop (signed in as Marcus) drag it into the Inbox. Check that it shows Radhika as sender and Tomás on cc.

Either way, don’t attach the contract. The only copy should be in iManage.

## iManage matter: folders and document profiles

| Document (kit file name) | Folder | Description to set in iManage | Doc type / author |
|---|---|---|---|
| Cognivault AI Vendor Agreement v4.2.docx | 01 Vendor Paper | Cognivault AI Vendor Agreement v4.2, vendor draft (CVS-EA-2026-0417), received Oct 2, 2026 | Agreement / Cognivault |
| Cognivault Exhibit A - Service Description and SLA.docx | 01 Vendor Paper | Exhibit A: service levels (99.5% availability, credits) | Exhibit / Cognivault |
| Cognivault Exhibit B - Fee Schedule and Order Form.xlsx | 01 Vendor Paper | Exhibit B: fees, 5% escalator, payment schedule | Exhibit / Cognivault |
| Cognivault Exhibit C - Security and Data Protection.docx | 01 Vendor Paper | Exhibit C: security standards, SOC 2 Type I, 72-hour incident notice | Exhibit / Cognivault |
| Cognivault Exhibit D - Acceptable Use Policy.docx | 01 Vendor Paper | Exhibit D: acceptable use, suspension right, benchmarking ban | Exhibit / Cognivault |
| Verdantis AI Procurement Playbook v2.1.docx | 02 Playbooks | AI Procurement Playbook v2.1 (VTI-LEGAL-PB-AI-2.1), effective May 18, 2026 | Playbook / Marcus Hollowell |
| (empty) | 03 Research | Copilot saves the research note here in step 2 | — |
| (empty) | 04 Drafts | Copilot / Cowork save the redline, negotiation list and 1-pager here in steps 3–4 | — |

Also check: the iManage Work connector is enabled in Copilot and Marcus has signed in; Copilot Cowork is on the iManage “Allowed MCP clients” list; the iManage plugin is deployed in Cowork; write tools are enabled so Copilot can save to 03 Research and 04 Drafts.

## Exact Teams messages

### A) Group chat “Cognivault deal”: post in this order, the week before the lab

**Tomás Aguilar**, story time Tue Oct 6, ~10:14 AM

> Quick one on Cognivault. Our last vendor retired its model on 2 weeks’ notice and we couldn’t quote for a week. Can’t happen again.

**Radhika Sengupta**, ~10:20 AM

> Agreed. And we don’t go to the table without owning the fine-tuned model.

**Marcus Hollowell**, ~10:31 AM

> Understood. Their paper came in on Friday and it’s in the matter. I’ll review it against the playbook before the session on the 15th.

### B) Trigger: 1:1 chat, Tomás → Marcus, lab morning

**Tomás Aguilar**, story time Mon Oct 12, 8:07 AM

> Morning Marcus. Have you had a chance to look at Cognivault’s contract? We’d like to sign at the session with them on the 15th so we can go live on the 18th. Anything you need from me?

## What Copilot should produce (quick answer key)

| Step | Expect to see (check against 04_Answer_key) |
|---|---|
| 1  Catch up | Decided: Verdantis must own the fine-tuned model (Radhika’s email, confirmed in Teams); no more short-notice model retirements (Tomás); preference for Delaware law and courts (Radhika). <br>Radhika’s other asks: control over model changes (real advance notice, approval when outputs shift >2%, model cards); explainability, quarterly bias testing and annual audits for Colorado and New York examiners; clean exit; liability that matches a $14.75M deal. <br>Pending: Marcus’s playbook review; answering Tomás. The 15th is a negotiation session, not a signing. |
| 2  Check the law | Harvey: Colorado Regulation 10-1-1 (now covers private passenger auto, not homeowners; governance, testing, documentation). NY DFS Insurance Circular Letter No. 7 (2024): insurer stays responsible for vendor AI; contracts should give audit rights and require the vendor to cooperate with regulatory inquiries. <br>Gap table: contract §11 has no audit, bias-testing or explainability terms; §7.4 gives only 15 days’ notice of model changes; no regulator-cooperation duty. The playbook also has no regulator-cooperation clause, although Radhika’s email asks for one. |
| 3  Redline | Tracked changes and comments on §9 (model weights and outputs owned by Verdantis; opt-in before cross-customer training), §7.4 (60 days’ notice, approval for >2% variance, retired models kept 12 months), §11 (annual audit, quarterly bias testing, model cards, NIST AI RMF explainability, data lineage, and the new regulator-cooperation clause), §16.2 (cap from ~$1.36M to $5.9M; $8.85M super-cap), §20 (180-day exit, Parquet/CSV data back within 30 days, escrow). <br>Extra issues a full review catches: §18 indemnity scope, §17 insurance limits, §14 subcontracting, §22 Texas law and arbitration vs. Delaware, Exhibit C SOC 2 Type I, 5% escalator vs. CPI+1% capped at 3%. |
| 4  Package | Negotiation list (one row per tracked change, with playbook fallbacks and “do not concede” items), a plain-English 1-pager for Tomás and Radhika, a reply to Tomás, a cover email to Cognivault’s counsel, and a playbook-update note. |

## Changes from the benchmark files

- Dates shifted +17 months (June 2025 → November 2026); weekdays are preserved. Document ID CVS-EA-2025-0417 became CVS-EA-2026-0417.
- Radhika’s email: three references to outside counsel removed, so Marcus owns the review. Otherwise word for word.
- New content: the Teams group chat and the trigger message. They are not in the benchmark.
- Left out: Marcus’s kickoff email to outside counsel. It contains the full expert analysis, so it’s in the answer key instead.

## Before the lab, and between runs

- Indexing check (as Marcus, a day before): ask Copilot “What did Radhika send me about Cognivault?” and “What did Tomás say in Teams about model retirements?” Both should come back with sources.
- Rehearse step 2 and keep the NY DFS circular and Colorado regulation open in a browser as a backup.
- Reset between runs: delete the contents of 03 Research and 04 Drafts in iManage, delete emails sent to Tomás and to Cognivault’s counsel, and start a new Copilot chat. Then repost the trigger.
- Attribution: keep NOTICE_Harvey_LAB_MIT_License.txt with the kit if you share it.
