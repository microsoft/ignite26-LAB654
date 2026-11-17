# SharePoint to Backlog — Examples, Quick Reference & Implementation Notes

This content was relocated from `SKILL.md` to keep that file within the 20,000-character agent-skill limit. Load it when you need this detail.

## Examples

### Example 1: Simple Feature Spec

**Input Document:**

```
Feature: Dark Mode Support

Overview
Users request a dark mode option for the web application. This feature provides a toggle in user settings and automatically detects OS dark mode preference.

Requirements
1. Detect OS dark mode preference
   - Use prefers-color-scheme media query
   - Store preference in local storage
   - Default to OS preference if no local setting
2. Add Dark Mode toggle in Settings
   - Toggle under Appearance section
   - Label: "Dark Mode"
   - Switch control (not radio buttons)
3. Apply dark color palette
   - Background: #1a1a1a
   - Text: #ffffff
   - Accent: #0066cc
4. Update all UI components
   - Forms, buttons, modals, cards
   - Tables and data displays
   - Code syntax highlighting

Acceptance Criteria
- System shall detect OS dark mode on page load
- User preference shall override OS setting
- All text shall meet WCAG AA contrast ratios in dark mode
- Dark mode shall apply to all pages within 2 seconds of toggle
- Settings shall persist preference across sessions
```

**Parsed Output:**

```
Epic: PROJ-100 - Dark Mode Support
├─ Story: PROJ-101 - Detect OS Dark Mode Preference
│  ├─ Task: PROJ-102 - Implement prefers-color-scheme detection
│  ├─ Task: PROJ-103 - Store preference in local storage
│  ├─ Task: PROJ-104 - Set default to OS preference
│  └─ ACs: System shall detect on load; User preference shall override OS
│
├─ Story: PROJ-105 - Add Dark Mode Toggle in Settings
│  ├─ Task: PROJ-106 - Add toggle to Appearance section
│  ├─ Task: PROJ-107 - Implement switch control UI
│  └─ ACs: Label shall be "Dark Mode"; Switch control required
│
├─ Story: PROJ-108 - Apply Dark Color Palette
│  ├─ Task: PROJ-109 - Define CSS variables for dark colors
│  ├─ Task: PROJ-110 - Update global stylesheets
│  └─ ACs: BG #1a1a1a, Text #ffffff, Accent #0066cc
│
└─ Story: PROJ-111 - Update UI Components
   ├─ Task: PROJ-112 - Update forms, buttons, modals
   ├─ Task: PROJ-113 - Update tables and data displays
   ├─ Task: PROJ-114 - Update code highlighting
   └─ ACs: All text WCAG AA contrast; Apply within 2 seconds
```

### Example 2: Complex RFP Response

**Input Document (excerpt):**

```
Deliverable 1: API Authentication

As a system integrator, I want the API to support OAuth 2.0, 
so that third-party applications can authenticate securely.

Requirements:
1. OAuth 2.0 Implementation
   a. Authorization Code flow
   b. Refresh token support
   c. Token expiration (15 minutes for access, 7 days for refresh)
2. Scopes
   - read:users
   - write:data
   - admin:settings
3. Security
   - HTTPS only
   - CORS validation
   - Rate limiting (1000 req/min per client)

Acceptance Criteria:
Given: A third-party app requests an access token
When: User authorizes the request
Then: OAuth server returns access token, refresh token, and expiration
And: Token is valid for exactly 15 minutes

Given: Access token expires
When: App uses refresh token to get new token
Then: Server validates refresh token
And: Returns new access token
And: Old token is revoked
```

**Parsed Output:**

```
Epic: PROJ-200 - Deliverable 1: API Authentication
├─ Story: PROJ-201 - OAuth 2.0 Implementation (As a system integrator...)
│  ├─ Task: PROJ-202 - Implement Authorization Code flow
│  ├─ Task: PROJ-203 - Implement refresh token mechanism
│  ├─ Task: PROJ-204 - Set token expiration (15m access, 7d refresh)
│  └─ ACs: [Scenario 1: Token request], [Scenario 2: Token refresh]
│
├─ Story: PROJ-205 - Define OAuth Scopes
│  ├─ Task: PROJ-206 - Implement read:users scope
│  ├─ Task: PROJ-207 - Implement write:data scope
│  ├─ Task: PROJ-208 - Implement admin:settings scope
│  └─ ACs: Scopes shall be enforced in API calls
│
└─ Story: PROJ-209 - Security Hardening
   ├─ Task: PROJ-210 - Enforce HTTPS only
   ├─ Task: PROJ-211 - Implement CORS validation
   ├─ Task: PROJ-212 - Implement rate limiting (1000 req/min)
   └─ ACs: All endpoints HTTPS; Rate limit enforced; CORS validated
```


## Quick Reference

### Keyboard Shortcuts (N/A - this is a structured skill, not interactive UI)

### Common Commands

```
skill: sharepoint-to-backlog

Input:
  content: "Pasted text from Word/SharePoint"
  project_key: "PROJ"
  parent_issue: "PROJ-1" (optional)
  labels: ["from-sharepoint", "feature-x"] (optional)

Output:
  epic_created: "PROJ-123"
  stories_created: 3
  tasks_created: 12
  hierarchy_tree: [ASCII visualization]
  summary: [Table with issue keys and links]
```

### Validation Checklist Before Running

- [ ] Document has clear headings (H1, H2, H3)
- [ ] Requirements use "shall", "must", "will" language
- [ ] EngHub project key is confirmed and accessible
- [ ] No more than 100 items total (Epic + Stories + Tasks)
- [ ] Issue types (Epic, Story, Task) exist in the target project
- [ ] Assignees (if specified) have valid EngHub accounts
- [ ] Source document is readable (no corruption, OCR artifacts, etc.)

### Troubleshooting

| Problem | Solution |
|---------|----------|
| "EngHub project not found" | Verify project key; check EngHub access permissions |
| "No headings detected" | Add H2/H3 headings to organize content, or ask skill to infer from list structure |
| "Too many tasks created" | Review and merge/combine small tasks in the proposed hierarchy |
| "Acceptance criteria are blank" | Add requirement statements with "shall", "must", or "will" to the source doc |
| "Issue links are broken" | Skill may have created issues but failed to link. Use EngHub API to re-link manually |

---


## Architecture Notes for Implementers

**Data Flow:**
1. Parse input text → Extract headings, lists, requirement statements
2. Build in-memory tree structure (Epic → Stories → Tasks)
3. Validate against EngHub project schema (issue types, custom fields)
4. Construct API payload for EngHub (POST /issue for each, then PUT /issue/{key}/link for relationships)
5. Return results with keys and links

**Dependencies:**
- EngHub REST API v3 (for issue creation and linking)
- Text parsing library (stdlib regex + custom heading detection)
- No external dependencies preferred; use EngHub MCP tools if available

**Error Handling:**
- If EngHub API call fails for an issue, stop and rollback created issues (or log for manual cleanup)
- If a parent issue fails, all children are orphaned (flag and require user intervention)
- If a link fails, log and continue (non-blocking error)
