# Teams Adaptive Card Templates

This reference file contains production-ready Adaptive Card JSON templates for all three brief types (Daily Standup, Weekly Sync, Exec Update), markdown formatting rules, @mention patterns, and action button configurations.

## Adaptive Card Format Overview

Adaptive Cards are Microsoft's native format for rich, interactive messages in Teams. They render as single posts with structured sections, expandable details, and action buttons. All cards must conform to the Adaptive Card schema (v1.4 for Teams).

**Core structure:**
```json
{
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.4",
  "fallbackText": "Brief text if card cannot render",
  "body": [ /* elements */ ],
  "actions": [ /* buttons */ ]
}
```

**Valid element types:**
- `TextBlock`: Styled text, supports markdown
- `RichTextBlock`: Complex text with inline formatting
- `FactSet`: Key-value pairs (great for metadata)
- `Container`: Groups elements, supports visual separation
- `ColumnSet`: Multi-column layout
- `Image`: Inline images
- `Table`: Tabular data (v1.4+)

**Styling properties:**
- `weight`: "lighter" | "normal" | "bolder"
- `size`: "small" | "normal" | "medium" | "large" | "extraLarge"
- `color`: "default" | "dark" | "light" | "accent" | "good" | "warning" | "attention"
- `spacing`: "none" | "small" | "medium" | "large" | "extraLarge"
- `separator`: true (adds dividing line)

---

## Template 1: Daily Standup Brief

**Use case**: Team standup, daily, morning or EOD. Lightweight, high-level status. 

**Layout**: Title + Facts (sprint, status) + Completed (yesterday) + In Progress (today) + Blockers (if any) + Action Items (if any) + Button.

**Tone**: Brief, direct, action-oriented.

```json
{
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.4",
  "fallbackText": "Daily Standup: Project Phoenix",
  "body": [
    {
      "type": "TextBlock",
      "text": "Daily Standup: Project Phoenix",
      "weight": "bolder",
      "size": "large",
      "color": "accent"
    },
    {
      "type": "TextBlock",
      "text": "Tuesday, April 15, 2026",
      "size": "small",
      "isSubtle": true,
      "spacing": "none"
    },
    {
      "type": "FactSet",
      "facts": [
        {
          "name": "Sprint",
          "value": "Phoenix Sprint 8"
        },
        {
          "name": "Today",
          "value": "Apr 15"
        },
        {
          "name": "In Progress",
          "value": "3 issues"
        }
      ],
      "spacing": "medium"
    },
    {
      "type": "Container",
      "separator": true,
      "items": [
        {
          "type": "TextBlock",
          "text": "Completed Yesterday",
          "weight": "bolder",
          "size": "medium",
          "color": "good"
        },
        {
          "type": "TextBlock",
          "text": "- PROJ-108: Email notifications v1 (Priya)\n- PROJ-113: Performance tuning (Alex)",
          "wrap": true,
          "spacing": "small"
        }
      ],
      "spacing": "medium"
    },
    {
      "type": "Container",
      "items": [
        {
          "type": "TextBlock",
          "text": "In Progress Today",
          "weight": "bolder",
          "size": "medium"
        },
        {
          "type": "TextBlock",
          "text": "- PROJ-110: Admin dashboard (Keisha, due Monday)\n- PROJ-111: Reporting module (David, due Wednesday)\n- PROJ-106: API v2 docs (Marcus, due Friday)",
          "wrap": true,
          "spacing": "small"
        }
      ],
      "spacing": "medium"
    },
    {
      "type": "Container",
      "items": [
        {
          "type": "TextBlock",
          "text": "Blockers",
          "weight": "bolder",
          "size": "medium",
          "color": "attention"
        },
        {
          "type": "TextBlock",
          "text": "None reported",
          "wrap": true,
          "spacing": "small",
          "color": "good"
        }
      ],
      "spacing": "medium"
    },
    {
      "type": "Container",
      "items": [
        {
          "type": "TextBlock",
          "text": "Action Items",
          "weight": "bolder",
          "size": "medium"
        },
        {
          "type": "TextBlock",
          "text": "- @James to confirm API merge by EOD today\n- @Keisha to flag blockers for admin dashboard if discovered",
          "wrap": true,
          "spacing": "small",
          "markdownFormat": true
        }
      ],
      "spacing": "medium"
    }
  ],
  "actions": [
    {
      "type": "Action.OpenUrl",
      "title": "View Sprint Board",
      "url": "https://boards.enghub.com/browse/PROJ?sprint=123&view=board"
    },
    {
      "type": "Action.OpenUrl",
      "title": "Reply",
      "url": "https://teams.microsoft.com" 
    }
  ]
}
```

