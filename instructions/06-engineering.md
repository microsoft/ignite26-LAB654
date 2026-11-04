# Engineering track: One item at risk. Who is it waiting on?

> **Duration:** ~15 minutes | **Connectors:** Jira and Confluence (synced), Test_GitHub, Test_Rovo, Teams | **Surfaces:** Copilot Chat, Copilot Cowork

## What you'll take away

- **Synced connectors answer from the source of record:** Copilot reads the sprint straight from Jira and spots the one item that isn't on track.
- **The real blocker is spread across tools:** Jira knows the item is late, Confluence knows what was promised and who decides, and GitHub knows where the code stands. Together they show what the work is waiting on.
- **From investigation to action:** in Cowork, Copilot asks the right person for the decision and a partner skill turns the sprint into a leadership slide.

## The story

You're **Emil Vanggaard**, product manager for Aurora at Zava. Aurora is a smart-home hub that retail stores use to track devices. Lakeshore Retail is piloting it, and on **Monday, November 23**, every pilot store goes live.

Atul, the pilot coordinator, has emailed again: hubs keep showing Offline after they reconnect, and staff are restarting devices that are working fine. He wants to know if it'll be fixed before the expansion.

You open the Sprint 24 board. Almost everything is on track. One item isn't, and it's Atul's bug. The ticket says it's at risk, but not why, and nobody can give you a date. Before you answer Atul, you need to know who the work is really waiting on, and get it moving.

| Person | Role |
|---|---|
| **Emil Vanggaard** (you) | Product manager; owns the Lakeshore Retail pilot. |
| Atul Manohar | Pilot coordinator, Lakeshore Retail. |
| Triin Lepp | Engineer working on the fix. |
| Maria Oliva | Engineer who owns rollout and reconnect testing. |
| Tama Surya | Platform lead; signs off design changes and reviews the fix. |
| Kerry Allen | Engineering lead; runs the sprint. |

You won't change any code or ship a release. In **Copilot Chat** you'll investigate. Then you'll switch to **Copilot Cowork** to act.

## Before you start

- [ ] You completed [Getting started with connectors](02-getting-started.md).
- [ ] **Test_GitHub** and **Test_Rovo** show as connected.
- [ ] The **Jira** and **Confluence** synced connectors are available in your tenant (your facilitator set them up).

