# BRIEF mode: renewal brief

Goal: one answer that tells the account executive where the renewal stands, what's at risk and what to do next. Read-only.

## 1. Account and renewal (Salesforce)

Use `dispatch_readonly` with `method: "GET"` and `url: "/services/data/v62.0/query"`, passing the SOQL in `queryParams.q`. Replace `<NAME>` with the account name the user gave. Don't call `discover` or `describe`.

1. Find the user's account:
   `SELECT Id, Name, Industry, Description, Owner.Name FROM Account USING SCOPE mine WHERE Name LIKE '<NAME>%'`
   - One row: use it. Several rows: list Name and Description and ask which one. No rows: tell the user none of their accounts match and stop.
2. Renewal opportunity and the contract it renews:
   `SELECT Id, Name, StageName, Amount, CloseDate, Type, NextStep, Competitor__c, Description FROM Opportunity WHERE AccountId = '<ACCOUNT_ID>' ORDER BY CloseDate DESC`
   - The open renewal is the open opportunity (`StageName` not Closed) with `Type` "Existing Customer - Renewal". The current contract is the most recent Closed Won one.
3. Contacts: `SELECT Id, Name, Title, Email, Description FROM Contact WHERE AccountId = '<ACCOUNT_ID>'`
4. Win/loss against the same competitor (if `Competitor__c` is set on the renewal):
   `SELECT Name, Account.Name, StageName, Amount, CloseDate, Loss_Reason__c, Description FROM Opportunity WHERE Competitor__c = '<COMPETITOR>' AND IsClosed = true ORDER BY CloseDate DESC`

## 2. Open incidents (Jira through Rovo)

1. `getAccessibleAtlassianResources` for the `cloudId`.
2. The customer label is `customer-<first word of the account name, lower case>` (for example `customer-contoso` for Contoso Ltd). Never include labels for other companies with a similar name (for example `customer-contoso-pharma`).
3. `searchJiraIssuesUsingJql` with `project = INC AND labels = <LABEL> AND statusCategory != Done ORDER BY priority ASC, created ASC` and fields `summary, priority, assignee, created, labels, status`.
4. For each ticket: key, priority, age in days (today minus `created`), owner ("Unassigned" if none), one-line summary.

## 3. Open customer asks and roadmap (Confluence connector)

Confluence is indexed into Microsoft 365 by the Confluence connector. Search Microsoft 365, not Rovo.

1. Find the page "<Account> account overview" (for example "Contoso Ltd account overview"). Pull the "Open customer asks" rows that aren't Done.
2. For each open ask, find the matching Product roadmap page (for example "Identity and SSO roadmap"). Note which items are committable and their dates. Don't promise anything in the brief; this feeds CLOSE-OUT.

## 4. Microsoft 365

Search the user's own Microsoft 365 content for the account:

- **Pricing email thread** with the customer's buyer: the latest agreed position (for example "agreed on <date> to cap the uplift at 5%") and anything the buyer asked for next (proposal deadline, written commitments).
- **QBR transcript and QBR notes**: attendees and roles, the customer's asks, price sensitivity and why, any competitor quote.
- **Internal Teams chats** about the account (for example an escalation chat): what was escalated, by whom, the symptoms, any new competitor move and any pricing guidance from the sales director.

## 5. Connect the dots

- Match the escalation symptoms (region, endpoints, timing) to the open tickets. Say which tickets match and why, for example "EU region, API calls 4 to 6 s, morning export timeouts → INC-40211 and INC-40302".
- Compare the agreed pricing position with the competitor's latest offer. Use the win/loss records: what won against this competitor and what lost.
- Note if the renewal close date is near and which asks are still open.

## 6. Output

Use exactly these sections, in this order. Today's date drives "days to renewal" and ticket ages. The values below show the format only; use what the sources return. Cite inline in every row: the Source column names the system and carries its citation.

```
## <Account> renewal brief · <today>
**Bottom line:** <one sentence: where the renewal stands and the biggest risk>.

| Contract value | Renewal date | Days to renewal | Open incidents | Highest priority | Unassigned |
|---|---|---|---|---|---|
| $2.4M / year | Dec 31, 2026 | 43 | 3 | 2 | 2 |
Source: Salesforce (<opportunity name>) · Jira via Rovo

### 1 · Open incidents (live from Jira via Rovo)
| Ticket | Priority | Age | Owner | Summary | Linked escalation |
|---|---|---|---|---|---|
| INC-40211 | Highest | 9 days | Unassigned | <summary> | Yes: <who>, Teams, <date> |

### 2 · What's at risk: connecting the dots
| Risk | What we know | Source | Recommendation |
|---|---|---|---|
| Service | <escalation: who, when, symptoms> matches <tickets>; <n> have no owner | Teams · Jira via Rovo | Assign owners now |
| Price | Agreed <position> on <date>; price-sensitive because <why>; <competitor> <first quote> → <latest offer>; vs <competitor>: <won deal, what worked>, <lost deal, what failed> | Outlook · QBR meeting · Teams · Salesforce | Hold the agreed position; don't match |
| Open ask | <ask>, open since <date>; committable: <capability and date> | Confluence · QBR meeting | Commit in writing with the proposal |

### 3 · Stakeholders
| Name | Role | What they care about | Source |

### 4 · Recommended next steps
1. Assign owners to <unassigned tickets> (suggest who, based on past incidents).
2. Send the formal renewal proposal: <agreed pricing> + written <ask> commitment, before <deadline from email>.
3. Draft the renewal order form from the current contract.
4. Update the Salesforce opportunity.

**Sources:** Salesforce · Jira via Rovo · Confluence · Outlook · Teams · QBR meeting · OneDrive

Want me to close these out? Say "Close out the <account> risks before renewal".
```

Keep the whole brief to one screen. Don't analyse ticket owners beyond one line here; CLOSE-OUT does that.
