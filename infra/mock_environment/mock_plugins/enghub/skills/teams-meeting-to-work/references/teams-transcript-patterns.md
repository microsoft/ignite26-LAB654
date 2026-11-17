# Teams Transcript Patterns Reference

This reference document details the patterns used to extract action items, decisions, blockers, and follow-ups from Teams meeting transcripts.

## Common Teams Transcript Formats

### Format 1: Auto-Generated Transcription (Default Teams Export)

Teams' built-in transcription service generates structured transcripts with clear speaker attribution and timestamps.

**Structure**:
```
[Speaker Name]
[MM:SS or HH:MM:SS]
[Message text, may span multiple paragraphs]

[Next Speaker]
[MM:SS]
[Message text]
```

**Characteristics**:
- Speaker name appears on its own line, in title case
- Timestamp follows immediately after
- Message text may contain multiple sentences or paragraphs
- Line breaks separate speaker turns
- Punctuation is usually present (periods, commas, question marks)
- No explicit metadata (no "meeting title" or "attendees" in the transcript itself)

**Accuracy**:
- Speaker names: 95% accurate (Teams matches speaker via device/phone login)
- Speech-to-text: 80-85% accurate for native English speakers, lower for accents or domain jargon
- Common errors: Technical terms ("EngHub" → "gear", "React" → "re-act"), quick cross-talk attribution

**Example**:
```
Sarah Chen
00:15
We need to prioritize the accessibility audit for the next release.

Marcus Rodriguez
01:02
Agreed. How long do you think it will take?

Sarah Chen
01:23
Based on the last time we did an audit, probably two weeks with one contractor.

Marcus Rodriguez
02:15
Can we get that started by the end of the month?

Sarah Chen
02:45
Yeah, I'll reach out to the contractor pool today.
```

**Extraction Notes**:
- "prioritize the accessibility audit" + "next release" = [DECISION] + [ACTION] with implied deadline
- "Agreed" = [DECISION] (consensus signal)
- "Can we get that started by end of month?" = asking for commitment + deadline
- "I'll reach out to the contractor pool today" = [ACTION] (Sarah, due today)

---

### Format 2: Manual Notes (Free-Form or Structured)

When someone copies the Teams chat into a document or writes meeting notes manually, the format varies widely. Common patterns:

**Unstructured Narrative**:
```
In our product planning meeting on Monday, Sarah and Marcus discussed the 
accessibility audit. Sarah said we should prioritize it for next release, 
and Marcus agreed. They decided to bring in a contractor for two weeks. 
Sarah will reach out to the contractor pool by end of week.
```

**Semi-Structured Bullets**:
```
Product Planning Meeting - April 14, 2026

Attendees: Sarah Chen, Marcus Rodriguez

Key Points:
- Accessibility audit needed for next release
- Marcus agrees with priority
- Estimated effort: 2 weeks with contractor
- Sarah to contact contractor pool by EOW
```

**Decision Log Format**:
```
Decision: Prioritize accessibility audit in next release
Owner: Sarah Chen
Status: Agreed (consensus)
Next Steps: Sarah contacts contractor pool (EOW deadline)
```

**Characteristics**:
- Indirect speech ("Sarah said", "Marcus agreed") instead of direct quotes
- Implicit speakers (pronouns like "they" instead of names)
- Narrative flow instead of line-by-line structure
- Deadlines expressed as natural language ("EOW", "next sprint", "before the release")
- May include summary-level interpretation, not word-for-word quotes

**Extraction Challenges**:
- Need to resolve indirect speech to find speakers
- May miss nuance (e.g., was Marcus enthusiastic or reluctant?)
- Requires inference for deadlines
- May conflate multiple decision discussions into one summary

**Example**:
```
The team discussed performance optimization. They agreed to focus on query 
indexing first because the database team has bandwidth. Priya will run profiling 
and create a report. Marcus will design the new index structure. Both deliverables 
due before Q2 planning (April 28).
```

