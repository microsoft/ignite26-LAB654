---
name: teams-meeting-to-work
description: "Convert Microsoft Teams meeting transcripts into tracked work. Extracts decisions, action items, and blockers from Teams transcripts with speaker attribution, then (1) creates Jira tickets with proper assignees, (2) posts a structured meeting recap to Confluence, (3) identifies follow-up deadlines, and (4) links related existing Jira issues."
---

# Teams Meeting to Work

## Keywords

teams, meeting, transcript, action items, decisions, jira, confluence, recap, minutes, blockers, decisions, speaker attribution, follow-ups, deadlines

## Overview

Teams meetings generate knowledge that lives in video recordings and chat history—and then disappears. By the time someone transcribes the meeting or writes minutes, the conversation's intent has been simplified. Action items get lost in Teams threads. Decisions fade into "I thought we agreed on that." Blockers don't surface until they're blocking again.

This skill extracts the real commitments from Teams meeting transcripts and routes them into your work system. It identifies speakers, parses action items with assignees and deadlines, surfaces decisions, flags blockers, and creates a single source of truth: Jira tickets for tracked work + a Confluence recap page for async reference. The result is that decisions become searchable, action items show up in assignees' queues, and blockers are visible to the team that can unblock them.

## Workflow

### Step 1: Accept Teams Transcript

Provide the Teams meeting transcript in one of these formats:

- **Pasted text**: Transcript copied directly from Teams "Meeting details" → "Transcription" (auto-generated or manually edited)
- **URL to Teams recording**: Link to the Teams meeting page; the system will extract the transcript if available
- **Plain-text transcript**: Any structured or unstructured notes from the meeting, as long as speakers are attributed

The system will ask clarifying questions if speaker names are ambiguous or if multiple meetings are referenced.

### Step 2: Parse Transcript

The system reads through the transcript and extracts:

- **Speakers**: Identified by name/title/display name in Teams format (e.g., "Sarah Chen (Atlassian)")
- **Action items**: Patterns like "[name] will [verb] [commitment]", "[name] to [verb]", "we need [name] to do [thing]"
- **Decisions**: Patterns like "we decided to", "agreed on", "let's go with", "we're moving forward with", "[name] decided"
- **Blockers**: Patterns like "blocked by", "waiting on", "can't proceed until", "need [dependency] first"
- **Follow-ups**: Explicit deadlines ("by Friday", "next sprint", "before next meeting") or inferred from context

Each extracted item is tagged with:
- Speaker(s) involved
- Raw quote from transcript
- Inferred deadline (if any)
- Related topic/project area

### Step 3: Ask for Target Jira Project

Which Jira project should tickets be created in? Provide the project key (e.g., "PLAT", "CONF", "PMM").

The system will validate that the project exists and that you have permission to create issues in it.

### Step 4: Look Up Jira Account IDs

For each speaker and assignee identified in the transcript, the system:

- Queries Atlassian Directory for account IDs matching the Teams display name
- Handles common name variations (e.g., "Sarah" → "Sarah Chen", "SC" → "Sarah Chen")
- Flags ambiguous matches (e.g., two people named "Alex") and asks you to clarify

Once resolved, the system builds a mapping of Teams names → Jira account IDs for ticket creation.

### Step 5: Search Jira for Related Issues

The system queries Jira for existing issues that might be related to:

- The same project
- Keywords from the transcript (e.g., if the meeting was about "performance optimization", search for issues with that label or title)
- Assignees mentioned in the meeting

This prevents duplicate tickets and identifies issues to link from new tickets.

### Step 6: Present Extracted Items for Confirmation

The system groups extracted items by type:

- **[DECISION]** items (with consensus level: unanimous, majority, or tentative)
- **[ACTION]** items (with assignee, deadline, estimated effort)
- **[BLOCKER]** items (with dependency chain and who can unblock)
- **[FOLLOW-UP]** items (with deadline and owner)

Each item shows:
- The raw quote from the transcript
- Extracted assignee / owner
- Inferred deadline
- Links to related existing Jira issues

