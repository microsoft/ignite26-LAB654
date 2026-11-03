---
name: sharepoint-to-backlog
description: "Point this skill at a SharePoint site, document library, or specific document. It discovers specs and requirements documents, then auto-organizes them into structured Jira epics with user stories, tasks, and acceptance criteria. Single document or batch processing across a library."
---

# SharePoint to Backlog

Point this skill at a SharePoint site, document library, or specific document. It discovers specs, requirements, and project plan documents, then auto-organizes them into structured Jira epics with user stories, tasks, and acceptance criteria. Process one document at a time, or batch multiple documents from the same site into related epics with unified tracking.

## Keywords

sharepoint, word, onedrive, requirements, backlog, epic, stories, jira, specs, requirements-to-backlog, document-parsing, specification, user-stories, acceptance-criteria

## Overview

Enterprises write technical specifications, product requirements, and design documents across SharePoint sites and document libraries. Engineers track work in Jira. This skill bridges the gap by discovering and organizing work at scale.

**The Problem:** Requirements are scattered across SharePoint sites, document libraries, and team drives. Some live in Jira, some in Word docs, some in pages. Information gets duplicated, falls out of sync, or is manually retyped—introducing errors and eating cycles.

**The Solution:** Point this skill at a SharePoint site, document library, or specific document. It discovers specs, requirements, and project plan documents, lets you select which ones to process, then auto-generates a structured Jira hierarchy: an Epic for each major document, with child Stories and Tasks, full descriptions, acceptance criteria, and proper issue linking. Process one document at a time, or batch multiple documents from the same site into related epics.

**Use Case Scenarios:**
- A product manager writes a 10-page feature spec in Word; you want it in Jira without manual data entry
- A SharePoint document lists 20 acceptance criteria for a release; you need them as child tasks under a story
- A design document in OneDrive describes a workflow with 5 main steps; you want each as a task under an epic
- An RFP response document outlines deliverables; you want them tracked as a Jira roadmap with dependencies

## Workflow

### Step 1: Accept SharePoint Source

The skill accepts input from three sources:

1. **SharePoint Site URL** (e.g., `https://company.sharepoint.com/sites/MyTeam`)
   - The skill browses the site, identifies document libraries, and lists all discoverable specs, requirements, and project plan documents.
   
2. **Document Library URL** (e.g., `https://company.sharepoint.com/sites/MyTeam/Shared Documents`)
   - The skill lists all documents in the library and identifies those that look like specs or requirements.
   
3. **Specific Document URL** (e.g., `https://company.sharepoint.com/sites/MyTeam/Shared Documents/Feature Spec - Authentication.docx`)
   - The skill downloads and processes the document directly.

### Step 2: Discovery and Selection

If a site or library URL is provided, the skill:

1. **Browses the SharePoint structure** to locate:
   - Word documents (.docx) with common spec/requirements keywords in the filename or metadata
   - SharePoint pages marked with content types like "Specification", "Requirements", "Project Plan"
   - Recently modified documents that suggest active planning work
   
2. **Ranks and presents discovered documents** with:
   - Document name and type (Word, Page, etc.)
   - Last modified date and owner
   - A confidence score indicating likelihood it's a specification (based on filename patterns, metadata, file size)
   
3. **Allows selection**:
   - "Process document X individually"
   - "Process documents X, Y, Z as a batch" (creates related epics linked by a common parent or label)
   - "Skip and provide a document URL manually"

### Step 3: Analyze Document Structure

The skill examines each selected document for:

1. **Hierarchical structure**: Heading levels (H1, H2, H3 → Epic, Story, Task)
2. **Requirement patterns**: "Shall", "Must", "Will" statements; numbered lists; matrices
3. **Story format**: Standard "As a [user], I want..., so that..." or "As a [role]..."
4. **Acceptance criteria blocks**: Lines starting with "Given/When/Then" (BDD format) or standalone criteria lists
5. **Task markers**: Numbered lists, sub-bullets, action items
6. **Table structures**: If a doc has a requirements matrix (ID | Requirement | Status | Owner), parse as individual stories or tasks

See **Document Structure Patterns** section for detailed parsing rules.

### Step 4: Ask for Target Jira Project

The skill requests:
1. **Project Key** (e.g., "MYPROJ")
2. **Available Issue Types** (Story, Task, Bug, Subtask, etc.)—queries Jira to confirm
3. **Parent Issue** (optional): If attaching to an existing Epic, Feature, or Initiative
4. **Default Assignee** (optional): Who should own stories by default?
5. **Labels** (optional): Tags to add to all created issues (e.g., "from-sharepoint", "feature-x")