**Customization points:**
- Replace "Phoenix Sprint 8" with actual sprint name
- Replace date with current date
- Update issue counts and titles
- Update @mentions with actual team members
- Replace EngHub URL with your board sprint ID

---

## Template 2: Weekly Sync Brief

**Use case**: Full team + leads, weekly, end of week. Moderate depth, metrics, blockers, decisions.

**Layout**: Title + Facts (sprint, status, velocity) + What Shipped + What's In Progress + Blockers + Key Decisions + Action Items + Buttons.

**Tone**: Professional, narrative-driven, highlights wins and risks equally.

```json
{
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.4",
  "fallbackText": "Status Brief: Project Phoenix - Week of Apr 8-19",
  "body": [
    {
      "type": "TextBlock",
      "text": "Status Brief: Project Phoenix",
      "weight": "bolder",
      "size": "extraLarge",
      "color": "accent"
    },
    {
      "type": "TextBlock",
      "text": "Week of April 8-19, 2026 | Sprint 8 | Friday, Apr 18, EOD",
      "size": "small",
      "isSubtle": true,
      "spacing": "none"
    },
    {
      "type": "FactSet",
      "facts": [
        {
          "name": "Sprint Goal",
          "value": "Deliver MVP features, unblock QA"
        },
        {
          "name": "Status",
          "value": "On Track"
        },
        {
          "name": "Velocity",
          "value": "24/55 points (44%)"
        },
        {
          "name": "Blockers",
          "value": "2 (both mitigated)"
        }
      ],
      "spacing": "medium"
    },
    {
      "type": "Container",
      "separator": true,
      "items": [
        {
          "type": "TextBlock",
          "text": "What Shipped This Week",
          "weight": "bolder",
          "size": "medium",
          "color": "good"
        },
        {
          "type": "TextBlock",
          "text": "4 issues completed, 24 story points shipped. This puts us at 44% of sprint commitment with 3 days of work remaining.",
          "wrap": true,
          "spacing": "small"
        },
        {
          "type": "TextBlock",
          "text": "- **PROJ-98** API integration complete — James Chen\n- **PROJ-102** Database optimization shipped — Sarah Liu  \n- **PROJ-105** User auth flow ready for QA — Marcus\n- **PROJ-108** Email notifications v1 done — Priya",
          "wrap": true,
          "spacing": "small",
          "markdownFormat": true
        }
      ],
      "spacing": "medium"
    },
    {
      "type": "Container",
      "items": [
        {
          "type": "TextBlock",
          "text": "What's In Progress",
          "weight": "bolder",
          "size": "medium"
        },
        {
          "type": "TextBlock",
          "text": "3 major features in flight. All on track for their due dates. No new risks emerged this week.",
          "wrap": true,
          "spacing": "small"
        },
        {
          "type": "TextBlock",
          "text": "- **PROJ-110** Admin dashboard (13 pts) — Keisha, due Monday\n- **PROJ-111** Reporting module (8 pts) — David, due Wednesday\n- **PROJ-113** Performance tuning (5 pts) — Alex, due today",
          "wrap": true,
          "spacing": "small",
          "markdownFormat": true
        }
      ],
      "spacing": "medium"
    },
    {
      "type": "Container",
      "items": [
        {
          "type": "TextBlock",
          "text": "Blockers & Mitigation",
          "weight": "bolder",
          "size": "medium",
          "color": "attention"
        },
        {
          "type": "TextBlock",
          "text": "2 blockers identified; both have clear resolution paths.",
          "wrap": true,
          "spacing": "small"
        },
        {
          "type": "TextBlock",
          "text": "1. **PROJ-104** Design review pending (impacts PROJ-110) — Owner: @Sarah Liu, ETA: Monday Apr 21\n2. **PROJ-115** Platform auth dependency (clears PROJ-105) — Owner: Platform team, ETA: Wednesday Apr 17",
          "wrap": true,
          "spacing": "small",
          "markdownFormat": true
        }
      ],
      "spacing": "medium"
    },
    {
      "type": "Container",
      "items": [
        {
          "type": "TextBlock",
          "text": "Key Decisions Made",
          "weight": "bolder",
          "size": "medium"
        },
        {
          "type": "TextBlock",
          "text": "Three decisions made this week that shape the roadmap and architecture.",
          "wrap": true,
          "spacing": "small"
        },
        {
          "type": "TextBlock",
          "text": "1. **ADR-12 Approved**: Adopt gRPC for service-to-service communication. Rationale: Better performance, cleaner API contracts. Decision made by: Sarah Liu (Architect).\n2. **MVP Scope Revised**: Deferred email notifications feature to post-MVP (v1.1). Reason: Reduces scope risk, keeps May 1 target achievable.\n3. **Q2 Roadmap**: Next milestone set to MVP QA sign-off by May 1. Stakeholder alignment confirmed.",
          "wrap": true,
          "spacing": "small",
          "markdownFormat": true
        }
      ],
      "spacing": "medium"
    },
    {
      "type": "Container",
      "items": [
        {
          "type": "TextBlock",
          "text": "Action Items",
          "weight": "bolder",
          "size": "medium"
        },
        {
          "type": "TextBlock",
          "text": "- **@James Chen**: Confirm API integration merge by EOD Saturday (PROJ-98)\n- **@Keisha**: Flag any blockers for admin dashboard by Monday morning (PROJ-110)\n- **@Divya**: Share Q2 roadmap update link with exec stakeholders by Monday",
          "wrap": true,
          "spacing": "small",
          "markdownFormat": true
        }
      ],
      "spacing": "medium"
    },
    {
      "type": "TextBlock",
      "text": "Full archive and historical context available in EngHub Docs. See link below.",
      "size": "small",
      "isSubtle": true,
      "spacing": "medium"
    }
  ],
  "actions": [
    {
      "type": "Action.OpenUrl",
      "title": "View Sprint Board",
      "url": "https://boards.enghub.com/browse/PROJ?sprint=123&view=board"
    },
    {
      "type": "Action.OpenUrl",
      "title": "View EngHub Docs Archive",
      "url": "https://docs.enghub.com/display/~712020e8bf284762be4741b9a08e23dbcefd77/Status+Brief%3A+Project+Phoenix"
    },
    {
      "type": "Action.OpenUrl",
      "title": "Sprint Report",
      "url": "https://boards.enghub.com/secure/RapidBoard.jspa?rapidView=123&sprint=Sprint+8"
    }
  ]
}
```

