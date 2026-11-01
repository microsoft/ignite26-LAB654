# Custom connector track: Bring your own app

> Source: *LAB654_LOB_Track_ContosoExpense.docx* (owner: Anshuman, + Teekam). Converted to Markdown for reference; formatting differs from the original, wording is preserved.
>
App: Verdantis Expense (custom MCP connector) | ~20 min hands-on | Owner: Anshuman (+ Teekam)

## What attendees take away

- **Connect your own app, with no code.** Point Copilot at the app's MCP server from the admin center. It sits next to the catalog connectors, under the same admin controls.
- **Finish a real job end to end.** Marcus goes from receipts in his inbox to a report that is checked, fixed and submitted, without opening the expense tool.
- **Your company's rules, built in.** A Verdantis travel-policy skill checks every report before it goes anywhere, so it's right the first time.

## The story

### Set up Verdantis Expense

You're Marcus Hollowell. Verdantis runs much of its work on apps it built itself, and Verdantis Expense is the one everyone uses for travel. You already use Copilot with your other work apps, and you'd like it to work with Verdantis Expense too. Your expense tool is built in-house, so its not part of the copilot catalog will ever list it. But the app team has put it behind an MCP server, so you connect it yourself, with no code.

### Use Copilot to file your expenses

Later that week, you're back from a client trip to Seattle. Verdantis Expense emails a reminder: submit the trip by Friday, November 20. Your receipts are scattered across your inbox, and your last report was rejected for a missing receipt. This time, you file it from Copilot and get it right first time.

### At a glance

| | |
|---|---|
| **Persona** | Marcus Hollowell, the only user. He sets up Verdantis Expense, then uses Copilot to file his expenses. |
| **The app** | Verdantis Expense: Verdantis' own expense system, reached through its MCP server. Not in any connector catalog. |
| **Goal** | The Seattle report passes policy and is submitted first time, without Marcus ever opening the expense tool. |

### Scenario script: read to the room (~50 sec)

> Every company has apps no connector catalog will ever list: its own expense system, its own HR tools, its own databases. You're Marcus at Verdantis, and you want Copilot to work with Verdantis Expense. Search the gallery, and it isn't there. So you'll connect it yourself, with no code.
>
> Later that week, Marcus is back from a client trip to Seattle. A reminder says the trip is due Friday, November 20, his receipts are buried in his inbox, and his last report was rejected for a missing receipt. Now that Verdantis Expense is in Copilot, he files the whole trip in one conversation, and gets it right first time.

## The job, in four steps

| Step | Min | Question | Output |
|---|---|---|---|
| Set up Verdantis Expense | 0–4 | Our expense tool isn't in the gallery. How do I connect it? | Verdantis Expense available in Copilot |
| 1 · Check where I stand | 4–7 | What's still open, and why was anything rejected? | Open reports and their reasons |
| 2 · File the trip | 7–12 | Can I file Seattle from my receipts, checked against policy? | Draft report with two issues flagged |
| 3 · Fix and submit | 12–16 | Can I fix the issue and get it submitted? | Report submitted, after Marcus approves |
| 4 · Review my spend | 16–20 | How am I tracking against my travel budget? | Excel summary of Q4 spend vs budget |

Each step feeds the next: the rejected Dallas report in step 1 shows why every receipt matters, step 2 checks every receipt, step 3 fixes what step 2 caught, and step 4 counts the submitted report.

## Set up Verdantis Expense

These are clicks in the Microsoft 365 admin center, not prompts. Lab seats have admin rights, so Marcus does this himself.

1. In the Microsoft 365 admin center, go to **Copilot › Connectors › Gallery** and search for Verdantis Expense. It isn't listed, because it's built in-house.
2. Go to **Agents › Settings › Agent and plugin access** and make sure **Allow agents and plugins built by your organization** is selected.
3. Back in the Gallery, under **Created by your org**, select **Create a new connector**, then **Connect to MCP server**.
4. Display name: Verdantis Expense. Base URL: the MCP server address (provided). Authentication: No Auth for the lab. Select **Save**.
5. Make it available to yourself under **Staged rollout**. Verdantis Expense now appears in **Your connections**, next to the catalog connectors.
6. In Copilot, open **… › Settings › Sources** and connect Verdantis Expense.

**Say this:** "That's the whole integration. Any app your company can put behind an MCP server can be connected this way, and admins govern it like any other connector."

## Use Copilot to file your expenses

Run steps 1–4 in one Copilot chat: each new chat starts from the original data.

| Step | Prompt | Expected response |
|---|---|---|
| 1 | Using Verdantis Expense, which expense reports do I still have open, and why was any of them rejected or returned? | Four open reports:<br>• ER-1044 (Dallas) was rejected because the $142.60 Pappas Bros receipt is missing.<br>• ER-1046 was returned because it has no business purpose.<br>• ER-1045 (Austin, $631.50) is pending approval.<br>• ER-1051 (October local expenses, $953.09) is pending approval. |
| 2 | Find the receipts from my Seattle trip in my email and create an expense report in Verdantis Expense for the Fabrikam partnership review. Check it against our travel policy before anything is submitted. | Draft report ER-2001 has 6 items totalling $2,052.65, with every receipt attached.<br>• Blocking: the Westin charged $389 for the night of Oct 28, which is $139 over the $250 Seattle cap.<br>• Warning: the $52.30 Uber ride was charged twice (TX-10111). Ask Aisha Rahman in Finance Operations to reverse it. |
| 3a | The last night was a city-wide convention rate, and no hotel near the Fabrikam office was under the cap. Add that as the justification and submit the report to my manager. | Copilot reruns the check, which now shows no blocking issues and one justified exception. An approval card appears.<br>After Marcus approves, Copilot confirms that ER-2001 ($2,052.65) was submitted to Daniel Park. |
| 3b | Has my report gone through? Who approves it? | ER-2001 is pending approval. It was submitted today, and Daniel Park is the approver. |
| 4 | How am I tracking against my Q4 travel budget? Put it in an Excel workbook with a chart. | Marcus has spent $4,309.55 of his $6,800 budget (63%), with 51% of the quarter gone.<br>He's over budget on meals and entertainment (106%) and ground transport (111%), and lodging is at 80%. |
