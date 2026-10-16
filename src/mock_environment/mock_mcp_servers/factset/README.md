# FactSet mock server

Mock of the FactSet MCP server for the [finance scenario](../../../scenarios/finance/scenario.md). The server isn't built yet. This README specifies the data it must serve; `seed_files/` will hold that data.

Match tool names, descriptions and input schemas to the real FactSet MCP server when the server is built. The groupings below describe data, not tool names.

## Prompts it powers

| Prompt | What Copilot asks FactSet for |
|--------|-------------------------------|
| 1b | How profitable NVIDIA, AMD and Broadcom have been over the past 5 years, using gross margin and return on invested capital (ROIC) |
| 1c | Indirectly: the one-line verdict draws on 1b |

## Data required

Company coverage: **NVIDIA (NVDA), AMD (AMD), Broadcom (AVGO)**.

### Company identifiers

Name, ticker, exchange and FactSet identifier for each company, so a request by name or ticker resolves.

### Profitability history (1b)

Five fiscal years per company, annual values:

| Field | Notes |
|-------|-------|
| Fiscal year label and end date | The three companies have different year-ends (NVIDIA late January, AMD December, Broadcom early November). Keep each company's own fiscal years and label them. |
| Revenue | USD, for context |
| Gross margin % | Gross profit ÷ revenue |
| ROIC % | State the definition used (e.g. NOPAT ÷ average invested capital) and use it for all three companies |
| Inputs behind the ratios | Optional: gross profit, NOPAT, invested capital, so the ratios can be checked |

Optional: a 5-year average or median per company, which lets Copilot rank them in one step.

## Consistency rules

- One **as-of date** for all FactSet data, on or before `ASK_DATE` in `tools/scenarios/finance/__init__.py`.
- The same five-year window and the same ROIC definition for every company.
- NVIDIA revenue here should match LSEG's historical revenue for the same fiscal years, so answers don't contradict each other.
- Every record carries a source label and as-of date for citations.

## Open questions

- Real published figures or clearly synthetic ones? Real figures need a licensing check; synthetic ones should be labelled as such.
