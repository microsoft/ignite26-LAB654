# Salesforce mock server (BRK220)

Mock of the Salesforce Hosted MCP server for the [BRK220 scenario](../../scenario.md). In Copilot it appears as the **Salesforce** connector. Adapted from the LAB654 Salesforce mock (`microsoft/ignite26-LAB654`, branch `mock-environment-setup`); the five tools (`discover`, `describe`, `dispatch_readonly`, `dispatch`, `display_widget`) and their response envelopes are unchanged.

It serves a small Sales Cloud org for **Northwind Ltd**. Megan Bowen owns the Contoso Ltd account and its open FY27 renewal. Copilot can read the org with SOQL, GraphQL, search and sObject reads, and create, update or delete records. Changes are kept per conversation, and a Lightning Experience look-alike viewer shows them.

## Data

| Object | Records |
|--------|---------|
| Users | Megan Bowen (Account Executive, signed in), Alex Wilber (Regional Sales Director, Megan's manager), Lee Gu (Account Executive) |
| Accounts | **Contoso Ltd** (Customer, Megan), **Contoso Pharmaceuticals** (Prospect, Lee Gu; tests that Copilot picks the right Contoso), Tailwind Traders, Adatum Corporation |
| Contacts | Lidia Holloway (CIO) and Daniel Okafor (Head of Procurement), both at Contoso Ltd |
| Open renewal | *Contoso Ltd – FY27 platform renewal*: Value Proposition, $2,400,000, close Dec 31, 2026, Type Existing Customer - Renewal, Competitor Fabrikam |
| Current contract | *Contoso Ltd – Platform subscription 2025–2026*: Closed Won, $2,400,000 a year |
| Win/loss vs Fabrikam | *Tailwind Traders – FY26 platform renewal*: Closed Won, held a 4% uplift against Fabrikam's 25% off, named engineer on open P1s. *Adatum Corporation – FY26 platform renewal*: Closed Lost (Competitor), matched 15% late with P1s unassigned and lost anyway |
| Activities | Event *Contoso Ltd – Q3 QBR* (Sep 29) and two completed Tasks (renewal kickoff, pricing options sent). The agreed 5% cap is **not** in Salesforce; it's in the Outlook thread |
| Dashboard | *FY27 Renewals Pipeline* |

The data is built in `mock_salesforce/seed.py`. `catalog.json` (recorded `discover` cards) and `limits.json` are unchanged from LAB654.

## Calls the renewal-prep skill makes

| Step | Call |
|------|------|
| Find the account | `SELECT … FROM Account USING SCOPE mine WHERE Name LIKE 'Contoso%'` → only Contoso Ltd |
| Renewal and contract | `SELECT … FROM Opportunity WHERE AccountId = '<id>' ORDER BY CloseDate DESC` |
| Win/loss | `SELECT … FROM Opportunity WHERE Competitor__c = 'Fabrikam' AND IsClosed = true` |
| Close-out write | `PATCH /sobjects/Opportunity/<id>` (Stage Proposal/Price Quote, Amount $2,520,000, Next Step) and `POST /sobjects/Task` |

All are covered by `tests/test_salesforce.py`.

## Run and test

From `infra/brk220_environment/mock_mcp_servers`:

```powershell
pip install -r requirements-dev.txt
$env:PYTHONPATH = "_framework;salesforce"
python -m mock_salesforce             # http://localhost:8000/mcp and the viewer at http://localhost:8000/
python -m pytest salesforce/tests
docker build -f salesforce/Dockerfile -t mock-salesforce-brk220:latest .
```

| Variable | Default | Purpose |
|----------|---------|---------|
| `PUBLIC_BASE_URL` | `http://localhost:8000` | Public address. Used for the instance URL in `url` fields and for viewer links |
| `SALESFORCE_VIEW_SECRET` | random per process | Key for the viewer's link tokens |
| `TENANT_EMAIL_DOMAIN` (or `SF_EMAIL_DOMAIN`) | `northwind-ltd.example` | Email domain for users and Contoso contacts. Set it to the COEP tenant's domain so contacts match meeting attendees by email |
| `MOCK_NOW` | the real time | The server's "now" |
| `MOCK_SHARED_STATE` | unset | `1`: all conversations and header-less calls share one set of changes (for Demo 2 → Demo 3 across surfaces). Restart to reset |

Run one replica: conversation changes live in memory.

## Changes from the LAB654 mock

- New seed (`seed.py`); "Existing Customer - Renewal" added to the Opportunity Type picklist (`schema.py`).
- The clock defaults to the real time (`server.py`); dashboard and footer text (`web.py`).
- Optional shared state across conversations, `MOCK_SHARED_STATE` (`store.py`).
