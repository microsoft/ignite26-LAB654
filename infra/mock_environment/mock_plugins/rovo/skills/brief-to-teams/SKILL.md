---
name: brief-to-teams
description: "Generate and deliver structured status briefs to Microsoft Teams channels. Queries Jira for sprint progress, blockers, and metrics, pulls recent Confluence updates and decisions, then (1) synthesizes a narrative brief with key highlights, (2) formats it for Teams channel posting, (3) includes action items with @mentions, and (4) archives the brief to Confluence."
---

# Brief to Teams

## Keywords

brief, teams, status, update, channel, jira, confluence, standup, sync, daily, weekly, sprint, blockers, metrics, action items, narrative, adaptive card, team communication, async update, work visibility

## Overview

Teams chat is where your team lives. Jira and Confluence are where your work lives. But status updates — the glue that keeps distributed teams aligned — live in neither. They're scattered across email threads, Teams messages, and copy-pasted sprint reports that go stale by Wednesday.

Brief to Teams closes that gap. It pulls structured data from Jira (sprint progress, blockers, metrics) and Confluence (recent decisions, updated specs, architectural notes), synthesizes it into a narrative brief with a clear arc (What shipped → What's in progress → What's blocked → Key decisions → Action items), formats it as a Teams Adaptive Card (readable at a glance, with threading for details), and posts it directly to the channel where your team already gathers. The brief is then archived to Confluence for async discovery and historical reference.

No more context switching. No more copy-paste. No more status reports that feel like busywork. Just structured updates where the audience already is.

## Workflow

**Step 1: Identify Scope and Audience**
Define what you're briefing on: project key (e.g., PROJ), sprint (current, or by date range), and audience level (daily standup for the team, weekly sync for leadership, exec update for stakeholders). The audience determines what metrics matter and how deep you go into detail.

**Step 2: Identify Target Teams Channel**
Specify the Teams channel where the brief will be posted. This can be a channel name (which requires a Teams API connector) or a webhook URL (simpler, one-way posting). If no Teams integration is available, the brief will be formatted as copy-paste-ready Markdown that you can post manually.

**Step 3: Query Jira for Project and Sprint Data**
Fetch sprint information (current sprint name, dates, goal), then query for issues in three states: completed (done in this sprint), in progress (started but not done), and blocked (impediments preventing progress). Capture key metrics: velocity, burn-down rate, escape rate (bugs found post-release), lead time for completed issues. For blockers, capture: issue key, summary, owner, blocking issues, estimated impact.

**Step 4: Query Confluence for Recent Decisions and Updates**
Search Confluence for pages recently updated (last 7 days) in the relevant spaces. Prioritize: decision records (ADRs or decision pages), architecture/design specs that were updated, project retrospectives, and roadmap updates. Extract: page title, date updated, key decision or change, owner. This gives leadership visibility into how decisions are being made, not just what's being built.

**Step 5: Synthesize Brief with Narrative Arc**
Organize content into five sections:
  - **What Shipped This Period**: Completed issues with business value. Lead with the most important thing. Use one sentence per item.
  - **What's in Progress**: Major work in flight. Include blocker status. Highlight if anything is at risk.
  - **What's Blocked**: Impediments with impact and owner. Be honest about severity. Link to blocking issues.
  - **Key Decisions**: Recent decisions made by the team. Include owner and rationale in one sentence.
  - **Action Items**: Specific next steps, owners, and due dates. Use @mentions for accountability.

**Step 6: Format for Teams**
Use Adaptive Card JSON format (see references/teams-adaptive-card-templates.md). Structure: title, summary section (ship/in progress/blocked counts), expandable "What Shipped" section with inline links, "Blockers" section (red accent if any), "Key Decisions" section, "Action Items" with owner tags, and footer with link to Confluence archive. Cards are scannable in a glance, with threading for details.

**Step 7: Present Brief for User Approval**
Before posting, display the brief to the user in rendered form (Teams preview or Markdown). Allow edits: highlight priority changes, remove sensitive details, add context. This is a checkpoint to ensure quality before sending to the channel.

**Step 8: Post to Teams Channel and Archive to Confluence**
Post the brief to the Teams channel (via webhook or API). Immediately create or update a Confluence page in an archive space (e.g., "Status Briefs / 2026 / Week 15") with the full brief, metadata (project, sprint, date, author), and a link back to the Teams post. This becomes the source of truth for historical context.

## Brief Templates

### Daily Standup Brief
**Audience**: Team members, daily, 9 AM sync.
**Depth**: Shallow. What are we working on today? Any blockers from yesterday? Quick wins from overnight.
**Metrics**: Issue count (in progress, completed since yesterday), blocker count, estimated completion rate.
**Length**: 3-5 sentences + bullet list.
**Example**: "Yesterday we completed 3 issues (PROJ-102, PROJ-105, PROJ-108). 8 issues in flight, 1 blocker (PROJ-110 waiting on design review from @Sarah). Today: focus on PROJ-113 and unblocking PROJ-110. No new risks."

