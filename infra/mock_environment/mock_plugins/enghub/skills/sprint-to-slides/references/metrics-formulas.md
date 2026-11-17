# Metrics Formulas & Interpretation Guide

Mathematical definitions and interpretation guidelines for sprint metrics used in sprint-to-slides reporting.

---

## Velocity

### Definition
Velocity is the total number of story points completed in a sprint, typically measured as stories moved to "Done" status by the sprint end date.

### Formula
```
Velocity = SUM(story_points WHERE status = "Done" AND sprint_end_date <= today)
```

### Example
If a sprint has these completed stories:
```
Story A: 5 points
Story B: 8 points
Story C: 3 points
Story D: 8 points
Story E: 5 points
Story F: 3 points
TOTAL: 34 points
```

Then **Velocity = 34 points**.

### Velocity Trend (3-Sprint Average)
```
Avg Velocity = (V(n-2) + V(n-1) + V(n)) / 3

Where:
V(n)   = current sprint velocity
V(n-1) = previous sprint velocity
V(n-2) = sprint before that
```

### Velocity Trend (Percentage Change)
```
Velocity Trend % = ((V(n) - Avg Velocity) / Avg Velocity) * 100

If V(n) = 34 and Avg = 28:
Trend = ((34 - 28) / 28) * 100 = 21.4% (trending up)

If V(n) = 24 and Avg = 28:
Trend = ((24 - 28) / 28) * 100 = -14.3% (trending down)
```

### Interpretation

**Strong velocity:**
- Velocity is consistent (low variance sprint-to-sprint)
- Trending up indicates team is getting more efficient or capacity increased
- Historical average enables forecasting: "If we maintain 30 points per sprint, Phase 1 completes in {phase_points / 30} sprints"

**Weak velocity signals:**
- High variance (e.g., 15, 28, 12, 35) indicates unpredictable scope, blockers, or capacity gaps
- Sharp drop after team increase suggests integration issues or process overhead
- Flat/declining over 4+ sprints suggests morale, process, or dependency problems

**Caveats:**
- Velocity is team-specific, not comparable across teams (different point scales)
- Velocity includes carry-over work; separate "new work velocity" if carry-over is high
- Points can inflate over time (scope creep per point), so trend alone can mislead
- External factors (vacation, hiring) create legitimate variance; context matters

---

## Completion Rate

### Definition
The percentage of committed stories that reach "Done" status by sprint end.

### Formula
```
Completion Rate % = (Stories Done / Stories Committed) * 100

Where:
Stories Done      = count of stories with status = "Done"
Stories Committed = count of all stories added to sprint backlog at sprint start
```

### Example
If a sprint commits to 14 stories and 12 reach "Done":
```
Completion Rate = (12 / 14) * 100 = 85.7%
```

### Point-Based Completion Rate
```
Point Completion Rate % = (Points Done / Points Committed) * 100

If a sprint commits to 36 points and delivers 34:
Completion = (34 / 36) * 100 = 94.4%
```

### Distinction: Story Count vs. Point-Based
- Use **story count** if your team works primarily on similar-sized tasks
- Use **point-based** if stories vary widely in size (recommended for Scrum teams)
- Report both if you want to show variance in point estimation

### Carry-Over Analysis
```
Carry-Over Stories = Stories Committed - Stories Done
Carry-Over Points  = Points Committed - Points Done
Carry-Over Rate %  = (Carry-Over Points / Points Committed) * 100

If committed 36 points, delivered 34, carry-over = 2:
Carry-Over Rate = (2 / 36) * 100 = 5.6%
```

### Interpretation

**Healthy completion rates:**
- 85–95% is typical for mature Scrum teams
- 90%+ indicates strong planning and execution
- Consistent 85%+ sprint-to-sprint is predictable

**Red flags:**
- Dropping below 75% suggests over-commitment, scope creep, or capacity issues
- Spiking to 100% two sprints in a row might indicate under-commitment (sandbagging)
- High variance (e.g., 92%, 68%, 88%) indicates estimation or scope control problems

**Context matters:**
- First sprint of new team: expect 60–75%
- Sprint with mid-sprint blocker: expect 70–80%
- Sprint with unplanned work (support, escalation): adjust target downward
- Sprint following a high-pressure release: expect lower completion as team stabilizes

---

## Carry-Over & Cumulative Flow

### Definition
Stories or points that remain incomplete at sprint end and roll into the next sprint.

### Formula
```
Carry-Over Points = Points Committed - Points Done

Carry-Over Impact (next sprint) = 
  Carry-Over Points + New Points Committed = Next Sprint Capacity

Carry-Over Ratio = Carry-Over Points / Total Capacity of Next Sprint
```

