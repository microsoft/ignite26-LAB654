# LSEG mock server

Mock of the LSEG MCP server for the [finance scenario](../../../../docs/scenarios/finance/scenario.md). See the [mock servers README](../README.md) for the shared architecture and how to run, test and deploy.

## Prompts it powers

| Prompt | What Copilot asks LSEG for |
|--------|----------------------------|
| 1a | NVIDIA's actual EPS and revenue for the last reported quarter vs. the analyst consensus |
| 2a | An equity research snapshot: FY1/FY2 forecasts, analyst coverage and dispersion, 5 years of financials, valuation |
| 2b | Low, mean and high FY2 EPS forecasts and the current share price |
| 3a | The same estimates and valuation, as evidence for and against buying more |

## Tools

| Tool | Serves | In the trace |
|------|--------|--------------|
| `qa_ibes_consensus` | Batch of `qa_ibes_consensus`, `qa_ibes_actuals` and `qa_ibes_measures` requests: consensus by fiscal period index, reported actuals by `pIndex`, measure catalogue | Yes |
| `qa_company_fundamentals` | Worldscope items by code and fiscal year (annual or quarterly) | Yes |
| `historical_pricing_summaries` | Daily, weekly, monthly, quarterly or yearly bars by `count`, `tenor` or `start`/`end` | Yes |
| `important_company_news` | Reuters headlines for a date window | Yes |
| `symbology_lookup` | Identifier conversion (ticker, RIC, ISIN, CUSIP, SEDOL, PermID) | No |

## Widgets

Three tools return MCP Apps widgets that mimic the live LSEG widgets in Microsoft 365 Copilot. The HTML is in `mock_lseg/ui/`.

| Tool | Resource | Widget |
|------|----------|--------|
| `qa_ibes_consensus` | `ui://lseg/ibes` | Actual vs. consensus chart, filters panel and a Tabulate table view |
| `historical_pricing_summaries` | `ui://lseg/pricing` | Candlestick chart with hover details, and a table view |
| `qa_company_fundamentals` | `ui://lseg/fundamentals` | Sortable, filterable table of Worldscope items |

No plugin manifest change is needed: Copilot discovers widgets from the tool's `_meta.ui.resourceUri`.

## Data

- `seed_files/`: the I/B/E/S measure catalogue, Worldscope item definitions, NVIDIA bars and news recorded in the trace, and the coverage list.
- `_domains/finance`: the shared model for all 8 companies (NVDA, AMD, AVGO, INTC, QCOM, MU, TXN, MRVL). NVIDIA values recorded in the trace are returned verbatim; everything else is generated deterministically from the model.

## Known differences from the live server

- `historical_pricing_summaries` with `interval: P1M, count: 13`: the live server returned only 2 bars; the mock returns all 13. Fixture `036` is marked as an expected failure.
- `symbology_lookup` wasn't called in the trace, so its schema and output follow LSEG's public description and may differ.
- Data for companies other than NVIDIA, and NVIDIA data outside what the trace recorded, is synthetic.