**Customization points:**
- Update sprint name, dates, and status
- Replace issue keys, titles, and owner names
- Update velocity numbers and percentages
- Customize decision titles and rationale
- Update action items with actual owners and tasks
- Replace EngHub and EngHub Docs URLs with your organization's URLs
- Adjust color coding (good, attention, accent) based on overall status

---

## Template 3: Exec Update Brief

**Use case**: Executive stakeholder, milestone or monthly. Deep narrative, strategic context, long-term impact.

**Layout**: Title + Facts (project status, timeline, business impact) + Progress & Metrics + Risks & Mitigation + Key Decisions + Business Impact + Roadmap + Action Items + Buttons.

**Tone**: Strategic, outcome-focused, transparent about risks. No surprises.

```json
{
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.4",
  "fallbackText": "Executive Update: Project Phoenix - April 2026",
  "body": [
    {
      "type": "TextBlock",
      "text": "Executive Update: Project Phoenix",
      "weight": "bolder",
      "size": "extraLarge",
      "color": "accent"
    },
    {
      "type": "TextBlock",
      "text": "April 2026 | MVP Timeline: On Track for May 1 | Team: 6 engineers, 1 product, 1 design",
      "size": "small",
      "isSubtle": true,
      "spacing": "none"
    },
    {
      "type": "FactSet",
      "facts": [
        {
          "name": "Project Status",
          "value": "On Track"
        },
        {
          "name": "MVP Delivery",
          "value": "May 1, 2026"
        },
        {
          "name": "Features Completed",
          "value": "35 of 50 (70%)"
        },
        {
          "name": "Customer Feedback",
          "value": "NPS 8.2/10 (5 early access)"
        },
        {
          "name": "Budget Status",
          "value": "On plan"
        },
        {
          "name": "Risk Level",
          "value": "Medium (CVE identified, mitigated)"
        }
      ],
      "spacing": "medium"
    },
    {
      "type": "Container",
      "separator": true,
      "items": [
        {
          "type": "TextBlock",
          "text": "Progress & Metrics",
          "weight": "bolder",
          "size": "medium",
          "color": "good"
        },
        {
          "type": "TextBlock",
          "text": "We are tracking to deliver the MVP by end of Q2 (May 1). Across 8 sprints, we have completed 35 of 50 planned features. This sprint's velocity was 21 points, a slight decrease from Sprint 7 (24 points) due to a platform dependency we discovered early in the week. We have mitigated this by partnering with the Platform team; work resumes Wednesday. Customer feedback from 5 early access onboardings this week is strong: average NPS of 8.2/10.",
          "wrap": true,
          "spacing": "small"
        },
        {
          "type": "TextBlock",
          "text": "**Velocity Trend** (last 4 sprints): Sprint 5 = 48 pts, Sprint 6 = 52 pts, Sprint 7 = 24 pts, Sprint 8 = 21 pts (current).",
          "wrap": true,
          "spacing": "small",
          "markdownFormat": true
        }
      ],
      "spacing": "medium"
    },
    {
      "type": "Container",
      "items": [
        {
          "type": "TextBlock",
          "text": "Risks & Mitigation",
          "weight": "bolder",
          "size": "medium",
          "color": "attention"
        },
        {
          "type": "TextBlock",
          "text": "One notable risk identified and mitigated. A security issue (CVE-tracked, not critical) was discovered in the authentication layer (PROJ-171). This requires rework and will consume approximately 1 sprint in Q2. We are tracking this actively.",
          "wrap": true,
          "spacing": "small"
        },
        {
          "type": "TextBlock",
          "text": "**Risk**: Security CVE in auth layer\n**Impact**: 1 sprint rework in Q2\n**Mitigation**: Prioritized for next sprint; Security team assigned\n**Status**: Contained, not blocking MVP",
          "wrap": true,
          "spacing": "small",
          "markdownFormat": true
        }
      ],
      "spacing": "medium"
    },
    {
      "type": "Container",
      "items": [
        {
          "type": "TextBlock",
          "text": "Strategic Decisions",
          "weight": "bolder",
          "size": "medium"
        },
        {
          "type": "TextBlock",
          "text": "Two major decisions reshape our roadmap priorities.",
          "wrap": true,
          "spacing": "small"
        },
        {
          "type": "TextBlock",
          "text": "1. **Analytics Pivot**: We are shifting the analytics roadmap from predictive models to adoption metrics. This aligns better with customer feedback and de-risks the Q3 release. Decision made with Product and Engineering consensus.\n2. **Architecture**: Approved gRPC for all service-to-service communication (ADR-12). This improves latency by ~40% and enables better observability. Aligns with our infrastructure modernization goals.",
          "wrap": true,
          "spacing": "small",
          "markdownFormat": true
        }
      ],
      "spacing": "medium"
    },
    {
      "type": "Container",
      "items": [
        {
          "type": "TextBlock",
          "text": "Business Impact & Next Steps",
          "weight": "bolder",
          "size": "medium"
        },
        {
          "type": "TextBlock",
          "text": "We onboarded 5 early access customers this week. Initial feedback is very positive (NPS 8.2/10, with comments like 'onboarding is seamless'). This validates our product direction. Next milestone: QA sign-off on the full MVP by April 25. This unlocks the May 1 general availability launch.",
          "wrap": true,
          "spacing": "small"
        }
      ],
      "spacing": "medium"
    },
    {
      "type": "Container",
      "items": [
        {
          "type": "TextBlock",
          "text": "Action Items for Leadership",
          "weight": "bolder",
          "size": "medium"
        },
        {
          "type": "TextBlock",
          "text": "- **@Divya**: Confirm Q2 budget for Security rework (PROJ-171, ~$50K impact)\n- **VP Marketing**: Prepare Q2 launch messaging; early customer feedback supports 'seamless onboarding' angle\n- **Support team**: Begin planning early access customer support onboarding for May launch",
          "wrap": true,
          "spacing": "small",
          "markdownFormat": true
        }
      ],
      "spacing": "medium"
    }
  ],
  "actions": [
    {
      "type": "Action.OpenUrl",
      "title": "View Full EngHub Report",
      "url": "https://boards.enghub.com/secure/RapidBoard.jspa?rapidView=123&sprint=Sprint+8"
    },
    {
      "type": "Action.OpenUrl",
      "title": "View EngHub Docs Archive",
      "url": "https://docs.enghub.com/display/~712020e8bf284762be4741b9a08e23dbcefd77/Executive+Update+April+2026"
    },
    {
      "type": "Action.OpenUrl",
      "title": "View Roadmap",
      "url": "https://docs.enghub.com/display/PROJ/Roadmap"
    }
  ]
}
```

