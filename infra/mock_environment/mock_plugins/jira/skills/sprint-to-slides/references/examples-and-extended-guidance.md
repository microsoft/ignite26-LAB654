# Sprint to Slides — Examples & Extended Guidance

This content was relocated from `SKILL.md` to keep that file within the 20,000-character agent-skill limit. Load it when you need this detail.

## Handling Edge Cases

### No Sprint Board (Kanban)
If the project uses Kanban instead of Scrum:
- Use date range instead of sprint
- Calculate metrics per sprint-length period (e.g., bi-weekly)
- Adapt "velocity" to "throughput" (count of stories, not points)
- Note absence of sprint goal in narrative

### Mixed Kanban/Scrum
- Query both sprint backlog and continuous flow items
- Segment metrics: "Sprint committed" vs. "Flow items"
- Narrative acknowledges both modes

### Cross-Project Sprints
- Query multiple projects, combine metrics
- Summarize by project in appendix
- Call out inter-team dependencies in blockers/risks

### Missing Historical Data
If past sprints unavailable:
- Use current sprint as baseline (no trend comparison)
- Narrative focuses on achievement, not predictability
- Add note: "Trend analysis unavailable; comparing to estimated velocity target"

### Zero Completed Stories
- Honest narrative: "This sprint focused on planning / technical debt / discovery"
- Shift emphasis to learning or process improvements
- Highlight blockers resolved or discovered

### No Bug Tracking
- Omit bug metrics
- Substitute with other quality signals: test coverage, code review cycles, performance metrics

---


## Tips for High-Quality Results

### 1. Narrative Over Numbers
Numbers alone feel like an HR report. Build a story:
- "We shipped three features and resolved a critical database bottleneck" (1 sentence, concrete)
- vs. "Completed 8 stories, 34 points, bug count 3" (dry, context-free)

### 2. Highlight People, Not Just Tickets
Include team member callouts:
- "Alice led the refactor that improved load times by 40%"
- "Bob unblocked the payment integration by pairing with the finance team"
- Especially important for executive and team audiences (board is less interested)

### 3. Contextualize Metrics
Metric + interpretation:
- "Velocity was 34 points, up 12% from last sprint" (ok)
- "Velocity was 34 points, up 12% from last sprint—the two-person boost to the backend team paid off" (better, explains the why)

### 4. Honest About Risks
Don't hide blockers or misses:
- Call out carry-over items explicitly
- Explain root causes (scope creep, discovery, external dependency)
- Propose mitigation for next sprint
- Builds trust with execs and team

### 5. Use Visuals Strategically
Not every metric needs a chart:
- **Velocity trend chart:** Always include (shows predictability)
- **Completion rate gauge:** Include if available (shows capacity planning accuracy)
- **Contributor breakdown table:** Include for team audience (shows participation)
- **Bug metrics table:** Include if quality variance is notable
- **Blockers list:** Text or bullet, not a chart

### 6. Audience-Specific Emphasis
- **Executive:** "We were 100% on velocity target, delivered two customer-facing features, and mitigated a platform risk"
- **Team:** "We shipped the feature faster than expected, learned a lot about our build system, and built momentum"
- **Board:** "This sprint completes Phase 1 of our Q2 roadmap, positioning us for the July release"

### 7. Next Sprint Preview
Don't end on metrics. End on optimism:
- "Next sprint, we're tackling the mobile experience and continuing the architecture cleanup"
- Gives audience a forward motion and clear priority

---


## Examples

### Full Worked Example: Sprint 42 (Rovo Team)

**Input:**
- Sprint name: "Sprint 42 — Relational Memory"
- Project: ROVO
- Dates: 2026-04-01 to 2026-04-12
- Audience: Executive (director-level stakeholder update)

**Jira Query Results:**
- 12 stories completed (34 story points)
- 2 stories carried over (5 points, blocked on backend API)
- Velocity last 3 sprints: 28, 31, 34 (trending up)
- Bugs found: 4, bugs fixed: 3, bugs open: 1
- Blockers: 1 (backend API rate limit), resolved at end of sprint
- Contributors: 5 people, lead contributor (Alice) with 12 points

