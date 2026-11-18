# Requirements Parsing Patterns

Reference guide for discovering requirements documents in SharePoint, and for detecting and extracting requirement statements, acceptance criteria, user stories, and structural patterns from Word documents and SharePoint pages.

## SharePoint Document Discovery

When browsing a SharePoint site or library to identify specs and requirements documents, use these signals:

### Filename Patterns (High Confidence)
Documents matching these patterns are likely specifications or requirements:
- `*spec*` (e.g., "Feature Spec", "Technical Specification")
- `*requirements*` (e.g., "Requirements Doc", "Project Requirements")
- `*design*` (e.g., "Design Spec", "System Design")
- `*rfc*` (e.g., "RFC - Feature X")
- `*proposal*` (e.g., "Product Proposal")
- `*roadmap*` (e.g., "Q3 Roadmap")
- `*prd*` (e.g., "Product Requirements Document")
- `*brd*` (e.g., "Business Requirements")
- `*sow*` (e.g., "Statement of Work")
- `*srs*` (e.g., "Software Requirements Specification")

### Content Type Markers
SharePoint pages and documents with these metadata tags are likely specifications:
- Content Type: "Specification", "Requirements", "Project Plan", "Design Document"
- Tags: "spec", "requirements", "planning", "design", "architecture"
- Category: "Product", "Engineering", "Planning"

### File Metadata Signals
- File size > 10KB (longer documents are more likely specs than notes)
- Recently modified (within last 30 days suggests active work)
- Owner is a PM, architect, product manager, or engineering lead
- Document properties include "Version" field (indicates formal spec)
- Document properties include "Status" field with values like "Draft", "In Review", "Approved"

### Document Structure Signals (Content-based)
After downloading a document, these structural patterns indicate it's a specification:
- Starts with a title + version number (e.g., "Feature Spec v2.1")
- Contains a table of contents or outline
- Has numbered sections with headings like "Overview", "Requirements", "Acceptance Criteria"
- Contains requirement matrices or tables with columns like "ID", "Requirement", "Priority", "Owner"
- Uses hierarchical heading structure (H1, H2, H3 clearly defined)

### Confidence Score Calculation (for implementers)
When ranking discovered documents:
```
confidence = 0
if filename matches spec_keywords: confidence += 0.3
if metadata content_type matches spec_types: confidence += 0.2
if file_size > 10KB: confidence += 0.1
if recently_modified (within 30 days): confidence += 0.1
if owner_is_pm_or_lead: confidence += 0.1
if document_has_version_field: confidence += 0.1
if document_has_status_field: confidence += 0.1

if confidence >= 0.5: rank as "Likely Spec"
elif confidence >= 0.3: rank as "Possible Spec"
else: rank as "Unlikely"
```

Rank all discovered documents by confidence score, with "Likely Spec" documents at the top.

---

## Requirement Language Patterns

### Mandatory Requirements (Highest Priority)

These create hard constraints and must be implemented exactly.

**Pattern: "shall"**
```
The system shall support SAML 2.0 authentication.
All API responses shall include rate-limit headers.
Users shall not be able to delete archived records.
The application shall validate email format before submission.
```

**Pattern: "must"**
```
Passwords must be at least 12 characters long.
All data transfers must use TLS 1.2 or higher.
The API must return responses within 500ms.
Login failures must be logged with timestamp and IP address.
```

**Pattern: "must not"**
```
The system must not allow concurrent logins from the same account.
API keys must not be stored in plain text.
Users must not be able to export confidential data.
```

**Detection Rule:** Any sentence containing "shall", "must", or "must not" is a firm requirement. Extract as-is. Create an acceptance criterion.

**Regex Pattern (for implementers):**
```regex
^\s*(The\s+)?(system|user|api|application|[A-Z]\w+)\s+(shall|must|must\s+not)\s+.+\.?$
```

---

### Strong Requirements (High Priority)

These indicate what the system will do, with strong commitment.

**Pattern: "will"**
```
The system will send confirmation emails within 60 seconds.
Users will be able to customize their dashboard.
The API will support both JSON and XML formats.
The platform will scale to 100,000 concurrent users.
```

