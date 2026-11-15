# Finance track: Should we buy more Litware?

> **Duration:** ~20 minutes | **Connectors:** LSEG_Lab, FactSet_Lab, Moodys_Lab | **Surfaces:** Copilot Chat, Copilot Cowork

In this module, you'll use the **LSEG**, **FactSet** and **Moody's** connectors to take one investment question from a quick sense check to a committee-ready memo, across Copilot Chat and Copilot Cowork.

## The story

Zava, an insurer, invests the premiums it holds, and Litware, a chipmaker, is one of its biggest holdings. Kristian Stensen, who runs the portfolio, messages you on Teams:

> "Committee wants a view on Litware Monday. Should we add more? Bring a short memo."

The committee will challenge the case, so every number has to be sourced and checked. For Monday, you need:

1. Is the business beating expectations?
2. Is it stronger than its rivals?
3. What's the upside and downside at today's price?
4. A view that survives tough questions, written up as a memo.

*Not in finance?* The same steps work for any business case.

<details><summary>New to finance? Terms you'll see</summary>

| Term | Meaning |
|---|---|
| EPS (earnings per share) | Profit divided by the number of shares |
| Consensus | The average forecast from analysts who follow the company |
| Gross margin | How much of each $1 of sales is left after making the product |
| ROIC | Profit earned on the money put into the business |
| P/E (price-to-earnings) | How much investors pay for $1 of profit |
| FY1 / FY2 | This fiscal year / next fiscal year |
| Bear / base / bull | Worst, middle and best case |
| Credit rating | A grade for how likely a company is to repay its debts |
| SWOT | Strengths, weaknesses, opportunities and threats |

</details>

## What you'll take away

- **Trusted data where you work.** LSEG, FactSet and Moody's answer in Copilot, with every number cited.
- **Connect once, use everywhere.** The same connectors work in Copilot Chat and Copilot Cowork, and in the workbook Cowork builds in Excel.
- **Partner expertise, not just data.** LSEG and Moody's skills apply their analysts' methods.
- **A case that holds up.** Real Excel formulas, and Copilot challenges your view before the committee does.

## How the track flows

![Step 1 in Copilot Chat gives a verified verdict. Steps 2 and 3 run in one Copilot Cowork task: it builds the workbook, adds scenarios and credit analysis, then gives a pressure-tested view and memo](images/finance-workflow.svg)

| Step | Time | Question | Output |
|---|---|---|---|
| 1 · Sense check | ~5 min | Is Litware worth a closer look? | Quick read on earnings, rivals and credit |
| 2 · Dig into the numbers | ~8 min | What do the numbers say, and what's the upside? | "Litware Committee Pack" workbook: snapshot, scenarios, credit |
| 3 · Back-check and report | ~7 min | Does my view hold up? | Pressure-tested view and committee memo |

## Before you start

- [ ] You completed [Getting started with connectors](02-getting-started.md).

> [!NOTE]
> LSEG, FactSet and Moody's are financial data providers that investment teams use for market data, company fundamentals and credit ratings. **LSEG_Lab**, **FactSet_Lab** and **Moodys_Lab** are the lab versions of their connectors.

### Read Kristian's message in Teams

