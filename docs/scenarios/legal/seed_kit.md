# Lab seed kit: scenario #1, Zava × Trey Research

> Converted from `00_Seed_Kit_Guide.docx` in *legal v1 seed kit 1.zip* (November edition). The kit was written for the earlier five-step legal flow; the lab now runs the v3 short flow in [scenario.md](scenario.md). Differences that matter for seeding:
>
> - **03 Research is no longer used.** v3 has no research step in Word; the regulator check runs inside the Cowork step and Cowork saves everything to the Drafts folder.
> - **The lab matter is slimmer than the kit's.** The mock iManage matter holds only `Playbooks` (the playbook) and an empty `Drafts`. The agreement is seeded in the tenant in Emil's OneDrive (`Trey Research` folder) and opened in Word from there (Word can't open a document from the mock server), using [`files/Trey Research Vendor Agreement v4.2.docx`](files/). Emil's group-chat line says the paper is "in my OneDrive" rather than "in the matter". The exhibits aren't seeded. The folder table and the "only copy should be in iManage" note below describe the kit's original setup.
> - **The agreement in Word is the shortened lab edition** ("original section numbers"). The kit and `infra/mock_environment/mock_mcp_servers/imanage/seed_files` still hold the full-length v4.2.
> - The quick answer key below describes the older five-step outputs. Use the "What comes back" column in [scenario.md](scenario.md) for v3.
>
> Seed data built from this kit lives in `infra/mock_environment` (tenant: `tools/scenarios/legal/`; iManage: `mock_mcp_servers/imanage/seed_files`). Dates follow the lab-wide rule: everything seeded is dated on or before Oct 30, 2026 (the tenant is loaded once, before the Nov 17–19 lab), and what is still to come in the story (negotiation, go-live) falls after the lab. To move them, run `tools/scenarios/legal/redate.py --lab-date <Monday> --negotiation-date <Thursday>`.

*AI underwriting platform contract  |  US  |  Data adapted from Harvey LAB (MIT License)*

Everything to load before the lab: who sends what to whom, when, and which files go into iManage. Story date of Luc's trigger: Monday, October 26, 2026. Every date inside the files has been shifted to fit (negotiation Thursday Dec 10, go-live Sunday Dec 13), so attendees on Nov 17–19 see a deal that is still open.

## Kit folder layout

- `01_Outlook_Emil_mailbox`: Hemanti’s email (.eml to import, plus HTML/TXT body to paste)
- `02_Teams`: the exact Teams messages and who posts them
- `03_iManage_TreyResearch-AIPlatform_matter`: 6 documents in 2 folders, plus 2 folders left empty for Copilot’s output
- `04_Answer_key_DO_NOT_SEED`: 83 grading criteria and an expert issue list, for checking Copilot’s output

## Story timeline

| Story date | What happens | Where it lives |
|---|---|---|
| Mon Oct 12, 2026 | Hemanti emails Emil (cc Luc) the business’s ranked must-haves for the Trey Research deal. | Outlook (seed) |
| Fri Oct 16 | Trey Research sends its AI Vendor Agreement v4.2 + Exhibits A–D. Emil files them in iManage. | iManage (seed) |
| Tue Oct 20 | Group chat: Luc, Hemanti and Emil agree on two must-haves; Emil says he’ll review before the 10th. | Teams (seed) |
| Mon Oct 26, 8:07 AM | TRIGGER: Luc asks Emil whether they can sign on the 10th. | Teams (seed) |
| Nov 17–19 | The lab: steps 1–4 (v3 short flow). Emil still hasn't answered Luc. | Live |
| Thu Dec 10 | Negotiation session with Trey Research’s counsel. Mentioned in the email and chat only; no calendar item needed. | — |
| Sun Dec 13 | Target effective date / go-live. | In the contract |

## Demo accounts

| Persona | Role | Account needs |
|---|---|---|
| Emil Vanggaard (presenter) | Associate General Counsel, Technology Transactions, Zava | Microsoft 365 Copilot license; Copilot Cowork; Word Legal Agent (Frontier program + Anthropic enabled); iManage Work account with access to the matter. Mailbox and Teams. |
| Hemanti Baishya | SVP, Strategic Procurement & Vendor Management, Zava | Mailbox and Teams only. |
| Luc Lacombe | Chief Underwriting Officer, Zava | Mailbox and Teams only. (A co-presenter can sign in as Luc to send the trigger live.) |
| Andreea Bojin, Vira Sokur | Trey Research sales lead and counsel | No accounts. Named in the documents only. |

Use these exact display names. Prompts refer to Hemanti and Luc by name, and Copilot matches on display names. The .eml uses @zava-online.com addresses; replace them with your tenant’s addresses.

## Seeding checklist

| # | Item | From → To / location | When | Kit file |
|---|---|---|---|---|
| 1 | Business priorities email (≈1,500 words). Subject: “Trey Research AI Platform – Business Requirements & Negotiation Priorities” | Hemanti → Emil, cc Luc | Ideally 2 weeks before the lab (at least 2 days, for indexing) | 01_Outlook…/Radhika_to_Marcus_email_BODY.html (or .eml) |
| 2 | Group chat “Trey Research deal”: 3 short messages | Luc, Hemanti, Emil | The week before the lab | 02_Teams/Teams_messages_to_post.txt (part A) |
| 3 | iManage workspace and 6 documents | Client: Zava, Inc. · Matter: “Trey Research – AI Platform Agreement” | Any time before; check Emil’s access | 03_iManage… (see section 4) |
| 4 | Trigger message | Luc → Emil, 1:1 chat | Seeded, dated Mon Oct 26 | 02_Teams/… (part B) |
| — | Answer key | Do not load anywhere Emil can see | — | 04_Answer_key_DO_NOT_SEED |

### How to seed the email

- Option A (recommended): signed in as Hemanti, open the BODY.html file in a browser, copy everything, paste into a new email to Emil (cc Luc) with the subject above, and send. It arrives from a real tenant user, but with the real send date.
- Option B (keeps the Oct 12 date): edit the From/To/Cc addresses in the .eml to your tenant users, then in Outlook desktop (signed in as Emil) drag it into the Inbox. Check that it shows Hemanti as sender and Luc on cc.

Either way, don’t attach the contract. The only copy should be in iManage.

## iManage matter: folders and document profiles

| Document (kit file name) | Folder | Description to set in iManage | Doc type / author |
|---|---|---|---|
| Trey Research Vendor Agreement v4.2.docx | 01 Vendor Paper | Trey Research Vendor Agreement v4.2, vendor draft (TR-EA-2026-0417), received Oct 16, 2026 | Agreement / Trey Research |
| Trey Research Exhibit A - Service Description and SLA.docx | 01 Vendor Paper | Exhibit A: service levels (99.5% availability, credits) | Exhibit / Trey Research |
| Trey Research Exhibit B - Fee Schedule and Order Form.xlsx | 01 Vendor Paper | Exhibit B: fees, 5% escalator, payment schedule | Exhibit / Trey Research |
| Trey Research Exhibit C - Security and Data Protection.docx | 01 Vendor Paper | Exhibit C: security standards, SOC 2 Type I, 72-hour incident notice | Exhibit / Trey Research |
| Trey Research Exhibit D - Acceptable Use Policy.docx | 01 Vendor Paper | Exhibit D: acceptable use, suspension right, benchmarking ban | Exhibit / Trey Research |
| Zava AI Procurement Playbook v2.1.docx | 02 Playbooks | AI Procurement Playbook v2.1 (ZAVA-LEGAL-PB-AI-2.1), effective June 1, 2026 | Playbook / Emil Vanggaard |
| (empty) | 03 Research | Copilot saves the research note here in step 2 | — |
| (empty) | 04 Drafts | Copilot / Cowork save the redline, negotiation list and 1-pager here in steps 3–4 | — |

Also check: the iManage Work connector is enabled in Copilot and Emil has signed in; Copilot Cowork is on the iManage “Allowed MCP clients” list; the iManage plugin is deployed in Cowork; write tools are enabled so Copilot can save to 03 Research and 04 Drafts.

## Exact Teams messages

### A) Group chat “Trey Research deal”: post in this order, the week before the lab

**Luc Lacombe**, story time Tue Oct 20, ~10:14 AM

> Quick one on Trey Research. Our last vendor retired its model on 2 weeks’ notice and we couldn’t quote for a week. Can’t happen again.

**Hemanti Baishya**, ~10:20 AM

> Agreed. And we don’t go to the table without owning the fine-tuned model.

**Emil Vanggaard**, ~10:31 AM

> Understood. Their paper came in on Friday and it’s in the matter. I’ll review it against the playbook before the session on the 10th.

### B) Trigger: 1:1 chat, Luc → Emil

**Luc Lacombe**, story time Mon Oct 26, 8:07 AM

> Morning Emil. Have you had a chance to look at Trey Research’s contract? We’d like to sign at the session with them on the 10th so we can go live on the 13th. Anything you need from me?

## What Copilot should produce (quick answer key)

| Step | Expect to see (check against 04_Answer_key) |
|---|---|
| 1  Catch up | Decided: Zava must own the fine-tuned model (Hemanti’s email, confirmed in Teams); no more short-notice model retirements (Luc); preference for Delaware law and courts (Hemanti). <br>Hemanti’s other asks: control over model changes (real advance notice, approval when outputs shift >2%, model cards); explainability, quarterly bias testing and annual audits for Colorado and New York examiners; clean exit; liability that matches a $14.75M deal. <br>Pending: Emil’s playbook review; answering Luc. The 10th is a negotiation session, not a signing. |
| 2  Check the law (now inside step 4) | Public regulations (web): Colorado Regulation 10-1-1 (now covers private passenger auto, not homeowners; governance, testing, documentation). NY DFS Insurance Circular Letter No. 7 (2024): insurer stays responsible for vendor AI; contracts should give audit rights and require the vendor to cooperate with regulatory inquiries. <br>Gap table: contract §11 has no audit, bias-testing or explainability terms; §7.4 gives only 15 days’ notice of model changes; no regulator-cooperation duty. The playbook also has no regulator-cooperation clause, although Hemanti’s email asks for one. |
| 3  Redline | Tracked changes and comments on §9 (model weights and outputs owned by Zava; opt-in before cross-customer training), §7.4 (60 days’ notice, approval for >2% variance, retired models kept 12 months), §11 (annual audit, quarterly bias testing, model cards, NIST AI RMF explainability, data lineage, and the new regulator-cooperation clause), §16.2 (cap from ~$1.36M to $5.9M; $8.85M super-cap), §20 (180-day exit, Parquet/CSV data back within 30 days, escrow). <br>Extra issues a full review catches: §18 indemnity scope, §17 insurance limits, §14 subcontracting, §22 Texas law and arbitration vs. Delaware, Exhibit C SOC 2 Type I, 5% escalator vs. CPI+1% capped at 3%. |
| 4  Package | Negotiation list (one row per tracked change, with playbook fallbacks and “do not concede” items), a plain-English 1-pager for Luc and Hemanti, a reply to Luc, a cover email to Trey Research’s counsel, and a playbook-update note. |

## Changes from the benchmark files

- Dates shifted from June 2025 into Oct–Dec 2026; weekdays are preserved. Document ID TR-EA-2025-0417 became TR-EA-2026-0417.
- Hemanti’s email: three references to outside counsel removed, so Emil owns the review. Otherwise word for word.
- New content: the Teams group chat and the trigger message. They are not in the benchmark.
- Left out: Emil’s kickoff email to outside counsel. It contains the full expert analysis, so it’s in the answer key instead.

## Before the lab, and between runs

- Indexing check (as Emil, a day before): ask Copilot “What did Hemanti send me about Trey Research?” and “What did Luc say in Teams about model retirements?” Both should come back with sources.
- Rehearse step 2 and keep the NY DFS circular and Colorado regulation open in a browser as a backup.
- Reset between runs: delete the contents of 03 Research and 04 Drafts in iManage, delete emails sent to Luc and to Trey Research’s counsel, and start a new Copilot chat. Then repost the trigger.
- Attribution: keep NOTICE_Harvey_LAB_MIT_License.txt with the kit if you share it.