**Pattern: "is required to"**
```
The login flow is required to complete within 3 seconds.
The API is required to return paginated results.
User profiles are required to include a profile picture field.
```

**Detection Rule:** These are strong commitments, but slightly weaker than "shall"/"must". Treat as acceptance criteria, but may have more flexibility in implementation.

**Regex Pattern:**
```regex
^\s*(The\s+)?(system|user|api|application|[A-Z]\w+)\s+(will|is\s+required\s+to)\s+.+\.?$
```

---

### Medium Priority (Should)

These are highly desirable but negotiable. Deprioritize or mark as "future work" if needed.

**Pattern: "should"**
```
The system should support dark mode.
Users should be able to export data in CSV format.
Error messages should be written in plain language.
The API should include webhook support for real-time updates.
```

**Pattern: "is expected to"**
```
The onboarding flow is expected to take less than 5 minutes.
User profiles are expected to be complete before access.
The dashboard is expected to display real-time metrics.
```

**Detection Rule:** Mark these as "nice to have" acceptance criteria. They are valuable but lower priority than "shall"/"must".

**Regex Pattern:**
```regex
^\s*(The\s+)?(system|user|api|application|[A-Z]\w+)\s+(should|is\s+expected\s+to)\s+.+\.?$
```

---

### Conditional Requirements

These specify behavior under specific conditions.

**Pattern: "if...then"**
```
If a user fails to log in 5 times, then lock the account for 15 minutes.
If the API response exceeds 5MB, then compress the payload.
If a file upload fails, then retry up to 3 times automatically.
```

**Pattern: "when...then"**
```
When a user clicks "Save", then all changes are persisted to the database.
When an API token expires, then return a 401 Unauthorized response.
When the system detects a duplicate entry, then ask the user to confirm.
```

**Detection Rule:** Extract the condition and the action as a single, detailed acceptance criterion.

---

## Acceptance Criteria Formats

### BDD Format (Gherkin)

Behavior-Driven Development format using Given/When/Then structure. Most structured and testable.

```gherkin
Feature: User Registration

Scenario: New user signs up with valid email
  Given: User is on the login page
  When: User enters a valid email and password
  Then: System sends a confirmation email
  And: User sees message "Check your email"
  And: User is redirected to the email verification page

Scenario: New user signs up with invalid email
  Given: User is on the login page
  When: User enters an invalid email format
  Then: Form displays error "Invalid email format"
  And: No confirmation email is sent
```

**Detection Rule:** Look for lines starting with "Given:", "When:", "Then:", "And:", or "Feature:", "Scenario:". These are explicit BDD-formatted criteria. Extract the entire scenario block as one criterion.

---

### Narrative Format

Written as a story or narrative description of expected behavior.

```
User Registration:
When a new user signs up, they enter their email and password. The system validates the email format and checks if it's already registered. If validation passes, the system sends a confirmation email. The user must click the link in the email to activate their account. If they don't click within 24 hours, the temporary registration expires and they must sign up again.
```

**Detection Rule:** Extract as a single, detailed AC. May span multiple sentences or paragraphs. Rewrite as bullet points or BDD for clarity.

---

### Bullet List Format

Short, bulleted acceptance criteria. Easy to read, but requires careful parsing to extract dependencies.

```
Acceptance Criteria:
- Email must be valid format (RFC 5322)
- Email must not already exist in the system
- Password must be at least 12 characters
- Password must include uppercase, lowercase, number, and symbol
- Confirmation email must be sent within 60 seconds
- Email link must expire after 24 hours
- User must see confirmation message after successful signup
```

**Detection Rule:** Look for lines starting with "-", "*", or "•" after an "Acceptance Criteria:" header. Each bullet is one criterion.

---

### Checklist Format

Checkboxes or numbered list indicating items to verify.

```
Acceptance Criteria:
[X] Email validation works for valid addresses
[ ] Email validation rejects invalid addresses
[X] Confirmation email is sent
[ ] Confirmation email includes clickable link
[ ] Link expires after 24 hours
[ ] User can resend confirmation email
```

**Detection Rule:** Extract each checkbox item as a criterion. "X" indicates done/verified; "[ ]" indicates pending.

---

### Performance / Non-Functional Requirements

