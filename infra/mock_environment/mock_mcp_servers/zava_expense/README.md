# Zava Expense mock server

Mock of **Zava Expense**, Zava's in-house expense system, for the custom connector scenario ([module 07](../../../../instructions/07-custom-mcp.md)). The lab user connects a line-of-business app that isn't in any connector catalog, then uses it in Copilot. The user is **Emil Vanggaard**. There's no sign-in and no MCP Apps widget.

There's no real server to copy: the tools, data and policy are written for the lab.

## Tools

| Tool | Kind | Purpose |
|------|------|---------|
| `list_expense_reports` | Read | Reports and their status, including why one was rejected or returned |
| `get_expense_report` | Read | One report with line items, receipts, approver and a policy check |
| `list_card_transactions` | Read | Corporate card charges, unreported by default; flags duplicates |
| `get_travel_policy` | Read | Hotel caps by city, meal and entertainment limits, receipt rules |
| `check_expense_report` | Read | Policy check before submitting: blocking issues and warnings |
| `get_spend_vs_budget` | Read | Quarter-to-date travel spend vs budget by category |
| `create_expense_report` | Write | Draft a report from receipts; each one is matched to its card charge |
| `update_expense_report` | Write | Add or remove items, attach receipts, add a justification |
| `submit_expense_report` | Write | Submit to the manager; refuses while a blocking issue remains |

## The story data

`scripts/build_seed.py` builds `seed_files/expense_seed.json` from `seed_files/expense_world.json`. The server only reads the built seed. After editing the world file, run the script and the tests.

- **Emil Vanggaard**, Stamford, CT. Corporate card ending 4417. Approver: **Hannes Niemi**. Finance contact: **Ebere Ibeabuchi**.
- 111 card charges from June to mid-November 2026 and 11 past reports: 7 approved, 2 pending, 1 rejected (missing receipt for a $142.60 dinner), 1 returned (no business purpose).
- A 12-rule travel policy (TE-01 to TE-12) and a Q4 travel budget of $6,800.
- **The Seattle trip** (Mon Oct 26 to Thu Oct 29, client Fabrikam, Inc.): 8 card charges, not on any report yet. Two planted problems:
  - The Westin's last night (Oct 28) is **$389**, over the **$250** Seattle cap. Submitting is blocked until Emil adds a justification.
  - The last Uber ride was **charged twice** (TX-10111). The check warns not to claim it twice and to have it reversed.

The tests pin the numbers the lab guide quotes: open reports ER-1044, ER-1045 ($631.50), ER-1046 and ER-1051 ($953.09); a six-receipt Seattle report of $2,052.65; and Q4 spend of $4,309.55 of $6,800 (63%), with meals at 106%, ground transport at 111% and lodging at 80%.

## Dates

The clock is fixed at **Mon Nov 16, 2026, 9 AM ET** (lab week), so "today", the submission deadline and the share of the quarter elapsed (51%) always match the lab guide. `MOCK_NOW` (ISO 8601) overrides it for testing; leave it unset in production.

## Receipt emails in Emil's mailbox

The tenant seeds these in Emil's inbox. Copilot reads them and passes them to `create_expense_report`; each receipt is matched to its card charge by date, merchant and amount.

| Received | From | Subject | Amount |
|---|---|---|---|
| Mon Oct 19 | Alaska Airlines | Your receipt: Seattle (SEA) round trip, confirmation KXQ4TZ | $486.40 |
| Mon Oct 26 | Seattle Yellow Cab | Seattle Yellow Cab — trip receipt | $58.75 |
| Tue Oct 27 | Canlis | Your receipt from Canlis — party of 5 | $540.00 |
| Wed Oct 28 | Din Tai Fung | Your Din Tai Fung receipt | $48.20 |
| Thu Oct 29 | The Westin Seattle | Your folio from The Westin Seattle | $867.00 |
| Thu Oct 29 | Uber Receipts | Your Thursday morning trip with Uber | $52.30 |
| Fri Oct 30 | Zava Expense | Reminder: submit your Seattle trip expenses by Friday, November 20 | – |

The bodies are in `seed_files/expense_world.json` (`seattle_trip.receipt_emails`).

## How writes work

Writes are kept per conversation using the `x-microsoft-ai-conversationid` header. Reads return the seed plus the same conversation's changes; other conversations and seats never see them; state is dropped after 2 hours idle. A new conversation always starts clean, so there's nothing to reset between lab sessions. Run **one replica** (`--max-replicas 1`).

## Run locally

From `infra/mock_environment/mock_mcp_servers`:

```powershell
$env:PYTHONPATH = "_framework;zava_expense"
python zava_expense\scripts\build_seed.py   # only after editing expense_world.json
python -m mock_zava_expense                 # streamable HTTP on :8000/mcp
python -m pytest zava_expense               # tests
```

## Deploy

Follow [DEPLOYMENT.md](../DEPLOYMENT.md) with `$S = "zava_expense"`, but name the app and image `mock-zava-expense`, and use `--max-replicas 1`. The plugin in [`mock_plugins/zava_expense`](../../mock_plugins/zava_expense) expects `https://mock-zava-expense.yellowsand-9530f5dc.eastus.azurecontainerapps.io/mcp`.
