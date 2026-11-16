# Set up the BRK220 demo in a new tenant

How to stand up the BRK220 Contoso renewal demo (Demos 1 and 2) for a new Copilot user in a separate tenant. The demo user is **Megan Bowen**, Account Executive at Northwind Ltd. For the story and the expected answers, see [scenario.md](scenario.md).

No credentials are stored in this repo. Get user passwords from the tenant itself (for a COEP tenant, from the tenant's **View users** dialog in the SEVAL portal).

## What the demo needs

| Piece | Where it comes from | Folder |
|---|---|---|
| 7 users, 4 emails, 1 Teams chat, the Q3 QBR meeting with its transcript, 3 OneDrive Word files | COEP grounding package | [`tenant/Connectors_BRK220_Demo/`](tenant/Connectors_BRK220_Demo) |
| **Rovo** connector (Jira; Confluence fallback) and **Salesforce** connector, installed for Megan | Microsoft 365 app packages that point at the mock MCP servers | [`mock_plugins/`](mock_plugins) |
| `renewal-prep` skill | Ships inside the Salesforce package | [`mock_plugins/salesforce/skills/renewal-prep/`](mock_plugins/salesforce/skills/renewal-prep/SKILL.md) |
| Jira incidents and Salesforce renewal data | Mock MCP servers on Azure Container Apps | [`mock_mcp_servers/`](mock_mcp_servers) |
| Confluence account page and product roadmap | Real Confluence Cloud site, indexed by the **Confluence connector** | [`confluence/`](confluence) |

### Users

| User (UPN prefix) | Name | Role | Copilot licence |
|---|---|---|---|
| `megan` | Megan Bowen | Account Executive (the demo user) | Yes |
| `alex` | Alex Wilber | Regional Sales Director | No |
| `isaiah` | Isaiah Langer | Customer Success Manager | No |
| `arjun` | Arjun Kumar | Senior Support Engineer, EU Platform | No |
| `rosa` | Rosa Diaz | Support Engineer | No |
| `lidia` | Lidia Holloway | Contoso CIO (mailbox and Teams only) | No |
| `daniel` | Daniel Okafor | Contoso Head of Procurement (mailbox and Teams only) | No |

## 1. Mock MCP servers

Two servers are already deployed and kept warm (`--min-replicas 1`):

| Connector | MCP URL |
|---|---|
| Rovo | `https://northwind-atlassian.salmonstone-078b8962.eastus.azurecontainerapps.io/mcp` |
| Salesforce | `https://northwind-salesforce.salmonstone-078b8962.eastus.azurecontainerapps.io/mcp` |

Writes are kept per Copilot conversation, so several tenants can share these servers without seeing each other's changes. Each server has one email domain (`TENANT_EMAIL_DOMAIN`), currently the existing BRK220 tenant's. Salesforce contacts and Jira users use that domain, so in a new tenant Demo 2's proposal email would be addressed to the old tenant's Daniel.

Choose one:

- **Deploy your own pair (recommended).** Follow [README.md → Deploy from scratch](README.md#deploy-from-scratch) and set `TENANT_EMAIL_DOMAIN` to the new tenant's domain. Keep `--min-replicas 1` and neutral app names; Copilot shows the host name in citations. Then go to step 2.
- **Ask Shiladitya to deploy a second pair** with the new domain (about 15 minutes), then go to step 2.
- **Reuse the shared servers** as they are, if the email recipient doesn't matter. Skip step 2; the committed packages already point at them.

## 2. Point the packages at your servers

Only needed if the MCP URLs changed.

1. In `mock_plugins/rovo/manifest.json` and `mock_plugins/salesforce/manifest.json`, set `mcpServerUrl` to your servers' `/mcp` URLs and bump `version` (for example `1.0.3`).
2. Rebuild and validate (from the repo root):

```powershell
pip install -r infra/brk220_environment/tenant/requirements.txt
python infra/brk220_environment/mock_plugins/build_plugins.py
python infra/brk220_environment/tenant/tools/build_tenant.py
python infra/brk220_environment/tenant/tools/validate_package.py
```

`build_tenant.py` copies the packages into `DAConfig/` and writes `das.config.json` with `ActionType: Install` for Megan.

## 3. Create the tenant (COEP)

1. Zip the **contents** of `tenant/Connectors_BRK220_Demo/` (files at the zip root, not inside a folder).
2. In [SEVAL](https://seval.microsoft.com) → **Eval Set** → **Publish EvalSet**, upload the zip. Offerings: BizChat Web and DA.
3. **Tenant and Ingestion Progress** → **Create**. Choose the evalset and version, Ring **MSIT**, Region **NAM**, default licences and SPO instance, and meeting transcript ingestion **Yes** (API-based). Provisioning takes about 35 to 60 minutes.
4. When every entity shows 100%, open **View users** and copy Megan's password. Her first sign-in asks her to register Microsoft Authenticator.
5. Check that Copilot shows **Rovo** and **Salesforce** under **+** → **Change data sources**.

To change the packages later, bump each manifest version, rebuild with `build_tenant.py --da-update 2` (then 3, and so on), publish a new evalset version and **Update** the tenant. Updates are incremental: items whose IDs already exist are skipped.

**Not using COEP?** Seed the same content by hand from [`tenant/tools/scenario.py`](tenant/tools/scenario.py) (emails, chat, meeting, transcript) and the Word files in `tenant/Connectors_BRK220_Demo/files/brk220/`, then upload the two ZIPs in `mock_plugins/` as custom apps for Megan. The tenant must allow custom apps; the original COEP tenant doesn't allow sideloading, which is why the packages go through `das.config.json`.

## 4. Confluence

The skill reads the account page and roadmap through the Confluence connector, not Rovo.

1. **Pages.** The Customer Success (`CS`) and Product Roadmap (`PROD`) spaces already exist on `graphc-test.atlassian.net`. To use another site, create the spaces, pages, labels and tables exactly as in [`confluence/BRK220_Confluence_Seed_Pages.docx`](confluence/BRK220_Confluence_Seed_Pages.docx). The skill finds pages by title and by the `contoso-ltd` label.
2. **Connector.** In the new tenant's Microsoft 365 admin center, add the **Confluence Cloud** Copilot connector for the site, include the `CS` and `PROD` spaces, and make sure Megan can see them. Denny Pang set this up for the original tenant.
3. **Megan's Atlassian account.** Invite Megan's address to the Atlassian site. Her first **Continue with Microsoft** sign-in asks for an emailed verification code and a robot check, which have to be done by hand.
4. **Check.** Once the crawl finishes, ask Copilot as Megan: *Find the Confluence page "Contoso Ltd – account overview" and summarize the open customer asks.*

## 5. Run the demos

| Demo | Prompt | Typical time |
|---|---|---|
| 1 | *Prep me for my Contoso renewal.* | About 60 s |
| 2 | *Close out the Contoso risks before renewal: assign owners to the latency tickets, send Contoso the renewal proposal, and draft the renewal contract.* Then approve each step | See known issues |

The expected results for each step are in [scenario.md](scenario.md). Demo 2 writes to Jira and Salesforce. Issue and record links in Copilot's answers open the mock servers' Jira and Salesforce pages, which show that conversation's changes.

## Known issues

| Issue | What to do |
|---|---|
| Demo 2: after approving the Jira step, Copilot repeated the same assign and comment calls five times (19 *Allow once* prompts, about 9 minutes). Every call succeeded on the server | Copilot-side. Use the recorded video for Demo 2 until it's fixed |
| Copilot answers *We're currently experiencing high traffic* | Service throttling. Wait a few minutes and retry |
| Copilot reports a connector as unavailable | Check `/healthz` on the server and that it runs with `--min-replicas 1` |
| Demo 2 leaves an Outlook draft and a `(DRAFT).docx` in Megan's OneDrive | Delete them between rehearsals so Demo 1 doesn't cite them |

All names, companies and data are fictitious.