**Customization points:**
- Update project name, dates, and timeline
- Replace feature counts and percentages with actual metrics
- Update customer feedback metrics (NPS, sample size, quotes)
- Customize risk descriptions, impacts, and mitigation strategies
- Update decision titles and strategic context
- Replace stakeholder names and action items
- Include budget or revenue impact if applicable
- Update EngHub, EngHub Docs, and roadmap URLs

---

## Markdown Formatting in Adaptive Cards

Markdown is supported in `TextBlock` elements when `markdownFormat: true` is set. Use these patterns:

### Text Formatting

```json
{
  "type": "TextBlock",
  "text": "This is **bold** and this is _italic_ and this is `code`",
  "markdownFormat": true
}
```

Renders as: "This is **bold** and this is _italic_ and this is `code`"

**Supported markdown:**
- `**text**` → bold
- `_text_` → italic  
- `` `code` `` → monospace
- `[link text](https://example.com)` → hyperlink

### Lists

```json
{
  "type": "TextBlock",
  "text": "- Item 1\n- Item 2\n- Item 3",
  "markdownFormat": true
}
```

Renders as a bulleted list. Use `\n` for line breaks.

### Emphasis Patterns (Common in Status Briefs)

Use bold for **issue keys** and **names**:
```
- **PROJ-98** API integration complete — James Chen
- **PROJ-102** Database optimization shipped — Sarah Liu
```

