# Mock MCP servers

Mock MCP servers for the third-party connectors used in the scenarios. Each server has its own folder. It should expose the same tool names, descriptions and input schemas as the real MCP server, and serve the scenario data in its `seed_files/` subfolder.

| Server | Scenario | Seed data |
|--------|----------|-----------|
| [`imanage/`](imanage/README.md) | Legal | Cognivault-Nexus matter: agreement, Exhibits A–D, playbook |
| [`harvey/`](harvey/README.md) | Legal | None yet (answers from public law) |