### Example
```
Sprint 42:
- Committed: 36 points
- Done: 34 points
- Carry-over: 2 points

Sprint 43:
- Carry-over from Sprint 42: 2 points
- New capacity: 35 points
- Total Sprint 43 capacity: 2 + 35 = 37 points
- Recommended new work: 33 points (leaving 2-point buffer)

Carry-over ratio = 2 / 37 = 5.4% (healthy, below 15% threshold)
```

### Healthy Carry-Over Thresholds
- **0–10%:** Excellent. Shows strong planning and execution.
- **10–15%:** Good. Normal variance, acceptable.
- **15–25%:** Attention needed. Either scope creep or estimation drift.
- **25%+:** Problem. Indicates systemic over-commitment or blockers.

### Carry-Over Reasons (categorize for root cause analysis)
```
Reason 1: Scope Expansion (planned change mid-sprint)
Reason 2: External Blocker (dependency on another team)
Reason 3: Internal Blocker (tech discovery, integration issues)
Reason 4: Estimation Error (story was harder than expected)
Reason 5: Capacity Loss (unplanned absence, support escalation)
Reason 6: Priority Shift (product requirement changed)
```

### Tracking Carry-Over Trend
```
Sprint 40: 3 points (8% carry-over)
Sprint 41: 5 points (14%)
Sprint 42: 2 points (5%)
Sprint 43: 8 points (22%) <-- Problem detected, investigate

Average carry-over (last 4 sprints) = (3+5+2+8)/4 = 4.5 points
If this exceeds 15% of average velocity, escalate to team/product lead.
```

---

## Bug Metrics

### Bugs Found vs. Fixed

#### Formula
```
Bugs Found (sprint) = COUNT(issues WHERE type = "Bug" AND created_date in sprint)
Bugs Fixed (sprint) = COUNT(issues WHERE type = "Bug" AND resolved_date in sprint)
Bugs Open (end of sprint) = COUNT(issues WHERE type = "Bug" AND status != "Done")

Bug Resolution Rate % = (Bugs Fixed / Bugs Found) * 100
```

#### Example
```
Sprint 42:
- Bugs found: 4
- Bugs fixed: 3
- Bugs open (cumulative, all time): 2

Resolution rate = (3 / 4) * 100 = 75%

Interpretation: We're fixing bugs faster than we're finding them, which is good. 
But we have 2 bugs in the backlog, which we should prioritize next sprint.
```

### Bug Ratio (Quality Indicator)

#### Formula
```
Bug Ratio = Bugs Found / Stories Completed

If 4 bugs found and 12 stories completed:
Bug Ratio = 4 / 12 = 0.33 bugs per story
```

#### Interpretation
- **< 0.25:** Excellent quality. Few defects escaping to QA.
- **0.25–0.5:** Good quality. Normal for feature development.
- **0.5–1.0:** Acceptable for new features, concerning for maintenance/refactoring.
- **> 1.0:** Quality issue. More bugs than stories—investigate design or testing.

**Context:**
- New features typically have higher bug ratios (0.5–0.75)
- Refactoring/maintenance should be lower (0.1–0.3)
- If ratio spiked from 0.3 to 0.8 sprint-to-sprint, check: Did testing change? Did we add junior devs? Did scope expand?

### Bug Age (Time to Resolution)

#### Formula
```
Average Bug Age = AVG(resolved_date - created_date for all resolved bugs)
Bugs Older Than 1 Sprint = COUNT(bugs created > {current_sprint_start})

If bugs are aging (open for 3+ sprints), prioritization is broken.
```

### Bug Escape Rate (Post-Release Quality)

#### Formula
```
Escape Rate % = (Bugs Found in Production / Bugs Found in QA) * 100

If QA found 20 bugs and customers found 2:
Escape rate = (2 / 20) * 100 = 10%

Target: < 5% (excellent) | 5–10% (acceptable) | > 10% (investigate)
```

---

## Team Metrics

### Contributor Breakdown

#### Formula
```
Points per Contributor = SUM(story_points WHERE assignee = person) 
                         for all people in sprint

Total Contributors = COUNT(DISTINCT assignee) in sprint

Average Points per Contributor = Total Points / Total Contributors
```