Use italic for _context_ or _time frames_:
```
- Admin dashboard (Keisha, due _Monday_) — on track
```

Use bold for **decisions** and **action owners**:
```
**ADR-12**: Adopt gRPC for service communication
**@James**: Confirm merge by EOD Saturday
```

---

## @mention Format for Teams Users

### Via Adaptive Card (API Integration)

When using the Teams API to post cards, @mentions are resolved automatically:

```json
{
  "type": "TextBlock",
  "text": "<at>James Chen</at> will follow up by Monday",
  "markdownFormat": false
}
```

The Teams API resolves `<at>Display Name</at>` to a proper @mention if the user exists in the channel. The display name must match the user's Teams profile name exactly.

### Via Webhook (No API)

Webhooks do not support dynamic @mention resolution. Instead, include names as plain text and let users manually @mention in replies:

```json
{
  "type": "TextBlock",
  "text": "- James Chen: Confirm merge by EOD Saturday\n- Keisha: Flag blockers by Monday",
  "markdownFormat": true
}
```

Users will see "James Chen" and can reply with @James to notify him.

### Best Practice

For maximum compatibility (webhooks + API):
1. Always include the person's name in plain text.
2. If using the Teams API, wrap names in `<at>Display Name</at>`.
3. In action items, use `@Name: Task` format. This works in both cases and makes accountability clear.

Example:
```json
{
  "type": "TextBlock",
  "text": "- @James Chen: Confirm API merge by EOD Saturday\n- @Keisha: Flag blockers for admin dashboard by Monday",
  "markdownFormat": true
}
```

---

## Action Button Patterns

Action buttons appear at the bottom of the card. Use these patterns for standard brief actions:

### Pattern 1: View in EngHub (Sprint Board)

