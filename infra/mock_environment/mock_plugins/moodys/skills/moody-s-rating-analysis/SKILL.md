---
name: moody-s-rating-analysis
description: >
  Produce a Rating Pitch Report for a company using Moody's GenAI MCP tools, delivered as a
  self-contained HTML file saved to disk. Use this skill whenever the user asks to create
  a rating pitch, rating pitch deck, credit pitch, rating presentation, rating pitch
  report, or rating HTML report. Also trigger when they ask for a comprehensive credit
  overview combining sector analysis, company financials, SWOT, peer comparison, and ESG
  into a single report or presentation. Trigger even if they just name a company and say
  "pitch deck", "rating deck", "credit deck", or "rating report".
---

# Rating Pitch Skill

Produce the requested rating pitch as a self-contained HTML report built from a resolved data payload.

## Required workflow

Before gathering data or creating the report, read [the complete workflow](references/complete-workflow.md) end to end. Follow every requirement in that reference, including its tool sequence, payload schema, period-selection rules, section contracts, rendering rules, HTML delivery contract, partial-data behavior, and final checks. The reference is authoritative; do not omit or replace any step because it is not repeated here.
