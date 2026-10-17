# Legal track: Can we sign on the 15th?

> **Duration:** ~15 minutes | **Connectors and agents:** Work IQ (email and Teams), Harvey, Test_iManage | **Surfaces:** Copilot Chat, Word Legal Agent, Copilot Cowork

## The story

Verdantis wants to use **Cognivault Nexus**, an AI underwriting platform, to help decide who gets a car or home insurance policy and at what price: up to 4 million decisions a month. It's a five-year, **$14.75 million** deal.

When an AI helps set insurance prices, regulators care. Insurance regulators in states like Colorado and New York hold the insurer responsible, even when the AI belongs to a vendor. So Verdantis needs a contract that lets it check, explain and control the AI, and, because the AI is trained on Verdantis's claims data, it wants to own what gets built.

Nothing is signed. Cognivault sent its own contract, written in its favor. A negotiation session with Cognivault's lawyer is booked for **Thursday the 15th**.

| Person | Role |
|---|---|
| **Marcus Hollowell** (you) | Associate General Counsel, Technology. You own this contract. |
| Tomás Aguilar | Chief Underwriting Officer. Business owner; wants the AI live by the 18th. |
| Radhika Sengupta | SVP, Procurement. Emailed you the business's must-haves two weeks ago. |
| Priya Ramasubramanian | Cognivault's lawyer. Across the table on the 15th. |

It's Monday morning. Tomás pings you on Teams:

> "Morning Marcus. Have you had a chance to look at Cognivault's contract? We'd like to sign at the session with them on the 15th so we can go live on the 18th. Anything you need from me?"

To answer, you need four things: what's already been decided, what the regulators expect, a redline of Cognivault's contract, and a plain-English answer for the business. That's usually days of digging through email, the document system, legal research and Word. You'll do it in five steps, approving everything.

## Before you start

- [ ] You completed [Getting started with connectors](02-getting-started.md).
- [ ] **Test_iManage** shows as connected in Settings › Sources.
- [ ] You can see Tomás's message in Teams.

The contract and its exhibits are in the iManage matter **Cognivault – Nexus AI Platform Agreement**, together with the **Verdantis AI Procurement Playbook**, the company's rulebook for what it will and won't accept in AI contracts.

## Step 1: Catch up

*Copilot Chat (Work mode) · Work IQ*

Open Copilot and enter:

```text
Can you help summarize the latest discussions and decisions we made with Radhika and Tomás about the Cognivault deal, and what's pending?
```

**What to look for:**

- **Decided:** Verdantis must own the fine-tuned model; no more short-notice model retirements; Delaware law and courts rather than the vendor's arbitration.
- **Radhika's other asks:** control over model changes, explainability for Colorado and New York examiners, a clean exit, and liability that matches the deal size.
- **Pending:** the contract review against the playbook, an answer for Tomás, and what the regulators will expect. The 15th is a negotiation session, not a signing.
- Each point links to the email or chat it came from.

> [!TIP]
> Tomás's message never mentioned model ownership or regulators. Copilot found those decisions in a two-week-old email and a Teams chat.

## Step 2: Check the law

*Same chat · Harvey agent, then Test_iManage*

Follow up on the open regulator question:

```text
@Harvey Colorado and New York regulators are looking hard at AI in underwriting. If we use Cognivault's model for our auto and homeowners policies, what will they expect from us, and what do we need from the vendor to show it?
```

Then check the contract against what Harvey found:

```text
Does the Cognivault agreement in our iManage matter give us those rights? Short table, and save it to the matter as a research note.
```

**What to look for:**

- **Harvey, with sources:** Colorado's insurer AI rule (Regulation 10-1-1), and New York DFS Circular Letter No. 7, under which the insurer stays responsible for vendor AI, so the contract should give audit rights and require the vendor to cooperate with regulators.
- **The gap table:** the draft has no audit right, no bias testing, no regulator cooperation, only 15 days' notice of model changes, and nothing on explainability.
- A bonus finding: the Verdantis playbook itself has no regulator-cooperation clause.
- When you approve, the research note is saved to the matter's **03 Research** folder.