**Teamwork Graph Results:**
- PR activity: 18 PRs authored, 47 PR reviews total
- Top reviewer: Bob (14 reviews), Carol (12 reviews)
- Collaboration pairs: 8 unique pairs (healthy cross-pollination)
- Cross-tool activity: All 5 team members active in Jira + Bitbucket; 4 of 5 also contributed to Confluence (docs, architecture decisions)
- Unblocking moments: Alice + Bob pair-worked on API rate limit issue; Carol unblocked payment validation by writing integration tests
- Code review density: 2.6 reviews per PR (strong review culture)

**Computed Metrics:**
- Velocity: 34 points (up 21% from 3-sprint average of 28)
- Completion rate: 86% (12 of 14 committed stories)
- Carry-over points: 5 (14%)
- Bug ratio: 0.33 (4 bugs per 12 stories, low)
- Blocker resolution: 1 blocker, resolved within sprint
- Collaboration health: 8 unique pairs across 5 people = high cross-functional work; PR review density 2.6 = strong code quality discipline
- Cross-tool engagement: 80% of team (4/5) contributing to docs and knowledge sharing

**Narrative Arc:**
1. **Act 1:** "Committed to 14 points and delivery of the relational memory prototype"
2. **Act 2:** "Completed 12 stories, including the memory layer API, UI persistence, and session recovery—core features for the prototype demo. Team showed strong cross-functional collaboration: 8 unique pairs worked together, with Bob and Carol leading code reviews (14 and 12 PRs each)"
3. **Act 3:** "Hit a blocker with the backend API rate limit mid-sprint. Alice and Bob pair-worked on the solution with the platform team, resolving it within 2 days. Learned we need to pre-allocate quota for high-throughput features. Carol also unblocked the payment validation work by writing integration tests that the frontend team used immediately"
4. **Act 4:** "2 stories (payment validation refactor) carried over; prioritizing that next sprint before merging with the main release branch. Momentum strong: cross-tool engagement at 80%, team active in Jira, Bitbucket, and Confluence"

**Word Report Output:**
- **Title page:** "Sprint 42 Review — Relational Memory (2026-04-01 to 2026-04-12)"
- **Executive Summary:** 34 points shipped, 86% completion, platform partnership breakthrough, 1 carry-over item. Collaboration snapshot: "Strong cross-functional teamwork with 8 unique collaboration pairs and 2.6 reviews per PR—team is quality-focused and well-connected"
- **Metrics:** Velocity chart (trending up), completion gauge, contributor breakdown, bug metrics
- **Accomplishments:** "Shipped relational memory API (Alice led, with Bob's platform support), UI session persistence (Bob led), recovery flow (Carol led), test suite (Dave led). Carol's integration tests unblocked frontend work immediately"
- **Collaboration Insights:** 
  - Top collaborators: Bob (14 PR reviews, platform enabler), Carol (12 PR reviews, integration specialist)
  - Cross-tool activity: All 5 team members in Jira + Bitbucket; 4 of 5 contributed to Confluence (architecture decisions, API documentation)
  - Collaboration health: 8 pairs = high cross-functional work; 2.6 reviews/PR = strong review discipline
  - Unblocking moments: Alice+Bob pair-worked API rate limit fix (2 days); Carol unblocked payment validation via integration tests
- **Blockers & Learnings:** "Resolved API rate limit blocker through pair work; learned to pre-allocate quota. Team demonstrated strong collaboration—pair work and mentoring accelerated resolution. Need clearer API contract documentation for future features"
- **Next Sprint:** Carry-over payment refactor, begin integration testing, planning session with product team. Continue fostering pair work and cross-team code reviews
- **Appendix:** Full story list, Jira sprint board export, collaboration pair matrix

**PowerPoint Outline Output (Executive audience, 9 slides):**