Quantified criteria for performance, security, or infrastructure.

```
Acceptance Criteria:
- Login must complete within 3 seconds
- API must handle 10,000 requests per minute
- Error rate must be less than 0.1%
- Uptime must be 99.9% (SLA)
- Data must be encrypted at rest (AES-256)
- All passwords must be hashed with bcrypt (cost factor 12)
```

**Detection Rule:** Look for time values (seconds, milliseconds), throughput (req/sec), percentages, and security/encryption terms. These are non-functional requirements. Mark clearly as performance or security criteria.

---

## User Story Patterns

Standard user story format using the "As a [role], I want [action], so that [benefit]" template.

### Classic Format

```
As a new user, I want to register with my email address, 
so that I can access the platform.

Acceptance Criteria:
- Email must be validated before submission
- Confirmation email must be sent
- User must click email link to activate account
```

**Detection Rule:** Look for lines starting with "As a", "I want", "so that". Extract the entire story block (story + criteria) as one unit.

---

### Role Variations

```
As a system administrator, I want to configure SAML providers,
so that enterprise customers can use their identity provider.

As a product manager, I want to see real-time usage analytics,
so that I can identify trending features.

As an API consumer, I want to retry failed requests automatically,
so that I don't lose data due to temporary network issues.

As the system, I want to log all user actions,
so that compliance audits can be conducted.
```

**Detection Rule:** Role can be any persona: user, admin, developer, customer, etc. Extract and preserve the role in the story title.

---

### Implicit User Stories

Some documents describe user stories without the "As a..." template.

```
Feature: Dark Mode Support
Users want a dark mode option that automatically detects their OS preference. When a user enables dark mode, all UI elements should use the dark color palette. The preference should persist across sessions.
```

**Detection Rule:** Look for sentences describing user goals or desires (want, wish, expect, prefer). Rewrite as explicit user stories: "As a user, I want dark mode to detect my OS preference, so that I don't need to configure it manually."

---

## Structural Patterns

### Heading Hierarchy

How to infer story/task structure from document headings.

**Hierarchy Levels:**

```
H1: Feature Title or Epic Name
  H2: Major Feature Section (Story)
    H3: Sub-feature or Task (Task)
      H4: Implementation Detail (Sub-task or Context)
        H5: Low-level detail (Context/Description)
```

**Example:**

```markdown
# Dark Mode Support (Epic)

## Detect OS Dark Mode Preference (Story)

### Use prefers-color-scheme Media Query (Task)

#### Check browser compatibility
#### Store in local storage
#### Default to system preference

### Fallback for Unsupported Browsers

#### Load dark mode by default
#### Provide toggle in Settings
```

**Parsing Rule:**
- H1 = Epic title
- H2 = Story titles
- H3 = Task titles
- H4+ = Context/description (include in task description field)

---

### Numbered Lists

Numbered lists typically represent ordered steps or tasks.

```
1. User Registration
   a. Validate email format
   b. Check for duplicate email
   c. Hash password with bcrypt
2. Send Confirmation Email
   a. Generate confirmation token
   b. Set expiration (24 hours)
   c. Send via SMTP
3. Verify Email Link
   a. Check token validity
   b. Activate user account
   c. Redirect to login
```

**Parsing Rule:**
- Top-level numbers (1, 2, 3) = Stories or major tasks
- Sub-level letters (a, b, c) = Child tasks
- Nested bullets under letters = Context/description

---

### Bulleted Lists

Bulleted lists typically represent features, components, or attributes.

```
## Features of Dark Mode

- Automatic detection of OS preference
- Manual toggle in Settings
- Applies to all pages
- Includes custom color palette
  - Background: #1a1a1a
  - Text: #ffffff
  - Accent: #0066cc
- Respects WCAG AA contrast ratios
```

**Parsing Rule:**
- Top-level bullets = Features (map to stories or tasks)
- Nested bullets = Details/components (map to acceptance criteria or sub-tasks)
- Bullets with colons indicate attributes/settings (map to configuration requirements)

---

### Requirement Matrices / Tables

Documents sometimes include requirement matrices in table format.

