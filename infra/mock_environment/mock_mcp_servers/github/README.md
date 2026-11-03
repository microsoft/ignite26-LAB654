# GitHub mock server

A mock of the GitHub MCP server ([github/github-mcp-server](https://github.com/github/github-mcp-server)). It supports the [engineering scenario](../../../../docs/scenarios/engineering/scenario.md) and [lab part 6](../../../../instructions/06-engineering.md), where it appears as the **Test_GitHub** connector. For the shared framework, and for how to run, test and deploy, see the [mock servers README](../README.md).

It serves one organization, **zava-lab**, which has one private repository: **aurora-status** (the Aurora hub status service). That repository holds four pull requests and their reviews. Copilot can search and read them, and can comment, review, label and edit them. Each conversation's changes are kept separately and never touch the original data.

## Background

Version 1 of this mock had read-only tools. Version 2 adds the live server's write tools that fit the data, kept per conversation like the other mocks.

## Prompts it powers

| Lab step | What Copilot asks GitHub for |
|----------|------------------------------|
| 2 | The pull request that references AUR-142 (PR #287), its state, and Tama's changes-requested review |
| 2 (fallback) | "Search GitHub for a pull request that references AUR-142." |

## Tools

18 tools: 8 read tools and 10 write tools. Their names, descriptions, input schemas and annotations come from the github-mcp-server source (`seed_files/tool_schemas.json`). Read tools have `readOnlyHint: true`; write tools have `readOnlyHint: false`.

### Read tools

| Tool | Serves |
|------|--------|
| `get_me` | The signed-in user (Emil Vanggaard) |
| `search_users` | Users, matched on login and name. Supports `type:` and `org:` |
| `search_repositories` | zava-lab/aurora-status. Supports `repo:`, `org:`, `user:` and `is:private`/`is:public` |
| `search_pull_requests` | GitHub issue search for pull requests. Free text matches the title, body and review text, so `AUR-142` finds #287. Supports `is:`, `state:`, `repo:`, `org:`/`user:`, `author:`, `assignee:`, `reviewed-by:`, `involves:`, `label:`, `milestone:`, `review:`, `no:`, `in:`, `-` negation and `@me`. Unknown qualifiers are ignored |
| `list_pull_requests` | Pull requests in a repository. `state` defaults to `open` |
| `pull_request_read` | `get`, `get_reviews`, `get_comments` and `get_review_comments`. `get_diff`, `get_status`, `get_files`, `get_commits` and `get_check_runs` return an error saying the mock has no such data |
| `list_label`, `get_label` | The repository's 5 labels |

### Write tools

| Tool | Does |
|------|------|
| `add_issue_comment` | Adds a comment to a pull request's conversation, and/or a reaction to the pull request or to a comment (`comment_id`) |
| `update_issue_comment` | Edits a comment's body |
| `issue_write` | `update` edits a pull request's title, body, labels, assignees and state, because GitHub treats pull requests as issues. `create` fails with "Issues are disabled for this repo", because the team tracks work in Jira |
| `label_write` | Creates, updates and deletes repository labels |
| `pull_request_review_write` | `create` (with an `event`, or pending without one), `submit_pending`, `delete_pending`, `resolve_thread` and `unresolve_thread` |
| `add_comment_to_pending_review` | Adds a file or line comment to your pending review |
| `add_reply_to_pull_request_comment` | Replies to, or reacts to, a review comment |
| `update_pull_request` | Edits title, body, state, base, draft and `maintainer_can_modify`, and requests reviewers (`copilot` requests Copilot) |
| `merge_pull_request` | Merges, subject to branch protection on `main`: it needs an approving review and no outstanding changes requested. PR #287 can't be merged while Tama's review stands, which matches the scenario |
| `request_copilot_review` | Requests a review from Copilot |

Rules follow GitHub: you can't approve or request changes on your own pull request, a pending review is visible only to you, unknown reviewers return 422, and unknown comments return 404.

### Left out

| Tools | Why |
|-------|-----|
| `create_pull_request`, `update_pull_request_branch`, `create_pull_request_with_copilot` | The seed has no branches or commits |
| `sub_issue_write` and other issue-only tools | Issues are disabled. Work is tracked in Jira |
| File, branch, repository, Actions, gist, notification and security tools | The seed has no such data |

### Output
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

## Conversations and the viewer

Each tool call carries the host's `x-microsoft-ai-conversationid` header. Writes go to that conversation's own copy of the data, held in memory. Reads in the same conversation see the changes; other conversations, and calls without the header, see the original data. Writes without the header have no effect. Copies are lost when the server restarts.

The viewer is a look-alike of GitHub, marked **MOCK GITHUB**.

| Path | Page |
|------|------|
| `/zava-lab` | The organization and its repository |
| `/zava-lab/aurora-status` | Repository home with recent pull requests |
| `/zava-lab/aurora-status/pulls` | Pull request list. `?q=` takes the same search syntax as the tools |
| `/zava-lab/aurora-status/pull/{number}` | Pull request conversation: description, reviews, comments, threads and sidebar |
| `/zava-lab/aurora-status/labels` | Labels |
| `/{login}` | User profile |

The `html_url` links in tool results point to the viewer. In a conversation with changes, they start with `/v/{token}/`, which shows that conversation's copy. The token is an HMAC of the conversation ID, so it doesn't reveal it. A token with no saved changes (for example after a restart) shows the original data with a notice.

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
| `GITHUB_VIEW_SECRET` | random per process | Key for the `/v/{token}` viewer links. Set it so links survive a new revision's process |

Conversation copies live in process memory and expire after 2 hours without use, so run exactly one replica.

## Known differences from the live server

- Only the tools that the data supports are exposed (see [Left out](#left-out)). Read tools such as `get_file_contents`, `list_issues` and `list_commits` are also left out because the seed has no files, issues or commits.
- Write tool results follow the live server's shapes (`MinimalResponse` with a string `id` and a `url`, or plain-text messages). A few error messages, such as approving your own pull request, are written to match GitHub's API but weren't captured from the live server.
- Search supports the qualifiers listed above, not the full GitHub search syntax.
- Users have no email. The repository has 0 stars and forks, and no topics or language.
- `github.com` is never used. Links point to the viewer.
