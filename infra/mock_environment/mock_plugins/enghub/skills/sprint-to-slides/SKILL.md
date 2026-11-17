---
name: sprint-to-slides
description: "Transform EngHub sprint data into presentation-ready deliverables. Queries sprint or project data from EngHub, enriches with Teamwork Graph collaboration insights, then (1) generates a structured Word report with metrics, accomplishments, team collaboration, and risks, (2) produces a PowerPoint-ready outline with slide-by-slide content including team dynamics, (3) creates an EngHub Docs archive page, and (4) identifies key talking points and narrative arc."
---

# Sprint to Slides

Transform EngHub sprint data into presentation-ready deliverables. Queries sprint or project data from EngHub, enriches with collaboration patterns from Teamwork Graph, then generates (1) a structured Word report with metrics, accomplishments, team collaboration, and risks, (2) a PowerPoint-ready outline with slide-by-slide content including team dynamics, (3) an EngHub Docs archive page, and (4) identifies key talking points and narrative arc.

**Problem it solves:** Every PM manually copies EngHub data into slides each sprint, but misses the cross-tool collaboration story—who reviewed PRs, who authored docs, who unblocked whom. This skill automates the data-to-narrative pipeline, turning sprint metrics AND team collaboration patterns into exec-ready presentations in minutes instead of hours.

---

## Keywords

sprint, retro, retrospective, report, powerpoint, word, slides, presentation, stakeholder, review, metrics, velocity, burndown, deliverables, storytelling, team highlights, narrative arc, collaboration, teamwork graph, cross-tool activity, PR reviews, code review culture, team dynamics, pair work

---

## Overview

Sprint retros and stakeholder reviews require the same painful manual workflow:
1. Export EngHub sprint board
2. Count completed stories, sum story points
3. Calculate velocity trend, identify blockers
4. Copy metrics into a slide deck or report
5. Manually add team highlights and narrative
6. Create talking points for the exec audience

