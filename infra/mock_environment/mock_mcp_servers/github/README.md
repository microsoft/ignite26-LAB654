# GitHub mock server

A read-only mock of the GitHub MCP server ([github/github-mcp-server](https://github.com/github/github-mcp-server)). It supports the [engineering scenario](../../../../docs/scenarios/engineering/scenario.md) and [lab part 6](../../../../instructions/06-engineering.md), where it appears as the **Test_GitHub** connector. For the shared framework, and for how to run, test and deploy, see the [mock servers README](../README.md).

It serves one organization, **zava-lab**, which has one private repository: **aurora-status** (the Aurora hub status service). That repository holds four pull requests and their reviews. Copilot can search, list and read them, but can't change anything.

## Why read-only

Test_GitHub used to be a synced connector (Graph connector) seeded in the COEP tenant. A synced connector only indexes content: Copilot can find and cite pull requests, but it can't act on them. This mock keeps that behaviour by exposing only the live server's read tools. It has no write tools, such as `create_pull_request`, `merge_pull_request` or `pull_request_review_write`.

The original connector seed (`Connectors_Ignite_EMP/customconnectors/customconnectors_engineering.jsonl`) is unchanged and remains tenant data. This mock is built from the same items.

## Prompts it powers

| Lab step | What Copilot asks GitHub for |
|----------|------------------------------|
| 2 | The pull request that references AUR-142 (PR #287), its state, and Tama's changes-requested review |
| 2 (fallback) | "Search GitHub for a pull request that references AUR-142." |

## Tools

All 8 tools are read-only tools on the live server. Their names, descriptions, input schemas and annotations come from the github-mcp-server source (`seed_files/tool_schemas.json`). Every tool has `readOnlyHint: true`.

| Tool | Serves |
|------|--------|
| `get_me` | The signed-in user (Emil Vanggaard) |
| `search_users` | Users, matched on login and name. Supports `type:` and `org:` |
| `search_repositories` | zava-lab/aurora-status. Supports `repo:`, `org:`, `user:` and `is:private`/`is:public` |
| `search_pull_requests` | GitHub issue search for pull requests. Free text matches the title, body and review text, so `AUR-142` finds #287. Supports `is:`, `state:`, `repo:`, `org:`/`user:`, `author:`, `assignee:`, `reviewed-by:`, `involves:`, `label:`, `milestone:`, `review:`, `no:`, `in:`, `-` negation and `@me`. Unknown qualifiers are ignored |
| `list_pull_requests` | Pull requests in a repository. `state` defaults to `open` |
| `pull_request_read` | `get`, `get_reviews`, `get_comments` and `get_review_comments`. `get_diff`, `get_status`, `get_files`, `get_commits` and `get_check_runs` return an error saying the mock has no such data |
| `list_label`, `get_label` | The repository's 5 labels |

- Successes are JSON in the live server's minimal shapes, such as `MinimalPullRequest`, `MinimalUser` and search results with `total_count`, `incomplete_results` and `items`.
- Failures are plain text, as on the live server. Examples: `failed to get pull request: GET https://api.github.com/repos/zava-lab/aurora-status/pulls/9: 404 Not Found []` and `missing required parameter: repo`.
- `fields` on `list_pull_requests` and `search_pull_requests` keeps only the requested top-level fields.

## Data

| Item | Content |
|------|---------|
| Users | Emil Vanggaard (signed in), Triin Lepp, Maria Oliva, Kerry Allen, Tama Surya |
| PR #287 | *Fix stale offline state after reconnect*, by Triin. Open and unmerged, milestone Aurora Sprint 24. The body references AUR-142. Tama's review on October 28 requests changes: the fix targets the old polling service, and the pilot moves to the event-driven service after the November 20 cutover |
| PR #281 | *Add retry backoff to status poller*, by Triin. Merged, approved by Tama |
| PR #276 | *Event-driven status service: publish device heartbeat events*, by Tama. Merged, approved by Maria |
| PR #269 | *Rollout regression suite: add store-group targeting tests*, by Maria. Merged, approved by Kerry |

#281, #276 and #269 are decoys, so Copilot has to pick #287. The data is in `seed_files/seed.json`. It's built from the connector seed, with the same titles, bodies, people, labels, milestones, dates and reviews. Names come from CELA's approved fictitious names list (see the [mock environment README](../../README.md)). IDs are generated.

## Viewer

The viewer is a read-only look-alike of GitHub, marked **MOCK GITHUB**.

| Path | Page |
|------|------|
| `/zava-lab` | The organization and its repository |
| `/zava-lab/aurora-status` | Repository home with recent pull requests |
| `/zava-lab/aurora-status/pulls` | Pull request list. `?q=` takes the same search syntax as the tools |
| `/zava-lab/aurora-status/pull/{number}` | Pull request conversation: description, reviews and sidebar |
| `/zava-lab/aurora-status/labels` | Labels |
| `/{login}` | User profile |

The `html_url` links in tool results point to the viewer.

## Run and test

From `infra/mock_environment/mock_mcp_servers`:

```powershell
$env:PYTHONPATH = "_framework;github"
python -m mock_github                    # http://localhost:8000/mcp and the viewer at http://localhost:8000/
python -m pytest github/tests
docker build -f github/Dockerfile -t mock-github:latest .
```

| Variable | Default | Purpose |
|----------|---------|---------|
| `PUBLIC_BASE_URL` | `http://localhost:8000` | Public address, used for `html_url` and avatar links |
| `MOCK_NOW` | `2026-10-29T13:00:00Z` | The server's "now" (the scenario's snapshot) |

The mock keeps no state, so any number of replicas works.

## Known differences from the live server

- Only the 8 tools that the scenario needs are exposed. The live server's other read tools, such as `get_file_contents`, `list_issues` and `list_commits`, are left out because the seed has no files, issues or commits.
- Search supports the qualifiers listed above, not the full GitHub search syntax.
- Users have no email. The repository has 0 stars and forks, and no topics or language.
- `github.com` is never used. Links point to the viewer.