## Step 3: Redline the contract

*Word · Copilot pane · Legal Agent*

1. Select the agreement in Copilot's answer. It opens from iManage in Word.
2. Open the **Copilot** pane and choose the **Legal Agent**.
3. Enter the prompt below. Use **/** to attach the playbook and your research note from iManage.

```text
Redline this version against our AI procurement playbook. What matters most to the business is owning the fine-tuned model and getting real notice before model changes, and we need the regulator rights from my research note. Explain each change in a comment so I can walk Cognivault's counsel through it.
```

**What to look for:** tracked changes, each with a comment explaining why. For example:

- Verdantis owns the fine-tuned model and its outputs (a playbook "hard stop").
- 60 days' notice and Verdantis sign-off for material model changes; retired models kept for 12 months (Tomás's concern).
- A yearly audit, quarterly bias testing and a new clause requiring the vendor to cooperate with regulator inquiries (from your research note).
- The liability cap raised from about $1.36M (6 months of fees) to $5.9M (2× the annual value).
- A 180-day exit, with data returned within 30 days.

## Step 4: Get ready for the 15th

*Copilot Cowork, opened from the Copilot pane in Word*

When your redline is done, open **Cowork** from the same Copilot pane and enter:

```text
I've finished my redline of the Cognivault agreement. Get me ready for the 15th: save it to the matter, turn my changes into a negotiation list with our fallback for each, write a one-page plain-English version for Tomás and Radhika, draft my reply to Tomás, and draft the cover email to Cognivault's counsel.
```

**What to look for:** Cowork shows its plan, then produces:

- A **negotiation list:** one row per tracked change, with Cognivault's draft, Verdantis's ask, the playbook fallback, and "do not concede" items marked.
- A **one-pager** in plain English, such as "Yes to the 15th if Cognivault moves on 3 points", with the regulator points keeping their source links.
- A reply to Tomás, a cover email to Cognivault's counsel, and a note asking the knowledge team to add a regulator-cooperation clause to the playbook.

Nothing is sent yet. Cowork asks before sending any email.

## Step 5: Review and send

*Cowork review list → Word and Outlook*

There's no new prompt. Cowork pauses with items ready for your review. Select each one:

1. Open the one-pager in Word and edit it if you need to.
2. Check the two regulator statements. Each carries the source link Harvey gave in Step 2. Select it to open the New York DFS circular or the Colorado rule.
3. Approve the reply to Tomás and the cover email to Cognivault's counsel. Cowork sends both from your Outlook.

> [!NOTE]
> All recipients are lab mailboxes in the demo tenant. Cognivault's counsel has no real mailbox.

**Result:** Tomás has a clear answer the same morning, Cognivault's counsel gets a reasoned redline before the 15th, and every file is in the iManage matter.

## If it goes wrong

| What happens | Try this |
|---|---|
| Step 1 misses the email or chat | Ask "What did Radhika send me about Cognivault?" and "What did Tomás say in Teams about model retirements?" |
| Copilot can't find the contract | Ask for "the Cognivault AI Vendor Agreement v4.2 in the Cognivault – Nexus matter in iManage". |
| Test_iManage shows as not connected | Ask a proctor. It's pre-configured for the lab. |
| Harvey isn't available | Continue with the second prompt in Step 2, asking Copilot what the Colorado and New York rules require. |

## Checkpoint

- [ ] You summarized decisions and open items from email and Teams.
- [ ] You saved a sourced research note to the iManage matter.
- [ ] You produced a redline with a comment on every change.
- [ ] You reviewed and approved the negotiation pack and emails.

**Optional encore:** after the 15th, ask Copilot "What did we concede?" to update the negotiation list.

---

**Next:** another track ([Finance](03-finance.md) · [Productivity](05-productivity.md)) or the [Summary](06-summary.md)