```markdown
| ID | Requirement | Priority | Owner |
|----|-------------|----------|-------|
| REQ-001 | Support SAML 2.0 | High | Auth Team |
| REQ-002 | Email validation | High | API Team |
| REQ-003 | Rate limiting | Medium | Infra Team |
| REQ-004 | Dark mode support | Low | Frontend Team |
```

**Parsing Rule:**
- Each row = one story or task
- ID column = label or external reference
- Requirement column = title
- Priority column = custom field or story point hint
- Owner column = assignee (if Jira user mapping exists)

---

### Implicit Requirements in Narrative Text

Sometimes requirements are buried in descriptive prose, not in structured lists.

```
The system should support multiple authentication methods including 
username/password, SAML 2.0, and OAuth 2.0. When a user logs in, 
the system must validate credentials and return a session token 
within 3 seconds. Failed login attempts should be logged and the 
account locked after 5 failed attempts within 1 hour.
```

**Parsing Rule:**
1. Look for "should", "must", "will", "shall"
2. Extract each into a separate requirement/AC
3. Identify implicit requirements (e.g., "return within 3 seconds" = performance AC)
4. Break complex sentences into simpler criteria

**Extracted Requirements:**
- System supports SAML 2.0 authentication
- System supports OAuth 2.0 authentication
- Login must validate credentials
- Login must return session token within 3 seconds
- Failed login attempts must be logged
- Account must be locked after 5 failed attempts within 1 hour

---

## Edge Cases and Ambiguities

### Ambiguous Pronouns

**Problem:**
```
"The user enters their password. It must be at least 12 characters."
```

**What does "it" refer to?** The password or the entire login process?

**Solution:** Assume pronouns refer to the nearest noun. Rewrite for clarity: "The password must be at least 12 characters."

---

### Conflicting Requirements

**Problem:**
```
"The system shall support unlimited file uploads."
"The maximum file size is 10GB per upload."
```

These seem contradictory (unlimited vs. 10GB limit).

**Solution:** Flag during review. Ask the user to clarify: Is the limit 10GB, or is it truly unlimited? Proceed with the most restrictive interpretation if unsure.

---

### Quantified Requirements Without Context

**Problem:**
```
"Response time must be under 500ms."
```

**Missing context:** Under what load? Under what network conditions? For which endpoints?

**Solution:** Extract as-is, but note in the AC description: "Context: Network conditions and concurrent user load not specified—verify with product team."

---

### Negatively Stated Requirements

**Problem:**
```
"Users must not be able to delete archived records."
"The API must not allow requests over 5MB."
```

**Parsing:** These are constraints (what NOT to do), not features.

**Solution:** Extract as-is and mark as "constraint" or "guard rail" in the task description. Emphasize in testing: "Verify that archived records CANNOT be deleted."

---

### Requirements That Are Actually Design Decisions

**Problem:**
```
"Use a red button for delete actions."
"Store passwords in bcrypt with cost factor 12."
```

**These are implementation details, not requirements.**

**Solution:** Flag and ask: "Is this a requirement (must happen) or a design decision (how we'll do it)?" If design decision, consider moving to a linked design doc rather than creating an AC.

---

### Vague or Subjective Requirements

**Problem:**
```
"The system should be user-friendly."
"Make the dashboard intuitive."
"Improve performance."
```

**These are too vague to test.**

**Solution:** During review, ask for specifics: "What does 'user-friendly' mean? Can you quantify?" Suggest measurable criteria:
- "The onboarding flow should take less than 5 minutes"
- "Users should complete the common task in under 2 clicks"
- "API response time should improve by 30% (from 800ms to 560ms)"

---

## Extraction Algorithms

### Algorithm: Detect Requirement Statements

**Input:** A paragraph of text

**Output:** List of extracted requirement statements

```python
def extract_requirements(text):
    requirements = []
    keywords = ["shall", "must", "will", "should", "is required to", "is expected to"]
    
    for sentence in text.split("."):
        sentence = sentence.strip()
        for keyword in keywords:
            if keyword in sentence.lower():
                requirements.append(sentence)
                break
    
    return requirements

# Example
text = "The system shall support SAML. Users must receive confirmation within 60 seconds."
print(extract_requirements(text))
# Output: ["The system shall support SAML", "Users must receive confirmation within 60 seconds"]
```