### Step 5: Structure Breakdown

The skill proposes a hierarchy for each document:

```
Epic: [Document title / main goal]
├─ Story: [Section 1 heading]
│  ├─ Task: [Subsection or numbered item 1]
│  ├─ Task: [Subsection or numbered item 2]
│  └─ Acceptance Criteria: [Requirement statements parsed from text]
├─ Story: [Section 2 heading]
│  ├─ Task: [Sub-item A]
│  ├─ Task: [Sub-item B]
│  └─ Acceptance Criteria: [Parsed from requirement lines]
└─ Story: [Section 3 heading]
   └─ Task: [Single deliverable item]
```

**Structural Rules:**
- **Epic title** comes from the document title or the first H1 heading
- **Stories** map to H2 headings or major feature sections
- **Tasks** map to H3 headings, numbered sub-items, or action items
- **Acceptance Criteria** extracted from requirement statements ("shall", "must", "will", "should") or explicit AC lists
- **Description fields** populated with surrounding context from the doc
- **Links** set up so child issues properly reference the parent

**For Batch Mode:**
- If processing multiple documents, each becomes a separate Epic
- All epics are linked with a common label (e.g., "batch-2026-04-14") or parent Feature/Initiative (if available)
- The skill offers to create a parent Feature or Program Epic to unify all related documents

### Step 6: Present Proposed Hierarchy for Review

Before creating anything, the skill displays a **tree view** of the proposed structure:

```
Epic: Feature XYZ - Multi-Tenant Onboarding
  Story: User Registration & Auth [3 tasks, 5 ACs]
    Task: Implement SAML 2.0 integration
      AC: System shall support SAML authentication
      AC: System must validate SAML assertions
      AC: Login flow shall complete within 3 seconds
    Task: Build password reset flow
    Task: Add MFA support
  Story: Tenant Configuration [4 tasks, 6 ACs]
  Story: Data Migration [2 tasks, 3 ACs]
```

The user reviews and can:
- **Confirm**: Proceed to create in Jira
- **Modify**: Ask to merge/split stories, rename tasks, adjust AC grouping
- **Cancel**: Start over or adjust the source document

### Step 7: Create Epics, Then Child Stories/Tasks

Once confirmed, the skill:

1. **Creates each Epic** in the target Jira project with:
   - Title from the document
   - Description with a link back to the SharePoint source
   - Labels and other metadata (including batch identifier if in batch mode)
   
2. **Creates each Story** with:
   - Title from the section heading
   - Description populated with the section's overview text
   - Status set to "To Do" or as configured
   - Linked to its parent Epic

3. **Creates each Task** with:
   - Title from the list item or sub-heading
   - Description with supporting context
   - Linked to its parent Story
   - Type: "Task" or "Subtask" (configurable per project)

4. **Adds Acceptance Criteria** to relevant stories/tasks as:
   - Description field additions, OR
   - Child "Acceptance Criteria" issues (if the project supports custom issue types), OR
   - Comments in a structured format

5. **Sets up issue links**:
   - Epic → Story: "contains" or "is epic of"
   - Story → Task: "is parent of"
   - Task → Task: "is related to" (if dependencies detected from the original doc)
   - In batch mode: Parent Epic/Feature → Child Epics (each document)

**Creation Sequence:**
- Parent Epic created first (if batch mode)
- Each document's Epic is created and returns an issue key (e.g., PROJ-123)
- Stories are created with parent link to their Epic
- Tasks are created with parent link to their story
- All links are verified and completed before returning results

### Step 8: Summary with Links and Hierarchy Visualization

Once complete, the skill outputs:

1. **Summary Table**:
   ```
   Created:
   - 1 Epic: PROJ-123 Feature XYZ - Multi-Tenant Onboarding
   - 3 Stories: PROJ-124, PROJ-125, PROJ-126
   - 9 Tasks: PROJ-127 through PROJ-135
   - 14 Acceptance Criteria: Embedded in descriptions
   ```

2. **Hierarchy Visualization**:
   ```
   PROJ-123 (Epic) https://jira.atlassian.net/browse/PROJ-123
   ├─ PROJ-124 (Story) https://jira.atlassian.net/browse/PROJ-124
   │  ├─ PROJ-127 (Task)
   │  ├─ PROJ-128 (Task)
   │  └─ PROJ-129 (Task)
   ├─ PROJ-125 (Story)
   │  ├─ PROJ-130 (Task)
   │  └─ PROJ-131 (Task)
   └─ PROJ-126 (Story)
      ├─ PROJ-132 (Task)
   ```

