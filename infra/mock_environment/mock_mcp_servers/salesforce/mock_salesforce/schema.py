"""Object metadata for the mock org: the standard fields the lab skills read, with the labels, data types and
relationship names recorded from a real org's UI API ``objectInfos`` responses (SEVAL traces), plus the picklists
the skills ground on.

Each object lists ``fields`` as (ApiName, label, dataType, extra). For REFERENCE fields ``extra`` is
(relationshipName, [target objects]); for PICKLIST and COMBOBOX fields it is the list of values.
"""

from __future__ import annotations

STAGES = [
    ("Prospecting", 10, "Pipeline"), ("Qualification", 10, "Pipeline"), ("Needs Analysis", 20, "Pipeline"),
    ("Value Proposition", 50, "Pipeline"), ("Id. Decision Makers", 60, "Pipeline"),
    ("Perception Analysis", 70, "Pipeline"), ("Proposal/Price Quote", 75, "Pipeline"),
    ("Negotiation/Review", 90, "Commit"), ("Closed Won", 100, "Closed"), ("Closed Lost", 0, "Omitted"),
]
OPEN_STAGES = [s for s, _, _ in STAGES if not s.startswith("Closed")]
INDUSTRIES = ["Agriculture", "Apparel", "Banking", "Chemicals", "Communications", "Construction", "Consulting",
              "Education", "Electronics", "Energy", "Engineering", "Entertainment", "Finance", "Food & Beverage",
              "Government", "Healthcare", "Hospitality", "Insurance", "Machinery", "Manufacturing", "Media",
              "Not For Profit", "Other", "Recreation", "Retail", "Shipping", "Technology", "Telecommunications",
              "Transportation", "Utilities"]
LEAD_SOURCES = ["Web", "Phone Inquiry", "Partner Referral", "Purchased List", "Other"]
RECORD_TYPE_MASTER = "012000000000000AAA"

_COMMON_TAIL = [
    ("CreatedDate", "Created Date", "DATETIME", None),
    ("CreatedById", "Created By ID", "REFERENCE", ("CreatedBy", ["User"])),
    ("LastModifiedDate", "Last Modified Date", "DATETIME", None),
    ("LastModifiedById", "Last Modified By ID", "REFERENCE", ("LastModifiedBy", ["User"])),
    ("SystemModstamp", "System Modstamp", "DATETIME", None),
    ("IsDeleted", "Deleted", "BOOLEAN", None),
]

