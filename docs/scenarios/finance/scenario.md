# LAB654 · Finance track: Should we buy more NVIDIA?

> Converted from `LAB654_Finance_Track_OnePager.docx` (owner: Anshuman). Wording is preserved; layout is simplified to Markdown.
>
> **Single lab persona:** one lab account plays all three domains, so Alex is replaced by Marcus Hollowell at Verdantis (the legal persona), the asset manager becomes the Verdantis Investment Office, and prompt 1a no longer states a job title.
>
> **Synced with commit `777ada5` (Anshuman):** the lab manual now frames the track around a case that holds up rather than weekend-vs-Copilot speed, drops "Friday 4pm", and says "committee pack" instead of "IC Pack". The same changes are applied below; prompts are unchanged.

**Connectors:** LSEG · FactSet · Moody's  |  **~15 min hands-on**  |  **Owner:** Anshuman

## What attendees take away

- **Do a real analyst job, end to end:** decide if a company is worth a closer look, dig into the numbers, then pressure-test the view and produce a committee-ready report.
- **Trusted data where they work:** LSEG, FactSet and Moody's answer inside Copilot, Excel and Word, with every number cited and dated.
- **Partner expertise, not just data:** LSEG and Moody's skills apply their analysts' methods, in the Copilot app and in Excel.
- **Connect once, use everywhere:** the same three connectors work in the Copilot app and in Excel, with no extra setup.
- **A case that holds up:** real Excel formulas you can check, and Copilot challenges the view before the committee does.
- **Take home:** the committee pack (workbook + memo) and prompts that work for any company.

## Persona and scenario

Marcus, at Verdantis, a US car and home insurer. Verdantis's investment portfolio already owns NVIDIA.

Jordan, the portfolio manager, asks, "Should we buy more NVIDIA (or Company X)? Bring it to Monday's investment committee."

Meet Marcus. Marcus works at Verdantis, an insurer whose Investment Office invests the premiums it holds to pay future claims. One of the portfolio's biggest holdings is NVIDIA, the company behind most AI chips. Jordan, who runs the portfolio, asks Marcus: "Should we buy more NVIDIA? Bring a recommendation to Monday's investment committee", the weekly meeting where senior people approve big investments, and they will challenge the case. A good answer has to hold up: every number sourced, checked across more than one provider, and challenged before the committee does it. Marcus builds that case with Copilot in three steps.

*Not in finance?* This is any business case: is it worth a closer look, what do the numbers say, does my argument survive tough questions, then write it up for the people who decide.

| | |
|---|---|
| **The people** | Marcus Hollowell: the Copilot user. · Jordan Reyes, portfolio manager, Verdantis Investment Office: asks the question. · The investment committee: senior people who approve big investments and will challenge the case. |
| **The trigger** | Jordan on Teams: "Committee wants a view on NVIDIA Monday. Should we add more? Bring a short memo." |
| **Why it matters** | The portfolio already holds a lot of NVIDIA, so buying more puts even more policyholders' money on one company. A weak case gets torn apart on Monday. |
| **What Marcus needs for Monday** | 1. Is the business beating expectations? 2. Is it stronger than its rivals? 3. What's the upside and downside at today's price? 4. A view that survives tough questions, written up as a memo. |

## Flow

| Step | Min | Marcus's question | Output |
|---|---|---|---|
| 1 · Sense check | 0–4 | Is NVIDIA worth a closer look? | Quick read on earnings and rivals |
| 2 · Deep dive on the numbers | 4–12 | What do the numbers say, and what's the upside? | NVIDIA Committee Pack workbook: snapshot + scenarios |
| 3 · Back-check and report | 12–18 | Does my view hold up? | Pressure-tested view + committee memo |

## Prompts

| # | Step | Prompt | Connector / skill |
|---|---|---|---|
| | **Step 1 · Sense check: Is NVIDIA worth a closer look?** | | |
| 1a | Did it beat expectations? | [Copilot App] I'm preparing a recommendation for Monday's investment committee on whether our portfolio should buy more NVIDIA. To start with, Did NVIDIA beat analysts' expectations last quarter? Using LSEG, compare its actual earnings per share and revenue with the analyst consensus, and show the quarter and source. | LSEG |
| 1b | Is it stronger than rivals? | [Copilot App] Using FactSet, compare how profitable NVIDIA, AMD and Broadcom have been over the past 5 years, using gross margin and return on invested capital (ROIC). | FactSet |
| 1c | Is it worth a deeper look | [Copilot App] What is NVIDIA's credit rating and outlook according to Moody's and what's driving them? Then, based on everything so far, give me a one-line verdict on whether NVIDIA is worth a deeper look | Moody's |
| | **Step 2 · Deep dive on the numbers: What do the numbers say?** | | |
| 2a | Get the numbers in one place | [Copilot App] Using LSEG, create an Excel workbook called "NVIDIA Committee Pack" with an equity research snapshot of NVIDIA: analysts' earnings and revenue forecasts for this year and next (FY1, FY2), how many analysts cover it and how much they disagree, 5 years of financials, and valuation. Cite sources and dates. | LSEG · skill: equity-research |
| 2b | What's the upside? | [In Excel] Add a "Scenarios" sheet with worst, middle and best cases (bear, base, bull), using the lowest, average and highest FY2 earnings-per-share forecasts from the snapshot and NVIDIA's current share price. Make the price-to-earnings (P/E) multiple an editable input for each case and use formulas to show the implied share price and % upside or downside. | In Excel · workbook + LSEG · wow: change one number and everything updates |
| 2c | Is it financially sound? | [In Excel] Using Moody's, add a "Credit" sheet with a credit SWOT for NVIDIA (strengths, weaknesses, opportunities and threats) and the factors that could lead to a rating upgrade or downgrade | Moody's · skill: company-anlaysis |
| | **Step 3 · Back-check and report: Does my view hold up?** | | |
| 3a | Pressure-test my view | My view: we should buy more NVIDIA because its strong profits and earnings growth justify its high share price. Using the NVIDIA Committee Pack, LSEG and NVIDIA's Moody's credit rating, pressure-test this view: give the evidence for and against, the strongest case against buying, and the questions the committee is likely to ask. | LSEG + Moody's · skills: equity-research, company-analysis |
| 3b | Prepare the report | Turn this into a Word memo for the investment committee, reusing the workbook's charts. Cite sources and flag any missing data. | NVIDIA Committee Pack |
