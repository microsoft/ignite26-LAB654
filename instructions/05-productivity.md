# Productivity track: The vendor slipped, so fix the plan before standup

> **Duration:** ~10 minutes (+3 minute stretch) | **Connectors:** Test_Notion, Verdantis Hub (Test_Intranet) | **Surface:** Copilot Cowork

## The story

You're coordinating the retail launch of the **Verdantis Aurora** smart-home hub. The launch event is on **Nov 3**.

| Where it lives | What's there |
|---|---|
| **Notion** | The team workspace: the Aurora launch tracker, the launch plan and the Launch Decision Log |
| **Verdantis Hub** (intranet) | Company rules: the Retail Partner Launch Playbook, approved print vendors, partner communication guidelines |
| **Outlook** | Email from Riley at Contoso Retail, the retail partner |

It's Monday, Oct 12. The print vendor, Northwind Print, updated its row in the Notion launch tracker: brochures and in-store signage will be a week late. That collides with the POS kit shipment to Contoso Retail stores, and Riley has emailed asking for the kit ETA.

**Your goal:** fix the plan, log the decision, tell the partner and book the approval, all without opening Notion or the intranet.

## Two connector models, one answer

| | Verdantis Hub (Test_Intranet) | Test_Notion |
|---|---|---|
| **Model** | Synced | Federated |
| **How Copilot gets the data** | Indexed once by an admin for everyone | Read live from Notion |
| **Whose access** | Everyone in the organization | Your Notion permissions |
| **Freshness** | Re-crawled on a schedule | Real time |
| **Can Copilot make changes?** | No | Yes, after you approve |

> [!NOTE]
> `Test_…` connectors are mock versions of the real connectors, built for this lab with sample Verdantis data. They're pre-configured, so you don't need a Notion account.

## Step 0: Check your sources

*~30 sec · Copilot Chat › Settings › Sources*

1. In Microsoft 365 Copilot, open **…** › **Settings** › **Sources**.
2. Confirm **Test_Notion** and **Verdantis Hub (Test_Intranet)** show as **Connected**. If one doesn't, ask a proctor.

Then open **Cowork**. Sources available in Copilot Chat carry over.

## Step 1: Read your scheduled morning catch-up

*~2 min · Notion, Outlook*

Copilot already ran a scheduled prompt for you this morning. Open the **Aurora morning catch-up** result. This is the prompt it ran:

```text
I'm coordinating the Verdantis Aurora launch. Give me a catch-up for this week:
- from the Aurora launch tracker in Notion: tasks due in the next 3 weeks
and any vendor updates
- anything in my email from Contoso Retail
Flag any conflicts between vendor updates and the plan.
```

> [!TIP]
> If you don't see the scheduled result, paste the prompt above into Cowork and run it now.

**What to look for:** a short brief with citations to Notion and Outlook that calls out:

- Northwind Print's slip from **Oct 16 → Oct 23**, or a split: brochures Oct 20, signage Oct 23.
- The conflict with **"Ship POS kits to Contoso Retail stores"**, due **Oct 21**.
- Riley asking for the kit ETA. Stores need kits before staff training on **Oct 27**.

Copilot did the catch-up before you started your day. Any prompt you run every morning can be scheduled.

## Step 2: Check the fix against company policy

*~2 min · Verdantis Hub*

Your first idea is to ship the kits without signage and send the signage later. Check it:

```text
My idea: ship the POS kits to Contoso Retail on Oct 21 without signage, and
send the signage on Oct 27. Check the Retail Partner Launch Playbook on
Verdantis Hub. Is that allowed? Who has to approve it?
```

**What to look for:** an answer citing the *current* playbook, not the archived 2025 version:

- **No.** Every POS kit wave must be in partner stores at least 3 days before staff training, so signage must arrive by **Oct 24**.
- A split shipment **is** allowed, with approval from the Retail Ops lead (**Sam**), and must be logged in the Launch Decision Log.
- Northwind's split offer works: ship signage express on **Oct 23**, arriving **Oct 24**.

Copilot didn't just answer; it stopped you from breaking a partner commitment.

## Step 3: Update the plan and log the decision

*~2.5 min · Notion write actions*

```text
In Notion:
1. In the Aurora launch tracker, set "Print brochures & in-store signage" to
due Oct 23, status At Risk.
2. Add an entry to the Launch Decision Log: ship Contoso Retail POS kits in two
waves (kits + brochures Oct 21; signage express Oct 23, in stores Oct 24).
Owner: me. Approver: Sam Patel. Status: Proposed. In Context, summarize the
Northwind delay and link the playbook page.
```

**What to look for:** a confirmation card before each change (`notion-update-page`, then `notion-create-pages`).

1. Expand the card and review the parameters: which row or page, and which values.
2. Select **Allow once**.
3. Copilot confirms both changes.

> [!NOTE]
> Write actions run in Notion as you, with your permissions, and only after you approve. The card offers **Allow once**, **Allow for conversation** or **Always allow**. The choice applies per tool. You can reset it in **Settings › Sources › Test_Notion**.

> [!IMPORTANT]
> Test_Notion is shared by everyone in the lab, so your changes are kept only **in this conversation**. Ask Copilot to show the tracker here and you'll see them. A new conversation, or this one after about 2 hours, shows the original data.

The playbook said split shipments must be logged, and now this one is.

## Step 4: Email the partner and book the approval

*~2.5 min · Email and Scheduling skills*

```text
Following the partner communication guidelines on Verdantis Hub, draft an
email to Riley at Contoso Retail with the new two-wave timeline, cc Sam Patel.
Then schedule a 15-minute "Aurora POS kit approval" with Sam tomorrow
morning. Show me both before sending.
```

**What to look for:**

- Cowork loads the **Email** and **Scheduling** skills, which appear as chips in the side panel.
- The draft email follows the intranet's guideline structure: what changed, the impact on you, new dates, what we need from you, and a contact.
- A meeting proposal with Sam for tomorrow morning.
- Cowork pauses so you can choose **Send** and **Schedule**.

> [!NOTE]
> Riley Blake and Sam Patel are lab users in the demo tenant. Nothing leaves the tenant.

## Stretch: interactive launch dashboard

*+3 min · App skill (Frontier preview), if your tenant has it*

```text
Build me an interactive dashboard app from the Aurora launch tracker.
```

## If it goes wrong

| What happens | Try this |
|---|---|
| The scheduled catch-up isn't there | Paste the Step 1 prompt and run it. |
| The catch-up misses the vendor update | "Show me Northwind Print's latest vendor update in the Aurora launch tracker in Notion." |
| Copilot picks the wrong tracker | "Use the Verdantis Aurora Launch Tracker database." |
| The policy answer comes from general knowledge | "Search Verdantis Hub for the Retail Partner Launch Playbook." |
| A connector shows as not connected | Ask a proctor. The `Test_…` connectors are pre-configured. |
| Your Notion changes are gone | They're kept only in the conversation that made them. Go back to that conversation, or redo Step 3. |

## Checkpoint

- [ ] You read a catch-up across Notion and Outlook that Copilot prepared on a schedule.
- [ ] You checked your fix against the intranet playbook and changed it.
- [ ] You updated the tracker and logged the decision in Notion after approving each change.
- [ ] You drafted the partner update and booked the approval meeting.

**What you did:** Copilot prepared your morning, checked company policy, updated the plan and closed the loop with your partner. You approved every change, and you never opened Notion or the intranet.

---

**Next:** another track ([Finance](03-finance.md) · [Legal](04-legal.md)) or the [Summary](06-summary.md)