#### Example
```
Sprint 42 (34 points total):
- Alice: 12 points (35%)
- Bob: 8 points (24%)
- Carol: 6 points (18%)
- Dave: 6 points (18%)
- Eve: 2 points (6%)

Total: 5 contributors
Average per contributor: 34 / 5 = 6.8 points

Insight: Alice and Bob carried the load on the big architecture work. 
Carol and Dave contributed meaningfully. Eve had a light load 
(either by design or signal that she should take more next sprint).
```

### Team Engagement (Participation)

#### Formula
```
Engagement % = (Contributors Who Completed Work / Team Size) * 100

If 5 out of 5 team members completed at least 1 story:
Engagement = (5 / 5) * 100 = 100%

If 4 out of 5 team members completed work:
Engagement = (4 / 5) * 100 = 80% <-- One person needs check-in
```

#### Interpretation
- **100%:** Full participation. Everyone contributed.
- **80–99%:** Good. Most people contributed (acceptable for one-off support).
- **60–79%:** Concern. Someone is blocked or disengaged.
- **< 60%:** Problem. Investigate before next sprint.

---

## Blockers & Risks

### Blocker Resolution Rate

#### Formula
```
Blockers Found (sprint) = COUNT(issues labeled "blocker" OR status = "Blocked")
Blockers Resolved (sprint) = COUNT(issues labeled "blocker" AND status = "Done" OR "Resolved")

Blocker Resolution Rate % = (Blockers Resolved / Blockers Found) * 100

Average Time to Resolve = AVG(resolved_date - created_date) for blockers
```

#### Example
```
Sprint 42:
- Blockers found: 1 (API rate limit)
- Blockers resolved: 1 (resolved via platform team partnership)
- Time to resolve: 2 days

Resolution rate: (1 / 1) * 100 = 100%
Interpretation: Excellent. We found the blocker, escalated quickly, and solved it.
```

#### Thresholds
- **90–100%:** Excellent. Blockers are unblocking.
- **70–89%:** Acceptable. Most blockers resolved, some carrying over.
- **< 70%:** Problem. Blockers are accumulating; investigate escalation process.

### Active Blockers (End-of-Sprint Status)

#### Formula
```
Active Blockers = COUNT(issues WHERE status = "Blocked" at sprint end)

If 0 active blockers: Team is unblocked.
If 1–2 active blockers: Manageable, but should be resolved early next sprint.
If 3+ active blockers: Dependency problem; needs escalation.
```

---

## Velocity Forecast

### Simple Forecast (Constant Velocity)

#### Formula
```
Sprints Needed = Total Remaining Points / Average Velocity

Example:
- Phase 1 requires 180 points
- Average velocity: 32 points per sprint
- Sprints needed: 180 / 32 = 5.6 sprints ≈ 6 sprints
- Timeline: 6 sprints * 2 weeks = 12 weeks ≈ end of June
```

### Forecast with Confidence Interval (Range)

#### Formula
```
Conservative Estimate = Total Points / Max Velocity (best-case scenario)
Realistic Estimate = Total Points / Average Velocity
Pessimistic Estimate = Total Points / Min Velocity (worst-case scenario)

Example (Phase 1: 180 points):
- Recent sprints: 28, 31, 34, 29, 32 (avg = 30.8)
- Max velocity: 34
- Min velocity: 28

Conservative: 180 / 34 = 5.3 sprints (best case)
Realistic: 180 / 30.8 = 5.8 sprints (expected)
Pessimistic: 180 / 28 = 6.4 sprints (worst case)

Forecast: 5–6.5 sprints (10–13 weeks) with 80% confidence
```

### Adjusting for Known Factors

```
Base forecast (from velocity): 6 sprints

Adjustment Factors:
+ Planned vacation (2 people, 1 week): +0.5 sprints
+ New team member onboarding (learning curve): +0.5 sprints
- Process improvement (automated testing): -0.3 sprints
- Contractor support (Phase 1 only): -0.2 sprints

Adjusted forecast: 6 + 0.5 + 0.5 - 0.3 - 0.2 = 6.5 sprints (13 weeks)
```

---

## Quality & Code Health Metrics (Optional)

### Test Coverage

#### Formula
```
Test Coverage % = (Lines of Code Covered by Tests / Total Lines of Code) * 100

Healthy ranges:
- New features: 60–80% (some integration not yet tested)
- Maintenance: 80%+ (high confidence in existing behavior)
- Critical path: 90%+ (security, payment, core features)
```

### Code Review Cycle Time

#### Formula
```
Average Review Time = AVG(time from PR opened to PR merged)

If average review time:
- < 4 hours: Fast, good process
- 4–24 hours: Normal, acceptable
- 24+ hours: Slow, investigate bottlenecks
```

### Technical Debt Ratio (Optional)