**Extraction**:
- "discussed performance optimization" = context
- "agreed to focus on query indexing first" = [DECISION] (with rationale: database team bandwidth)
- "Priya will run profiling" = [ACTION] (Priya, implied deadline April 28)
- "Marcus will design new index structure" = [ACTION] (Marcus, implied deadline April 28)
- "before Q2 planning" = [DEADLINE] (April 28)

---

### Format 3: Hybrid (Transcript + Edits + Comments)

Often someone takes the auto-generated transcript and adds context, corrections, or commentary.

**Structure**:
```
[Auto-generated transcript text]

[Corrected speaker name if wrong]
[Timestamp]
[Edited or corrected quote]

[Editorial comment: "This is a decision"]
[Editorial comment: "Sarah to own this by April 18"]
```

**Example**:
```
Sarah Chen
00:15
[CORRECTED: "accessibility audit" not "access ability audit"]
We need to prioritize the accessibility audit for the next release.

[COMMENT: Decision approved - consensus]

Marcus Rodriguez
01:02
Agreed. How long do you think it will take?

[COMMENT: Action item - Sarah to provide estimate or contact contractor]

Sarah Chen
01:23
Based on the last time we did an audit, probably two weeks with one contractor.

[COMMENT: 2-week timeline confirmed]

[Editorial note: This assumes contractor availability. Sarah should verify.]
```

**Characteristics**:
- Starts with auto-generated transcript structure
- Inline corrections or strikethroughs for accuracy
- Bracketed comments (often in ALL CAPS: [ACTION], [DECISION], [BLOCKER])
- May include risk notes or assumptions
- Often more reliable than purely auto-generated (human verification applied)

**Extraction Notes**:
- Use corrected speaker names and quotes (not the original auto-generated text)
- Respect editorial comments if they explicitly tag action items or decisions
- Note editorial caveats (e.g., "assumes contractor availability" → potential blocker)

---

## Speaker Attribution Patterns

### Direct Attribution (Clearest)

**Pattern**: Speaker name on its own line, message follows.

```
Sarah Chen
We need to prioritize the accessibility audit.
```

**Extraction**: Sarah is the speaker making a statement about the accessibility audit.

---

### Quoted Attribution

**Pattern**: "Speaker name said / noted / mentioned / agreed that..."

```
In the meeting, Sarah said we should prioritize the accessibility audit.
```

**Extraction**: Sarah is the speaker. Verb ("said") indicates type of statement (neutral), not interpretation.

**Verb Types**:
- Neutral: "said", "stated", "mentioned", "noted"
- Positive/Agreement: "agreed", "confirmed", "supported", "advocated for"
- Negative/Disagreement: "disagreed", "cautioned", "raised concerns about"
- Uncertain: "suggested", "wondered about", "asked if"

---

### Implied Attribution (Indirect)

**Pattern**: Context + pronoun + action, no explicit speaker.

```
The team discussed performance optimization and agreed to focus on indexing.
```

**Extraction Challenge**: Who is "the team"? (Multiple speakers) Who owns the decision? (Unclear—usually the meeting facilitator or the person who will implement.)

**Resolution**:
- If facilitator is known, attribute decision to them
- If multiple people present, check transcript for who specifically advocated for the decision
- Mark as [TBD] if ambiguous; ask for clarification

---

### Absent Attribution (Unclear)

**Pattern**: Statement with no clear speaker.

```
It's important to note that we're waiting on the database team for approval.
```

**Extraction Challenge**: Who said this? Was it a decision or an observation?

**Resolution**:
- Mark as [BLOCKER] or [DECISION] based on context, but tag speaker as [TBD]
- Ask for clarification in Step 6 (confirmation step)

---

### Multiple Speakers, One Statement

**Pattern**: Multiple people make related statements that form a decision.

```
Sarah Chen
00:15
I think we should prioritize the accessibility audit.

Marcus Rodriguez
01:02
Yeah, I agree. That's the right call.

Priya Sharma
01:45
Agreed. I can start next week.
```

