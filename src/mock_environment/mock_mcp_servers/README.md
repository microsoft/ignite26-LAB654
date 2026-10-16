# Mock MCP servers

Mock MCP servers for the third-party connectors used in the scenarios. Each server goes in its own folder (for example `imanage/` or `harvey/`). It should expose the same tool names, descriptions and input schemas as the real MCP server and serve scenario-specific fixture data.

Planned servers for the legal scenario, from [legal.md](../../scenarios/legal.md):

- iManage: matter workspace, prior agreements and the negotiation playbook
- Harvey: legal research and clause analysis