#### Formula
```
Technical Debt Ratio = (Time to Ship with Debt / Time to Ship Clean) 

Example:
- With debt (quick hack): 2 days to implement
- Without debt (proper design): 5 days to implement
- Debt ratio: 2 / 5 = 0.4 (40% faster with debt)

Decision: If we'll pay back the debt next sprint, OK. 
If we'll pay back in 3+ sprints, reconsider (debt compounds).
```

---

## Combining Metrics into a Health Score (Optional)

### Simple Health Index
```
Health Score = (Completion Rate * 0.4) + (Velocity Trend * 0.3) + (Bug Ratio Score * 0.2) + (Blocker Resolution * 0.1)

Where:
- Completion Rate: 0–1.0 (100% = 1.0)
- Velocity Trend: 0–1.0 (stable/trending up = 1.0, declining = 0.5)
- Bug Ratio Score: 0–1.0 (< 0.5 bugs per story = 1.0, > 1.0 = 0.5)
- Blocker Resolution: 0–1.0 (100% resolution = 1.0)

Example:
Health = (0.86 * 0.4) + (1.0 * 0.3) + (0.8 * 0.2) + (1.0 * 0.1)
       = 0.344 + 0.3 + 0.16 + 0.1
       = 0.904 (90.4%, "Excellent")

Thresholds:
- > 0.85: Excellent (ship-ready)
- 0.75–0.85: Good (on track)
- 0.60–0.75: Caution (investigate blockers or quality issues)
- < 0.60: Problem (escalate)
```

---

## Data Sources & Query Examples

### EngHub API Queries

**Get sprint issues:**
```
GET /rest/api/3/sprints/{sprintId}/issues

Returns: issue.key, issue.points (customfield_10016), issue.status, issue.created, issue.resolution_date
```

**Get bugs by date range:**
```
GET /rest/api/3/issues?jql=
  type=Bug 
  AND created>={start_date} 
  AND created<{end_date}
  AND project={project_key}
```

**Get velocity history:**
```
GET /rest/api/3/sprints?boardId={boardId}&state=closed

Returns: sprint.name, sprint.startDate, sprint.endDate, plus issue data per sprint
```

### EngHub Docs & Manual Tracking

If EngHub data is incomplete, calculate from sprint notes:
- Copy completed story list from EngHub board export
- Count stories and sum points manually
- Document carry-over reasons in sprint retro notes
- Archive metrics in EngHub Docs for trend tracking

---

## Interpretation Playbook: What to Do When Metrics Change

### Velocity Dropped 20%+ Sprint-over-Sprint

**Investigate:**
1. Did team capacity change? (vacation, new hire, departure)
2. Did story complexity increase? (check point inflation)
3. Are blockers accumulating? (check active blocker count)
4. Is the team healthy? (one-on-ones, retro feedback)

**Action:**
- If capacity change: adjust forecast downward temporarily
- If complexity increased: validate estimation; ensure stories are sized correctly
- If blockers: escalate dependencies; unblock the team
- If morale issue: address in retro; consider reducing committed scope

### Completion Rate Dropped Below 80%

**Investigate:**
1. Over-commitment? (compare committed points to average velocity)
2. Scope creep? (track mid-sprint additions)
3. Estimation error? (audit high-variance stories)
4. New process overhead? (new tools, ceremonies, compliance)

**Action:**
- Next sprint: commit 10–15% less
- Product: review priorities; reduce scope if needed
- Team: discuss what would help (process, tooling, clarity)

### Bug Ratio Spiked Above 0.75

**Investigate:**
1. New feature complexity? (normal for exploratory work)
2. Testing change? (new QA person, reduced test time)
3. Design issue? (architecture decision causing downstream bugs)
4. Process change? (less code review, fewer tests)

**Action:**
- Audit the bugs: are they design flaws or implementation typos?
- If design: discuss in retro; adjust architecture
- If testing: increase test time next sprint; pair with QA
- If process: restore process; it was working before

### Blockers Not Resolving (>50% unresolved after 5 days)

**Investigate:**
1. External dependency? (waiting on another team)
2. Process gap? (unclear escalation path)
3. Missing context? (team doesn't understand the blocker)
4. Priority misalignment? (blocking team != priority for dependency)

**Action:**
- Escalate to engineering leadership if cross-team
- Create a clear escalation playbook (who to contact, when)
- Unblock the team (workaround, parallel path, reduce scope)
- Post-sprint: document what we learned to prevent next time

---

**Last updated:** 2026-04-14  
**Version:** 1.0 (Production-Ready)