OBJECTS: dict[str, dict] = {
    "User": {
        "label": "User", "plural": "Users", "prefix": "005", "name": ["Name"],
        "fields": [
            ("Id", "User ID", "ID", None),
            ("Name", "Full Name", "STRING", None),
            ("FirstName", "First Name", "STRING", None),
            ("LastName", "Last Name", "STRING", None),
            ("Username", "Username", "STRING", None),
            ("Email", "Email", "EMAIL", None),
            ("Title", "Title", "STRING", None),
            ("Department", "Department", "STRING", None),
            ("CompanyName", "Company Name", "STRING", None),
            ("Phone", "Phone", "PHONE", None),
            ("IsActive", "Active", "BOOLEAN", None),
            ("TimeZoneSidKey", "Time Zone", "PICKLIST", ["America/New_York", "America/Chicago", "America/Los_Angeles"]),
            ("LocaleSidKey", "Locale", "PICKLIST", ["en_US"]),
            ("ManagerId", "Manager ID", "REFERENCE", ("Manager", ["User"])),
            *_COMMON_TAIL,
        ],
        "children": [],
    },
    "Organization": {
        "label": "Organization", "plural": "Organizations", "prefix": "00D", "name": ["Name"],
        "fields": [
            ("Id", "Organization ID", "ID", None),
            ("Name", "Name", "STRING", None),
            ("OrganizationType", "Edition", "PICKLIST", ["Enterprise Edition", "Unlimited Edition", "Developer Edition"]),
            ("InstanceName", "Instance Name", "STRING", None),
            ("IsSandbox", "Is Sandbox", "BOOLEAN", None),
            ("DefaultLocaleSidKey", "Locale", "PICKLIST", ["en_US"]),
            ("TimeZoneSidKey", "Default Time Zone", "PICKLIST", ["America/New_York"]),
            ("City", "City", "STRING", None),
            ("State", "State/Province", "STRING", None),
            ("Country", "Country", "STRING", None),
            ("CreatedDate", "Created Date", "DATETIME", None),
        ],
        "children": [],
    },
    "Account": {
        "label": "Account", "plural": "Accounts", "prefix": "001", "name": ["Name"],
        "fields": [
            ("Id", "Account ID", "ID", None),
            ("Name", "Account Name", "STRING", None),
            ("Type", "Account Type", "PICKLIST", ["Prospect", "Customer - Direct", "Customer - Channel",
                                                  "Customer", "Channel Partner / Reseller", "Installation Partner",
                                                  "Technology Partner", "Other"]),
            ("Industry", "Industry", "PICKLIST", INDUSTRIES),
            ("NumberOfEmployees", "Employees", "INT", None),
            ("AnnualRevenue", "Annual Revenue", "CURRENCY", None),
            ("Website", "Website", "URL", None),
            ("Phone", "Account Phone", "PHONE", None),
            ("Description", "Account Description", "TEXTAREA", None),
            ("AccountSource", "Account Source", "PICKLIST", LEAD_SOURCES),
            ("BillingStreet", "Billing Street", "TEXTAREA", None),
            ("BillingCity", "Billing City", "STRING", None),
            ("BillingState", "Billing State/Province", "STRING", None),
            ("BillingPostalCode", "Billing Zip/Postal Code", "STRING", None),
            ("BillingCountry", "Billing Country", "STRING", None),
            ("ParentId", "Parent Account ID", "REFERENCE", ("Parent", ["Account"])),
            ("OwnerId", "Owner ID", "REFERENCE", ("Owner", ["User"])),
            ("LastActivityDate", "Last Activity", "DATE", None),
            *_COMMON_TAIL,
        ],
        "children": [("Contact", "Contacts", "AccountId"), ("Opportunity", "Opportunities", "AccountId"),
                     ("Task", "Tasks", "AccountId"), ("Event", "Events", "AccountId"),
                     ("ActivityHistory", "ActivityHistories", "AccountId"),
                     ("OpenActivity", "OpenActivities", "AccountId")],
    },
    "Contact": {
        "label": "Contact", "plural": "Contacts", "prefix": "003", "name": ["Name"],
        "fields": [
            ("Id", "Contact ID", "ID", None),
            ("Name", "Full Name", "STRING", None),
            ("Salutation", "Salutation", "PICKLIST", ["Mr.", "Ms.", "Mrs.", "Dr.", "Prof.", "Mx."]),
            ("FirstName", "First Name", "STRING", None),
            ("LastName", "Last Name", "STRING", None),
            ("AccountId", "Account ID", "REFERENCE", ("Account", ["Account"])),
            ("Title", "Title", "STRING", None),
            ("Department", "Department", "STRING", None),
            ("Email", "Email", "EMAIL", None),
            ("Phone", "Business Phone", "PHONE", None),
            ("MobilePhone", "Mobile Phone", "PHONE", None),
            ("MailingCity", "Mailing City", "STRING", None),
            ("MailingState", "Mailing State/Province", "STRING", None),
            ("MailingCountry", "Mailing Country", "STRING", None),
            ("LeadSource", "Lead Source", "PICKLIST", LEAD_SOURCES),
            ("Description", "Contact Description", "TEXTAREA", None),
            ("ReportsToId", "Reports To ID", "REFERENCE", ("ReportsTo", ["Contact"])),
            ("OwnerId", "Owner ID", "REFERENCE", ("Owner", ["User"])),
            ("LastActivityDate", "Last Activity", "DATE", None),
            *_COMMON_TAIL,
        ],
        "children": [("Opportunity", "Opportunities", "ContactId"), ("Task", "Tasks", "WhoId"),
                     ("Event", "Events", "WhoId"), ("ActivityHistory", "ActivityHistories", "WhoId"),
                     ("OpenActivity", "OpenActivities", "WhoId")],
    },
    "Lead": {
        "label": "Lead", "plural": "Leads", "prefix": "00Q", "name": ["Name"],
        "fields": [
            ("Id", "Lead ID", "ID", None),
            ("Name", "Full Name", "STRING", None),
            ("FirstName", "First Name", "STRING", None),
            ("LastName", "Last Name", "STRING", None),
            ("Company", "Company", "STRING", None),
            ("Title", "Title", "STRING", None),
            ("Email", "Email", "EMAIL", None),
            ("Phone", "Phone", "PHONE", None),
            ("Status", "Status", "PICKLIST", ["Open - Not Contacted", "Working - Contacted",
                                              "Closed - Converted", "Closed - Not Converted"]),
            ("LeadSource", "Lead Source", "PICKLIST", LEAD_SOURCES),
            ("Industry", "Industry", "PICKLIST", INDUSTRIES),
            ("IsConverted", "Converted", "BOOLEAN", None),
            ("OwnerId", "Owner ID", "REFERENCE", ("Owner", ["User"])),
            *_COMMON_TAIL,
        ],
        "children": [("Task", "Tasks", "WhoId"), ("Event", "Events", "WhoId")],
    },
    "Opportunity": {
        "label": "Opportunity", "plural": "Opportunities", "prefix": "006", "name": ["Name"],
        "fields": [
            ("Id", "Opportunity ID", "ID", None),
            ("Name", "Name", "STRING", None),
            ("AccountId", "Account ID", "REFERENCE", ("Account", ["Account"])),
            ("ContactId", "Contact ID", "REFERENCE", ("Contact", ["Contact"])),
            ("StageName", "Stage", "PICKLIST", [s for s, _, _ in STAGES]),
            ("Amount", "Amount", "CURRENCY", None),
            ("Probability", "Probability (%)", "PERCENT", None),
            ("ExpectedRevenue", "Expected Amount", "CURRENCY", None),
            ("CloseDate", "Close Date", "DATE", None),
            ("Type", "Opportunity Type", "PICKLIST", ["Existing Customer - Upgrade", "Existing Customer - Replacement",
                                                     "Existing Customer - Downgrade", "New Customer"]),
            ("LeadSource", "Lead Source", "PICKLIST", LEAD_SOURCES),
            ("NextStep", "Next Step", "STRING", None),
            ("Description", "Description", "TEXTAREA", None),
            ("ForecastCategoryName", "Forecast Category", "PICKLIST", ["Omitted", "Pipeline", "Best Case",
                                                                      "Commit", "Closed"]),
            ("IsClosed", "Closed", "BOOLEAN", None),
            ("IsWon", "Won", "BOOLEAN", None),
            ("Competitor__c", "Primary Competitor", "STRING", None),
            ("Loss_Reason__c", "Loss Reason", "PICKLIST", ["Price", "Product Fit", "Competitor", "No Decision",
                                                         "Timing", "Other"]),
            ("FiscalYear", "Fiscal Year", "INT", None),
            ("FiscalQuarter", "Fiscal Quarter", "INT", None),
            ("LastActivityDate", "Last Activity", "DATE", None),
            ("LastStageChangeDate", "Last Stage Change Date", "DATETIME", None),
            ("OwnerId", "Owner ID", "REFERENCE", ("Owner", ["User"])),
            *_COMMON_TAIL,
        ],
        "children": [("OpportunityHistory", "OpportunityHistories", "OpportunityId"),
                     ("Task", "Tasks", "WhatId"), ("Event", "Events", "WhatId"),
                     ("ActivityHistory", "ActivityHistories", "WhatId"),
                     ("OpenActivity", "OpenActivities", "WhatId")],
    },
    "OpportunityHistory": {
        "label": "Opportunity History", "plural": "Opportunity History", "prefix": "008", "name": ["Id"],
        "fields": [
            ("Id", "Opportunity History ID", "ID", None),
            ("OpportunityId", "Opportunity ID", "REFERENCE", ("Opportunity", ["Opportunity"])),
            ("StageName", "Stage", "PICKLIST", [s for s, _, _ in STAGES]),
            ("Amount", "Amount", "CURRENCY", None),
            ("Probability", "Probability (%)", "PERCENT", None),
            ("CloseDate", "Close Date", "DATE", None),
            ("ForecastCategory", "Forecast Category", "PICKLIST", ["Omitted", "Pipeline", "BestCase",
                                                                  "Forecast", "Closed"]),
            ("PrevAmount", "Previous Amount", "CURRENCY", None),
            ("PrevCloseDate", "Previous Close Date", "DATE", None),
            ("CreatedDate", "Created Date", "DATETIME", None),
            ("CreatedById", "Created By ID", "REFERENCE", ("CreatedBy", ["User"])),
            ("SystemModstamp", "System Modstamp", "DATETIME", None),
            ("IsDeleted", "Deleted", "BOOLEAN", None),
        ],
        "children": [],
    },
    "Event": {
        "label": "Event", "plural": "Events", "prefix": "00U", "name": ["Subject"],
        "fields": [
            ("Id", "Activity ID", "ID", None),
            ("Subject", "Subject", "COMBOBOX", ["Call", "Email", "Meeting", "Send Letter/Quote", "Other"]),
            ("StartDateTime", "Start Date Time", "DATETIME", None),
            ("EndDateTime", "End Date Time", "DATETIME", None),
            ("ActivityDateTime", "Due Date Time", "DATETIME", None),
            ("ActivityDate", "Due Date Only", "DATE", None),
            ("EndDate", "End Date", "DATE", None),
            ("DurationInMinutes", "Duration", "INT", None),
            ("IsAllDayEvent", "All-Day Event", "BOOLEAN", None),
            ("Location", "Location", "STRING", None),
            ("Description", "Description", "TEXTAREA", None),
            ("Type", "Type", "PICKLIST", ["Call", "Email", "Meeting", "Other"]),
            ("ShowAs", "Show Time As", "PICKLIST", ["Busy", "OutOfOffice", "Free"]),
            ("EventSubtype", "Event Subtype", "PICKLIST", ["Event"]),
            ("IsPrivate", "Private", "BOOLEAN", None),
            ("WhoId", "Name ID", "REFERENCE", ("Who", ["Contact", "Lead"])),
            ("WhatId", "Related To ID", "REFERENCE", ("What", ["Account", "Opportunity"])),
            ("AccountId", "Account ID", "REFERENCE", ("Account", ["Account"])),
            ("OwnerId", "Assigned To ID", "REFERENCE", ("Owner", ["User"])),
            *_COMMON_TAIL,
        ],
        "required": ["OwnerId", "StartDateTime", "EndDateTime"],
        "children": [],
    },
    "Task": {
        "label": "Task", "plural": "Tasks", "prefix": "00T", "name": ["Subject"],
        "fields": [
            ("Id", "Activity ID", "ID", None),
            ("Subject", "Subject", "COMBOBOX", ["Call", "Send Letter", "Send Quote", "Other"]),
            ("ActivityDate", "Due Date Only", "DATE", None),
            ("Status", "Status", "PICKLIST", ["Not Started", "In Progress", "Completed", "Waiting on someone else",
                                              "Deferred"]),
            ("Priority", "Priority", "PICKLIST", ["High", "Normal", "Low"]),
            ("Type", "Type", "PICKLIST", ["Call", "Email", "Meeting", "Other"]),
            ("TaskSubtype", "Task Subtype", "PICKLIST", ["Task", "Email", "Call"]),
            ("Description", "Comments", "TEXTAREA", None),
            ("CompletedDateTime", "Completed Date/Time", "DATETIME", None),
            ("IsClosed", "Closed", "BOOLEAN", None),
            ("IsHighPriority", "High Priority", "BOOLEAN", None),
            ("CallType", "Call Type", "PICKLIST", ["Internal", "Inbound", "Outbound"]),
            ("CallDurationInSeconds", "Call Duration", "INT", None),
            ("WhoId", "Name ID", "REFERENCE", ("Who", ["Contact", "Lead"])),
            ("WhatId", "Related To ID", "REFERENCE", ("What", ["Account", "Opportunity"])),
            ("AccountId", "Account ID", "REFERENCE", ("Account", ["Account"])),
            ("OwnerId", "Assigned To ID", "REFERENCE", ("Owner", ["User"])),
            *_COMMON_TAIL,
        ],
        "required": ["OwnerId", "Status", "Priority"],
        "children": [],
    },
}

