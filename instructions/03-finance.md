# Finance track: Should we buy more NVIDIA?

> **Duration:** ~18 minutes | **Connectors:** Test_LSEG, Test_FactSet, Test_Moodys | **Surfaces:** Microsoft 365 Copilot app, Excel, Word

## What you'll take away

- **Trusted data where you work.** LSEG, FactSet and Moody's answer inside Copilot, Excel and Word, with every number cited and dated.
- **Connect once, use everywhere.** The same three connectors work in the Copilot app and in Excel, with no extra setup.
- **Partner expertise, not just data.** LSEG and Moody's skills apply their analysts' methods, in the Copilot app and in Excel.
- **A case that holds up.** Real Excel formulas you can check, and Copilot challenges your view before the committee does.

## The story

Zava invests the insurance premiums it holds so it can pay future claims. One of the portfolio's biggest holdings is NVIDIA, the company behind most AI chips.

Kristian Stensen, who runs the portfolio, messages you on Teams:

> "Committee wants a view on NVIDIA Monday. Should we add more? Bring a short memo."

Zava already holds a lot of NVIDIA, so buying more puts even more policyholders' money on one company. The investment committee is the weekly meeting where senior people approve big investments, and they will challenge the case. A good answer has to hold up: every number sourced, checked across more than one provider, and challenged before the committee does it. You'll build that case with Copilot in three steps.

**What you need for Monday:**

1. Is the business beating expectations?
2. Is it stronger than its rivals?
3. What's the upside and downside at today's price?
4. A view that survives tough questions, written up as a memo.

*Not in finance?* This works for any business case: is it worth a closer look, what do the numbers say, does my argument survive tough questions, and how do I write it up for the people who decide?

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

## Before you start

- [ ] You completed [Getting started with connectors](02-getting-started.md).
- [ ] **Test_LSEG**, **Test_FactSet** and **Test_Moodys** appear in Settings › Sources.

| Step | Time | Question | Output |
|---|---|---|---|
| 1 · Sense check | ~4 min | Is NVIDIA worth a closer look? | Quick read on earnings, rivals and credit |
| 2 · Deep dive on the numbers | ~8 min | What do the numbers say, and what's the upside? | "NVIDIA Committee Pack" workbook: snapshot, scenarios, credit |
| 3 · Back-check and report | ~6 min | Does my view hold up? | Pressure-tested view and committee memo |

## Step 1: Sense check

*Microsoft 365 Copilot app*

### 1a. Did it beat expectations?

Start a new chat and enter:

```text
I'm preparing a recommendation for Monday's investment committee on whether our portfolio should buy more NVIDIA. To start with, did NVIDIA beat analysts' expectations last quarter? Using LSEG, compare its actual earnings per share and revenue with the analyst consensus, and show the quarter and source.
```

**What to look for:** actual and consensus figures for EPS and revenue, the fiscal quarter, and LSEG as the cited source.

> [!TIP]
> LSEG can return charts and analysis cards, not just text: the provider's own experience, inside Copilot.

### 1b. Is it stronger than its rivals?

```text
Using FactSet, compare how profitable NVIDIA, AMD and Broadcom have been over the past 5 years, using gross margin and return on invested capital (ROIC).
```

**What to look for:** five years of gross margin and ROIC for all three companies, sourced from FactSet.

### 1c. Is it worth a deeper look?

```text
What is NVIDIA's credit rating and outlook according to Moody's and what's driving them? Then, based on everything so far, give me a one-line verdict on whether NVIDIA is worth a deeper look.
```

**What to look for:** a Moody's rating and outlook with the reasons behind them, then a one-line verdict that draws on all three sources.

> [!TIP]
> Three connectors, one conversation. Copilot keeps the context, so the verdict in 1c builds on the LSEG and FactSet answers above it.

## Step 2: Deep dive on the numbers

### 2a. Get the numbers in one place

*Microsoft 365 Copilot app · LSEG equity research skill*

```text
Using LSEG, create an Excel workbook called "NVIDIA Committee Pack" with an equity research snapshot of NVIDIA: analysts' earnings and revenue forecasts for this year and next (FY1, FY2), how many analysts cover it and how much they disagree, 5 years of financials, and valuation. Cite sources and dates.
```

**What to look for:**

- Copilot uses LSEG's **equity research** skill. You get the partner's analyst method as well as its data.
- A workbook named **NVIDIA Committee Pack**, with sources and dates.

Open the workbook in **Excel** for the next two prompts.

### 2b. What's the upside?

*Excel · Copilot pane*

```text
Add a "Scenarios" sheet with worst, middle and best cases (bear, base, bull), using the lowest, average and highest FY2 earnings-per-share forecasts from the snapshot and NVIDIA's current share price. Make the price-to-earnings (P/E) multiple an editable input for each case and use formulas to show the implied share price and % upside or downside.
```

**Try this:** change one P/E multiple on the **Scenarios** sheet and watch the implied price and upside update.

> [!TIP]
> You didn't re-explain anything. Copilot in Excel picked up the context from the workbook, and these are real formulas you can check.

### 2c. Is it financially sound?

*Excel · Copilot pane · Moody's company analysis skill*

```text
Using Moody's, add a "Credit" sheet with a credit SWOT for NVIDIA (strengths, weaknesses, opportunities and threats) and the factors that could lead to a rating upgrade or downgrade.
```

**What to look for:** a **Credit** sheet with a SWOT and upgrade and downgrade drivers. The Moody's skill works in Excel too, not just in Cowork.

## Step 3: Back-check and report

*Microsoft 365 Copilot app*

### 3a. Pressure-test your view

```text
My view: we should buy more NVIDIA because its strong profits and earnings growth justify its high share price. Using the NVIDIA Committee Pack, LSEG and NVIDIA's Moody's credit rating, pressure-test this view: give the evidence for and against, the strongest case against buying, and the questions the committee is likely to ask.
```

**What to look for:** evidence on both sides, the strongest counter-argument, and likely committee questions, drawing on the workbook and both connectors.

> [!TIP]
> Copilot argued against your view, so the committee isn't the first to find the weak spot.

### 3b. Prepare the report

```text
Turn this into a Word memo for the investment committee, reusing the workbook's charts. Cite sources and flag any missing data.
```

**What to look for:** a Word memo with citations, charts from the workbook, and a note on any gaps in the data.

**Result:** a committee pack you can defend on Monday: a workbook with real formulas, a memo where every number is cited, and the gaps flagged instead of guessed.

## If it goes wrong

| What happens | Try this |
|---|---|
| Copilot answers from general knowledge without a source | Name the connector at the start: "Using LSEG, …" or "Using Moody's, …" |
| The first answer from a connector is slow | Wait a few seconds and ask again. The test services may need a moment to start. |
| Copilot asks which company or ticker | Reply "NVIDIA (NVDA)". |
| Workbook steps don't apply to the right file | Open **NVIDIA Committee Pack** in Excel and run 2b and 2c from Copilot in Excel. |

## Checkpoint

- [ ] You compared NVIDIA's results with consensus, rivals and its credit rating.
- [ ] Your **NVIDIA Committee Pack** has snapshot, **Scenarios** and **Credit** sheets.
- [ ] You have a pressure-tested view and a committee memo with sources.

**What you take away:** the committee pack (workbook and memo), and prompts that work for any company. Swap NVIDIA for another company and run them again.

---

**Next:** [Bring your own app](07-custom-mcp.md), or try another track ([Legal](04-legal.md) · [Productivity](05-productivity.md) · [Engineering](06-engineering.md))
