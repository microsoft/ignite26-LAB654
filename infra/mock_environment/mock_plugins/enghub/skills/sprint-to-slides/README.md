# Sprint to Slides — MCP Skill Directory

Production-ready skill for transforming EngHub sprint data into presentation deliverables.

## Directory Contents

```
sprint-to-slides/
├── SKILL.md                              (552 lines)
│   Complete skill documentation with workflow, examples, and guidelines
│
└── references/
    ├── sprint-report-templates.md        (484 lines)
    │   Word and PowerPoint templates, EngHub Docs page structure
    │
    └── metrics-formulas.md               (578 lines)
        Mathematical definitions and interpretation guides
```

**Total: 1,614 lines of production-quality documentation**

---

## Quick Start

### What This Skill Does

- Queries EngHub for sprint data (velocity, completion, blockers, bugs, team metrics)
- Generates a polished Word report (4–6 pages, exec-ready)
- Produces a PowerPoint outline (8–12 slides, audience-specific)
- Optionally publishes an EngHub Docs archive page
- Exports talking points and narrative arc

### Key Sections in SKILL.md

1. **Workflow** (8 steps) — From scope identification to deliverable summary
2. **Report Templates** — Word doc structure (title, metrics, accomplishments, risks, next steps)
3. **PowerPoint Slide Templates** — 3 audience variants (executive, team, board)
4. **Edge Cases** — Kanban, cross-project sprints, missing data
5. **Worked Example** — Sprint 42 (EngHub) with full Word + PowerPoint output
6. **Quick Reference** — CLI usage, integration points, key files

### Key Files in references/

**sprint-report-templates.md:**
- Word document structure (6 pages breakdown)
- PowerPoint slide decks by audience (8–9 slides each)
- EngHub Docs page template
- Styling guidelines (fonts, colors, spacing)

**metrics-formulas.md:**
- Velocity (definition, formula, trend calculation, interpretation)
- Completion rate (story count vs. point-based, carry-over analysis)
- Bug metrics (ratio, resolution rate, escape rate)
- Team metrics (contributor breakdown, engagement)
- Blocker resolution rate
- Velocity forecast (with confidence intervals)
- Interpretation playbook (what to do when metrics change)

---

## Design Philosophy

- **No emoji** — Clean, professional tone throughout
- **Minimal aesthetic** — Helvetica Neue, black/white/gray palette, thin rules
- **Exec-ready** — BLUF structure, narrative over numbers, context-aware metrics
- **Production quality** — 1,600+ lines of documented patterns, not skeleton
- **Flexible templates** — Adaptable to different audiences and team structures

---

## Audiences Supported

1. **Executive** (8 slides) — Business impact, metrics, forecasting, risk mitigation
2. **Team** (9 slides) — Accomplishments, learning, retro themes, celebration
3. **Board** (9 slides) — Strategic context, roadmap alignment, financial metrics, milestones

---

## Integration Points

- **EngHub API** — Sprint metadata, issue data, velocity history
- **EngHub Docs API** — Archive page creation and updates
- **python-docx** — Word report generation
- **python-pptx** — PowerPoint outline creation (or Markdown for designer handoff)
- **Slack** — (Optional) Summary post with deliverable links

---

## Status

- **Version:** 1.0
- **Status:** Production-ready
- **Last updated:** 2026-04-14
- **Target audience:** PMs, Scrum Masters, Team Leads, Product Leadership

---

## What's Inside

### SKILL.md Highlights

- **Problem it solves:** Automates the data-to-narrative pipeline (hours → minutes)
- **Keywords:** sprint, retro, metrics, powerpoint, word, slides, report, velocity, burndown
- **Workflow:** 8-step process from scope to deliverables
- **Tips for quality:** Narrative over numbers, highlight people, contextualize metrics
- **When NOT to use:** Custom narratives, sensitive communications, real-time dashboards
- **Full worked example:** Sprint 42 (EngHub Team) with sample output

### Template Examples

**Word Report Structure:**
- Title page with metadata
- Executive summary (1 page)
- Metrics dashboard (1 page, tables + charts)
- Accomplishments (1–2 pages, feature-organized with team callouts)
- Blockers & learnings (0.5–1 page)
- Next sprint goals (0.5 page)
- Appendix (story list, burn-down)

**PowerPoint Decks (by audience):**

Executive (8 slides):
1. Title
2. Sprint at a Glance
3. Business Impact
4. What We Shipped
5. Metrics Dashboard
6. Blockers & Risks
7. Capacity & Forecast
8. Q&A

Team (9 slides):
1. Title
2. Sprint Goal Review
3. Accomplishments
4. Demo Highlights
5. Metrics & Trends
6. Blockers & Learning
7. Retro Themes
8. Next Sprint Preview
9. Appreciation

Board (9 slides):
1. Title
2. Strategic Context
3. Sprint Focus
4. Key Deliverables
5. Metrics & Predictability
6. Quality & Risk Management
7. Roadmap Impact
8. Financial & Organizational
9. Next Milestones

### Metrics Formulas

- **Velocity** — Points completed, 3-sprint average, trend percentage
- **Completion Rate** — Story count vs. point-based, carry-over analysis
- **Carry-Over Ratio** — % of capacity used for unfinished work (threshold: 15%)
- **Bug Metrics** — Found/fixed/open, ratio per story, resolution rate
- **Team Metrics** — Points per contributor, engagement %, participation
- **Blocker Resolution** — Rate, time-to-resolve, active blockers
- **Velocity Forecast** — Conservative/realistic/pessimistic estimates with confidence
- **Health Index** — Optional: Combined score across completion, velocity, quality, blockers

---

## Design Notes

All documentation follows these principles:

1. **BLUF (Bottom Line Up Front)** — Key information first, details second
2. **Minimal visual language** — No colored boxes, gradients, or emoji
3. **Helvetica Neue typography** — Professional, clean, system-standard
4. **Executive context** — Why this metric matters, what to do with it
5. **Production patterns** — Real templates, not sketches; ready to adapt and use

---

## Next Steps

1. **Read SKILL.md** — Understand the workflow and output formats
2. **Review templates** — Familiarize yourself with Word and PowerPoint structures
3. **Study metrics** — Learn formulas and interpretation guidelines
4. **Adapt to your context** — Customize templates for your organization
5. **Run your first sprint** — Query EngHub, generate deliverables, iterate

---

**Created:** 2026-04-14
**For:** EngHub employees and partners
**License:** Internal use