**Extraction**:
- [DECISION] Accessibility audit is top priority (Consensus: Sarah, Marcus, Priya)
- [ACTION] Priya to start implementation (Due: next week)
- Note: Unanimous agreement (all three speakers align)

---

### Speaker Name Variations

Teams transcripts may contain variations of the same person's name:

- "Sarah Chen" vs "Sarah" vs "SC" vs "Sarah (Product)" vs "sarah.chen@enghub.com"

**Extraction Rule**: When you see a name variation, resolve it to one canonical form (e.g., "Sarah Chen") before creating EngHub tickets.

**Process**:
1. Collect all speaker names from transcript
2. Ask: "Are these the same people?" (show variations)
3. User confirms canonical names
4. Re-parse transcript using canonical names
5. Look up EngHub account IDs for canonical names

---

## Action Item Detection Patterns

Action items are commitments to do work. They have three parts:

1. **Owner** (who will do it)
2. **Verb** (what will they do)
3. **Deadline** (when)

### Pattern 1: Direct Commitment (Clearest)

**Form**: `[Name] will [verb] [object] by [deadline]`

```
Sarah will investigate the performance regression by Friday.
```

**Extracts As**:
- Owner: Sarah
- Action: Investigate the performance regression
- Deadline: Next Friday
- Confidence: High

**Variations**:
- "Sarah will investigate..." (future tense)
- "Sarah to investigate..." (implicit future)
- "Sarah, please investigate..." (imperative with name)

---

### Pattern 2: Explicit Assignment with Verbal Confirmation

**Form**: `[Assigner] asks [Owner] to [verb], and [Owner] confirms`

```
Marcus: Can you investigate the performance regression, Sarah?
Sarah: Yeah, I'll look into it this week.
```

**Extracts As**:
- Owner: Sarah
- Action: Investigate the performance regression
- Deadline: This week (by Friday of current week)
- Confidence: High (Sarah explicitly committed)

---

### Pattern 3: Implied Ownership (From Domain Expertise)

**Form**: `We need [thing] done. [Person with relevant role] would normally do this.`

```
We need to set up a performance baseline. The infra team should take this.
```

**Extracts As**:
- Owner: [Infra team lead - ask for name]
- Action: Set up a performance baseline
- Deadline: [Missing - flag for clarification]
- Confidence: Medium (assignment implied but not explicit)

**Note**: Don't assume the right owner. Ask for confirmation.

---

### Pattern 4: Vague or Distributed Ownership

**Form**: `We should [verb] [object]` or `Someone needs to [verb]`

```
We should create a performance optimization plan.
```

**Extracts As**:
- Owner: [TBD - ask who is leading this]
- Action: Create a performance optimization plan
- Deadline: [Missing]
- Confidence: Low

**Resolution**: Ask for clarification. If truly distributed, create one ticket and ask who is coordinating.

---

### Pattern 5: Time-Bound Commitment (With Explicit Deadline)

**Form**: `[Name] will have [deliverable] ready by [deadline]`

```
Priya will have the profiling results ready by Wednesday.
```

**Extracts As**:
- Owner: Priya
- Action: Run performance profiling and produce results
- Deadline: Wednesday (specific date)
- Confidence: High

---

### Pattern 6: Concurrent Action (Multiple People, Same Goal)

**Form**: `[Name1] will [verb1], and [Name2] will [verb2]` (same goal)

```
Marcus will design the new index structure, and Sarah will run the performance tests.
```

**Extracts As**:
- [ACTION] Marcus to design new index structure (due [date])
- [ACTION] Sarah to run performance tests (due [date])
- Context: Both are part of the performance optimization project

**Note**: Create separate tickets but link them.

---

## Decision Detection Patterns

Decisions are agreements on direction, approach, or priority. They often include a rationale.

### Pattern 1: Explicit Decision Statement