1. Select **Microsoft Edge** on the taskbar, then go to [teams.cloud.microsoft](https://teams.cloud.microsoft/).
2. In the left rail, select **Chat**.
3. Under **Chats**, select **Kristian Stensen**.
4. Check that you see Kristian's message: *Committee wants a view on Litware Monday. Should we add more? Bring a short memo.*

   ![Microsoft Teams on the web with the Chat view open. Kristian Stensen is selected under Chats, and his message asking for a view on Litware for Monday's committee is shown in the conversation](images/finance-teams-kristian-message.png)

## Step 1: Run a sense check

> **Where:** Copilot Chat.

### 1a. Check whether Litware beat expectations

1. Open a new browser tab and go to [copilot.cloud.microsoft](https://copilot.cloud.microsoft/).
2. In Copilot, select **Chat** at the top of the left pane, then select **New chat**.

   ![The Copilot left pane with the Chat tab selected and New chat highlighted below it](images/copilot-new-chat.png)

3. Enter:

   ```text
   I'm preparing a recommendation for Monday's investment committee on whether our portfolio should buy more Litware. To start with, did Litware beat analysts' expectations last quarter? Using LSEG, compare its actual earnings per share and revenue with the analyst consensus, and show the quarter and source.
   ```

**What to look for:** trusted, verified figures straight from LSEG: what Litware earned last quarter against what analysts expected, with LSEG cited as the source.

> [!TIP]
> LSEG can return charts and analysis cards, not just text: the provider's own experience, inside Copilot.

> [!TIP]
> **A skill was used here.** A skill is a set of expert instructions that comes with a connector. You didn't ask for it: Copilot picked LSEG's **equity-research** skill because you asked to compare results with analyst forecasts. The skill tells Copilot how an analyst does this: pull consensus estimates and actuals, then show the gap in a clear table.

### 1b. Compare Litware with its rivals

In the same chat, enter:

```text
Using FactSet, compare how profitable Litware, A. Datum and Relecloud have been over the past 5 years, using gross margin and return on invested capital (ROIC).
```

**What to look for:** verified profitability figures for Litware, A. Datum and Relecloud from FactSet, and a clear view of which company is strongest.

### 1c. Decide if it's worth a deeper look

In the same chat, enter:

```text
What is Litware's credit rating and outlook according to Moody's and what's driving them? Then, based on everything so far, give me a one-line verdict on whether Litware is worth a deeper look.
```

**What to look for:** a Moody's rating and outlook with the reasons behind them, then a one-line verdict that draws on all three sources.

> [!TIP]
> **Another skill, picked for you.** Copilot used Moody's **company-analysis** skill because you asked about a credit rating and what's driving it. The skill tells Copilot to find the company in Moody's first, then read its rating, outlook and credit opinion, without inventing any numbers.

> [!TIP]
> Three connectors, one conversation. Copilot keeps the context, so the verdict in 1c builds on the LSEG and FactSet answers above it.

## Step 2: Dig into the numbers

> **Where:** Copilot Cowork. Steps 2 and 3 all run in one Cowork task.

### 2a. Build the committee workbook

This is a long-running task, so you'll use Cowork. Cowork creates the workbook and saves it to your OneDrive.

Cowork uses only the plugins you turn on, so first turn on the finance connectors.

1. In Copilot, select **Cowork** at the top of the left pane.
2. In the left pane, select **Customize**.
3. Next to **Added**, select **Manage all**.

   ![The Cowork Customize page, with Customize highlighted in the left pane and Manage all highlighted next to the Added list of connectors](images/cowork-customize.png)

4. Turn on **LSEG_Lab**, **FactSet_Lab** and **Moodys_Lab**.
5. Turn off **Fabric IQ**, which is on by default.

   ![The Added list in Cowork Customize, with Moodys_Lab, LSEG_Lab and FactSet_Lab turned on and Fabric IQ turned off](images/cowork-customize-finance.png)

6. In the left pane, select **New task**.

   ![The Copilot left pane with the Cowork tab selected and New task highlighted below it](images/copilot-new-cowork-task.png)

7. Enter:

   ```text
   Using LSEG, create an Excel workbook called "Litware Committee Pack" with an equity research snapshot of Litware: analysts' earnings and revenue forecasts for this year and next (FY1, FY2), how many analysts cover it and how much they disagree, 5 years of financials, and valuation. Cite sources and dates.
   ```

**What to look for:**

- Cowork uses LSEG's **equity research** skill. You get the partner's analyst method as well as its data.
- A workbook named **Litware Committee Pack**, with sources and dates.

> [!TIP]
> Building the workbook can take a few minutes. Select the thought process to watch what Cowork is doing.

### 2b. Model the upside

1. In the same Cowork task, enter:

   ```text
   Using LSEG, add a "Scenarios" sheet with worst, middle and best cases (bear, base, bull), using the lowest, average and highest FY2 earnings-per-share forecasts and Litware's current share price. Make the price-to-earnings (P/E) multiple an editable input for each case and use formulas to show the implied share price and % upside or downside.
   ```

2. Select **Litware Committee Pack** in the task to open the workbook next to the chat and check the new sheet.

**What to look for:** a **Scenarios** sheet built on LSEG's verified forecasts and share price, with LSEG cited as the source.

**Try this:** change one P/E multiple on the **Scenarios** sheet and watch the implied price and upside update.

> [!TIP]
> You didn't re-explain anything. Cowork kept the context from the task, and these are real formulas you can check.

### 2c. Check that it's financially sound

In the same Cowork task, enter:

```text
Using Moody's, add a "Credit" sheet with a credit SWOT for Litware (strengths, weaknesses, opportunities and threats) and the factors that could lead to a rating upgrade or downgrade.
```

**What to look for:** a **Credit** sheet with a SWOT and upgrade and downgrade drivers, sourced from Moody's verified credit research.

## Step 3: Back-check and report

> **Where:** Copilot Cowork, in the same task, continuing from Step 2.

### 3a. Pressure-test your view (stretch goal)

```text
My view: we should buy more Litware because its strong profits and earnings growth justify its high share price. Using the Litware Committee Pack and the latest data from LSEG and Moody's, pressure-test this view: give the evidence for and against, the strongest case against buying, and the questions the committee is likely to ask.
```

**What to look for:** evidence on both sides, the strongest counter-argument, and likely committee questions, each backed by sourced figures from LSEG, Moody's and your workbook.

> [!TIP]
> Copilot argued against your view, so the committee isn't the first to find the weak spot.

### 3b. Write the committee memo

```text
Turn this into a Word memo for the investment committee, reusing the workbook's charts. Cite LSEG, FactSet and Moody's as the source for every number, and flag any missing data.
```

**What to look for:** a Word memo where every number is cited to LSEG, FactSet or Moody's, with charts from the workbook and a note on any gaps in the data.

**Result:** a committee pack you can defend on Monday: a workbook with real formulas, a memo where every number is cited, and the gaps flagged instead of guessed.

## If it goes wrong

| What happens | Try this |
|---|---|
| Copilot answers from general knowledge without a source | Name the connector at the start: "Using LSEG, …" or "Using Moody's, …" |
| The first answer from a connector is slow | Wait a few seconds and ask again. The test services may need a moment to start. |
| Copilot asks which company or ticker | Reply "Litware (LITW)". |
| Workbook steps don't apply to the right file | In the same Cowork task, start the prompt with "In Litware Committee Pack, …". |

## Checkpoint

- [ ] You compared Litware's results with consensus, rivals and its credit rating.
- [ ] Your **Litware Committee Pack** has snapshot, **Scenarios** and **Credit** sheets.
- [ ] You have a committee memo with sources.

## Key takeaways

- **Finish a full finance workflow in Copilot.** You went from a first question to a committee memo on trusted data from LSEG, FactSet and Moody's, without leaving Microsoft 365.
- **Excel analysis on verified data, in minutes.** Cowork built the workbook, scenarios and real formulas from connector data you can trace back to the source.
- **Reuse it for any company.** Swap Litware for another company and run the same prompts.

> [!TIP]
> In this track, Copilot picked skills for you based on what you asked. You can also call a skill by name with a slash command. To try that, take the [engineering track](06-engineering.md).

## More connectors to try

The same pattern works with other connectors. Try them in your own tenant for similar scenarios.

<table>
  <tr>
    <td align="center"><img src="images/connectors/sp-global.svg" alt="S&P Global" width="200"></td>
    <td align="center"><img src="images/connectors/morningstar.svg" alt="Morningstar" width="200"></td>
  </tr>
</table>

<sub>Logos are trademarks of their respective owners.</sub>

---

**Next:** [Bring your own app](07-custom-mcp.md), or try another track ([Legal](04-legal.md) · [Productivity](05-productivity.md) · [Engineering](06-engineering.md))
