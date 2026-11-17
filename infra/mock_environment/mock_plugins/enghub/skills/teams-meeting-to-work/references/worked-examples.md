# Teams Meeting to Work — Worked Examples

This content was relocated from `SKILL.md` to keep that file within the 20,000-character agent-skill limit. Load it when you need this detail.

## Examples

### Worked Example 1: Product Planning Meeting

**Input Transcript** (auto-generated, 10 min):

```
Sarah Chen
00:15
Today we're planning Q2. We need to decide between two approaches for mobile redesign.
Approach A: incremental updates. Approach B: full redesign.

Marcus Rodriguez
01:20
I prefer B because the current design is really outdated. We'd also get better performance.

Priya Sharma
02:10
I agree, but we need the design system team to finalize the component specs first.
Otherwise we'll just be redoing work.

Sarah Chen
02:45
Fair point. Priya, can you coordinate with the design system team and get us a timeline?
We need that by next Friday.

Priya Sharma
03:15
Yeah, I'll reach out to them today.

Marcus Rodriguez
04:00
I'll start sketching the information architecture while we wait. We can review it when
the design specs are ready.

Sarah Chen
04:45
Perfect. One more thing: we should set up a review cadence. Let's do weekly syncs
during Q2 to track progress.

Everyone
05:10
Sounds good.
```

**Step 2 Extraction**:

- [DECISION] Approved: Mobile redesign approach B (full redesign) over approach A (incremental)
  - Speaker: Sarah (facilitator), Marcus (advocate), Priya (conditional approval)
  - Note: Consensus with condition—depends on design system specs

- [ACTION] Priya to coordinate with design system team and get timeline
  - Speaker: Sarah (assigner), Priya (owner)
  - Deadline: Next Friday (inferred as 2026-04-18)
  - Blocker: Design system team must finalize component specs

- [ACTION] Marcus to sketch information architecture
  - Speaker: Marcus (owner)
  - Deadline: None explicit; can start immediately but blocked by design specs being finalized
  - Related to: Mobile redesign project

- [ACTION] Set up weekly sync meetings for Q2 to track progress
  - Speaker: Sarah (owner/facilitator)
  - Deadline: Before Q2 starts (inferred as next Monday, 2026-04-16)
  - Recurring: Weekly throughout Q2

- [BLOCKER] Design system team must finalize component specs
  - Owner: Design system team (external)
  - Blocker for: Mobile redesign timeline
  - Unblock signal: When Priya receives timeline

**Step 3**: Target EngHub project = "PLAT" (Platform team)

**Step 4**: Speaker account IDs:
- Sarah Chen → sarah.chen@enghub.com
- Marcus Rodriguez → marcus.rodriguez@enghub.com
- Priya Sharma → priya.sharma@enghub.com

**Step 5**: EngHub search results:
- Found: PLAT-1024 "Mobile experience Q2 roadmap" (existing epic)
- Found: PLAT-892 "Design system component library" (related blocker ticket)

**Step 6**: Review and confirm (example edits):
- Clarify: Is "weekly sync" a single action (create meeting series) or ongoing? → Create one ticket: "Establish Q2 mobile redesign weekly sync meetings"
- Deadline for Marcus's IA sketch? → "By April 21 (allow time for design specs to arrive)" → 2026-04-21
- Link Marcus's action to PLAT-1024 (epic)
- Link Priya's action to PLAT-892 (design system blocker)

**Step 7**: Tickets created:

```
PLAT-2847: Coordinate design system component specs for mobile redesign
Assignee: Priya Sharma
Due: 2026-04-18
Description: Reach out to design system team and get timeline for finalizing 
mobile redesign component specs. Blocking: PLAT-2848 (IA sketches) and PLAT-2849 (full redesign work).
Labels: teams-generated, meeting-followup, q2-planning, 2026-04-14
Linked: PLAT-892 (Design system component library - related)
```

```
PLAT-2848: Sketch information architecture for mobile redesign (Approach B)
Assignee: Marcus Rodriguez
Due: 2026-04-21
Description: Create initial IA sketches for full mobile redesign (Approach B).
Blocked by: PLAT-2847 (design specs). Review with team once specs available.
Labels: teams-generated, meeting-followup, q2-planning, 2026-04-14
Linked: PLAT-1024 (Mobile experience Q2 roadmap - epic)
```

```
PLAT-2849: Establish Q2 mobile redesign weekly sync meetings
Assignee: Sarah Chen
Due: 2026-04-16
Description: Set up recurring weekly meetings for Q2 (April - June) to track mobile redesign progress.
Labels: teams-generated, meeting-followup, q2-planning, 2026-04-14
```

**Step 7**: EngHub Docs recap page created:

```
Meeting Recap: Q2 Product Planning - April 14, 2026

Attendees: Sarah Chen, Marcus Rodriguez, Priya Sharma

Decisions
- Mobile redesign approach: APPROVED for Approach B (full redesign)
  Rationale: Current design outdated, better performance potential
  Condition: Depends on design system team finalizing component specs

Action Items
1. Priya Sharma - Get design system component specs timeline (Due: April 18)
   → EngHub: PLAT-2847
2. Marcus Rodriguez - Sketch IA for mobile redesign (Due: April 21)
   → EngHub: PLAT-2848
3. Sarah Chen - Establish weekly sync meetings for Q2 (Due: April 16)
   → EngHub: PLAT-2849

Blockers
- Design system team must finalize mobile redesign components
  Owner: Design system team (external)
  Blocking: PLAT-2847, PLAT-2848
  Related: PLAT-892

Related EngHub Issues
- PLAT-1024: Mobile experience Q2 roadmap (epic)
- PLAT-892: Design system component library

Next Steps
- Weekly syncs begin after April 16
- PLAT-2847 due April 18 (blocks IA work)
- Review IA sketches week of April 21
```

### Worked Example 2: Incident Response Meeting (30 min)

**Scenario**: Database query performance incident. Meeting between product, engineering, and infra.

**Extracted Items**:
- [DECISION] Root cause: Query optimization needed, not scaling issue
- [BLOCKER] Need perf baseline from analytics team (waiting on ETL pipeline output)
- [ACTION] Engineering to create query optimization plan (due tomorrow, 9am standup)
- [ACTION] Infra to review current query patterns and flag top 10 slowest (due in 2 hours)
- [ACTION] Product to assess customer impact and create comms plan if needed (due by EOD)
- [FOLLOW-UP] Meeting tomorrow at 9am to review progress

**Tickets Created**:
- INC-4521: Query optimization plan (Engineering)
- INC-4522: Top 10 slowest queries analysis (Infra)
- INC-4523: Customer impact assessment & comms plan (Product)
- EngHub Docs recap with incident timeline, decisions, and escalation path

---
