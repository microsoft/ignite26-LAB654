# Mock environment

Synthetic tenant data for testing the LAB654 scenarios (legal, finance and productivity). The tenant is provisioned with [COEP schemas](https://coep.microsoft.com/schema/portal).

## Layout

| Path | Purpose |
|------|---------|
| `_schemas/` | The latest COEP schemas, rules and examples for every type, laid out as `<Category>/<type>/`. `manifest.json` records the version and fetch date. |
| `Connectors_Ignite_EMP/` | The COEP package for the virtual tenant: `config.json` plus a `<type>.config.json` for each type that has data (currently users, emails and chats). |
| `Connectors_Ignite_EMP/files/` | Enterprise documents for `files.config.json`. Created only when a scenario puts files in the tenant. The legal scenario has none. |
| `mock_mcp_servers/` | Mock MCP servers for third-party connectors, each with a `seed_files/` folder. See [its README](mock_mcp_servers/README.md). |
| `tools/` | The generator, validator and schema refresh scripts. |
| `tools/scenarios/` | One module per scenario holding its tenant seed data, plus `<scenario>_content/` for source content such as email bodies. |

The package files are generated, so make changes in `tools/scenarios/<scenario>.py` and rebuild rather than editing the JSON directly.

## Build and validate

Requires Python 3.10 or later with `jsonschema` installed.

```powershell
pip install jsonschema
python src/mock_environment/tools/build_tenant.py
python src/mock_environment/tools/validate_package.py
```

The validator checks the package against `_schemas` (JSON Schema 2020-12). It also applies the main COEP cross-file rules:

- user and license references
- that referenced files exist and match `FileName`
- shared links and placeholders
- email reply chains
- chat membership
- that timestamps are before `--as-of` (the planned provisioning time; defaults to now)

COEP rejects timestamps in the future. The legal story is pinned to a Monday lab date (`LAB_DATE` in `tools/scenarios/legal/__init__.py`, currently Mon Oct 12, 2026). The email is 14 days earlier, the group chat 6 days earlier, and the trigger message is at 8:07 AM ET on the lab date. The kit's original lab date was Mon Nov 9, 2026; every date in the seed data, the iManage documents and the scenario docs was moved back 28 days so everything is in the past, keeping weekdays and the contract's anniversary and payment schedule intact. To move the story again (for example, closer to the event), run:

```powershell
python src/mock_environment/tools/scenarios/legal/redate.py --lab-date 2026-11-02
python src/mock_environment/tools/build_tenant.py
```

## Refresh the schemas

```powershell
$env:COEP_TOKEN = "<bearer token from the COEP portal>"
python src/mock_environment/tools/refresh_schemas.py
```

To get a token, sign in to the portal and copy the `Authorization` bearer value from any `/schema/api/v1` request in the browser dev tools. After refreshing, run the validator again.

## Scenarios

| Scenario | Source | Tenant seed | Connector seed |
|----------|--------|-------------|----------------|
| Legal | [scenario](../scenarios/legal/scenario.md), [seed kit](../scenarios/legal/seed_kit.md) | `tools/scenarios/legal/`: 3 users, 1 email, 2 chats | `mock_mcp_servers/imanage/seed_files/` |
| Finance | [scenario](../scenarios/finance/scenario.md) | `tools/scenarios/finance/`: 2 users, 1 chat | Pending: data specs in `mock_mcp_servers/lseg/`, `factset/`, `moodys/` |
| Productivity | Pending | Pending | Pending |

To add a scenario, create a module or package under `tools/scenarios/` that exposes `users()`, `emails()`, `chats()`, `events()` and `files()`, and optionally `build_documents(files_dir)`. Then add it to `SCENARIOS` in `build_tenant.py`.

## Assumptions to review

- User aliases (`mhollowell`, `rsengupta`, `taguilar`) follow the kit's .eml addresses. Marcus has the Microsoft 365 Copilot license; Radhika and Tomás have mailbox and Teams only, as the kit specifies.
- External people (Diane Xu and Priya Ramasubramanian at Cognivault) have no accounts and appear only in documents.
- Finance: the one-pager names only "Alex" and "Jordan" at "an asset manager". The surnames (Morgan, Reyes), aliases (`amorgan`, `jreyes`), firm (Woodgrove Asset Management) and New York / Eastern time are placeholders. Alex has the Microsoft 365 Copilot license; Jordan has mailbox and Teams only.
- Finance: Jordan's trigger message is pinned to Fri Oct 9, 2026, 4:00 PM ET (`ASK_DATE` in `tools/scenarios/finance/__init__.py`). The investment committee isn't seeded as people or a meeting because the one-pager doesn't name its members or time.
