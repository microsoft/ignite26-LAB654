# FactSet mock server

Mock of the FactSet MCP server for the [finance scenario](../../../../docs/scenarios/finance/scenario.md). See the [mock servers README](../README.md) for the shared architecture and how to run, test and deploy.

## Prompts it powers

| Prompt | What Copilot asks FactSet for |
|--------|-------------------------------|
| 1b | 5-year gross margin and ROIC for Litware, A. Datum and Relecloud |
| 1c | Indirectly: the one-line verdict draws on 1b |

## Tools

| Tool | Serves | In the trace |
|------|--------|--------------|
| `FactSet_Metrics` | Metric-code search for natural-language concepts | Yes |
| `FactSet_EntityReference` | Entity and security ids, profile, headquarters, classification | Yes |
| `FactSet_Fundamentals` | Reported fundamentals by fiscal period (`ANN`, `QTR`, `LTM`, …) | Yes |
| `FactSet_RBICS` | Industry classification and revenue focus | No |
| `FactSet_EstimatesConsensus` | Broker consensus for one metric per call | No |
| `FactSet_GlobalPrices` | End-of-day prices and volume, with split adjustment and currency conversion | No |
| `FactSet_CompanyScreener` | Always returns the "not entitled" error, as an unentitled real account does | No |

## Data

- `seed_files/`: the metric catalogue, entity reference records, RBICS classifications and corporate actions, plus the fundamentals and metric search results recorded in the trace.
- `_domains/finance`: the shared company model, so FactSet figures agree with LSEG and Moody's.

## Known differences from the live server

- Tools not called in the trace follow FactSet's public descriptions; their schemas and output may differ from the live server.
- Currency conversion uses a fixed FX table.
- On weekly or monthly price bars, `UNSPLIT` adjustment uses the bar's end date.
- Data outside what the trace recorded is synthetic.