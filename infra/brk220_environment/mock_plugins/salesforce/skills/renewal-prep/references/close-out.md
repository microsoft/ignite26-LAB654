# CLOSE-OUT mode: remove renewal risk, with approvals

Goal: turn the brief into completed work in the systems of record. Four steps, each with a preview and an explicit approval before any write or send.

If the brief hasn't run in this conversation, run BRIEF steps 1 to 4 silently first (no brief output) so you have the account, renewal opportunity, tickets, asks, pricing position and stakeholders.

## Plan

Show the plan before step 1 and update it after each step:

```
### <Account> renewal plan
| Step | Writes to | Status |
|---|---|---|
| 1 · Assign latency tickets | Jira via Rovo | Awaiting approval |
| 2 · Renewal proposal email | Outlook | Not started |
| 3 · Renewal contract | Word (OneDrive) | Not started |
| 4 · Update opportunity | Salesforce | Not started |
```

Statuses: Not started → Awaiting approval → ✓ Done (with a short result such as "✓ 2 assigned", "✓ Sent", "✓ Draft ready", "✓ Updated") or Skipped.

## Step 1. Assign owners to the unassigned incidents (Jira through Rovo)

1. Unassigned open tickets for the account: `project = INC AND labels = <LABEL> AND statusCategory != Done AND assignee is EMPTY`. If the user named a kind of ticket (for example "latency tickets"), keep only those (label `latency` or matching summaries).
2. Suggest an owner from history: `project = INC AND labels = <LABEL> AND labels = <topic label, for example latency> AND statusCategory = Done ORDER BY updated DESC` with fields `summary, assignee, comment`. The person who resolved the most of these is the suggestion. Say why in one line, citing the ticket keys and what they fixed (from the resolving comment), for example "Arjun Kumar resolved both earlier Contoso EU latency incidents (INC-39412, INC-39750)".
3. **Preview and wait:**
   ```
   Assign INC-40211 and INC-40302 to Arjun Kumar and add this work note:
   "Assigned to Arjun Kumar ahead of the Contoso Ltd renewal (Dec 31). Related CIO escalation on Nov 4: EU API latency and morning export timeouts. Arjun resolved INC-39412 and INC-39750 for this customer."
   Approve?
   ```
4. After yes: `lookupJiraAccountId` for the owner, then for each ticket `editJiraIssue` with `fields: {"assignee": {"accountId": "<id>"}}` and `addCommentToJiraIssue` with the work note. Read each ticket back with `getJiraIssue` and report it as a write: "Written to Jira via Rovo: <key> assigned to <owner>, work note added" with the link.

## Step 2. Renewal proposal email (Outlook)

1. Draft the email using `drafting.md` → "Proposal email". To: the buyer from the pricing thread. Cc: the executive sponsor and the customer success manager.
2. **Preview the full email** (To, Cc, Subject, body) and wait. Accept edits.
3. After yes: send it with the user's Outlook/email capability. If you can only create a draft, create it and tell the user it's in Drafts. Never send without the yes.

## Step 3. Renewal contract draft (Word)

1. Open the current order form for the account and the renewal order form template from the user's OneDrive (search Microsoft 365 for "Order Form" with the account name, and "Renewal Order Form template").
2. Fill the template using `drafting.md` → "Renewal order form". Every number must match Salesforce and the agreed pricing position.
3. Create the Word document in the same OneDrive folder as the current order form, named `<Account> - Renewal Order Form FY<yy> (DRAFT).docx`. Creating a draft document doesn't need approval, but don't share it.
4. Report the link and a 4-line summary: term, fee, change from prior term, roadmap commitments.

## Step 4. Update the Salesforce opportunity

1. **Preview and wait:**
   ```
   Update "<opportunity name>":
   - Stage: <current> → Proposal/Price Quote
   - Amount: $2,400,000 → $2,520,000 (5% uplift cap agreed Oct 8)
   - Next step: "Proposal sent <today>. Follow up with Daniel by <today + 5 business days>; contract draft with Legal."
   And log a completed Email task "Sent FY27 renewal proposal" on it, related to <buyer>.
   Approve?
   ```
2. After yes, with `dispatch`:
   - `PATCH /services/data/v62.0/sobjects/Opportunity/<OPP_ID>` with body `{"StageName": "Proposal/Price Quote", "Amount": <new amount>, "NextStep": "<text>"}` (expect status 204).
   - `POST /services/data/v62.0/sobjects/Task` with body `{"Subject": "Sent FY27 renewal proposal", "WhatId": "<OPP_ID>", "WhoId": "<buyer contact Id>", "Status": "Completed", "Type": "Email", "TaskSubtype": "Email", "Priority": "Normal", "ActivityDate": "<today>", "Description": "<one-line summary of the proposal>"}` (expect status 201).
   - If step 2 was skipped, leave Stage unchanged and say why.
3. Read the opportunity back with `dispatch_readonly` (`GET /services/data/v62.0/sobjects/Opportunity/<OPP_ID>`) and report it as a write: "Written to Salesforce: <field> <old> → <new>" with the record link.

## Pricing guardrail

If the user asks to match or approach the competitor's discount, or to go below the agreed position: don't put it in the email or contract. Say it needs approval from the sales director (from the internal chat or the template's approval rules), cite the win/loss evidence, and offer to create a Salesforce Task for that approval (same preview and approval rule, `OwnerId` = the director's Salesforce user Id from `SELECT Id, Name FROM User WHERE Name = '<name>'`).

## Finish

Show the final plan table, then the writes:

```
### Written back to your systems
| System | Record | Change |
|---|---|---|
| Jira via Rovo | INC-40211 (link) | Assignee → Arjun Kumar; work note added |
| Salesforce | <opportunity> (link) | Amount $2.4M → $2.52M; next step updated |
```

Then one line on anything still open (for example "SSO commitment answered in the proposal; Legal review of the contract draft pending").
