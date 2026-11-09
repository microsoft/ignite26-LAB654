# Finance track: Should we buy more Litware?

> **Duration:** ~20 minutes | **Connectors:** LSEG_Lab, FactSet_Lab, Moodys_Lab | **Surfaces:** Copilot Chat, Copilot Cowork, Excel

In this module, you'll use the **LSEG**, **FactSet** and **Moody's** connectors to take one investment question from a quick sense check to a committee-ready memo, across Copilot Chat, Copilot Cowork and Excel.

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

- **Trusted data where you work.** LSEG, FactSet and Moody's answer in Copilot and Excel, with every number cited.
- **Connect once, use everywhere.** The same connectors work in Copilot Chat, Cowork and Excel.
- **Partner expertise, not just data.** LSEG and Moody's skills apply their analysts' methods.
- **A case that holds up.** Real Excel formulas, and Copilot challenges your view before the committee does.

## How the track flows

![Step 1 in Copilot gives a verified verdict; Step 2a in Copilot in Cowork mode builds the workbook; Steps 2b and 2c in Excel add scenarios and credit analysis; Step 3 back in Copilot gives a pressure-tested view and memo](images/finance-workflow.svg)

## Before you start

- [ ] You completed [Getting started with connectors](02-getting-started.md).
- [ ] **LSEG_Lab**, **FactSet_Lab** and **Moodys_Lab** appear in Settings › Sources.

| Step | Time | Question | Output |
|---|---|---|---|
| 1 · Sense check | ~5 min | Is Litware worth a closer look? | Quick read on earnings, rivals and credit |
| 2 · Deep dive on the numbers | ~8 min | What do the numbers say, and what's the upside? | "Litware Committee Pack" workbook: snapshot, scenarios, credit |
| 3 · Back-check and report | ~7 min | Does my view hold up? | Pressure-tested view and committee memo |

## Step 1: Sense check

### 1a. Did it beat expectations?

> **Where:** Copilot. Start a new chat, in either Chat or Cowork mode.

> [!IMPORTANT]
> The first time you use Cowork, select **Customize** and turn on **LSEG_Lab**, **FactSet_Lab** and **Moodys_Lab**. Then turn off the **Fabric IQ** plugin, which is on by default.

```text
I'm preparing a recommendation for Monday's investment committee on whether our portfolio should buy more Litware. To start with, did Litware beat analysts' expectations last quarter? Using LSEG, compare its actual earnings per share and revenue with the analyst consensus, and show the quarter and source.
```

**What to look for:** trusted, verified figures straight from LSEG: what Litware earned last quarter against what analysts expected, with LSEG cited as the source.

> [!TIP]
> LSEG can return charts and analysis cards, not just text: the provider's own experience, inside Copilot.

> [!TIP]
> If Copilot doesn't give the response you expect, select the model name at the top of the chat, switch from **Auto** to a GPT model that isn't a quick-response one, and send the prompt again.

### 1b. Is it stronger than its rivals?

> **Where:** Copilot, in the same chat.

```text
Using FactSet, compare how profitable Litware, A. Datum and Relecloud have been over the past 5 years, using gross margin and return on invested capital (ROIC).
```

**What to look for:** verified profitability figures for Litware, A. Datum and Relecloud from FactSet, and a clear view of which company is strongest.

### 1c. Is it worth a deeper look?

> **Where:** Copilot, in the same chat.

```text
What is Litware's credit rating and outlook according to Moody's and what's driving them? Then, based on everything so far, give me a one-line verdict on whether Litware is worth a deeper look.
```

**What to look for:** a Moody's rating and outlook with the reasons behind them, then a one-line verdict that draws on all three sources.

> [!TIP]
> Three connectors, one conversation. Copilot keeps the context, so the verdict in 1c builds on the LSEG and FactSet answers above it.

## Step 2: Deep dive on the numbers

### 2a. Get the numbers in one place

> **Where:** Copilot. Start a new chat and select **Cowork** mode, because this is a long-running task. Cowork creates the workbook and saves it to your OneDrive.

