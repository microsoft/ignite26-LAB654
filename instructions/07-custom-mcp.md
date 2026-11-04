# Bring your own app: Zava Expense

> **Duration:** ~20 minutes | **Connectors:** Zava Expense (custom MCP connector), Outlook | **Surfaces:** Microsoft 365 admin center, Copilot Chat, Excel

Most companies run part of their work on apps they built themselves, and no connector catalog will ever list those apps. In this module, you'll connect **Zava Expense**, Zava's in-house expense app, as a custom connector, with no code. Employees use Zava Expense to file trip expenses, track their reports and check their travel budget. Zava's app team has already made it available through an MCP server (a standard way for AI tools to talk to an app), so you only need to connect it, then use it to file a trip from Copilot.

## The story

You're back from a client trip to Seattle for the Fabrikam, Inc. partnership review. Zava Expense emails you a reminder: submit your trip expenses by Friday, November 20. Your receipts are scattered across your inbox, and your last report was rejected for a missing receipt. This time, you'll file it from Copilot and get it right the first time.

## What you'll take away

- **Connect your own app, with no code.** Add the app's MCP server in the admin center. It sits next to the catalog connectors, under the same admin controls.
- **Finish a real job end to end.** You go from receipts in your inbox to a report that's checked, fixed and submitted, without opening the expense app.
- **Your company's rules, built in.** Zava Expense checks every report against the travel policy before it's submitted, so it's right the first time.

## Before you start

- [ ] You finished one of the tracks: [Finance](03-finance.md), [Legal](04-legal.md), [Productivity](05-productivity.md) or [Engineering](06-engineering.md).
- [ ] You can open the **Microsoft 365 admin center**. Lab seats have admin rights.

## Set up Zava Expense

> **Where:** Microsoft 365 admin center. There are no prompts in this part.

1. Go to **Copilot › Connectors**.
2. On the **Gallery** tab, under **Created by your org**, select **Create a new connector**, then **Connect to MCP server**.
3. Fill in the form:

   | Field | Enter |
   |---|---|
   | Display name | `Zava Expense` |
   | Description | `Zava's in-house expense app. Use it to see the signed-in employee's expense reports and why any were rejected or returned, find corporate card charges for a trip, create a report from receipts, check it against the Zava travel policy, submit it for manager approval, and compare travel spend with budget.` |
   | Base URL | `https://mock-zava-expense.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp` |
   | Developer name | `Zava` |
   | Website URL | `https://github.com/microsoft/ignite26-LAB654` |
   | Privacy URL | `https://www.microsoft.com/privacy/privacystatement` |
   | Terms of use URL | `https://www.microsoft.com/legal/terms-of-use` |
   | Authentication | **No Auth** |

   (This lab uses **No Auth** so you can connect quickly. In your own tenant, choose the authentication your app needs, such as **Microsoft Entra SSO** or **OAuth 2.0**.)

   > [!TIP]
   > Copilot reads the description to decide when to use Zava Expense and what to ask it. A good description says, in plain words, what data the app holds and what it can do.

4. Select **Save**.
5. Under **Staged rollout**, make Zava Expense available to yourself. It now appears under **Your connections**, next to the catalog connectors. Changes can take up to 10 minutes.
6. In the Microsoft 365 Copilot app, open **… › Settings › Sources** and connect **Zava Expense**.

> [!TIP]
> That's the whole integration. Any app your company can make available through an MCP server can be connected this way, and admins govern it like any other connector.

## Step 1: Check where you stand

> **Where:** Copilot Chat in the Microsoft 365 Copilot app. Start a new chat and run Steps 1 to 4 in it. Each new chat starts from the original data.

```text
Using Zava Expense, show me my open expense reports. Were any of them rejected or sent back, and why?
```

**What to look for:**

- Four open reports.
- **ER-1044** (Dallas) was rejected: the $142.60 Pappas Bros receipt is missing.
- **ER-1046** was returned: it has no business purpose.
- **ER-1045** (Austin, $631.50) and **ER-1051** (October local expenses, $953.09) are pending approval.

## Step 2: File the trip

> **Where:** The same chat. Copilot reads your Outlook inbox and writes to Zava Expense.

```text
Find the receipts from my Seattle trip in my inbox and use them to create a Zava Expense report for the Fabrikam, Inc. partnership review. Check the report against our travel policy, but don't submit it yet.
```

**What to look for:**

- Draft report **ER-2001**: six items totalling **$2,052.65**, with every receipt attached.
- **Blocking:** the Westin charged $389 for the night of Oct 28, which is $139 over the $250 Seattle cap.
- **Warning:** the $52.30 Uber ride was charged twice (TX-10111). Copilot suggests asking Ebere Ibeabuchi in Finance Operations to reverse it.

> [!TIP]
> The policy check ran before anything was submitted. That's why the report will be right the first time.

## Step 3: Fix and submit

> **Where:** The same chat. This step submits the report, so Copilot asks for your approval first.

```text
Add a justification for the $389 Westin night: a city-wide convention pushed up hotel rates, and no hotel near the Fabrikam, Inc. office was under the cap. Then submit the report to my manager.
```

**What to look for:**

- Copilot reruns the check: no blocking issues and one justified exception.
- An approval card appears. Approve it.
- Copilot confirms that ER-2001 ($2,052.65) was submitted to **Hannes Niemi**.

Then check the status:

```text
Has my Seattle report gone through? Who's approving it?
```

ER-2001 is pending approval, and Hannes Niemi is the approver.

## Step 4: Review your spend

> **Where:** The same chat. Copilot creates the Excel workbook for you.

```text
How am I doing against my Q4 travel budget? Put it in an Excel workbook with a chart.
```

**What to look for:**

- You've spent **$4,309.55 of $6,800** (63%), with about half the quarter gone.
- Over budget on meals and entertainment (106%) and ground transport (111%); lodging is at 80%.
- An Excel workbook with a chart.

## If it goes wrong

| What happens | What to do |
|---|---|
| **Create a new connector** is missing or greyed out | In the admin center, go to **Agents › Settings › Agent and plugin access** and select **Allow agents and plugins built by your organization**. |
| Zava Expense doesn't appear in Sources | Check that staged rollout includes you, wait a few minutes, then refresh Copilot. |
| Copilot doesn't use Zava Expense | Start the prompt with "Using Zava Expense". |
| Copilot says Zava Expense isn't responding | Wait 15 seconds, then send the same prompt again in the same chat. |
| Step 2 misses some receipts | Ask: "Find all my Seattle receipts from October in my inbox." |
| Step 3 says ER-2001 doesn't exist | You started a new chat. Rerun Step 2 in this chat first. |

## Checkpoint

- [ ] Zava Expense is connected and shows in your sources.
- [ ] ER-2001 was checked against policy, justified and submitted after your approval.
- [ ] You have an Excel summary of your Q4 travel spend.

**What you take away:** If your company can make an app available through an MCP server, Copilot can work with it, under the same admin controls and approvals as every other connector.

---

**Next:** [Summary](08-summary.md)
