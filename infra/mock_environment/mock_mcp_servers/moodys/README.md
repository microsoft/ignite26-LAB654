# Moody's mock server

Mock of the Moody's MCP server for the [finance scenario](../../../../docs/scenarios/finance/scenario.md). The server isn't built yet. This README specifies the data it must serve; `seed_files/` will hold that data.

Match tool names, descriptions and input schemas to the real Moody's MCP server when the server is built. The groupings below describe data, not tool names.

## Prompts it powers

| Prompt | What Copilot asks Moody's for |
|--------|-------------------------------|
| 1c | NVIDIA's credit rating and outlook, and what's driving them |
| 2c | A credit SWOT for a "Credit" sheet in the workbook, plus the factors that could lead to an upgrade or downgrade |
| 3a | NVIDIA's rating, used as evidence when pressure-testing the buy case |

The partner skill `company-analysis` (2c, 3a; spelled "company-anlaysis" in the one-pager) is applied by Copilot. The mock serves data only.

## Data required

Company coverage: **NVIDIA** only.

### 1. Rating and outlook (1c, 3a)

| Field | Notes |
|-------|-------|
| Issuer name and Moody's identifier | |
| Long-term issuer or senior unsecured rating | Moody's scale (e.g. Aa3, A1) |
| Rating outlook | Positive, stable, negative or developing |
| Rating action date and last review date | Before `ASK_DATE` in `tools/scenarios/finance/__init__.py` |
| Short-term rating | Optional |

### 2. Rating rationale (1c)

A short research-style summary of what's driving the rating, split into **credit strengths** and **credit challenges**. Two to five points each, written as plain text that Copilot can quote.

### 3. Credit SWOT (2c)

Two to five points in each of strengths, weaknesses, opportunities and threats. These can reuse the rationale points but must cover all four quadrants.

### 4. Rating sensitivities (2c)

- **What could lead to an upgrade:** two to four factors, ideally with measurable thresholds (e.g. a leverage or cash flow level)
- **What could lead to a downgrade:** two to four factors, same style

### 5. Key credit metrics (optional, supports 2c and 3a)

Recent fiscal years of leverage (debt ÷ EBITDA), interest coverage, cash and liquidity, and free cash flow to debt. Figures should agree with LSEG's financials for the same years.

## Consistency rules

- One **as-of date**, on or before `ASK_DATE`.
- The outlook, rationale, SWOT and sensitivities must tell the same story: a stable outlook shouldn't come with mostly negative drivers.
- Every record carries a source label and date for citations.

## Open questions

- Real Moody's ratings and research text or clearly synthetic ones? Real content needs a licensing check; synthetic content should be labelled as such.
