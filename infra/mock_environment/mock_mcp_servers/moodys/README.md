# Moody's mock server

Mock of the Moody's MCP server for the [finance scenario](../../../../docs/scenarios/finance/scenario.md). See the [mock servers README](../README.md) for the shared architecture and how to run, test and deploy.

## Prompts it powers

| Prompt | What Copilot asks Moody's for |
|--------|-------------------------------|
| 1c | Litware's credit rating and outlook, and what's driving them |
| 2c | A credit SWOT plus the factors that could lead to an upgrade or downgrade |
| 3a | Litware's rating, as evidence when pressure-testing the buy case |

## Tools

| Tool | Serves | In the trace |
|------|--------|--------------|
| `findEntity` | Up to 3 matches per name (one name or a list of up to 25), with `entityId`, ticker, rating, country and sector; unmatched names in `notFound` | Yes |
| `getEntityRatings` | Current rating, outlook and rating actions for the last `years` (1–30, default 5) | Yes |
| `getCreditOpinion` | The latest credit opinion, limited to the requested `sections` | Yes |
| `getEntityBeneficiaryOwners` | Beneficial owners at the 25% threshold (none, for these public companies) | No |

Sections: `Summary`, `CreditStrengths`, `CreditChallenges`, `RatingOutlook`, `FactorsLeadingToUpgrade`, `FactorsLeadingToDowngrade`, `Liquidity`, `ESGConsiderations`. The default is the first four.

## Data

- `seed_files/ratings.json` and `opinions.json`: Litware's rating history and credit opinion as recorded in the trace.
- Other issuers: rating histories and opinions generated from the shared company model. Rating moves follow the outlook (positive outlooks trend up, stable ones don't get downgraded), and opinion text draws on each company's financials. Analyst names are fictional.

## Known differences from the live server

- Moody's tool schemas aren't published, so input schemas are inferred from the calls in the trace.
- Section names beyond the five seen in the trace are assumptions.
- `getEntityBeneficiaryOwners` was not called in the trace; its output shape is a guess.
- Only Litware's content is recorded; all other issuers are synthetic.