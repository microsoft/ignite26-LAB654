# Productivity track: The vendor slipped, so fix the plan before standup

> **Duration:** ~10 minutes (+3 minute stretch) | **Connectors:** Test_Smartsheet, Test_Notion, Verdantis Hub (Test_Intranet) | **Surface:** Copilot Cowork (Copilot Chat also works for Steps 1–4)

## The story

You're coordinating the retail launch of the **Verdantis Aurora** smart-home hub. The launch event is on **Nov 3**.

| Where it lives | What's there |
|---|---|
| **Smartsheet** | The launch tracker: tasks, owners, dates, status, and vendor comments |
| **Notion** | The team's launch plan, weekly sync notes and the Launch Decision Log |
| **Verdantis Hub** (intranet) | Company rules: the Retail Partner Launch Playbook, approved print vendors, partner communication guidelines |
| **Outlook** | Email from Riley at Contoso Retail, the retail partner |

It's Monday, Oct 12. Overnight, the print vendor, Northwind Print, commented on its Smartsheet row: brochures and in-store signage will be a week late. That collides with the POS kit shipment to Contoso Retail stores, and Riley has emailed asking for the kit ETA.

**Your goal:** spot the conflict, check your fix against company policy, update the plan, log the decision, update the partner and book an approval meeting, all without opening Smartsheet, Notion or the intranet.

## Three connector models, one answer

| | Verdantis Hub (Test_Intranet) | Test_Smartsheet | Test_Notion |
|---|---|---|---|
| **Model** | Synced | Hybrid | Federated |
| **How Copilot gets the data** | Indexed once by an admin for everyone | Indexed for search, and read live for the latest values | Read live from Notion |
| **Whose access** | Everyone in the organization | Your Smartsheet permissions | Your Notion permissions |
| **Can Copilot make changes?** | No | Yes, after you approve | Yes, after you approve |

> [!NOTE]
> `Test_…` connectors are mock versions of the real connectors, built for this lab with sample Verdantis data. They're pre-configured, so you don't need a Smartsheet or Notion account.

## Step 0: Check your sources

*~30 sec · Copilot Chat › Settings › Sources*

1. In Microsoft 365 Copilot, open **…** › **Settings** › **Sources**.
2. Confirm **Test_Smartsheet**, **Test_Notion** and **Verdantis Hub (Test_Intranet)** show as **Connected**. If one doesn't, ask a proctor.

Then open **Cowork**. Sources available in Copilot Chat carry over.

## Step 1: Morning catch-up

*~2.5 min · Smartsheet, Notion, Outlook*

```text
I'm coordinating the Verdantis Aurora launch. Give me a catch-up for this week:
- find our Aurora launch tracker in Smartsheet: tasks due in the next
3 weeks, and any new vendor comments
- check the Aurora Launch Plan and latest weekly sync notes in Notion
- check my email for anything from Contoso Retail
Flag any conflicts between vendor updates and the plan.
```

**What to look for:** a short brief with citations to Smartsheet, Notion and Outlook that calls out:

- Northwind Print's slip from **Oct 16 → Oct 23**, or a split: brochures Oct 20, signage Oct 23.
- The conflict with **"Ship POS kits to Contoso Retail stores"**, due **Oct 21**.
- Riley asking for the kit ETA. Stores need kits before staff training on **Oct 27**.
- Good news: Fabrikam Creative says the hero video is approved, but its status still says *In Progress*.

> [!TIP]
> You didn't name the sheet exactly. Copilot found the **Verdantis Aurora Launch Tracker** among several similar sheets, and it only sees what you can see.

## Step 2: Check the fix against company policy

*~1.5 min · Verdantis Hub*

Your first idea is to ship the kits without signage and send the signage later. Check it:

```text
My idea: ship the POS kits to Contoso Retail on Oct 21 without signage, and
send the signage on Oct 27. Check the Retail Partner Launch Playbook on Verdantis
Hub. Is that allowed? Who has to approve it? And do we have an approved backup
print vendor?
```

**What to look for:** an answer citing the *current* playbook, not the archived 2025 version:

- **No.** Every POS kit wave must be in partner stores at least 3 days before staff training, so signage must arrive by **Oct 24**.
- A split shipment **is** allowed, with approval from the Retail Ops lead (**Sam**), and must be logged in the Launch Decision Log.
- Northwind's split offer works: ship signage express on **Oct 23**, arriving **Oct 24**.
- Backup vendor: **Litware Print**, 3-business-day rush, +15% surcharge, Procurement approval needed.

Copilot didn't just answer; it stopped you from breaking a partner commitment.

## Step 3: Fix the plan in Smartsheet

*~1.5 min · Smartsheet write actions*

```text
Update the Verdantis Aurora Launch Tracker in Smartsheet:
1. "Print brochures & in-store signage": due date Oct 23, status At Risk
2. "Final hero video": status Complete
3. Add a comment on "Ship POS kits to Contoso Retail stores": wave 1 (kits +
brochures) ships Oct 21; wave 2 (signage) ships express Oct 23, in stores
Oct 24 per the playbook. Pending Retail Ops approval.
```

**What to look for:** a confirmation card before each change.

1. Expand the card and review the parameters: which rows and which values.
2. Select **Allow once**.
3. Copilot confirms the rows changed.

> [!NOTE]
> Write actions run in Smartsheet as you, with your permissions, and only after you approve. The card offers **Allow once**, **Allow for conversation** or **Always allow**. The choice applies per tool. You can reset it in **Settings › Sources › Test_Smartsheet**.

## Step 4: Log the decision in Notion

*~1.5 min · Notion write actions*

```text
Add an entry to the "Launch Decision Log" database in Notion:
Decision: Ship Contoso Retail POS kits in two waves – kits + brochures on
Oct 21, signage express on Oct 23 (in stores Oct 24)
Owner: me · Approver: Sam (Retail Ops) · Status: Proposed
Context: summarize the Northwind delay and link the playbook page and the
Smartsheet row.
```

**What to look for:** a confirmation card, then a new row in the **Launch Decision Log** with the context and links to both the playbook and the Smartsheet row. The playbook said split shipments must be logged, and now this one is.

## Step 5: Tell people and book the approval

*~2 min · Email and Scheduling skills*

```text
Following the partner communication guidelines on Verdantis Hub, draft an email to
Riley at Contoso Retail and the Aurora core team with the new two-wave
timeline, linking the Notion decision. Then schedule a 15-minute "Aurora POS
kit approval" with Sam and the core team tomorrow morning. Show me both
before sending.
```

**What to look for:**

- Cowork loads the **Email** and **Scheduling** skills, which appear as chips in the side panel.
- The draft email follows the intranet's guideline structure: what changed, the impact on you, new dates, what we need from you, and a contact.
- A meeting proposal for tomorrow morning.
- Cowork pauses so you can choose **Send** and **Schedule**.

> [!NOTE]
> All recipients are lab mailboxes in the demo tenant. Riley and Sam are lab users.

## Stretch: interactive launch dashboard

*+3 min · App skill (Frontier preview), if your tenant has it*

```text
Build me an interactive launch dashboard app from the Verdantis Aurora Launch
Tracker: tasks by workstream, at-risk items highlighted, and a timeline to
the Nov 3 launch.
```

## If it goes wrong

| What happens | Try this |
|---|---|
| The catch-up misses the vendor comment | "Show me Northwind Print's latest comment in the Aurora tracker." |
| Copilot picks the wrong sheet | "Use the Verdantis Aurora Launch Tracker sheet." |
| The policy answer comes from general knowledge | "Search Verdantis Hub for the Retail Partner Launch Playbook." |
| After Step 3, Copilot reports the old status | Ask it to read the row live from Smartsheet. The search index refreshes on its next crawl. |
| A connector shows as not connected | Ask a proctor. The `Test_…` connectors are pre-configured. |

## Checkpoint

- [ ] You got one catch-up across Smartsheet, Notion and Outlook, with citations.
- [ ] You checked your fix against the intranet playbook and changed it.
- [ ] You updated Smartsheet and Notion after approving each change.
- [ ] You drafted the partner update and booked the approval meeting.

**What you did:** read → decide → act → communicate, without leaving Copilot and without anything happening that you didn't approve.

---

**Next:** another track ([Finance](03-finance.md) · [Legal](04-legal.md)) or the [Summary](06-summary.md)
