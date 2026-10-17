# LSEG mock server

Mock of the LSEG MCP server for the [finance scenario](../../../../docs/scenarios/finance/scenario.md). The server isn't built yet. This README specifies the data it must serve; `seed_files/` will hold that data.

Match tool names, descriptions and input schemas to the real LSEG MCP server when the server is built. The groupings below describe data, not tool names.

## Prompts it powers

| Prompt | What Copilot asks LSEG for |
|--------|----------------------------|
| 1a | NVIDIA's actual EPS and revenue for the last reported quarter vs. the analyst consensus, with the quarter and source |
| 2a | An equity research snapshot for the "NVIDIA Committee Pack" workbook: FY1/FY2 forecasts, analyst coverage and dispersion, 5 years of financials, valuation |
| 2b | The low, mean and high FY2 EPS forecasts and the current share price (read from the 2a snapshot; LSEG must supply them) |
| 3a | The same estimates and valuation, used as evidence for and against buying more |

The partner skill `equity-research` (2a, 3a) is applied by Copilot. The mock serves data only.

## Data required

Company coverage: **NVIDIA (NVDA)** only. AMD and Broadcom are FactSet's job in this scenario.

### 1. Last-quarter results vs. consensus (1a)

One record for the most recent quarter NVIDIA reported before the scenario's Friday (`ASK_DATE` in `tools/scenarios/finance/__init__.py`).

| Field | Notes |
|-------|-------|
| Fiscal period | Label and end date, e.g. "Q2 FY2027". NVIDIA's fiscal year ends in late January. |
| Report date | Must be before `ASK_DATE` |
| Actual EPS | Say whether it's GAAP or adjusted (non-GAAP). Consensus must use the same basis. |
| Consensus EPS | Mean estimate just before the report, plus the number of estimates |
| Actual revenue | USD |
| Consensus revenue | USD, plus the number of estimates |
| Surprise | EPS and revenue surprise in USD and % (or derivable) |
| Source and as-of date | For citation |

### 2. Forward estimates (2a, 2b, 3a)

For **FY1** (current fiscal year) and **FY2** (next fiscal year), for both EPS and revenue:

| Field | Notes |
|-------|-------|
| Mean (consensus), median | |
| Low, high | 2b uses low / mean / high FY2 EPS as the bear / base / bull cases. Low < mean < high. |
| Standard deviation | Answers "how much they disagree" |
| Number of estimates | Answers "how many analysts cover it" |
| Fiscal year end date, as-of date | |

Optional, if the real server provides them: number of analysts, recommendation breakdown (buy / hold / sell), mean price target.

### 3. Historical financials (2a)

Five full fiscal years, most recent reported year last. Annual values in USD:

- Revenue, gross profit, operating income, net income
- Diluted EPS
- Operating cash flow, capital expenditure, free cash flow
- Cash and equivalents, total debt, shareholders' equity
- Diluted shares outstanding

### 4. Price and valuation (2a, 2b, 3a)

| Field | Notes |
|-------|-------|
| Last share price, with date | 2b's "current share price". Should be the close on or before `ASK_DATE`. |
| Market capitalisation | |
| Enterprise value | |
| P/E trailing and forward (FY1, FY2) | Forward P/E should equal price ÷ the consensus EPS above |
| EV/EBITDA, EV/sales | Trailing and forward |
| 52-week high and low | Optional, helps the committee-style questions in 3a |

## Consistency rules

- One **as-of date** for all LSEG data, on or before `ASK_DATE`.
- Ratios must agree with the inputs (forward P/E = price ÷ EPS; surprise = actual − consensus).
- Every record carries a source label and as-of date so Copilot can cite them (1a, 2a, 3b).
- Units are explicit: USD, fiscal-year labels, millions vs. billions.

## Open questions

- Real published figures or clearly synthetic ones? Real figures need a licensing check; synthetic ones should be labelled as such.
