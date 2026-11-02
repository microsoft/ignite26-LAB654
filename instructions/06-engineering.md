# Engineering track: The fix exists. The customer is still waiting.

> **Duration:** ~15 minutes | **Connectors:** Test_Jira, Test_GitHub, Outlook, Teams | **Surfaces:** Copilot Chat, Copilot Cowork

## What you'll take away

- **A status isn't a commitment:** Copilot connects a customer's email to the team's recorded work and shows what's missing.
- **The real blocker is spread across tools:** only by joining the code review and a Teams discussion do you see why the customer is still waiting.
- **From evidence to decision:** a partner skill turns engineering context into a decision-ready slide, and Copilot drafts the team post and the customer reply for you to review.

## The story

You're **Emil Vanggaard** at Zava. You have an email from **Atul Manohar**, the pilot coordinator at Lakeshore Retail. Aurora smart-home hubs keep showing as offline after they reconnect, so store staff are restarting devices that are actually working.

Lakeshore Retail expands its pilot on **Monday, November 23**, and Atul needs a status update before then. You remember a Jira bug, but its last update only says someone has started working on the fix. Before you reply, you need to know what's really happening.

| Person | Role |
|---|---|
| **Emil Vanggaard** (you) | Owns the Lakeshore Retail pilot relationship. |
| Atul Manohar | Pilot coordinator, Lakeshore Retail. |
| Triin Lepp | Engineer working on the fix. |
| Maria Oliva | Engineer who owns rollout and reconnect testing. |
| Tama Surya | Platform lead; reviews the fix. |
| Kerry Allen | Engineering lead; approves sprint scope. |

You won't change any code or ship a release. Your job is to find the real status, understand what's blocking the fix, work out the sprint trade-off, then align the team and reply to Atul.

## Before you start

- [ ] You completed [Getting started with connectors](02-getting-started.md).
- [ ] **Test_Jira** and **Test_GitHub** show as connected.
- [ ] You can see Atul's email, *Aurora pilot - offline status still wrong*, in Outlook.

To see what Copilot will read, open the [Aurora Sprint 24 board](https://mock-jira.yellowsand-9530f5dc.eastus.azurecontainerapps.io/jira/software/projects/AUR/boards/57) in Test_Jira and the [aurora-status pull requests](https://mock-github.yellowsand-9530f5dc.eastus.azurecontainerapps.io/zava-lab/aurora-status/pulls) in Test_GitHub.

## Step 1: Where are we with the customer issue?

*Copilot Chat · Outlook · Test_Jira*

```text
Atul is asking if the Aurora offline-status bug will be fixed before the pilot expansion. Where are we with the fix, and what have we already told them?
```

**What to look for:**

- Copilot connects Atul's email to Jira issue [**AUR-142**](https://mock-jira.yellowsand-9530f5dc.eastus.azurecontainerapps.io/browse/AUR-142).
- What you told Atul: engineering is working on a fix. You didn't promise a date.
- AUR-142 is In Progress. The last update, on October 26, only says "I have started working on the fix", so the ticket doesn't say whether a fix is ready.
- Citations to the email and the Jira issue.

> [!TIP]
> A tracker status isn't a customer commitment. Copilot exposed the missing detail.

## Step 2: Has someone already raised a fix?

*Same chat · Test_GitHub · Teams*

```text
Can you find the PR for this item and where it is blocked?
```

**What to look for:**

- Copilot finds [**PR #287**](https://mock-github.yellowsand-9530f5dc.eastus.azurecontainerapps.io/zava-lab/aurora-status/pull/287) from its reference to AUR-142. The Jira issue doesn't link to it.
- The PR is open and unmerged. Tama requested changes: it fixes the old polling service, but the Teams discussion confirms the Lakeshore Retail pilot moves to the new event-driven service after the November 20 cutover.
- Two things are needed: Triin adapts the fix to the new service, and Maria adds and runs the new-service reconnect tests. Then Tama reviews again.

> [!TIP]
> The fix exists, but for the old service. Only joining the code review with the migration discussion shows why the customer is still blocked.

## Step 3: Make the sprint impact clear

*Copilot Cowork · Test_Jira sprint-to-slides skill*

Open Copilot Cowork and start a new task. Enter:

```text
/skill sprint-to-slides
Create one PowerPoint slide for Aurora Sprint 24 showing the impact of this fix and what we should move to make room for LT approval.
```

**What to look for:**

- The bug now needs 24 hours (from the newer [AUR-145](https://mock-jira.yellowsand-9530f5dc.eastus.azurecontainerapps.io/browse/AUR-145) breakdown), not the 8 recorded on AUR-142.
- Revised scope is 48 hours against 32 hours of capacity before the November 20 checkpoint: a **16-hour gap**.
- The proposal: defer the 16-hour custom dashboard filters work ([AUR-151](https://mock-jira.yellowsand-9530f5dc.eastus.azurecontainerapps.io/browse/AUR-151)) and keep the required rollout regression.
- One slide with customer impact, blocker, trade-off, owners and the decision needed.

> [!TIP]
> If Cowork doesn't have the context from Step 2, paste Copilot's Step 2 answer into the task first.

## Step 4: Align the team and reply to Atul

*Same Cowork task · Teams · Outlook*

```text
Share this slide in Aurora's engineering channel and ask LT to approve the revised sprint plan. Draft a reply to Atul with our progress and an update on November 20 at 3 pm.
```

**What to look for:**

- A Teams post for the Aurora **Engineering** channel with the slide, the 16-hour trade-off and named owners, asking the leadership team (Kerry and Tama) to approve.
- A customer-friendly reply to Atul: the fix needs validation on the service the pilot will use, and the next update is **Friday, November 20 at 3 pm**.
- No promised delivery date, no internal review friction and no invented workaround.
- Nothing is posted or sent until you approve it. Keep the email to Atul as a draft.

> [!TIP]
> One evidence base became two useful messages: an internal decision request and an honest customer update.

## If it goes wrong

| What happens | What to do |
|---|---|
| Step 1 doesn't find Atul's email | Ask: "Find Atul's email about Aurora offline status." |
| Step 2 doesn't find the PR | Ask: "Search GitHub for a pull request that references AUR-142." |
| The skill returns an outline, not a slide | Reply: "Create the .pptx file with one slide." |
| Copilot offers to send the email | Say no. Keep it as a draft. |

## Checkpoint

- [ ] You know the real status: a fix exists for the old service, and two tasks remain.
- [ ] You have one sprint slide showing the 16-hour gap and the proposed deferral.
- [ ] A Teams post and a reply to Atul are ready for your approval.

**What you take away:** You started with a customer email and a stale ticket. Copilot found the real blocker, showed the sprint trade-off, and helped you bring a clear plan to the team and the customer.

---

**Next:** [Bring your own app](07-custom-mcp.md), or try another track ([Finance](03-finance.md) · [Legal](04-legal.md) · [Productivity](05-productivity.md))