---

### Algorithm: Parse Heading Hierarchy

**Input:** Document with headings (H1, H2, H3, etc.)

**Output:** Tree structure of headings

```python
def parse_heading_hierarchy(document):
    headings = extract_headings(document)  # Returns [(level, text), ...]
    tree = {"level": 0, "title": "Root", "children": []}
    stack = [tree]
    
    for level, text in headings:
        while stack[-1]["level"] >= level:
            stack.pop()
        
        node = {"level": level, "title": text, "children": []}
        stack[-1]["children"].append(node)
        stack.append(node)
    
    return tree

# Resulting structure:
# {
#   "title": "Root",
#   "children": [
#     {"level": 1, "title": "Feature X", "children": [
#       {"level": 2, "title": "Component A", "children": [...]},
#       {"level": 2, "title": "Component B", "children": [...]}
#     ]},
#     {"level": 1, "title": "Feature Y", ...}
#   ]
# }
```

---

### Algorithm: Detect BDD Scenarios

**Input:** Text block with BDD-formatted criteria

**Output:** Parsed scenario with steps

```python
def parse_bdd_scenario(text):
    scenario = {
        "name": "",
        "given": [],
        "when": [],
        "then": []
    }
    
    lines = text.split("\n")
    current_section = None
    
    for line in lines:
        line = line.strip()
        if line.startswith("Scenario:"):
            scenario["name"] = line.replace("Scenario:", "").strip()
        elif line.startswith("Given"):
            current_section = "given"
        elif line.startswith("When"):
            current_section = "when"
        elif line.startswith("Then"):
            current_section = "then"
        elif line.startswith("And") and current_section:
            scenario[current_section].append(line.replace("And", "").strip())
        elif current_section and line:
            scenario[current_section].append(line)
    
    return scenario
```

---

## Common Mistakes and Corrections

| Mistake | Example | Correction |
|---------|---------|-----------|
| Missing requirement keyword | "Users can export data" | "Users must be able to export data in CSV format" |
| Too vague | "System should be fast" | "API responses must complete within 500ms" |
| Mixing multiple requirements | "The system shall support SAML and OAuth" | Split into two ACs |
| Negating instead of stating | "Don't allow invalid emails" | "System must validate email format before acceptance" |
| Passive voice obscuring owner | "Email validation should be done" | "System must validate email before storage" |
| Subjective language | "Nice UI", "good performance" | Quantify: "Response time < 500ms", "WCAG AA compliant" |
| Implicit dependencies | "Delete button removes record" | Explicit: "When user clicks Delete, system shall show confirmation dialog and require password re-entry" |

---

## Reference: Jira Mapping

How parsed elements map to Jira issue structure:

```
Heading Hierarchy              Jira Issue Type
H1 (Feature Title)             Epic
H2 (Section)                   Story
H3 (Sub-section)               Task
H4 (Detail)                    Subtask or AC

Requirement Statements         Issue Field
"The system shall..."           Acceptance Criteria / Description
"Users must..."                 Acceptance Criteria
BDD Given/When/Then             Acceptance Criteria (structured)
Table row                       Story or Task (depends on context)
Bulleted list item              Task or Acceptance Criterion

Requirement Priority
"shall", "must"                 High Priority (Story Points: 8-13)
"will", "is required to"        Medium Priority (Story Points: 5-8)
"should"                        Low Priority (Story Points: 2-5)
"could", "consider"             Future / Backlog (Story Points: TBD)
```

---

## Validation Checklist for Extracted Requirements

Before converting to Jira issues, verify:

- [ ] Each requirement is singular (one idea per criterion)
- [ ] Requirements use clear, active voice
- [ ] Quantified metrics have units (seconds, bytes, percentage)
- [ ] Conditional requirements include the condition and outcome
- [ ] No requirements are marked both "must" and "optional"
- [ ] Acceptance criteria are testable (can be verified yes/no)
- [ ] Story titles start with action verb (e.g., "Implement", "Add", "Support")
- [ ] Nested structure matches heading hierarchy (no orphaned tasks)
- [ ] User stories include a clear user role and benefit
- [ ] Dependencies between items are explicitly noted