3. **Next Steps Guidance**:
   - "The Epic is ready for planning. Assign stories to sprints."
   - "5 tasks are missing assignees—review and assign."
   - "Link any related work from other projects using the Jira link panel."

## Document Structure Patterns

How to parse Word/SharePoint formatting:

### Heading Hierarchy

| Markdown | Word Style | SharePoint | Maps To | Example |
|----------|-----------|-----------|---------|---------|
| H1 / # | Heading 1 | Header 1 | Epic | Feature: Multi-Tenant Onboarding |
| H2 / ## | Heading 2 | Header 2 | Story | User Registration & Auth |
| H3 / ### | Heading 3 | Header 3 | Task | Implement SAML 2.0 |
| H4 / #### | Heading 4 | Header 4 | Task / Subtask | API Endpoint Design |
| Normal | Body Text | Body Text | Context / Description | Supporting paragraph |

**Rule:** If a document has clear H1→H2→H3 structure, use that directly. If all headings are H2, infer the H1 from the document filename or first paragraph.

### Requirement Statements

The skill looks for requirement language:

```
"The system shall support SAML 2.0 authentication."
"Users must receive email confirmation within 60 seconds."
"The API will handle up to 10,000 concurrent connections."
"All data transfers should be encrypted with AES-256."
```

**Parsing Rule:** Any line starting with "shall", "must", "will", "should", or "must not" is marked as an Acceptance Criterion. Group them under the closest parent heading.

### Numbered and Bulleted Lists

```
## User Registration Flow

1. Display login page
   a. Show email field
   b. Show password field
   c. Add "Forgot Password" link
2. Validate email format
3. Hash password with bcrypt
   - Use bcrypt version 2b or later
   - Set cost factor to 12
4. Store in database
```

**Parsing Rule:**
- Top-level numbered items (1, 2, 3...) become Tasks
- Sub-items (a, b, c or bullet points under a number) become sub-tasks or acceptance criteria
- Indented sub-bullets become context in the task description

### Requirement Tables

If the document includes a requirement matrix:

```
| ID | Requirement | Priority | Owner |
|----|-------------|----------|-------|
| REQ-1 | Support SAML 2.0 | High | Auth Team |
| REQ-2 | Email validation | High | API Team |
| REQ-3 | Rate limiting | Medium | Infra Team |
```

**Parsing Rule:** Each row becomes a Story or Task, with ID as a label, requirement as the title, and priority/owner as custom fields (if the Jira project supports them).

### BDD Acceptance Criteria

```
## User Registration

Scenario: New user signs up with email
  Given: User is on the login page
  When: User enters email and password
  Then: System sends confirmation email
  And: User is redirected to email verification page
```

**Parsing Rule:** Extract the entire scenario as one acceptance criterion, or split Given/When/Then into sub-criteria. Keep the structure intact in the task description.

### Implicit Story Format

Some docs already use story format:

```
As a system administrator, I want to configure SAML providers, 
so that enterprise customers can use their identity provider.

Acceptance Criteria:
- Admin can upload SAML metadata file
- System validates metadata before saving
- Login page shows SAML provider button after configuration
```

**Parsing Rule:** If the text contains "As a [role]...", treat it as a complete story definition. Extract the user story line as the title and the AC block as explicit acceptance criteria.

## Handling Edge Cases

### No Clear Hierarchy

**Problem:** The document is all plain text with no headings.

**Solution:**
1. Ask the user: "Is each numbered item a separate Story, or are they all tasks under one Story?"
2. Or: "Do you want me to infer stories from paragraph breaks?"
3. Offer to create a single Epic with all items as Tasks, then let the user re-organize in Jira

### Mixed Heading Levels

**Problem:** Document jumps from H1 to H4, skipping H2 and H3.

**Solution:**
1. Treat H1 as Epic
2. Treat H4 as Stories (next defined level below H1)
3. Treat any plain text under H4 as Tasks
4. Flag this in the review step so the user can approve the inferred structure

### Requirement Statements Without Clear Parent

**Problem:** "The system shall support SAML" appears in the overview, not under a specific story heading.

**Solution:**
1. Attach it as an AC to the Epic itself, OR
2. Create a standalone "System Requirements" story and attach it there, OR
3. Ask the user: "Should this be an Epic-level AC or a separate story?"

### Tables, Inline Formatting, Special Characters

**Problem:** The doc has tables, bold text, italics, or special characters.

**Solution:**
1. Strip formatting and extract plain text
2. Preserve table structure and convert rows to list items if needed
3. Handle Unicode correctly (accented characters, symbols)
4. For inline formatting (bold, italic), convert to plain text with context markers (e.g., `[bold: text]` or just strip)