# ActivityHistory (completed tasks and past events) and OpenActivity (open tasks and upcoming events) are read-only
# views over Task and Event; they share these fields.
_ACTIVITY_VIEW = [
    ("Id", "Activity ID", "ID", None),
    ("Subject", "Subject", "COMBOBOX", ["Call", "Email", "Meeting", "Other"]),
    ("ActivityDate", "Due Date Only", "DATE", None),
    ("ActivityType", "Type", "PICKLIST", ["Call", "Email", "Meeting", "Other"]),
    ("ActivitySubtype", "Activity Subtype", "PICKLIST", ["Task", "Event", "Email", "Call"]),
    ("Status", "Status", "PICKLIST", ["Not Started", "In Progress", "Completed"]),
    ("Priority", "Priority", "PICKLIST", ["High", "Normal", "Low"]),
    ("Description", "Description", "TEXTAREA", None),
    ("StartDateTime", "Start", "DATETIME", None),
    ("EndDateTime", "End", "DATETIME", None),
    ("DurationInMinutes", "Duration", "INT", None),
    ("Location", "Location", "STRING", None),
    ("CompletedDateTime", "Completed Date/Time", "DATETIME", None),
    ("IsTask", "Task", "BOOLEAN", None),
    ("IsClosed", "Closed", "BOOLEAN", None),
    ("WhoId", "Name ID", "REFERENCE", ("Who", ["Contact", "Lead"])),
    ("WhatId", "Related To ID", "REFERENCE", ("What", ["Account", "Opportunity"])),
    ("AccountId", "Account ID", "REFERENCE", ("Account", ["Account"])),
    ("OwnerId", "Assigned To ID", "REFERENCE", ("Owner", ["User"])),
    ("CreatedDate", "Created Date", "DATETIME", None),
    ("LastModifiedDate", "Last Modified Date", "DATETIME", None),
]
OBJECTS["ActivityHistory"] = {"label": "Activity History", "plural": "Activity Histories", "prefix": None,
                              "name": ["Subject"], "fields": _ACTIVITY_VIEW, "children": [], "virtual": True}