**Form**: `We decided to [direction]` or `We agreed on [approach]`

```
We decided to prioritize the accessibility audit for the next release.
```

**Extracts As**:
- [DECISION] Accessibility audit is a priority for next release
- Consensus level: [Infer from context - if no objections, unanimous]
- Rationale: [Ask if not explicit]

---

### Pattern 2: Decision with Rationale

**Form**: `We're going with [choice] because [reason]`

```
We're going with approach B (full redesign) because the current design is outdated and approach B gives us better performance.
```

**Extracts As**:
- [DECISION] Mobile redesign approach B (full redesign) approved
- Rationale: Current design outdated; better performance potential
- Alternatives considered: Approach A (incremental updates) - rejected
- Consensus level: [Infer]

---

### Pattern 3: Consensus Affirmation

**Form**: Speaker 1 proposes, Speaker 2+ agree/confirm

```
Sarah: We should prioritize the accessibility audit.
Marcus: Yeah, agreed.
Priya: Good idea. Let's do it.
```

**Extracts As**:
- [DECISION] Accessibility audit is a priority
- Consensus: Unanimous (all three speakers agree)
- Advocate: Sarah (first to propose)

**Consensus Levels**:
- **Unanimous**: All speakers agree, no objections
- **Majority**: Most agree, some reservation but not blocking
- **Tentative**: Agreement with significant caveats or conditions
- **Contested**: Disagreement or unresolved tension

---

### Pattern 4: Decision with Condition

**Form**: `We'll do [A], but only if [B] happens first` or `We'll move forward with [A], conditional on [B]`

```
We approved the mobile redesign approach, but only if the design system team finishes 
the component specs by April 18.
```

**Extracts As**:
- [DECISION] Mobile redesign approach approved (conditional)
- Condition: Design system component specs must be finalized by April 18
- Related blocker: Design system team must deliver specs
- Confidence: Conditional (will become firm once condition is met)

---

### Pattern 5: Decision by Default (No Objection)

**Form**: `Does anyone object to [proposal]?` [silence] `OK, let's do it.`

```
Should we move forward with the Q2 roadmap as drafted? [No one objects.] 
Alright, let's go with it.
```

**Extracts As**:
- [DECISION] Q2 roadmap approved
- Consensus: Default agreement (no objections noted)
- Confidence: Medium (not enthusiastic endorsement, but no blocking concerns)

---

### Pattern 6: Deferred Decision

**Form**: `Let's revisit this [timeframe]` or `We'll decide [when]`

```
We don't have enough information to decide on the vendor yet. Let's revisit next week.
```

**Extracts As**:
- [ACTION] Revisit vendor decision (owner: facilitator or person tasked to prepare info, due next week)
- Not yet: [DECISION] (pending more information)

---

## Blocker Detection Patterns

Blockers are external dependencies or obstacles that prevent work from proceeding. They have:

