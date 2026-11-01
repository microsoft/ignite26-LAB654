# Bring your own app: Verdantis Expense

> **Duration:** ~20 minutes | **Connectors:** Verdantis Expense (custom MCP connector), Outlook | **Surfaces:** Microsoft 365 admin center, Copilot Chat, Excel

## What you'll take away

- **Connect your own app, with no code.** Point Copilot at the app's MCP server from the admin center. It sits next to the catalog connectors, under the same admin controls.
- **Finish a real job end to end.** You go from receipts in your inbox to a report that's checked, fixed and submitted, without opening the expense tool.
- **Your company's rules, built in.** A travel-policy skill checks every report before it goes anywhere, so it's right the first time.

## The story

Verdantis runs much of its work on apps it built itself, and **Verdantis Expense** is the one everyone uses for travel. It's built in-house, so no connector catalog will ever list it. But the app team has put it behind an MCP server, so you'll connect it yourself.

Later that week, you're back from a client trip to Seattle. Verdantis Expense emails a reminder: submit the trip by Friday, November 20. Your receipts are scattered across your inbox, and your last report was rejected for a missing receipt. This time, you'll file it from Copilot and get it right first time.

## Before you start

- [ ] You finished one of the tracks: [Finance](03-finance.md), [Legal](04-legal.md), [Productivity](05-productivity.md) or [Engineering](06-engineering.md).
- [ ] You can open the **Microsoft 365 admin center**. Lab seats have admin rights.
- [ ] You have the **Verdantis Expense MCP server address** from your seat card.

## Set up Verdantis Expense

*Microsoft 365 admin center · no prompts*

1. Go to **Copilot › Connectors › Gallery** and search for *Verdantis Expense*. It isn't listed, because it's built in-house.
2. Go to **Agents › Settings › Agent and plugin access** and make sure **Allow agents and plugins built by your organization** is selected.
3. Back in the Gallery, under **Created by your org**, select **Create a new connector**, then **Connect to MCP server**.
4. Enter the display name **Verdantis Expense** and the MCP server address from your seat card. Set authentication to **No Auth**, then select **Save**.
5. Under **Staged rollout**, make it available to yourself. Verdantis Expense now appears in **Your connections**, next to the catalog connectors.
6. In Copilot, open **… › Settings › Sources** and connect **Verdantis Expense**.

> [!TIP]
> That's the whole integration. Any app your company can put behind an MCP server can be connected this way, and admins govern it like any other connector.

Run Steps 1–4 in **one Copilot chat**. Each new chat starts from the original data.

## Step 1: Check where you stand

*Copilot Chat · Verdantis Expense*

```text
Using Verdantis Expense, which expense reports do I still have open, and why was any of them rejected or returned?
```

**What to look for:**

- Four open reports.
- **ER-1044** (Dallas) was rejected: the $142.60 Pappas Bros receipt is missing.
- **ER-1046** was returned: it has no business purpose.
- **ER-1045** (Austin, $631.50) and **ER-1051** (October local expenses, $953.09) are pending approval.

## Step 2: File the trip

*Same chat · Outlook · Verdantis Expense*

```text
Find the receipts from my Seattle trip in my email and create an expense report in Verdantis Expense for the Fabrikam partnership review. Check it against our travel policy before anything is submitted.
```

**What to look for:**

- Draft report **ER-2001**: six items totalling **$2,052.65**, with every receipt attached.
- **Blocking:** the Westin charged $389 for the night of Oct 28, which is $139 over the $250 Seattle cap.
- **Warning:** the $52.30 Uber ride was charged twice (TX-10111). Copilot suggests asking Aisha Rahman in Finance Operations to reverse it.

> [!TIP]
> The policy check ran before anything was submitted. That's why the report will be right first time.

## Step 3: Fix and submit

*Same chat · Verdantis Expense · write action*

```text
The last night was a city-wide convention rate, and no hotel near the Fabrikam office was under the cap. Add that as the justification and submit the report to my manager.
```

**What to look for:**

- Copilot reruns the check: no blocking issues and one justified exception.
- An approval card appears. Approve it.
- Copilot confirms that ER-2001 ($2,052.65) was submitted to **Daniel Park**.

Then check the status:

```text
Has my report gone through? Who approves it?
```

ER-2001 is pending approval, and Daniel Park is the approver.

## Step 4: Review your spend

*Same chat · Verdantis Expense · Excel*

```text
How am I tracking against my Q4 travel budget? Put it in an Excel workbook with a chart.
```

**What to look for:**

- You've spent **$4,309.55 of $6,800** (63%), with about half the quarter gone.
- Over budget on meals and entertainment (106%) and ground transport (111%); lodging is at 80%.
- An Excel workbook with a chart.

## If it goes wrong

| What happens | What to do |
|---|---|
| Verdantis Expense doesn't appear in Sources | Check that staged rollout includes you, then refresh Copilot. |
| Copilot doesn't use Verdantis Expense | Start the prompt with "Using Verdantis Expense". |
| Step 2 misses some receipts | Ask: "Find all my Seattle receipts from October in my email." |
| Step 3 says ER-2001 doesn't exist | You started a new chat. Rerun Step 2 in this chat first. |

## Checkpoint

- [ ] Verdantis Expense is connected and shows in your sources.
- [ ] ER-2001 was checked against policy, justified and submitted after your approval.
- [ ] You have an Excel summary of your Q4 travel spend.

**What you take away:** If your company can put an app behind an MCP server, Copilot can work with it, under the same admin controls and approvals as every other connector.

---

**Next:** [Summary](08-summary.md)
