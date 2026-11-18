# Teams Meeting to Work Skill

A complete MCP skill for converting Microsoft Teams meeting transcripts into tracked work items in Jira and Confluence.

## Directory Structure

```
teams-meeting-to-work/
├── SKILL.md                    # Main skill documentation (527 lines, 21KB)
├── references/
│   └── teams-transcript-patterns.md    # Reference guide for transcript parsing (852 lines, 23KB)
└── README.md                   # This file
```

## Contents

### SKILL.md (Production Skill Documentation)

Complete skill guide with 14 major sections:

1. **Keywords**: teams, meeting, transcript, action items, decisions, jira, confluence, recap, minutes
2. **Overview**: Problem statement + solution approach (2 paragraphs)
3. **Workflow**: 8-step process from transcript intake to final summary
   - Step 1: Accept Teams transcript (pasted text or URL)
   - Step 2: Parse transcript (speakers, action items, decisions, blockers)
   - Step 3: Ask for target Jira project key
   - Step 4: Look up Jira account IDs for assignees
   - Step 5: Search Jira for related existing issues
   - Step 6: Present extracted items for confirmation
   - Step 7: Create Jira tickets + Confluence recap page
   - Step 8: Summary with links
4. **Teams Transcript Patterns**: 4 formats with extraction logic
   - Auto-generated transcription (timestamps + speakers)
   - Manual notes (free-form narrative)
   - Hybrid (transcript + editorial comments)
   - Reaction markers and @ mentions
5. **Handling Edge Cases**: 7 common scenarios with resolution steps
6. **Tips for High-Quality Results**: 7 best practices
7. **When NOT to Use This Skill**: 5 scenarios where this skill is overkill
8. **Examples**: 2 complete worked examples (product planning + incident response)
9. **Quick Reference**: Tools, extraction patterns, deadline inference, common mistakes

### references/teams-transcript-patterns.md (Reference Guide)

Comprehensive pattern library with 8 major sections:

1. **Common Teams Transcript Formats** (3 deep-dive formats with characteristics, accuracy, extraction challenges)
2. **Speaker Attribution Patterns** (6 patterns from direct to implied)
3. **Action Item Detection Patterns** (6 patterns with examples)
4. **Decision Detection Patterns** (6 patterns including consensus, conditions, defaults)
5. **Blocker Detection Patterns** (6 patterns from explicit to conditional)
6. **Follow-Up & Deadline Patterns** (7 deadline types and how to infer them)
7. **Special Patterns** (at-mentions, reactions, multiple meetings, speaker errors, jargon)
8. **Using This Reference in Practice** (5-step process)

## Key Features

- **No emoji**: All content uses plain text markers like [ACTION], [DECISION], [BLOCKER]
- **Production-ready**: 1,379 lines total (527 in SKILL.md + 852 in reference)
- **Comprehensive**: Covers auto-generated, manual, and hybrid transcript formats
- **Practical**: 2 complete worked examples (product planning + incident response)
- **Extensible**: Reference guide enables building extraction logic for Teams transcripts
- **Jira/Confluence integration**: Clear integration points with Atlassian tools

## How to Use This Skill

### For End Users (Sid)

1. Paste your Teams meeting transcript (or provide URL to Teams recording)
2. Specify the target Jira project
3. Review and confirm extracted action items, decisions, and blockers
4. Skill creates Jira tickets + Confluence recap automatically

### For Developers Building the Skill

1. Read **SKILL.md** overview to understand the user workflow (Steps 1-8)
2. Use **references/teams-transcript-patterns.md** to build the extraction logic
3. Key extraction patterns to implement:
   - Speaker attribution (direct, quoted, implied)
   - Action items (commitments with owner + deadline)
   - Decisions (explicit agreements + consensus signals)
   - Blockers (external dependencies + obstacles)
   - Deadlines (explicit dates, relative timelines, sprint-based, event-based, vague)

## Integration Points

### Atlassian Tools Required

- **Jira**: `search_jira_using_jql`, `create_jira_issue`, `get_jira_issue`
- **Confluence**: `create_confluence_page`, `update_confluence_page`
- **Atlassian Directory**: User lookup for account IDs (Teams name → Jira account ID mapping)

### Data Flow

```
Teams Transcript
    ↓
Parse speakers, action items, decisions, blockers
    ↓
Normalize speaker names → Look up Jira account IDs
    ↓
Search Jira for related existing issues
    ↓
Present to user for confirmation (Step 6)
    ↓
Create Jira tickets + Confluence recap page
    ↓
Return summary with links
```

## Quality Standards

- **Speaker attribution**: Must match Teams display names to Jira accounts
- **Action items**: One owner per ticket (no distributed ownership without clarification)
- **Deadlines**: Explicit dates required (vague deadlines flagged in Step 6)
- **Blockers**: Clear dependency chain (what's blocked, what's blocking, who unblocks)
- **Confluence recap**: Includes attendees, decisions, actions, blockers, related Jira issues

## Testing Checklist

When implementing this skill, test with:

- [ ] Auto-generated Teams transcript (with timestamps)
- [ ] Manual notes transcript (narrative format)
- [ ] Hybrid transcript (edited auto-generated + comments)
- [ ] Edge case: Vague deadlines (should flag for user confirmation)
- [ ] Edge case: Ambiguous speaker attribution (should ask for clarification)
- [ ] Edge case: Distributed ownership (should ask who is leading)
- [ ] Edge case: Blocker with no unblock timeline (should ask for estimate)
- [ ] Integration: Creating Jira tickets with correct assignees
- [ ] Integration: Creating Confluence recap with proper links
- [ ] Integration: Linking related existing Jira issues

## Notes

- This skill assumes the user has access to Jira and Confluence
- Speaker names in the transcript must be matchable to Jira accounts (or manually specified)
- Deadlines can be vague in the transcript; Step 6 clarification is critical
- The Confluence recap page is the source of truth for async readers—must be complete and well-formatted

---

**Version**: 1.0  
**Created**: April 14, 2026  
**Status**: Production-ready