This skill eliminates steps 1-5. It:
- **Queries EngHub** for sprint data (stories, velocity, burndown, blockers, bugs)
- **Queries Teamwork Graph** for collaboration insights (who worked with whom, cross-tool contributions, PR reviews, EngHub Docs edits, activity patterns)
- **Computes metrics** (velocity trend, completion rate, carry-over, bug ratio, contributor breakdown, collaboration health)
- **Builds narrative** (what we shipped, what we learned, who unblocked whom, cross-team dynamics, what's next, key risks)
- **Generates Word report** (polished, shareable, exec-ready, includes collaboration section)
- **Produces PowerPoint outline** (slide-by-slide content, team collaboration slide, structured for your design system)
- **Archives to EngHub Docs** (optional, for async stakeholder access)
- **Exports talking points** (key moments, quotable insights, collaboration highlights, narrative arc)

**Output:** A complete sprint package—Word report with collaboration insights, PowerPoint outline with team dynamics slide, EngHub Docs page, and speaker notes—ready for review or presentation in under 2 minutes.

---

## Workflow

### Step 1: Identify Scope

Gather context before querying EngHub:
- **Sprint name or project key** (e.g., "DT-34" or "EngHub" or date range)
- **Date range** (sprint start/end, or custom range for cross-sprint analysis)
- **Audience** (executive, team, board—affects narrative tone and metric emphasis)
- **Report style** (formal/casual, quantitative/qualitative balance)
- **EngHub Docs space** (optional, for archival page creation)

**Why this matters:** A board presentation emphasizes risk and capacity. A team retro emphasizes learning and collaboration. This skill adapts narrative voice accordingly.

---

### Step 2: Query EngHub for Sprint Data

Using EngHub API or GraphQL, fetch:
- **Story list** (key, summary, status, story points, assignee, due date)
- **Completed stories** (status = "Done" within sprint date range)
- **Sprint metadata** (sprint name, start date, end date, goal, target velocity)
- **Burndown data** (daily committed points, daily completed points, if available from EngHub timeline)
- **Blockers and risks** (issues marked with blocker label, "Blocked" status, or parent epic risks)
- **Bug metrics** (bugs found, bugs fixed, open bug count)
- **Velocity history** (past 3-4 sprints, for trend calculation)

**API calls needed:**
- `GET /rest/api/3/sprints/{sprintId}` (sprint metadata)
- `GET /rest/api/3/sprints/{sprintId}/issues` (all sprint issues)
- `GET /rest/api/3/projects/{projectKey}/issue-search` (blockers, bugs, risks across sprints)

**Fallback:** If EngHub API is unavailable, query from EngHub Docs sprint pages or ask user to provide an EngHub sprint board export (CSV).

---

### Step 3: Query Teamwork Graph for Collaboration Insights

Using Teamwork Graph APIs, fetch collaboration and activity data for sprint participants:

**Data to pull:**
- **Team composition** (members of the project/team)
- **Work activity** (who created, updated, or contributed to work items during sprint period)
- **PR activity** (who authored, reviewed, merged PRs; review cycles; collaboration patterns)
- **Page contributions** (who created or edited EngHub Docs pages; collaborative documents)
- **Collaboration pairs** (who worked with whom; frequency of interactions)
- **Cross-tool activity summary** (combined activity across EngHub, Bitbucket, EngHub Docs)

**API calls needed:**
- `get_work_summary_for_given_user` (per team member) — assigned issues, created/reviewed PRs, contributed pages
- `get_collaboration_summary_between_users` (key pairs) — PR reviews, page collaboration, issue comments
- `get_team_users` — list team members to query
- `get_activities_linked_to_project` — PRs, branches, builds, deployments linked to sprint project
- `get_project_context` — contributors, followers, owners of the project

**Why this matters:** Collaboration insights reveal who unblocked whom, which pairs work well together, and whether the team is working in silos or cross-pollinating. This becomes a powerful narrative element: "Alice reviewed 8 PRs and unblocked Bob's payment integration" is more credible and human than "8 PRs merged."

**Fallback:** If Teamwork Graph is unavailable, rely on EngHub assignee data and optional Bitbucket PR review data from EngHub links.

---

### Step 4: Analyze and Compute Metrics

Calculate key performance indicators:

#### Velocity
- **Current sprint velocity:** Sum of story points in "Done" status
- **Average velocity (last 3 sprints):** (v1 + v2 + v3) / 3
- **Velocity trend:** Current vs. average (e.g., "+12%" or "-5%")

#### Completion
- **Completion rate:** (Stories done / Stories committed) * 100
- **Carry-over count:** Stories still in progress or backlog at sprint end
- **Carry-over points:** Story points of carry-over items

#### Quality
- **Bug ratio:** (Bugs found / Stories completed) * 100 (lower is better, context-dependent)
- **Bug resolution rate:** (Bugs fixed / Bugs found) * 100
- **Open bug trend:** Compare to previous sprint

#### Team & Throughput
- **Contributor count:** Number of unique assignees
- **Average points per contributor:** Total points / contributor count
- **Most active contributors** (top 3 by points, for team highlights)

#### Collaboration Health (TWG-powered)
- **PR review density:** Average reviews per PR (higher = more code review discipline)
- **Top reviewers:** Who reviewed the most PRs (signals code quality gatekeepers)
- **Collaboration pairs:** Number of unique pairs who worked together (higher = less siloing)
- **Cross-tool contributions:** Percentage of contributors active in multiple tools (EngHub + Bitbucket + EngHub Docs)
- **Unblocking moments:** Issues resolved through pair work or cross-team support (from TWG collaboration analysis)

#### Risk & Blockers
- **Active blockers:** Issues still in "Blocked" status at sprint end
- **Blocker resolution rate:** (Blockers resolved / Blockers found) * 100
- **Risk list:** Issues labeled with "risk" or "blocker" (count and names)

See `references/metrics-formulas.md` for detailed formulas and interpretation.

---

### Step 5: Generate Narrative Arc

Transform metrics into a story with:

#### Act 1: What We Set Out to Do
- Sprint goal and success criteria
- Velocity target vs. historical average
- Team capacity for the sprint

#### Act 2: What We Shipped
- Top 3-5 completed stories (summarized, not a list)
- Key features or improvements
- Standout moments (bugs fixed, performance gains, customer wins)
- Collaboration highlights (who worked together, cross-team partnerships, unblocking moments)

#### Act 3: What We Learned
- Blockers encountered and how we resolved them (especially pair-work or cross-team resolutions)
- Process improvements or team observations
- Collaboration patterns (are we siloing? cross-pollinating? review culture strong?)
- Lessons for next sprint

#### Act 4: What's Next
- Carry-over items and priority
- Next sprint focus
- Dependencies or risks ahead
- Team collaboration priorities (strengthen review culture, enable pair work, cross-team learning)

**Narrative tone adjusts by audience:**
- **Executive:** Emphasize business impact, risk mitigation, capacity planning
- **Team:** Emphasize learning, collaboration, technical achievement
- **Board:** Emphasize strategic alignment, competitive context, stakeholder confidence

---

### Step 6: Produce Word Report

Generate a structured Word document with sections:

1. **Executive Summary** (1 page)
   - Sprint at a glance: dates, goal, velocity, completion rate
   - Key highlight (1-2 sentences on biggest win)
   - Collaboration snapshot (1-2 sentences: e.g., "Strong cross-team pairing on the payment flow" or "5 unique contributor pairs, healthy review culture")
   - Risks (if any, summarized)

2. **Sprint Metrics Dashboard** (1 page)
   - Velocity chart (current + 3-sprint trend)
   - Completion rate (visual gauge)
   - Contributor breakdown (table or chart)
   - Bug metrics (found/fixed/open)

3. **What We Accomplished** (1-2 pages)
   - Organized by epic or feature
   - Brief description of each completed story
   - Team member callouts with collaboration context (e.g., "Alice led the refactor with support from Bob's platform expertise")

4. **Collaboration Insights** (0.5-1 page, new)
   - Top collaborators this sprint (who reviewed most PRs, who contributed to most pages)
   - Cross-tool activity (not just EngHub tickets: PRs merged, docs written, knowledge shared)
   - Collaboration health (PR review density, collaboration pairs, silo risks)
   - Unblocking moments (examples of cross-team support that moved work forward)

5. **Blockers, Risks & Learnings** (0.5-1 page)
   - Active blockers and resolution status
   - Risks for next sprint
   - Key process observations

6. **Next Sprint Goals** (0.5 page)
   - Carry-over items and priority
   - Focus areas
   - Dependencies to manage
   - Collaboration priorities

7. **Appendix** (as needed)
   - Full story list (table)
   - Burn-down chart (if available)
   - Detailed risk register
   - Collaboration pair matrix (who worked with whom)

**Output format:** `.docx` file using `python-docx` library (or template-based using Mail Merge).

See `references/sprint-report-templates.md` for the full Word template structure.

---

### Step 7: Produce PowerPoint Outline

Generate a structured PowerPoint outline (content + speaker notes, ready for design):

**Slide deck (10-14 slides, by audience):**

#### Executive Audience
1. **Title Slide** — Sprint name, dates, team
2. **Sprint at a Glance** — Goal, velocity, completion rate, top metric
3. **Business Impact** — Revenue impact, customer satisfaction, strategic alignment (if applicable)
4. **What We Shipped** — Top 3 features, each in 1 sentence + visual placeholder
5. **Metrics Dashboard** — Velocity trend, completion, team capacity, quality
6. **Team Collaboration** — Top collaborators, PR review culture, cross-team moments (new TWG-powered slide)
7. **Blockers & Risks** — Active blockers, next sprint dependencies, mitigation plans
8. **Capacity & Forecast** — Next sprint velocity target, headroom for critical work
9. **Q&A** — Key questions anticipated + answers

#### Team Audience
1. **Title Slide** — Sprint name, dates, team, retro format (sync + async)
2. **Sprint Goal Review** — What we set out to do, did we hit it?
3. **Accomplishments** — 3-5 biggest wins, organized by theme
4. **Demo Highlights** — Key features demonstrated, team member callouts
5. **Metrics & Trends** — Velocity, completion, quality, process metrics
6. **Team Collaboration** — Collaboration highlights, pair work moments, who worked with whom, review culture (TWG-powered)
7. **Blockers & Learnings** — What we overcame, what we learned, cross-team support moments
8. **Retro Themes** — Common patterns: process wins, collaboration moments, pain points
9. **Next Sprint Preview** — Carry-over priorities, new goals, team dependencies, collaboration goals
10. **Appreciation** — Team highlights, shout-outs, celebration moments

#### Board Audience
1. **Title Slide** — Product/initiative, sprint cadence, reporting period
2. **Strategic Context** — Initiative goals, competitive landscape, customer needs
3. **Sprint Focus** — What we prioritized this sprint, why
4. **Key Deliverables** — Features shipped, release readiness, go-to-market prep
5. **Velocity & Predictability** — Trend analysis, sprint-to-sprint consistency, forecast accuracy
6. **Team Health & Collaboration** — Team capacity, key contributors, collaboration patterns, cross-team dependencies (TWG-powered)
7. **Quality & Risk Management** — Bug metrics, blocker resolution, dependencies on other teams
8. **Roadmap Impact** — How this sprint advances 90-day and annual goals
9. **Financial & People Metrics** — Cost per feature, team utilization, planned hiring
10. **Next Milestones** — Key dates ahead, board-level decisions needed

**Each slide includes:**
- **Content outline** (bullet points, no prose)
- **Speaker notes** (full narrative, talking points, data references)
- **Visual placeholders** (e.g., "CHART: Velocity trend, last 4 sprints" or "PHOTO: Team in retro")
- **Design notes** (e.g., "Use EngHub blue palette, hero image upper left")

**Output format:** `.pptx` or `.md` outline file with clear section breaks. If using `python-pptx`, create slide objects; if markdown, export as HTML or PDF for designer handoff.

See `references/sprint-report-templates.md` for the full PowerPoint slide templates and speaker notes.

---

### Step 8: Optionally Publish EngHub Docs Archive Page

If an EngHub Docs space is provided, create a page with:
- Sprint metadata (name, dates, team)
- Embedded executive summary
- Linked Word report (attachment)
- Linked PowerPoint outline (attachment or embedded preview)
- Embedded metrics dashboard (table or chart)
- Archived discussion or feedback section (for async retro)

**Page structure:**
```
Sprint {Name} Review — {Dates}
├─ Executive Summary
├─ Metrics at a Glance
├─ Deliverables
├─ Blockers & Risks
├─ Team Highlights
├─ Attachments (Word report, PowerPoint outline, EngHub export)
└─ Discussion (for async feedback)
```

**Permissions:** Default to same as parent page or project space.

---

### Step 9: Summary with Deliverable Links

Output a summary document (markdown or text) listing:
- **Word report** (file path or link)
- **PowerPoint outline** (file path or link)
- **EngHub Docs page** (URL, if created)
- **Key metrics snapshot** (table: velocity, completion rate, bugs, blockers)
- **Collaboration snapshot** (key contributors, collaboration health score, top pairs)
- **Talking points** (3-5 key moments to emphasize in presentation, including collaboration highlights)
- **Next steps** (e.g., "Design slides," "Schedule retro," "Share with board," "Discuss collaboration priorities")

---

## Report Templates

See `references/sprint-report-templates.md` for:
- **Word document structure** (sections, table styles, chart placeholder specs)
- **PowerPoint slide templates** (by audience, with speaker note guidelines)
- **EngHub Docs page template** (layout, metadata, discussion prompts)
- **Metric dashboard template** (table formats, chart types, data mapping)

---

## Handling Edge Cases

See [`references/examples-and-extended-guidance.md`](references/examples-and-extended-guidance.md) for this section (relocated to keep SKILL.md within the 20,000-character limit).

## Tips for High-Quality Results

See [`references/examples-and-extended-guidance.md`](references/examples-and-extended-guidance.md) for this section (relocated to keep SKILL.md within the 20,000-character limit).

## When NOT to Use This Skill

This skill is optimized for:
- **Structured, predictable sprints** (Scrum teams with sprint cycles)
- **Mature EngHub setup** (clear issue types, story points, sprint tagging)
- **Regular reporting cadence** (weekly, bi-weekly, or monthly retros/stakeholder updates)

**Don't use this skill if:**
- Your team doesn't use EngHub (or uses EngHub but not for sprint planning)
- You want a highly customized narrative (e.g., brand voice, specific data viz style)—use this skill as a first draft, then refine in PowerPoint or Word
- You're running a pure Kanban system without sprint cycles (consider adapting the workflow to date ranges instead)
- You need real-time burndown charts (this skill generates snapshots, not live dashboards)
- You're doing a sensitive layoff or org restructuring communication (don't rely on automated narratives for that)

---

## Examples

See [`references/examples-and-extended-guidance.md`](references/examples-and-extended-guidance.md) for this section (relocated to keep SKILL.md within the 20,000-character limit).

## Quick Reference

See [`references/examples-and-extended-guidance.md`](references/examples-and-extended-guidance.md) for this section (relocated to keep SKILL.md within the 20,000-character limit).
