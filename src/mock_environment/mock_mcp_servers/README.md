# Mock MCP servers

Mock MCP servers for the third-party connectors used in the scenarios. Each server has its own folder. It should expose the same tool names, descriptions and input schemas as the real MCP server, and serve the scenario data in its `seed_files/` subfolder.

| Server | Scenario | Seed data |
|--------|----------|-----------|
| [`imanage/`](imanage/README.md) | Legal | Cognivault-Nexus matter: agreement, Exhibits A–D, playbook |
| [`harvey/`](harvey/README.md) | Legal | None yet (answers from public law) |
| [`lseg/`](lseg/README.md) | Finance | Data spec only: NVIDIA quarter vs. consensus, FY1/FY2 estimates, 5-year financials, price and valuation |
| [`factset/`](factset/README.md) | Finance | Data spec only: 5-year gross margin and ROIC for NVIDIA, AMD and Broadcom |
| [`moodys/`](moodys/README.md) | Finance | Data spec only: NVIDIA rating, outlook, rationale, credit SWOT, upgrade/downgrade factors |
| [`smartsheet/`](smartsheet/README.md) | Productivity | Data spec only: Zava Aurora Launch Tracker (11 rows, 3 comments), 3 decoy sheets, per-seat copies |
| [`notion/`](notion/README.md) | Productivity | Data spec only: Aurora Launch Plan, Weekly Sync – Oct 6, Launch Decision Log with 3 prior decisions |
| [`zava_hub/`](zava_hub/README.md) | Productivity | Not an MCP server. Intranet pages are seeded in the tenant (`intranetwebsite`); README documents them |