To see what Copilot will read, open the [Aurora Sprint 24 board](https://mock-atlassian.yellowsand-9530f5dc.eastus.azurecontainerapps.io/jira/software/projects/AUR/boards/57), the [ADR-014 page](https://mock-atlassian.yellowsand-9530f5dc.eastus.azurecontainerapps.io/wiki/spaces/AUR/pages/98457) in Confluence, and the [aurora-status pull requests](https://mock-github.yellowsand-9530f5dc.eastus.azurecontainerapps.io/zava-lab/aurora-status/pulls) in GitHub.

## Part A: Investigate in Copilot Chat

### Step 1: How is the sprint going?

*Copilot Chat · Jira*

```text
What's the status of Aurora Sprint 24? Is anything at risk for the Lakeshore Retail pilot expansion?
```

**What to look for:**

- A summary of the six Sprint 24 items. Two are done, the cutover runbook and regression checks are on track, and custom dashboard filters is a low-priority stretch item.
- One item is at risk: [**AUR-142**](https://mock-atlassian.yellowsand-9530f5dc.eastus.azurecontainerapps.io/browse/AUR-142), *Aurora hubs remain offline after reconnect*. Kerry notes it's the only Sprint 24 item tied to the November 23 expansion that isn't on track.
- Citations to the Jira items.

> [!TIP]
> The board is mostly green, and Copilot picks out the one item that matters to your customer.

### Step 2: What's really going on with AUR-142?

*Same chat · Jira · Confluence · Test_GitHub*

```text
What's the current status of AUR-142, and what is it waiting on? Check Jira, Confluence and GitHub.
```

**What to look for:**

- **Jira:** AUR-142 is In Progress and at risk. Triin can't give a date until a design decision gets platform sign-off.
- **Confluence:** the *Lakeshore Retail pilot - delivery commitments* page says the pilot moves to the event-driven status service on November 20, and that platform sign-off is needed for any change to reconnect handling. [**ADR-014**](https://mock-atlassian.yellowsand-9530f5dc.eastus.azurecontainerapps.io/wiki/spaces/AUR/pages/98457) is still *Proposed*, and **Tama Surya** is the decision owner.
- **GitHub:** [**PR #287**](https://mock-github.yellowsand-9530f5dc.eastus.azurecontainerapps.io/zava-lab/aurora-status/pull/287) is open. It fixes only the old polling service, and Tama requested changes for the event-driven service.
- **The answer:** the fix is waiting on Tama's approval of ADR-014. After that, Triin updates PR #287, Maria adds the new tests, and Tama reviews again.

> [!TIP]
> No single tool had the whole story. Joining them shows the work isn't stuck on code. It's waiting on one approval.

## Part B: Act in Copilot Cowork

Open **Copilot Cowork** and start a new task. Cowork may not have your Chat conversation, so these prompts include the context they need.

### Step 3: Ask Tama for the decision

*Copilot Cowork · Teams*

```text
Send Tama Surya a Teams message. Ask Tama to approve ADR-014 so Triin can start the event-driven fix for AUR-142, and to re-review PR #287 once it's updated. Mention the November 20 cutover and include links to the ADR, the Jira item and the PR.
```

**What to look for:**

- A short Teams message to Tama: what's waiting, why it matters for November 20 and November 23, what happens after approval, and the three links.
- Cowork shows you the recipient and the message before sending. Check it, then approve.

> [!TIP]
> The investigation became one clear ask, sent to the right person with the evidence attached.

### Step 4: Turn the sprint into a slide

*Same Cowork task · Test_Rovo sprint-to-slides skill*

```text
/skill sprint-to-slides
Create one PowerPoint slide summarizing Aurora Sprint 24 for engineering leadership: what's on track, the one item at risk, what it's waiting on, and the next steps.
```

**What to look for:**

- One slide with the sprint goal and dates, the items on track, AUR-142 at risk, the blocker (ADR-014 waiting on Tama), and next steps with owners.
- Key dates: November 18 dry run, November 20 cutover, November 23 expansion.
- No invented delivery date, velocity or story points.

> [!TIP]
> A partner skill turned live Jira and Confluence data into a leadership-ready slide in one step.

## If it goes wrong

| What happens | What to do |
|---|---|
| Step 1 doesn't find the sprint | Ask: "Search Jira for the Aurora Sprint 24 work items." |
| Step 2 misses the Confluence or GitHub part | Ask: "Find ADR-014 in Confluence" or "Search GitHub for a pull request that references AUR-142." |
| The skill returns an outline, not a slide | Reply: "Create the .pptx file with one slide." |
| Cowork sends without showing you the message | Tell your facilitator. Messages should always ask for approval first. |

## Checkpoint

- [ ] You know which Sprint 24 item is at risk and why.
- [ ] You know the fix is waiting on Tama's approval of ADR-014, then code, tests and a re-review.
- [ ] A Teams message to Tama is sent or ready for your approval.
- [ ] You have one sprint slide for leadership.

**What you take away:** You started with a mostly green sprint board. Copilot found the one item at risk, joined Jira, Confluence and GitHub to show what it was waiting on, then Cowork asked for the decision and gave leadership a one-slide update.

## More connectors to try

The same pattern works with other connectors. Try them in your own tenant for similar scenarios.

<table>
  <tr>
    <td align="center"><img src="images/connectors/azure-devops.svg" alt="Azure DevOps" width="200"></td>
    <td align="center"><img src="images/connectors/linear.svg" alt="Linear" width="200"></td>
    <td align="center"><img src="images/connectors/webflow.svg" alt="Webflow" width="200"></td>
  </tr>
</table>

<sub>Logos are trademarks of their respective owners.</sub>

---

**Next:** [Bring your own app](07-custom-mcp.md), or try another track ([Finance](03-finance.md) · [Legal](04-legal.md) · [Productivity](05-productivity.md))