### Weekly Sync Brief
**Audience**: Full team + leads, weekly, end of week or start of week.
**Depth**: Medium. Sprint progress narrative. What's shipped, what's next, what's at risk. Key decisions made during the week.
**Metrics**: Velocity (completed vs. committed), burn-down (graphical or narrative), blocker count, escape rate if applicable, cycle time for issues closed this week.
**Length**: 8-12 sentences + sections with bullet points.
**Example**: "This week we shipped 12 issues and completed 85% of our sprint goal (15/18 committed). The API integration work (PROJ-98) is on track for Thursday. We're blocked on PROJ-104 (waiting for QA resources) — this will slip to next sprint unless we get support. We made two key decisions: adopt gRPC for service-to-service communication (ADR-12), and defer the email notification feature to Q3 (PROJ-121). Action items: @James to follow up with QA by EOD Tuesday; @Maya to schedule architecture review for gRPC choice."

### Exec Update Brief
**Audience**: Executive stakeholder, infrequent (milestone, monthly, or on-demand).
**Depth**: Deep narrative with strategic context. What progress was made toward OKRs? What risks exist? What decisions impact the roadmap?
**Metrics**: Sprint burn-down, trend (velocity over last 4 sprints), on-time delivery rate, quality metrics (escape rate, regression count), business impact (features shipped, customer impact, revenue/cost drivers).
**Length**: 15-20 sentences, structured sections.
**Example**: "Project Phoenix is tracking to deliver MVP by end of Q2 (on schedule). We've completed 35 of 50 planned features across 8 sprints. This sprint's velocity was 21 points, down 3 points from last sprint — due to platform dependency we uncovered on week 2 (PROJ-156). We've mitigated this by partnering with the Platform team; work resumes Wednesday. Business impact: we onboarded 5 early access customers this week; NPS feedback is strong (8.2/10). Risk: we discovered a security issue in the auth layer (CVE-tracked, not critical, but requires rework on PROJ-171). This will cost 1 sprint in Q2. Decision: we're pivoting the analytics roadmap to focus on adoption metrics instead of predictive features — this aligns better with customer asks and de-risks the Q3 release. Next milestone: QA sign-off by April 25."

## Teams Formatting Guide

### Adaptive Card JSON Structure
Adaptive Cards are the native format for Teams. They render as single-card posts with sections, expandable details, and action buttons. See references/teams-adaptive-card-templates.md for complete JSON examples.

Key structure:
- **Card version**: `1.4` (supports latest Teams features)
- **Body**: Array of elements (TextBlock, FactSet, Container for sections)
- **Actions**: Array of OpenUrl or Submit buttons
- **Schema**: JSON-LD, follows Microsoft Adaptive Card spec

Sample structure:
```json
{
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.4",
  "body": [
    {
      "type": "TextBlock",
      "text": "Status Brief: Project Phoenix",
      "weight": "bolder",
      "size": "large"
    },
    {
      "type": "FactSet",
      "facts": [
        {
          "name": "Sprint",
          "value": "Phoenix Sprint 8 (Apr 8-19)"
        },
        {
          "name": "Status",
          "value": "On track"
        }
      ]
    }
  ],
  "actions": [
    {
      "type": "Action.OpenUrl",
      "title": "View in Jira",
      "url": "https://jira.atlassian.com/browse/PROJ?sprint=123"
    }
  ]
}
```

### Markdown Formatting in Teams
Adaptive Cards support Markdown in TextBlock elements (`markdownFormat: true`). Use:
- `**bold**` for emphasis
- `_italic_` for context
- `[link text](url)` for hyperlinks
- Line breaks with `\n`
- Bullet lists with `- item` (one per line)

### @mention Format for Teams Users
To mention a user in Teams via Adaptive Card, use:
```html
<at>DisplayName</at>
```
In JSON, escape as:
```json
"text": "Action: <at>James Chen</at> to follow up with QA"
```

The Teams API will resolve the display name to a proper @mention if the user exists in the channel. Fallback: if using webhooks (no API), include plain names or email addresses; users can manually @mention in the channel.

### Action Button Patterns
Include 2-4 action buttons at card footer:
1. **View in Jira**: Links to filtered board (sprint or project board). URL: `https://jira.atlassian.com/browse/PROJ?sprint=SPRINTID`
2. **View in Confluence**: Links to archive page. URL: `https://confluence.atlassian.com/pages/...`
3. **Sprint Report**: Links to sprint report or dashboard. URL: varies by tool.
4. **Start conversation**: Opens Teams reply thread (implicit if user replies to card).