### Very Long Descriptions

**Problem:** A single task description is 5,000 characters, exceeds Jira field limits.

**Solution:**
1. Truncate to the first 1,500 characters
2. Add "..." and note that full context is in the source document
3. Suggest linking back to the SharePoint page or Word doc in the Epic description

### Duplicate Content

**Problem:** The same requirement statement appears in multiple sections.

**Solution:**
1. Detect exact duplicates and warn the user: "This AC appears in sections X and Y—create once or keep both?"
2. Suggest deduplication or creating a single shared story with dependencies
3. Let the user decide

### Missing Jira Project Info

**Problem:** User doesn't provide a project key or the project doesn't exist.

**Solution:**
1. Query Jira for accessible projects: "Which project should I create the epic in? Here are your options: [list]"
2. Require explicit confirmation before proceeding
3. If no projects are available, return an error with instructions to create/request access

## Tips for High-Quality Results

### Before You Start

1. **Clean up the source document**. Fix typos, inconsistent capitalization, and trailing whitespace.
2. **Use consistent heading levels**. If the doc is all H3s, massage it into a proper hierarchy (H1 → H2 → H3) before pasting.
3. **Remove metadata**. Strip out "Last Modified: ...", "Author: ...", table of contents, page breaks, and revision history.
4. **Explicit is better than implicit**. If a section is a "Story", say so. If items are "Tasks", label them. The skill will infer, but explicit beats inferred.

### Structuring Acceptance Criteria

**Good AC:**
```
Acceptance Criteria:
- System shall validate email format before submission
- User must receive confirmation email within 60 seconds
- Failed login attempts must be rate-limited to 5 per minute
```

**Better AC:**
```
Acceptance Criteria:
Given: User enters an invalid email
When: User clicks "Sign Up"
Then: Form shows error message
And: No email is sent

Given: User enters a valid email
When: User clicks "Sign Up"
Then: Confirmation email is sent within 60 seconds
And: User sees "Check your email" message
```

**Worst AC:**
```
The system needs to be good at email validation and stuff. Make sure it's fast and doesn't send too many emails.
```

### Story Titles

**Good:** "User Registration with Email Verification"
**Good:** "As a new user, I want to verify my email, so that I can activate my account"
**Bad:** "Authentication Stuff"
**Bad:** "Implement the thing from section 3"

The skill will extract good titles from well-written docs. If the doc has weak titles, ask the user to refine them during the review step.

### Task Granularity

**Too small:** "Type the letter 'S' in the SAML field"
**Too big:** "Implement entire authentication system"
**Good:** "Implement SAML 2.0 metadata parsing"
**Good:** "Add email validation with regex"

If the skill detects very small or very large tasks, it will flag them during the review step.

### Linking to Source Documents

Always include a link back to the source SharePoint page or Word doc in the Epic description:

```
Source: [Feature XYZ - Spec](https://sharepoint.company.com/sites/product/Feature%20XYZ%20Spec)
Last Updated: 2026-04-14
Owned by: Product Team
```

This keeps traceability and makes it easy to reference the original spec if questions arise.

## When NOT to Use This Skill

This skill is designed for **structured documents with clear requirements**. It may not be ideal for:

1. **Loosely written narrative documents** without hierarchy or clear sections. (Consider manually creating the first Epic, then using this for the details.)

2. **Design documents with heavy visual content** (wireframes, mocks, diagrams). The skill parses text, not images. (Extract text descriptions and use those as input.)

3. **Unstructured brainstorm notes or meeting transcripts**. The skill assumes requirements are written in a structured format. (Transcribe and organize first.)

4. **Single-line requirements or lists with no context**. (Add supporting context—why each task matters, acceptance criteria, etc.—before using the skill.)

5. **Jira is not your issue tracker** or you use a different tool. (This skill is Jira-specific. Adapt for Linear, Azure DevOps, etc. with manual translation.)

6. **The document changes frequently** and you want real-time sync. (This skill is one-time conversion. For continuous sync, consider a custom Jira plugin or Zapier automation.)

## Examples

See [`references/examples-and-reference.md`](references/examples-and-reference.md) for this section (relocated to keep SKILL.md within the 20,000-character limit).

## Quick Reference

See [`references/examples-and-reference.md`](references/examples-and-reference.md) for this section (relocated to keep SKILL.md within the 20,000-character limit).

## Architecture Notes for Implementers

See [`references/examples-and-reference.md`](references/examples-and-reference.md) for this section (relocated to keep SKILL.md within the 20,000-character limit).
