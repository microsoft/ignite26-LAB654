# Productivity track: Sales pitch prep

> **Duration:** ~10 minutes (+ stretch) | **Connectors:** Test_Salesforce, Test_Confluence, Teams, Outlook | **Surface:** Copilot Cowork

## What you'll take away

- **A skill that knows how sales teams work:** Salesforce's call-prep skill builds a brief from your real account data.
- **Grounded answers that keep you in policy:** Copilot quotes what the customer said and checks it against your pricing policy before you say it in the room.
- **From answer to action:** one prompt books a meeting and logs it in your CRM, with your yes before each change.

## The story

You're **Emil Vanggaard** at Zava, and you own the **Lakeshore Retail** account. Lakeshore Retail has piloted the **Aurora** smart-home hub in 50 stores for six weeks, ahead of the public launch event on Dec 8. Your next step is the **expansion pitch** to roll it out to all 400 stores.

- Atul Manohar, Lakeshore Retail's Director of Store Operations, emailed ahead of the pitch. Their CFO, **Nanami Nakayama**, is joining and wants the all-in cost for 400 stores. Lakeshore Retail IT (**Jahidi Juma**) wants Zava's security documentation before anything goes to 400 stores.
- On the Teams pilot review call, Atul said a competitor, Boulder Innovations, quoted about 20% under your list price.

You'll prep the call, handle the price objection and book the security review, without leaving Copilot.

## Before you start

- [ ] You completed [Getting started with connectors](02-getting-started.md).
- [ ] **Test_Salesforce** and **Test_Confluence** show as connected.
- [ ] Open **Copilot Cowork** and start a new task. Run every step in this one conversation: Step 3 reuses what Copilot learned in Steps 1 and 2.

To see what Copilot will read, open the [Lakeshore Retail account](https://mock-salesforce.yellowsand-9530f5dc.eastus.azurecontainerapps.io/lightning/r/Account/001Hp0000000001IAA/view) in Test_Salesforce.

## Step 1: Prep the call

*Copilot Cowork · Test_Salesforce call-prep skill · Outlook*

```text
Prep me for my Lakeshore Retail expansion pitch.
```

**What to look for:**

- The deal: the [*Lakeshore Retail – Aurora 400-store rollout*](https://mock-salesforce.yellowsand-9530f5dc.eastus.azurecontainerapps.io/lightning/r/Opportunity/006Hp0000000001IAA/view) opportunity, Proposal/Price Quote, $1,200,000.
- Who's in the room: Atul (champion), Jahidi (IT security; wants the security review first) and Nanami (CFO; wants the all-in cost).
- What to cover: the price comparison, the security review and next steps.

The layout can vary between runs. The content is what matters.

> [!TIP]
> One prompt turned the CRM and your inbox into a brief that already points to the pitch's two risks: the CFO's cost question and IT's security review.

## Step 2: Handle the price objection

*Same conversation · Teams · Test_Confluence*

```text
Lakeshore Retail said Boulder Innovations is 20% cheaper. What exactly did they say on the pilot review call, and what can I offer within our pricing policy?
```

**What to look for:**

- Quotes from the Teams meeting transcript: Atul on the Boulder Innovations quote and "sign this quarter", Atul on Nanami wanting the all-in cost, and Jahidi on the security review.
- The current *Aurora Retail Pricing & Discount Policy* in Confluence: up to 12% at 250+ stores with no approval; 12–15% needs Zoe Armstrong; above 15% needs VP Sales and Deal Desk. Copilot says **20% can't be offered in the pitch**.
- The in-policy counter: 12% (about $1.06M for 400 stores) plus bundled in-store install and staff training, which don't count as discount.
- The Boulder Innovations battlecard: about $3,250 all-in per store against Zava's $2,640. That's the number Nanami asked for.

> [!TIP]
> Copilot caught the non-compliant answer before you said it to the CFO, and turned the price gap into an all-in cost argument.

## Step 3: Book the security review and log it

*Same conversation · Test_Salesforce schedule-meeting skill · Outlook calendar · write actions*

```text
Send Jahidi and Atul a calendar invite for a 45-minute Aurora security review next week, and log it on the Lakeshore Retail opportunity.
```

**What to look for:**

1. Copilot finds Jahidi and Atul and the open opportunity in Salesforce, checks your calendar and proposes two or three slots next week.
2. **First confirmation:** a preview of the invite, with an agenda built from Steps 1 and 2. Approve it, and Copilot creates the Outlook invite.
3. **Second confirmation:** a preview of the Salesforce event. Approve it, and Copilot logs the event on the opportunity.
4. A confirmation with a link to the Salesforce record.

> [!TIP]
> One prompt booked the meeting and updated the CRM, and nothing changed until you said yes.

## Stretch: Send the pre-read

*Same conversation · Outlook (draft only)*

```text
Draft an email to Atul and Nanami ahead of the pitch: confirm the agenda and link our security FAQ and the Wide World Importers case study.
```

Copilot creates an Outlook draft with the agenda and links to the two Confluence pages. It stays a draft.

Or try: `Log the pilot review call on the Lakeshore Retail opportunity.`

## If it goes wrong

| What happens | What to do |
|---|---|
| Copilot asks which account or meeting | Reply: "The Lakeshore Retail expansion pitch." |
| The brief doesn't mention Nanami | Ask: "Who's on the call, and what does each of them care about?" |
| Step 2 answers from general knowledge | Reply: "Use the Teams recording of the Lakeshore Retail pilot review and our pricing policy in Confluence." |
| Slot picking runs long | Reply: "The first slot." |
| Copilot asks whether to email or invite | Reply: "Send the invite." |

## Checkpoint

- [ ] Your call brief covers the deal, all three attendees and the two risks.
- [ ] Copilot refused the 20% discount and proposed the in-policy counter with the all-in cost.
- [ ] The security review is on your calendar and logged on the Lakeshore Retail opportunity.

**What you take away:** Copilot moved from finding information to finishing the job: a brief, a compliant answer, a booked meeting and an updated CRM, with you approving each change.

---

**Next:** [Bring your own app](07-custom-mcp.md), or try another track ([Finance](03-finance.md) · [Legal](04-legal.md) · [Engineering](06-engineering.md))