## Handling Edge Cases

### No Blockers This Period
Don't force it. Simply omit the "Blocked" section or include a positive statement: "No external blockers reported. All work is on track."

### Empty Sprint (No Progress)
This happens during planning sprints or transition periods. Be transparent: "This is a planning sprint. No issues completed; team is in refinement and planning for Sprint 9. Expect updates next week."

### Cross-Project Brief
If briefing on multiple projects, create a single brief with a summary section per project, each with its own metrics. Use section separators in the Adaptive Card. Limit to 3 projects per brief to keep it scannable.

### No Teams Webhook Available
Generate the brief in Markdown format. Display it in the tool output. User can copy-paste to Teams manually, or you can post it to a Confluence page and share the link in Teams.

### Sensitive or Confidential Information
Before posting, filter for audience level. If briefing an exec update, you might include risk/blockers not mentioned in a team standup. Build a safety checkpoint: review brief before posting, allow user to redact sections.

### Sprint Spanning Calendar Boundaries (E.g., Ends on Weekend)
Use explicit dates (Apr 8-19) instead of "this sprint" to avoid confusion. Confirm sprint boundary with user before querying.

## Tips for High-Quality Results

### Narrative Over Numbers
Metrics without context are noise. Always pair numbers with narrative: "We completed 12 issues (85% of sprint goal)" not "12 issues, 85%." Explain the "so what": "This keeps us on track for MVP delivery in May."

### Highlight People
Name the people doing the work. "James and Sarah shipped the API integration" feels human. "The API integration was shipped" feels corporate. Use @mentions in action items to create accountability and celebrate wins.

### Keep It Scannable
Brief reader should be able to skim in 30 seconds and get the headline. Use section headers, short paragraphs, and bullet lists. Avoid dense prose. Adaptive Cards force this by design — use the structure.

### Use Threading for Details
Post the brief as a standalone card. If someone wants depth (full list of issues, detailed blocker analysis, metrics breakdown), they reply in thread or click "View in Jira." The brief is the headline; the tools are the archive.

### Signal Risk Early
If a blocker exists or velocity is down, lead with it in the "What's in Progress" or "Blocked" section. Don't bury it. Teams need to know fast if something is at risk.

### Include Decisions, Not Just Execution
Status briefs often cover only what was built. Add a "Key Decisions" section to show how the team is thinking. This builds trust with leadership and creates accountability for decisions made.

### Archive for Async Consumption
Not everyone reads the brief synchronously. Archiving to Confluence (with metadata) means someone joining the team in Q3 can read Q1 briefs and understand how decisions were made. This is organizational memory.

## When NOT to Use This Skill

- **Real-time incident updates**: Use Teams or Opsgenie. Briefs are for planned, periodic updates.
- **One-off messages to a single person**: Use DM or email. Briefs are for team-wide or leadership broadcast.
- **Detailed technical documentation**: Briefs are summaries. Technical specs belong in Confluence design docs or ADRs, not in a brief.
- **Feedback or performance reviews**: Use 1:1s or formal review processes. Briefs are about work, not people.
- **Social updates or celebrations**: Use Teams #wins channel or all-hands. Briefs are work-focused.

## Examples

### Worked Example: Weekly Sync for Project Phoenix

**Input Setup:**
- Project key: PROJ
- Sprint: Phoenix Sprint 8 (Apr 8-19, 2026)
- Audience: Full team + leads
- Target: Teams channel "project-phoenix-team" (webhook URL provided)
- Date: Friday, Apr 18, 2026

**Step 1-2: Scope & Target**
Confirmed. Full team weekly sync, Friday EOD.

**Step 3: Jira Query**
Query current sprint (PROJ, sprint 8):
- Completed issues this sprint (done since Apr 8):
  - PROJ-98: API integration (James Chen, 8 points)
  - PROJ-102: Database optimization (Sarah Liu, 5 points)
  - PROJ-105: User authentication flow (Marcus, 8 points)
  - PROJ-108: Email notifications (Priya, 3 points)
  - Total: 4 issues, 24 points
- In progress issues (started, not done):
  - PROJ-110: Admin dashboard (Keisha, 13 points, due Mon Apr 21)
  - PROJ-111: Reporting module (David, 8 points, due Wed Apr 19)
  - PROJ-113: Performance tuning (Alex, 5 points, due Fri Apr 18)
  - Total: 3 issues, 26 points
- Blocked issues:
  - PROJ-104: QA resources unavailable (Sarah Liu, design review blocker, PROJ-110 depends on this)
  - PROJ-115: Platform dependency (API auth layer, blocking PROJ-105, scheduled to resolve Wed Apr 17)
  - Total: 2 blockers