1. **What is blocking** (the dependency)
2. **What is blocked** (the work that can't proceed)
3. **Who owns the blocker** (who can resolve it)
4. **When it will unblock** (timeline)

### Pattern 1: Explicit Blocker

**Form**: `We're blocked by [dependency]` or `We can't proceed until [condition]`

```
We're blocked by the design system team finalizing the component specs.
```

**Extracts As**:
- [BLOCKER] Design system team must finalize component specs
- Blocks: Any work depending on those specs
- Owner: Design system team (external)
- When unblocked: [TBD - ask for timeline]

---

### Pattern 2: Waiting On External Team

**Form**: `We're waiting on [team/person] to [action]`

```
We're waiting on the database team to optimize the query for high-cardinality joins.
```

**Extracts As**:
- [BLOCKER] Database team must optimize query
- Blocks: Performance optimization work
- Owner: Database team (external)
- When unblocked: [When database team completes optimization]

---

### Pattern 3: Missing Information / Prerequisites

**Form**: `We need [information/data/approval] before we can [proceed]`

```
We need the ETL pipeline to finish running before we can analyze the performance impact.
```

**Extracts As**:
- [BLOCKER] ETL pipeline must complete
- Blocks: Performance impact analysis
- Owner: Data engineering team
- Estimated unblock time: [Ask - ETL SLA?]

---

### Pattern 4: Resource Constraint

**Form**: `[Person/Team] is the only one who can [do thing], and they're [not available / overallocated]`

```
Only Sarah knows the legacy codebase well enough to refactor the auth module. 
She's fully allocated through end of Q2.
```

**Extracts As**:
- [BLOCKER] Sarah is overallocated (no capacity for auth refactor)
- Blocks: Auth module refactor work
- Options: (1) De-allocate Sarah from other work, (2) Find another person to learn the codebase, (3) Defer the refactor
- Action: Discuss with Sarah's manager

---

### Pattern 5: Approval Dependency

**Form**: `We need [someone's] approval before we can [proceed]`

```
We need the legal team's approval on the data sharing agreement before we can 
close the partnership deal.
```

**Extracts As**:
- [BLOCKER] Legal team must approve data sharing agreement
- Blocks: Partnership deal closure
- Owner: Legal team
- Action: Send agreement to legal for review (who does this? ask)

---

### Pattern 6: Conditional Blocker (Unblocks When Condition Met)

**Form**: `We can't [proceed] until [person/team] [delivers something]`

```
We can't start the backend API design until the product team finalizes the requirements.
```

**Extracts As**:
- [BLOCKER] Product team must finalize requirements
- Blocks: Backend API design work
- Related action: Product team to finalize requirements (with deadline)
- Unblocks when: Requirements approved
- Related tickets: [DECISION] on requirements, [ACTION] for product team

---

## Follow-Up & Deadline Patterns

Deadlines can be explicit or inferred from context. The system flags vague deadlines for clarification.

### Pattern 1: Explicit Date

**Form**: `by [specific date]` or `on [day of week]`

```
We need the performance report by April 21.
Sarah will have the contractor list ready by Friday.
```

**Extracts As**:
- Deadline: April 21, 2026 or Next Friday (specific date)
- Confidence: High

---

### Pattern 2: Relative Timeline

**Form**: `by [relative time]` or `in [duration]`

```
We need this done by end of week.
Priya will run the profiling in the next 3 days.
```

**Extracts As**:
- Deadline: April 18, 2026 (end of this week) or April 17, 2026 (3 days from April 14)
- Confidence: High (requires knowing current date)

---

### Pattern 3: Sprint-Based Deadline

**Form**: `by [sprint]` or `before [sprint]` or `in the next sprint`

```
We'll have the feature ready by the end of Q2.
Before the Q2 sprint, we need to finalize requirements.
```

**Extracts As**:
- Deadline: [Look up Q2 end date or Q2 sprint end date in EngHub]
- Confidence: Medium (requires project calendar data)

---

### Pattern 4: Event-Based Deadline

**Form**: `before [event]` or `by the time [thing happens]`

```
We need to finalize the roadmap before the all-hands meeting.
```

**Extracts As**:
- Deadline: [Ask - when is the all-hands?]
- Confidence: Low (requires knowing event date)

---

### Pattern 5: Vague / No Deadline

**Form**: `We should [do thing]` with no time frame, or `eventually`, `when we have time`

```
We should improve our documentation.
Let's revisit this eventually.
```

**Extracts As**:
- Deadline: NONE / BACKLOG
- Confidence: Low (vague intent)
- Action: Flag in Step 6 for clarification. Ask: "When should this be addressed? Next sprint? Next quarter? No timeline needed?"

---

### Pattern 6: Urgent / ASAP

**Form**: `ASAP`, `urgent`, `immediately`, `by EOD`, `by tomorrow`

```
We need to fix this bug ASAP.
This needs to go out by EOD.
```

**Extracts As**:
- Deadline: Today (if EOD) or Next business day (if ASAP), or specific time if mentioned
- Confidence: High
- Context: Usually indicates production issue or customer-facing impact

---

### Pattern 7: Recurring / Ongoing

**Form**: `weekly`, `every X days`, `each sprint`, `monthly`

```
We'll have weekly syncs to track progress.
Let's do a monthly business review.
```

**Extracts As**:
- First deadline: Next occurrence (e.g., next Monday for weekly)
- Type: Recurring action item
- Action: Create an EngHub ticket for the first occurrence and note that this is recurring; consider creating an EngHub Docs "standing meetings" doc

---

## Special Patterns

### At-Mentions (@SomeoneElse)

When a transcript includes `@person_name`, the system treats it as an assignment signal:

```
@Marcus, can you run the performance profiling?
```

**Extracts As**:
- Owner: Marcus
- Action: Run performance profiling
- Deadline: [Infer from context or ask]

**Flag**: If multiple people are @-mentioned for the same action, ask for clarification (is this a team task or should it be split?).

---

### Reaction Markers

Teams reactions (thumbs up, fire, lol, etc.) sometimes appear in transcripts:

```
Sarah: Let's go with approach B.
[Reaction: thumbs_up from Marcus]
[Reaction: thumbs_up from Priya]
```

**Usage**:
- Gauge consensus (number of thumbs up / fire reactions = endorsement level)
- Ignore emoji in extraction (not substantive)
- Document in decision recap if helpful ("Decision approved with consensus: 3 thumbs up")

---

### Multiple Meetings in One Transcript

Occasionally a transcript will reference other meetings or decisions made elsewhere:

```
As we discussed last week in the steering committee, the budget is fixed.
```

**Action**:
- Ask: "Are there other meetings you want to link?" 
- Option: Search EngHub for related decisions/issues from steering committee
- Link those issues in the recap

---

### Speaker Errors (Mis-Attribution)

Sometimes Teams' transcription attributes a quote to the wrong person:

```
Sarah Chen
00:15
Marcus says the performance regression is critical.

[ERROR: This is actually Marcus speaking, not Sarah quoting.]
```

**Detection**:
- Speaker says something in third person about themselves (red flag)
- Grammatical mismatch ("Marcus says we should prioritize his ticket" - weird)
- User provides correction in editorial notes

**Action**:
- Correct the speaker name
- Re-extract with corrected attribution

---

### Technical Jargon & Domain Terms

Teams' speech-to-text often misrecognizes technical terms:

```
ACTUAL: "We need to optimize the query for high-cardinality joins."
TRANSCRIBED: "We need to optimize the query for high car reality joins."
```

**Action**:
- User corrects in the hybrid-format transcript
- System uses corrected version for extraction

---

## Using This Reference in Practice

### Step 1: Identify Transcript Format

When the user provides a transcript, scan it to determine the format:
- Auto-generated (timestamps + clear speakers) → High confidence extraction
- Manual notes (narrative) → Medium confidence, ask clarifying questions
- Hybrid (mixed) → Use corrected/commented sections, ignore errors

### Step 2: Normalize Speaker Names

Before extraction, collect all unique speaker names and variations. Ask user to confirm canonical names.

### Step 3: Apply Patterns

Use the patterns in this reference to identify:
- **Action items**: Direct commitments with owner + deadline
- **Decisions**: Explicit agreements or consensus signals
- **Blockers**: External dependencies or obstacles
- **Follow-ups**: Deadlines and event-based triggers

### Step 4: Flag Low-Confidence Extractions

If you match a pattern with medium or low confidence (e.g., vague deadline, implied owner, distributed responsibility), mark it as [TBD] and flag for Step 6 confirmation.

### Step 5: Present for User Confirmation

In Step 6, show the extracted items with their source quotes. User edits, confirms, or rejects. This is when you catch extraction errors and fill in missing info.

---

## Version History

- **v1.0** (April 14, 2026): Initial reference document. Covers all major Teams transcript formats and extraction patterns.