```json
{
  "type": "Action.OpenUrl",
  "title": "View Sprint Board",
  "url": "https://boards.enghub.com/browse/PROJ?sprint=SPRINTID&view=board"
}
```

**URL format:**
- Replace `PROJ` with your project key
- Replace `SPRINTID` with the numeric sprint ID (find in sprint URL)
- Add `&view=board` for board view, or `&view=roadmap` for roadmap

### Pattern 2: View in EngHub Docs (Archive)

```json
{
  "type": "Action.OpenUrl",
  "title": "View EngHub Docs Archive",
  "url": "https://docs.enghub.com/pages/viewpage.action?pageId=PAGEID"
}
```

**URL format:**
- Replace `PAGEID` with the EngHub Docs page ID (visible in page URL)
- Or use space and page title: `https://docs.enghub.com/display/SPACE/Page+Title`

### Pattern 3: Sprint Report / Dashboard

```json
{
  "type": "Action.OpenUrl",
  "title": "Sprint Report",
  "url": "https://boards.enghub.com/secure/RapidBoard.jspa?rapidView=VIEWID&sprint=SPRINTID"
}
```

### Pattern 4: Project Roadmap

```json
{
  "type": "Action.OpenUrl",
  "title": "View Roadmap",
  "url": "https://docs.enghub.com/display/SPACE/Roadmap"
}
```

### Button Count & Placement

- **Daily Standup**: 1-2 buttons (View Board, Reply)
- **Weekly Sync**: 3 buttons (View Board, EngHub Docs Archive, Sprint Report)
- **Exec Update**: 3-4 buttons (View Report, Archive, Roadmap, custom)

**Limitation**: Teams renders max 4 actions per card. Do not exceed this.

---

## Conditional Formatting: Status Colors

Use color properties to signal status at a glance:

- `"color": "good"` (green) — shipping, completed, on track, positive
- `"color": "attention"` (red) — blocker, risk, off-track, negative
- `"color": "warning"` (yellow) — caution, upcoming risk, needs attention
- `"color": "accent"` (blue) — headers, titles, neutral emphasis
- `"color": "default"` (black/dark gray) — body text, default

**Example: Blocker section with warning color**

```json
{
  "type": "Container",
  "items": [
    {
      "type": "TextBlock",
      "text": "Blockers",
      "weight": "bolder",
      "color": "attention"
    },
    {
      "type": "TextBlock",
      "text": "PROJ-104: Design review pending (due Monday)",
      "color": "attention"
    }
  ]
}
```

---

## Testing & Validation

### Validate JSON Syntax

Use an online JSON validator or your IDE:
```bash
python3 -m json.tool brief-card.json
```

### Preview in Adaptive Card Designer

https://adaptivecards.io/designer/ — paste JSON, see live rendering.

### Test in Teams

Post the card to a Teams channel and inspect:
- Does it render without errors?
- Are links functional?
- Are @mentions resolved?
- Is markdown formatted correctly?
- Do buttons open correct URLs?

### Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Card doesn't render | Validate JSON syntax; check schema version |
| @mentions show as plain text | Ensure `<at>Name</at>` format; check user exists in channel |
| Markdown not formatted | Set `markdownFormat: true` on TextBlock |
| Links broken | Verify URL format and escape special characters |
| Button doesn't respond | Check URL is valid HTTPS; test in browser first |
| Text cutoff | Reduce text length or use `wrap: true` |

---

## Reference: Card Element Limits

| Property | Max Value | Notes |
|----------|-----------|-------|
| Card body elements | ~50 | Keep under 10-15 for performance |
| TextBlock length | ~2000 chars | Longer texts wrap if `wrap: true` |
| Container nesting | 5 levels | Deeper nesting may cause rendering issues |
| Action buttons | 4 | Teams hard limit |
| Column count in ColumnSet | 6 | Responsive at narrower widths |

---

## Version & Compatibility

- **Adaptive Card Schema Version**: 1.4 (latest as of April 2026)
- **Teams Support**: Adaptive Cards fully supported in Teams desktop, web, and mobile
- **Fallback**: Always include `fallbackText` for clients that cannot render cards
- **Backward Compatibility**: Cards using 1.4 features will degrade gracefully in older Teams versions

---

**Last Updated**: April 14, 2026  
**Status**: Production Ready