- Sprint metrics:
  - Committed: 18 issues, 55 points
  - Completed so far: 24 points (44% of commitment)
  - In progress: 26 points
  - Blockers: 2 issues impacting 2 pieces of work
  - Velocity trend: Sprint 7 was 48 points, Sprint 6 was 52 points

**Step 4: Confluence Query**
Search for pages updated in PROJ space (last 7 days):
- "ADR-12: gRPC for Service Communication" (Updated Apr 16 by Sarah Liu) — decision approved
- "Phoenix MVP Spec v2" (Updated Apr 15 by James Chen) — scope refined, feature reductions approved
- "Q2 Roadmap Update" (Updated Apr 14 by Divya Mohan) — next milestone set to May 1 for MVP

**Step 5: Narrative Synthesis**
Brief narrative:
- **Shipped**: 4 issues this week, 24 of 55 committed points completed (44%). On pace to hit sprint goal if remaining 31 points complete by Monday.
- **In progress**: 3 major features in flight. Admin dashboard (Keisha) on track for Monday. Reporting module (David) due Wednesday. Performance tuning (Alex) wraps up today.
- **Blocked**: 2 blockers. QA review for PROJ-104 is waiting on @Sarah's design approval — estimated resolution Monday. Platform auth layer (PROJ-115) should clear Wednesday per Platform team.
- **Decisions**: Approved ADR-12 (gRPC adoption). Refined MVP scope (reduced email feature to v1.1 per cost analysis). Next milestone: MVP QA sign-off by May 1.
- **Action items**: @James to confirm API integration merge by EOD Saturday. @Keisha to flag any blockers for admin dashboard by Monday morning. @Divya to send out Q2 roadmap update link to stakeholders.

**Step 6: Adaptive Card Format**
(See references/teams-adaptive-card-templates.md for full JSON. Summary structure:)

```
TITLE: Project Phoenix Status Brief - Week of Apr 8-19
FACTS:
  Sprint: Phoenix Sprint 8 (Apr 8-19)
  Status: On Track
  Velocity: 24/55 points completed (44%)

WHAT SHIPPED:
  - API integration complete (James Chen)
  - Database optimization shipped (Sarah Liu)
  - User authentication flow ready (Marcus)
  - Email notifications v1 done (Priya)

WHAT'S IN PROGRESS:
  - Admin dashboard (Keisha, due Monday) — on track
  - Reporting module (David, due Wednesday) — on track
  - Performance tuning (Alex, wraps today) — on track

BLOCKERS (2):
  - PROJ-104: Design review pending @Sarah (impacts PROJ-110)
  - PROJ-115: Platform auth dependency (clears Wednesday)

KEY DECISIONS:
  - Approved gRPC for service communication (ADR-12)
  - Deferred email notifications v2 to post-MVP
  - MVP QA sign-off target: May 1

ACTION ITEMS:
  - @James: Confirm API merge by EOD Saturday
  - @Keisha: Flag blockers for admin dashboard by Monday
  - @Divya: Share Q2 roadmap update with stakeholders

BUTTONS:
  - View in Jira [sprint board link]
  - View Archive [Confluence link]
  - View Sprint Report [dashboard link]

FOOTER: Brief archived to Confluence [timestamp, link]
```

**Step 7: Review**
Display rendered card to user. User reviews, confirms no sensitive info, approves posting.

**Step 8: Post & Archive**
Post Adaptive Card to Teams channel "project-phoenix-team" via webhook. Create Confluence page:
- Title: "Status Brief: Project Phoenix, Week of Apr 8-19"
- Parent: "Status Briefs / 2026 / Week 15"
- Content: Full brief + metadata + Teams post link
- Shared with: project-phoenix-team space

Done. Brief is now live in Teams and archived for historical reference.

## Quick Reference

| Task | Command / Location |
|------|-------------------|
| Query current sprint in Jira | `GET /rest/api/3/board/{boardId}/sprint?state=active` |
| Get sprint issues | `POST /rest/api/2/search` with JQL: `project = PROJ AND sprint = SPRINTID` |
| Query Confluence updates | CQL: `space = PROJSPACE AND updated >= -7d` |
| Adaptive Card JSON schema | https://adaptivecards.io/explorer/ or references/teams-adaptive-card-templates.md |
| Teams webhook format | POST JSON to webhook URL; requires `Content-Type: application/json` |
| Archive to Confluence | Use create_confluence_page with parent_url (see skill: confluence) |
| @mention in Teams | `<at>Display Name</at>` in Adaptive Card TextBlock (API resolution required) |
| Markdown in Adaptive Card | Set `markdownFormat: true` on TextBlock, use `**bold**`, `_italic_`, `[link](url)` |

---

**Version**: 1.0  
**Last Updated**: April 14, 2026  
**Author**: Rovo Dev  
**Status**: Production