You review, edit, and confirm. The system flags:
- Missing assignees (can't create ticket without owner)
- Ambiguous deadlines ("soon", "eventually" → ask for specific date)
- Unrealistic commitments (multiple people assigned to one action item → clarify)

### Step 7: Create Jira Tickets + Confluence Recap

Once confirmed:

1. **Create Jira tickets** (one per action item + one per blocker):
   - Title: Extracted from action item (e.g., "Investigate performance regression in query indexing")
   - Description: Full quote from transcript + speaker attribution + related decisions
   - Assignee: The Jira account ID for the owner
   - Due date: Extracted deadline
   - Project: The selected Jira project
   - Labels: "teams-generated", "meeting-followup", "[meeting-date]"
   - Linked issues: Any related existing issues flagged in Step 5

2. **Post Confluence recap page** in the user's personal space (or a specified location):
   - Title: "Meeting Recap: [Meeting Title] - [Date]"
   - Sections: Attendees, Decisions, Action Items, Blockers, Related Jira Issues
   - Each section includes speaker attribution and quotes
   - Links to all created Jira tickets
   - Links to any linked existing issues

3. **Return summary** with:
   - List of created Jira tickets (with links)
   - Link to Confluence recap page
   - Count of decisions, actions, blockers, and follow-ups
   - Any flags or warnings (e.g., "5 action items have no deadline")

### Step 8: Summary with Links

The system provides a final summary showing:

- Jira tickets created (with project key, issue ID, and title)
- Confluence recap page (with direct link)
- Decisions tracked (with links to related tickets)
- Blockers escalated (with links to who can help unblock)
- Next steps (when to revisit, when blockers need follow-up)

## Teams Transcript Patterns

Teams transcripts come in several formats. The system handles these patterns:

### Auto-Generated Transcription Format

```
Sarah Chen
00:15
We need to look at the performance regression in query indexing.

Marcus Rodriguez
00:45
That's a big blocker for the next release. We're blocked by the database team.
```

**Patterns**:
- Speaker name on its own line
- Timestamp in MM:SS format
- Message text follows

**Extraction logic**:
- Speaker identified by line preceding timestamp
- `look at` + `performance regression` = action item → search for existing "regression" issues
- `blocked by` + `database team` = blocker with dependency

### Manual Notes Format (Free-form)

```
In the product planning meeting on Monday, Sarah said we should prioritize the 
mobile experience. Marcus agreed but noted we're waiting on the design system team.
By next sprint, we need to finalize requirements.
```

**Patterns**:
- Indirect speech ("Sarah said", "Marcus noted")
- Implicit deadlines ("by next sprint", "before the release")
- Decisions embedded in narrative ("agreed", "should prioritize")

**Extraction logic**:
- Named subject + sentiment verb (`agreed`, `noted`, `said`) = decision with speaker
- Duration reference (`by next sprint`) = deadline inference
- `waiting on` [team] = blocker with dependency

### Hybrid Format (Transcript + Comments)

```
Sarah Chen
01:23
Let's get the query performance fixed. Marcus, can you take that?

Marcus Rodriguez
01:45
Yeah, I'll handle it. Need it by Friday.
```

**Patterns**:
- Direct quote format mixed with speaker attribution
- Explicit assignment ("Marcus, can you take that?")
- Verbal commitment ("I'll handle it")

**Extraction logic**:
- Direct address + action verb (`take`) = action item assignment
- Verbal commitment + deadline = task with timeline
- Speaker responding = confirmation of assignment

### Reaction Markers

Teams transcripts sometimes include reactions (thumbs up, fire, lol, etc.). The system:

- Ignores emoji/reaction text in extraction (not substantive)
- Uses reaction counts to gauge consensus if needed (e.g., "3 thumbs up on the decision")

### @ Mentions

When a speaker includes `@SomeoneElse`, the system:

- Treats the mention as an assignment (if action-like context)
- Flags multi-person assignments for clarification (is it really a team task, or should it be split?)

## Handling Edge Cases

### Ambiguous Speaker Attribution

**Case**: "They said we should move ahead, but I'm not sure who owns it."

**Action**: Ask for clarification. If the speaker is unclear, mark as "[TBD]" in the draft and require confirmation before ticket creation.

### Overlapping Action Items

**Case**: Two people commit to the same action in different parts of the meeting.

**Action**: Surface both commitments. Ask: "Are these duplicates, or parallel tracks?" If duplicates, suggest merging under one assignee.

### Vague Deadlines

**Case**: "We'll get that done soon", "Let's revisit this later."

**Action**: Flag as missing deadline. Ask for specifics: "When is 'soon'? Next sprint? Next week? End of month?" Do not create the ticket until deadline is clarified or explicitly marked as "no deadline".

### Passive Voice / Distributed Ownership

**Case**: "The team should figure out the API design."

**Action**: Ask who on the team is leading this. If truly distributed, create one ticket and set the reporter as "owner of coordination" but flag that it needs internal sub-tasking.

### Meeting References Other Meetings

**Case**: "As we discussed last week in the steering committee..."

**Action**: The system will ask: "Are there other meetings you want to link to this recap?" Offer to search Jira for related decisions/tickets from those meetings.

### No Clear Deadline (Open-Ended Work)

**Case**: "We should improve our documentation" (no time frame).

**Action**: Create the ticket but mark it with label "backlog-item" and no due date. Ask the assignee to confirm this is intentional or to specify when it should be addressed.

### Blocked Before Starting

**Case**: An action item cannot start until a blocker is resolved.

**Action**: Create both the blocker ticket and the action ticket. Link them explicitly with "is blocked by" relationship. Mark the action ticket as "blocked" in the recap so it's not expected to move until the blocker is resolved.

## Tips for High-Quality Results

### 1. Transcript Quality Matters

- **Auto-generated transcripts** are 70-85% accurate. Proofread speaker names before confirming.
- **Manual notes** require more interpretation. The system will flag ambiguities.
- **Hybrid** (transcript + manual edits) is often best. Edit the auto-transcript to fix speaker attribution, then paste it in.

### 2. Speaker Names Must Be Consistent

Teams display names vary: "Sarah Chen (Atlassian)", "Sarah (Product)", "SC", "Sarah". Before parsing, the system will ask you to normalize names. Pick one consistent format for each person.

### 3. Specify Meeting Context

Tell the system:
- **Meeting title**: "Q2 Product Planning" (used in Confluence page title and Jira labels)
- **Meeting date**: "April 14, 2026" (used in linking and recap)
- **Attendees list** (optional): Helps resolve ambiguous speakers and identifies people who were present but silent

### 4. Use Explicit Language in Confirmations

When reviewing the extracted items (Step 6), be specific:
- Don't say "looks good"—confirm each action item individually
- Edit deadlines if they're vague in the transcript
- Rename action items if the extracted title is unclear
- Mark items as "low priority" or "can wait" if context suggests they shouldn't block anything

### 5. Link Existing Issues, Don't Create Duplicates

The system searches for related issues (Step 5), but you know the codebase better. If you see a related issue that wasn't surfaced, add it manually in Step 6.

### 6. Teams Doesn't Replace This

If the meeting included a Teams chat or channel thread where people said "I'll handle X", those commitments should also be extracted and included—they're part of the meeting's output.

### 7. Confluence Recap Is the Source of Truth for Async Readers

People who weren't at the meeting will read the Confluence recap. Make sure it's:
- **Complete**: All decisions and actions are listed
- **Attributed**: People can see who said what
- **Linked**: Related Jira issues are easy to find

## When NOT to Use This Skill

- **Brainstorming meetings with no decisions**: If the meeting was exploratory and produced no action items, this skill is overkill. A simple Confluence page with notes is better.
- **Meetings that are already documented**: If the team already created a Confluence recap and Jira tickets, you don't need this skill.
- **Verbal-only meetings without transcript**: If you don't have a transcript or detailed notes, the system can't extract action items reliably.
- **Meetings where actions are being tracked in another system**: If your team uses Asana, Monday.com, or another tool as the source of truth, this skill is for Jira/Confluence workflows only.
- **One-on-one status updates**: These usually don't produce Jira-worthy action items. A quick Confluence note is better.

## Examples

See [`references/worked-examples.md`](references/worked-examples.md) for this section (relocated to keep SKILL.md within the 20,000-character limit).

## Quick Reference

### Tools & APIs

**Jira**:
- `search_jira_using_jql`: Find related existing issues by keyword, assignee, or project
- `create_jira_issue`: Create new action/blocker tickets with assignee, due date, labels, linked issues
- `get_jira_issue`: Fetch full context if linking to an existing ticket

**Confluence**:
- `create_confluence_page`: Post meeting recap in user's personal space
- `update_confluence_page`: Update recap if new information emerges

**Atlassian Directory**:
- `get_user`: Look up account IDs by Teams display name
- Handle name variations and ask for clarification on ambiguous matches

### Key Extraction Patterns

| Pattern | Example | Extracts As |
|---------|---------|-------------|
| `[name] will [verb]` | Sarah will investigate the bug | ACTION (Sarah) |
| `we decided to [action]` | We decided to move forward with approach B | DECISION |
| `blocked by [thing]` | We're blocked by the design team | BLOCKER |
| `[name] agreed` | Marcus agreed with the plan | DECISION (consensus) |
| `by [date/timeframe]` | By next Friday, we need X | DEADLINE |
| `@[name] [action]` | @Marcus, can you check the logs? | ACTION (Marcus) |
| `waiting on [team/person]` | Waiting on infra to provision the database | BLOCKER |

### Deadline Inference Heuristics

- "by Friday" → Next Friday from meeting date
- "before the release" → Search Jira for next release date
- "next sprint" → Get sprint dates from project settings
- "ASAP" / "urgent" → Same day if possible, next business day otherwise
- "eventually" / "when we have time" → Flag as missing deadline, ask for specifics

### Common Mistakes to Avoid

1. **Creating one mega-ticket** instead of breaking into atomic action items
2. **Assigning to the whole team** instead of one owner per ticket
3. **Forgetting to link related existing issues** (creating duplicates)
4. **Using vague titles** like "Follow up on discussion" instead of "Investigate X"
5. **Not capturing the decision context** in ticket descriptions (so readers know the why)
6. **Missing blockers** that prevent work from starting
7. **Ignoring the Confluence recap** (treating it as optional documentation instead of source of truth for async readers)

---

**Version**: 1.0  
**Last Updated**: April 14, 2026  
**Maintained By**: Rovo Dev / AI PMM team at Atlassian