```text
Using LSEG, create an Excel workbook called "Litware Committee Pack" with an equity research snapshot of Litware: analysts' earnings and revenue forecasts for this year and next (FY1, FY2), how many analysts cover it and how much they disagree, 5 years of financials, and valuation. Cite sources and dates.
```

**What to look for:**

- Copilot uses LSEG's **equity research** skill. You get the partner's analyst method as well as its data.
- A workbook named **Litware Committee Pack**, with sources and dates.

> [!TIP]
> Building the workbook can take a few minutes. Select the thought process to watch what Cowork is doing, or go back to your Step 1 chat and its charts while the task finishes.

### 2b. What's the upside?

> **Where:** Excel. In the same Cowork chat, select **Litware Committee Pack** to open the workbook next to the chat, then run 2b and 2c there.

```text
Using LSEG, add a "Scenarios" sheet with worst, middle and best cases (bear, base, bull), using the lowest, average and highest FY2 earnings-per-share forecasts and Litware's current share price. Make the price-to-earnings (P/E) multiple an editable input for each case and use formulas to show the implied share price and % upside or downside.
```

**What to look for:** a **Scenarios** sheet built on LSEG's verified forecasts and share price, with LSEG cited as the source.

**Try this:** change one P/E multiple on the **Scenarios** sheet and watch the implied price and upside update.

> [!TIP]
> You didn't re-explain anything. Copilot in Excel picked up the context from the workbook, and these are real formulas you can check.

### 2c. Is it financially sound?

```text
Using Moody's, add a "Credit" sheet with a credit SWOT for Litware (strengths, weaknesses, opportunities and threats) and the factors that could lead to a rating upgrade or downgrade.
```

**What to look for:** a **Credit** sheet with a SWOT and upgrade and downgrade drivers, sourced from Moody's verified credit research. The Moody's skill works in Excel too, not just in Cowork.

## Step 3: Back-check and report

> **Where:** Copilot. Go back to your chat from Step 1.

### 3a. Pressure-test your view (stretch goal)

```text
My view: we should buy more Litware because its strong profits and earnings growth justify its high share price. Using the Litware Committee Pack and the latest data from LSEG and Moody's, pressure-test this view: give the evidence for and against, the strongest case against buying, and the questions the committee is likely to ask.
```

**What to look for:** evidence on both sides, the strongest counter-argument, and likely committee questions, each backed by sourced figures from LSEG, Moody's and your workbook.

> [!TIP]
> Copilot argued against your view, so the committee isn't the first to find the weak spot.

### 3b. Prepare the report

```text
Turn this into a Word memo for the investment committee, reusing the workbook's charts. Cite LSEG, FactSet and Moody's as the source for every number, and flag any missing data.
```

**What to look for:** a Word memo where every number is cited to LSEG, FactSet or Moody's, with charts from the workbook and a note on any gaps in the data.

**Result:** a committee pack you can defend on Monday: a workbook with real formulas, a memo where every number is cited, and the gaps flagged instead of guessed.

## If it goes wrong

| What happens | Try this |
|---|---|
| Copilot answers from general knowledge without a source | Name the connector at the start: "Using LSEG, …" or "Using Moody's, …" |
| Copilot doesn't give the response you expect | Select the model name at the top of the chat, switch from **Auto** to a GPT model that isn't a quick-response one, and send the prompt again. |
| The first answer from a connector is slow | Wait a few seconds and ask again. The test services may need a moment to start. |
| Copilot asks which company or ticker | Reply "Litware (LITW)". |
| Workbook steps don't apply to the right file | Open **Litware Committee Pack** next to your Cowork chat and start the prompt with "In Litware Committee Pack, …". |

## Checkpoint

- [ ] You compared Litware's results with consensus, rivals and its credit rating.
- [ ] Your **Litware Committee Pack** has snapshot, **Scenarios** and **Credit** sheets.
- [ ] You have a committee memo with sources.

## Key takeaways

- **Finish a full finance workflow in Copilot.** You went from a first question to a committee memo on trusted data from LSEG, FactSet and Moody's, without leaving Microsoft 365.
- **Excel analysis on verified data, in minutes.** Copilot built the workbook, scenarios and real formulas from connector data you can trace back to the source.
- **Reuse it for any company.** Swap Litware for another company and run the same prompts.

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