```
SLIDE 1: Title Slide
- Sprint 42: Relational Memory
- Dates: April 1–12, 2026
- Team: Rovo platform (5 engineers)

SLIDE 2: Sprint at a Glance
- Goal: Deliver relational memory prototype
- Velocity: 34 points (up 21% from 3-sprint average)
- Completion: 86% (12 of 14 stories)
- Quality: 4 bugs found, 3 fixed, 1 open
- Risk: Resolved 1 API rate limit blocker

SLIDE 3: Business Impact
- Prototype unlocks Phase 3 roadmap (AI session continuity)
- API partnership validated; new quota model established
- Ready for customer research, end of month
- De-risked: Platform team committed to support for Q2 release

SLIDE 4: What We Shipped
- Relational memory API (core data model, encryption, versioning)
- UI session persistence (browser storage, conflict resolution)
- Session recovery flow (user-facing undo, restore workflow)

SLIDE 5: Metrics Dashboard
- [CHART: Velocity trend, 4 sprints, trending up]
- [CHART: Completion rate gauge, 86%]
- [TABLE: Contributor breakdown—Alice (12pt), Bob (8pt), Carol (6pt), Dave (6pt), Eve (2pt)]
- [TABLE: Bug metrics—Found 4, Fixed 3, Open 1]

SLIDE 6: Team Collaboration (TWG-powered)
- Collaboration pairs: 8 unique pairs across 5 people (high cross-functional work)
- Code review culture: 2.6 reviews per PR (strong quality discipline)
- Top reviewers: Bob (14 PR reviews—platform enabler), Carol (12 PR reviews—integration specialist)
- Cross-tool engagement: 100% in Jira + Bitbucket; 80% also in Confluence (architecture, docs)
- Unblocking moments: Alice+Bob pair-worked API rate limit fix (2 days turnaround); Carol's integration tests unblocked frontend team
- Key insight: Strong peer collaboration accelerated blocker resolution

SLIDE 7: Blockers & Risks
- Blocker (resolved): Backend API rate limit
  - Mitigation: Platform team allocated dedicated quota; resolved via pair work
  - Learning: Pre-allocate quota for new high-throughput features
- Open: Payment validation refactor (2 stories, carrying over)
  - Plan: Prioritize next sprint, release blockers in API contract review

SLIDE 8: Capacity & Forecast
- Next sprint: Target 32–35 points (carry-over refactor + new work)
- Forecast: On track for Phase 1 completion by May 15
- Headroom: One spike week available for critical bugs or customer escalations
- Team momentum: Strong collaboration patterns suggest sustainable velocity

SLIDE 9: Q&A
- Q: Are we confident in the API contract for Phase 3?
  A: Yes. Platform team has committed to support; we've stress-tested the rate limit scenario.
- Q: What's the risk of the carry-over affecting the roadmap?
  A: Low. Refactor is independent of Phase 1 merge; we'll complete it early next sprint.
- Q: Are you getting feedback from customers yet?
  A: Early research starting next week; prototype is solid for that phase.
- Q: How's the team health and collaboration?
  A: Excellent. Strong peer review culture, active cross-tool work, and pair-work on blockers show team is resilient and well-connected.
```

**Confluence Page Output:**
- Title: "Sprint 42 Review — Relational Memory"
- Metadata: Dates, team, goal, velocity
- Embedded metrics table
- Narrative summary (executive tone)
- Attachments: Word report, PowerPoint outline
- Discussion section for async feedback

