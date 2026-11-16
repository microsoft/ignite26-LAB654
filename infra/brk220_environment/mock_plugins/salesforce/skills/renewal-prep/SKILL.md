---
name: renewal-prep
description: >-
  Prepare for and de-risk a customer renewal across CRM, support tickets, the knowledge base and Microsoft 365. Two modes. BRIEF: one renewal brief with the contract, open incidents, pricing position, competitor pressure, open customer asks and stakeholders. Use when the user says "prep me for my <account> renewal", "renewal prep for <account>", "where do we stand on the <account> renewal" or "what's at risk on <account>". CLOSE-OUT: plan and run the steps that remove renewal risk, with an approval before every write: assign owners to incident tickets, send the renewal proposal email, draft the renewal contract in Word and update the Salesforce opportunity. Use when the user says "close out the <account> risks before renewal", "assign owners to the <account> tickets and send the renewal proposal", "draft the <account> renewal contract" or "turn the renewal brief into action". Not for new-business deals or for prepping a single meeting (use call-prep for that).
---

# Renewal prep

Two modes share one set of sources. Pick the mode from the request; if the user asks for both, run BRIEF first.

| Mode | Trigger | Writes | Workflow |
|---|---|---|---|
| BRIEF | "Prep me for my <account> renewal" | None | `references/brief.md` |
| CLOSE-OUT | "Close out the <account> risks before renewal: …" | Jira, Outlook, Word, Salesforce, each after approval | `references/close-out.md` |

Read the workflow file for the mode completely before the first tool call, then follow it. Use `references/drafting.md` for the proposal email and the contract.

## Sources

| Source | How to reach it | What it holds |
|---|---|---|
| Salesforce | Salesforce connector: `dispatch_readonly` for reads, `dispatch` for writes | Account owner, renewal opportunity (amount, close date, stage, competitor), contacts, closed deals against the same competitor (win/loss) |
| Jira | Rovo connector: `searchJiraIssuesUsingJql`, `getJiraIssue`, `lookupJiraAccountId`, `editJiraIssue`, `addCommentToJiraIssue` | Customer incidents (project INC, label `customer-<name>`), owners, and who resolved similar incidents before |
| Confluence | Confluence connector: search Microsoft 365 for the page (don't use Rovo for Confluence) | Account overview with open customer asks; Product roadmap dates approved for customer commitments |
| Microsoft 365 | Work IQ / Microsoft 365 search available to you | Pricing emails with the buyer, QBR transcript and notes, internal Teams escalation chats, the prior order form and the renewal template in OneDrive |

## Ground rules

1. **Resolve the right account first.** Search Salesforce accounts owned by the user (`USING SCOPE mine`). If more than one matches, or none does, list what you found and ask; don't guess. Several companies can share a name (for example Contoso Ltd and Contoso Pharmaceuticals). Use the account's Jira label and Confluence page for that exact account only.
2. **Every fact has a citation.** Cite each number, date and quote inline, and fill the Source columns of the output with the system it came from: Salesforce, Jira via Rovo, Confluence, Outlook, Teams, the meeting or OneDrive. Name systems only this way, never by a connector's internal name. If a source returns nothing, say so; never fill gaps from general knowledge.
3. **Numbers come from the systems.** Contract value, renewal date and amounts from Salesforce; ticket priority, owner and age from Jira (age = today minus `created`, in days); the agreed pricing position from the customer email thread. Don't round or restate them differently in different sections.
4. **Pricing discipline.** The agreed pricing position (for example an uplift cap the buyer accepted in writing) is the floor for anything you draft. Never propose a discount or go below the agreed position because a competitor quoted lower; flag it and name who must approve (the sales director named in the internal chat or the template's approval rules). Use the win/loss history against the same competitor as evidence.
5. **Human in the loop for every write.** In CLOSE-OUT, show a preview of each write and wait for an explicit yes for that step before calling any write tool or sending anything. A yes for one step doesn't approve the next. If the user declines, skip the step and mark it "Skipped" in the plan.
6. **Roadmap commitments** only use capabilities and dates the Product roadmap page marks as committable, in its approved wording.
7. **Keep it on one screen.** Tables over prose for numbers and tickets. No tool names, JSON or query text in the answer.
8. **Salesforce calls are fixed.** Use only the `dispatch_readonly` and `dispatch` calls written in the workflow files. Never call `discover` or `describe`: every URL and query you need is already in the skill.
9. **Make writes visible.** Every write names the system it changed and links to the record, for example "Written to Jira via Rovo: INC-40211 assigned to Arjun Kumar".
