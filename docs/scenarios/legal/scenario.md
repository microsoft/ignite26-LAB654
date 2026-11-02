# Lab 654 – Legal workflow: scenario brief (short)

> Source: *654 Legal Lab scenario v3 (short) - updated.docx*. Converted to Markdown for reference; formatting differs from the original, wording is preserved. Replaces the earlier five-step legal scenario.
>
> Prompts run in Word with *Trey Research Vendor Agreement v4.2.docx* opened from the iManage matter. Seed content comes from *legal v1 seed kit 1.zip*; see [seed_kit.md](seed_kit.md).

## The setup and what the room takes away

**The setup:** Zava, a US car and home insurer, wants Trey Research's AI to make up to 4 million underwriting decisions a month: a five-year, $14.75M deal. Regulators in Colorado and New York hold the insurer responsible for vendor AI, and Zava trains the AI on its own claims data, so it must own what gets built.

**The situation:** Trey Research's one-sided draft is in the iManage matter. Luc (underwriting) asks Emil (in-house lawyer) in Teams: *"Can we sign on the 10th?"* Emil opens the draft from iManage in Word and needs the backstory, a redline and a plain-English answer before the negotiation session on Thursday, December 10. Three prompts in one Word chat, one in Cowork; Emil approves everything.

**What the room takes away:**

1. **Word legal skills** flag and redline the contract inside the document, with a reason on every change.
2. **Connectors** bring the matter to the work: the backstory from Outlook and Teams, the matter and playbook from iManage. No uploads.
3. **Cowork legal skills** turn the redline into the negotiation pack, and wait for Emil's approval before anything is sent.

## The flow

| Step · where | What Emil types | Connectors and skills | What comes back | Aha for the room |
|---|---|---|---|---|
| **1 Catch up**<br>Word, with the agreement opened from the iManage matter | *"Catch me up on the Trey Research deal in five bullets: what Hemanti and Luc asked for, what we've decided, and what's still open."* | Work IQ (Hemanti's email, the Teams chat), inside Word | Hemanti's five ranked priorities (model ownership is her red line) · Luc's worry: a model retired on two weeks' notice stopped quoting for a week · already agreed: own the fine-tuned model, no disruption to live underwriting, review against the playbook · open: will Trey Research accept any of it before the 10th. Linked to the email and the Teams chat. | Without leaving the contract, Copilot pulled the backstory from an older email and a Teams chat, and told apart who asked for what.<br><br>**Point out:** Luc only asked "can we sign?" · each bullet links to its email or chat · the 10th is a negotiation, not a signing · the two must-haves become Steps 2–3; the regulator ask becomes Step 4. |
| **2 Flag**<br>Same Word chat | *"Which clauses in this agreement break the hard stops in our AI Procurement Playbook in the Trey Research AI Platform matter in iManage? Add a comment on each one with the playbook section."* | iManage connector (reads the playbook in place)<br><br>Word legal skills | Eight comment suggestions covering all six hard stops; Emil clicks Apply 8 suggestions:<br><br>Outputs not owned (§3.2, §9.2) · nothing uncapped (§16.2, §16.3) · subcontractor liability capped (§14.2) · data back only in Trey Research's format (§20.2) · arbitration in Austin (§22.2) · class-action waiver (§22.4) | The playbook never left iManage, and nothing was uploaded. Each comment cites the playbook section and its hard-stop number, and Copilot caught the hard stops that show up in two places. |
| **3 Fix**<br>Same Word chat | *"Now redline this so we own the fine-tuned model, and Trey Research can't change or retire the model without real notice and our approval. Explain each change in a comment."* | iManage connector (playbook positions)<br><br>Edit contract skill | Eight tracked changes, each with a comment (two applied, then Apply 6 suggestions):<br><br>Zava owns fine-tuned models, delivered in a portable format (§9.1) · 60 days' detailed notice and Zava approval before any model change or retirement; continued use is not acceptance (§§7.2–7.4) · only non-behavioral fixes exempt · retired versions kept 12 months with migration help (§7.5) | One business sentence, no section numbers: Copilot found the five clauses itself and wrote the playbook's positions in. Luc's Teams worry is now contract language. |
| **4 Pack**<br>Copilot Cowork (from Word) | *"Get me ready for the December 10 session with Trey Research. Turn my redline and the flags into a negotiation list with our playbook fallbacks, check whether it covers what Colorado and New York regulators expect, write a one-page summary for Luc and Hemanti, and draft my reply to Luc. Save it all to the matter."* | iManage plugin · Work IQ (Hemanti's email, the Teams chat) · web (public regulations)<br><br>Summarize redlines · Identify regulatory gaps · Draft legal memo | Negotiation list: one row per change or flag, with the fallback and "do not concede" on hard stops. Regulator check: no audit right, bias testing or regulator cooperation, and the playbook itself has no regulator-cooperation clause. 1-pager: "The 10th is a negotiation, not a signing; three asks." Reply to Luc, held for approval. | One request becomes four deliverables across iManage and Outlook. Cowork asks before sending; the lawyer stays accountable. |

**Close:** Emil opens Cowork's review list, checks the 1-pager (regulator points link to the public regulations), and approves the reply to Luc.

## Seed data

- **Outlook:** Hemanti's email to Emil (cc Luc), two weeks earlier: the business's ranked must-haves.
- **Teams:** group chat (Luc: no more short-notice model retirements; Hemanti: we must own the fine-tuned model) and Luc's trigger message on the morning.
- **OneDrive (each attendee):** Trey Research Vendor Agreement v4.2, uploaded before the lab from [`files/`](files/). Shortened lab edition, original section numbers. Word opens it from here; it can't open a document from the mock iManage server.
- **iManage matter "Trey Research – AI Platform Agreement":** AI Procurement Playbook v2.1 (Playbooks); Drafts empty for Cowork's output.

## Before the lab

- iManage connector enabled for Copilot in Word and Cowork; iManage plugin added in Cowork, web search allowed, with write access to Drafts.
- Word desktop with the Legal plugin on. Say "redline … so that" or "which clauses break", not "review against the playbook": that phrase starts the upload-a-playbook review.
- Dry-run and time each step: Word steps take about 2–3 minutes each; Cowork runs in the background (have a finished run ready to show).
- Reset between runs: clear the comments and redline (re-upload the original to OneDrive), start a new conversation (the mock keeps Drafts per conversation), delete sent emails. Run Catch up on a clean copy, before Flag and Fix.
- Seed dates must match the agreement (effective 13 December, session on the 10th). Everything seeded is dated on or before Oct 30 (email Oct 12, group chat Oct 20, trigger Oct 26); the negotiation and go-live fall after the Nov 17–19 lab. Move them together with `infra/mock_environment/tools/scenarios/legal/redate.py`.

---

Legal Copilot Lab 654 | Fictional parties adapted from Harvey LAB (MIT). Not legal advice.