**Summary Output:**
```
Deliverables:
- Word report: sprint-42-report.docx (includes Collaboration Insights section)
- PowerPoint outline: sprint-42-slides-outline.pptx (includes Team Collaboration slide)
- Confluence page: https://hello.atlassian.net/wiki/spaces/.../Sprint+42+Review

Key Metrics:
- Velocity: 34 points (up 21% from 3-sprint average)
- Completion rate: 86%
- Carry-over: 2 stories (5 points, 14%)
- Bug ratio: 0.33 per story
- Active blockers at end: 0 (1 resolved mid-sprint)

Collaboration Snapshot:
- Collaboration pairs: 8 unique pairs (high cross-functional work)
- Code review density: 2.6 reviews per PR (strong quality discipline)
- Top collaborators: Bob (14 PR reviews), Carol (12 PR reviews)
- Cross-tool engagement: 80% of team in Confluence (architecture, docs)
- Unblocking moments: 2 key moments (Alice+Bob pair-work, Carol's integration tests)

Talking Points:
1. "We shipped the core relational memory API ahead of schedule"
2. "Partnership with platform team unlocked the rate limit blocker; pair work accelerated resolution"
3. "Quality is strong—only 1 open bug across 12 stories, supported by 2.6 reviews per PR"
4. "Team collaboration excellent—8 unique collaboration pairs, 80% cross-tool engagement"
5. "Unblocking moments: Alice and Bob's pair-work on API rate limit; Carol's integration tests unblocked frontend"
6. "Payment refactor carries over; independent of Phase 1 release"
7. "Ready for customer research, end of month"

Next Steps:
- Design PowerPoint slides (use outline as script; highlight Team Collaboration slide)
- Schedule executive stakeholder sync (30 min; discuss team health + collaboration patterns)
- Send Confluence page to board (emphasize collaboration insights)
- Plan next sprint retro with team (discuss pair-work effectiveness, code review culture)
```

---


## Quick Reference

### Command-Line Usage (if applicable)
```bash
# Generate Word + PowerPoint outline for a sprint
python3 sprint_to_slides.py \
  --sprint "Sprint 42" \
  --project "ROVO" \
  --audience "executive" \
  --output-dir "./deliverables"

# Generate for custom date range (Kanban)
python3 sprint_to_slides.py \
  --project "ROVO" \
  --start-date "2026-04-01" \
  --end-date "2026-04-12" \
  --audience "team" \
  --confluence-space "ROVO" \
  --publish

# Generate for team retro, including Confluence archive
python3 sprint_to_slides.py \
  --sprint "Sprint 42" \
  --project "ROVO" \
  --audience "team" \
  --confluence-space "ROVO" \
  --publish \
  --include-talking-points
```

### Integration Points
- **Jira API:** Query sprints, issues, velocity history
- **Teamwork Graph API:** Collaboration insights, work summaries, PR reviews, cross-tool activity
- **Confluence API:** Create or update archive page
- **python-docx:** Generate Word reports
- **python-pptx:** Generate PowerPoint outlines (or produce Markdown for designer handoff)
- **Teams:** (Optional) Post summary to Teams channel with deliverable links

### Key Files in This Skill
- **sprint_to_slides.py** — Main orchestration script
- **references/sprint-report-templates.md** — Word and PowerPoint templates (now includes Collaboration Insights sections)
- **references/metrics-formulas.md** — Velocity, completion rate, quality, collaboration health calculations
- **examples/sprint-42-report.docx** — Worked example Word report (with Collaboration Insights section)
- **examples/sprint-42-outline.pptx** — Worked example PowerPoint outline (with Team Collaboration slides)

### Teamwork Graph Tools Reference
Key TWG tools used in this skill:
- **`get_work_summary_for_given_user`** — Retrieve work summary for each team member (assigned issues, authored/reviewed PRs, contributed pages)
- **`get_collaboration_summary_between_users`** — Analyze collaboration between specific user pairs (PR reviews, page collaboration, issue comments)
- **`get_team_users`** — List team members for querying individual work summaries
- **`get_activities_linked_to_project`** — Fetch project-linked activities (PRs, branches, builds, deployments)
- **`get_project_context`** — Get project contributors, followers, owners, and team composition

---

**Last updated:** 2026-04-14 (TWG integration)
**Status:** Production-ready  
**Audience:** PMs, Scrum Masters, Team Leads, Product Leadership
**Note:** Now includes Teamwork Graph collaboration insights—team dynamics, cross-tool activity, PR review culture, and unblocking moments are integrated throughout the workflow and outputs.