OBJECTS["OpenActivity"] = {"label": "Open Activity", "plural": "Open Activities", "prefix": None,
                           "name": ["Subject"], "fields": _ACTIVITY_VIEW, "children": [], "virtual": True}

PREFIXES = {meta["prefix"]: name for name, meta in OBJECTS.items() if meta.get("prefix")}
SEARCHABLE = ["Account", "Contact", "Opportunity", "Lead", "Event", "Task", "User"]
WRITABLE = ["Account", "Contact", "Lead", "Opportunity", "Event", "Task"]
READ_ONLY_FIELDS = {"Id", "Name", "IsClosed", "IsWon", "CreatedDate", "CreatedById", "LastModifiedDate",
                    "LastModifiedById", "SystemModstamp", "IsDeleted", "AccountId", "LastActivityDate",
                    "ExpectedRevenue", "FiscalYear", "FiscalQuarter", "LastStageChangeDate", "DurationInMinutes",
                    "EndDate", "ActivityDateTime", "TaskSubtype", "EventSubtype"}


def fields(obj: str) -> dict[str, tuple]:
    return {f[0]: f for f in OBJECTS[obj]["fields"]}


def field(obj: str, api_name: str) -> tuple | None:
    return fields(obj).get(api_name)


def find_object(name: str) -> str | None:
    for key in OBJECTS:
        if key.lower() == name.lower():
            return key
    return None


def find_field(obj: str, name: str) -> tuple | None:
    for f in OBJECTS[obj]["fields"]:
        if f[0].lower() == name.lower():
            return f
    return None


def parent_relationship(obj: str, rel: str, case_insensitive: bool = False) -> tuple | None:
    """(fieldApiName, relationshipName, targets) for a parent relationship like Owner or What."""
    for f in OBJECTS[obj]["fields"]:
        if f[2] == "REFERENCE" and f[3]:
            name = f[3][0]
            if name == rel or (case_insensitive and name.lower() == rel.lower()):
                return f[0], name, f[3][1]
    return None


def child_relationship(obj: str, rel: str, case_insensitive: bool = False) -> tuple | None:
    """(childObject, relationshipName, fieldName) for a child relationship like Contacts."""
    for child in OBJECTS[obj]["children"]:
        if child[1] == rel or (case_insensitive and child[1].lower() == rel.lower()):
            return child
    return None


def stage_info(stage: str | None) -> tuple[int, str]:
    for name, probability, forecast in STAGES:
        if name == stage:
            return probability, forecast
    return 0, "Pipeline"
