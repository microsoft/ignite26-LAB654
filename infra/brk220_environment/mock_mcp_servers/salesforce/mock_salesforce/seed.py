"""The BRK220 demo's Salesforce org (scenario.md, Salesforce seed): Northwind Ltd, where Megan Bowen owns the Contoso Ltd
account, its open FY27 renewal and the current contract, plus two closed renewals against Fabrikam for win/loss
history. A second "Contoso" (Contoso Pharmaceuticals, owned by Lee Gu) tests that Copilot picks the right one.

People who are also tenant users use the tenant email domain, so attendees and contacts match by exact email. Set
``TENANT_EMAIL_DOMAIN`` (or ``SF_EMAIL_DOMAIN``) to the COEP tenant's domain.
"""

from __future__ import annotations

import os

from .ids import seed_id
from .schema import RECORD_TYPE_MASTER, stage_info

DEFAULT_EMAIL_DOMAIN = "northwind-ltd.example"
RENEWAL = "Existing Customer - Renewal"


def _ts(day: str, time: str = "15:00:00") -> str:
    return f"{day}T{time}.000Z"


def build_seed(email_domain: str | None = None) -> dict:
    domain = (email_domain or os.environ.get("TENANT_EMAIL_DOMAIN") or os.environ.get("SF_EMAIL_DOMAIN")
              or DEFAULT_EMAIL_DOMAIN)
    counters: dict[str, int] = {}

    def new_id(prefix: str) -> str:
        counters[prefix] = counters.get(prefix, 0) + 1
        return seed_id(prefix, counters[prefix])

    org_id = new_id("00D")
    megan, alex, lee = new_id("005"), new_id("005"), new_id("005")
    contoso, pharma, tailwind, adatum = new_id("001"), new_id("001"), new_id("001"), new_id("001")
    lidia, daniel = new_id("003"), new_id("003")
    renewal, current, tailwind_deal, adatum_deal, pharma_deal = (new_id("006") for _ in range(5))

    def stamp(rec: dict, created: str, owner: str | None = megan) -> dict:
        rec.setdefault("CreatedDate", created)
        rec.setdefault("CreatedById", owner or megan)
        rec.setdefault("LastModifiedDate", rec["CreatedDate"])
        rec.setdefault("LastModifiedById", owner or megan)
        rec.setdefault("SystemModstamp", rec["LastModifiedDate"])
        rec.setdefault("IsDeleted", False)
        if owner:
            rec.setdefault("OwnerId", owner)
        return rec

    def user(uid, first, last, title, manager=None):
        rec = {"Id": uid, "FirstName": first, "LastName": last, "Username": f"{first.lower()}@{domain}",
               "Email": f"{first.lower()}@{domain}", "Title": title, "Department": "Sales",
               "CompanyName": "Northwind Ltd", "IsActive": True, "TimeZoneSidKey": "America/New_York",
               "LocaleSidKey": "en_US"}
        if manager:
            rec["ManagerId"] = manager
        return stamp(rec, _ts("2025-01-06"), owner=None)

    users = [
        user(megan, "Megan", "Bowen", "Account Executive", manager=alex),
        user(alex, "Alex", "Wilber", "Regional Sales Director"),
        user(lee, "Lee", "Gu", "Account Executive", manager=alex),
    ]
    organization = [{"Id": org_id, "Name": "Northwind Ltd", "OrganizationType": "Enterprise Edition",
                     "InstanceName": "USA1000", "IsSandbox": False, "DefaultLocaleSidKey": "en_US",
                     "TimeZoneSidKey": "America/New_York", "Country": "United States",
                     "CreatedDate": _ts("2025-01-06")}]

    accounts = [
        stamp({"Id": contoso, "Name": "Contoso Ltd", "Type": "Customer", "Industry": "Manufacturing",
               "NumberOfEmployees": 38000, "Website": "contoso.com", "AccountSource": "Partner Referral",
               "BillingCity": "Munich", "BillingCountry": "Germany",
               "Description": "Manufacturing group with 14 subsidiaries in Europe and North America. Northwind "
                              "Platform customer since January 2025 (all subsidiaries, EU West and US East). "
                              "Not related to Contoso Pharmaceuticals."},
              _ts("2024-09-02", "14:10:00")),
        stamp({"Id": pharma, "Name": "Contoso Pharmaceuticals", "Type": "Prospect", "Industry": "Healthcare",
               "NumberOfEmployees": 6200, "Website": "contosopharma.com", "BillingCountry": "United States",
               "Description": "Prospect evaluating the Northwind Platform for compliance reporting. Not related "
                              "to Contoso Ltd."},
              _ts("2026-08-11", "16:30:00"), owner=lee),
        stamp({"Id": tailwind, "Name": "Tailwind Traders", "Type": "Customer", "Industry": "Retail",
               "NumberOfEmployees": 9100, "Website": "tailwindtraders.com", "BillingCountry": "United States",
               "Description": "Northwind Platform customer since 2024. Renewed for two years in June 2026."},
              _ts("2024-02-15", "16:30:00")),
        stamp({"Id": adatum, "Name": "Adatum Corporation", "Type": "Other", "Industry": "Technology",
               "NumberOfEmployees": 4800, "Website": "adatum.com", "BillingCountry": "United States",
               "Description": "Former customer. Moved to Fabrikam in October 2026."},
              _ts("2024-03-20", "13:45:00")),
    ]
    contacts = [
        stamp({"Id": lidia, "FirstName": "Lidia", "LastName": "Holloway", "AccountId": contoso,
               "Title": "Chief Information Officer", "Department": "IT", "Email": f"lidia@{domain}",
               "MailingCity": "Munich", "MailingCountry": "Germany",
               "Description": "Executive sponsor. Owns the SSO roadmap ask from the Q3 QBR."},
              _ts("2024-09-02", "14:20:00")),
        stamp({"Id": daniel, "FirstName": "Daniel", "LastName": "Okafor", "AccountId": contoso,
               "Title": "Head of Procurement", "Department": "Procurement", "Email": f"daniel@{domain}",
               "MailingCity": "Munich", "MailingCountry": "Germany",
               "Description": "Buyer for the renewal."},
              _ts("2024-09-02", "14:25:00")),
    ]

    opportunities = [
        stamp({"Id": renewal, "Name": "Contoso Ltd \u2013 FY27 platform renewal", "AccountId": contoso,
               "ContactId": daniel, "StageName": "Value Proposition", "Amount": 2400000.0,
               "CloseDate": "2026-12-31", "Type": RENEWAL, "LeadSource": "Other", "Competitor__c": "Fabrikam",
               "NextStep": "Send Contoso the formal renewal proposal before the end of November.",
               "Description": "Renewal of the Northwind Platform subscription for Contoso Ltd (all 14 "
                              "subsidiaries). Current contract: $2.4M a year, January 1, 2025 to December 31, "
                              "2026 (Order Form NW-OF-2025-0142). The contract allows up to a 7% uplift at "
                              "renewal.",
               "LastStageChangeDate": _ts("2026-10-08", "17:00:00")},
              _ts("2026-09-15", "15:00:00")),
        stamp({"Id": current, "Name": "Contoso Ltd \u2013 Platform subscription 2025\u20132026",
               "AccountId": contoso, "ContactId": daniel, "StageName": "Closed Won", "Amount": 2400000.0,
               "CloseDate": "2024-12-16", "Type": "New Customer", "LeadSource": "Partner Referral",
               "Description": "Two-year Northwind Platform subscription, $2.4M a year, January 1, 2025 to "
                              "December 31, 2026. Order Form NW-OF-2025-0142.",
               "LastStageChangeDate": _ts("2024-12-16", "20:00:00")},
              _ts("2024-09-02", "14:30:00")),
        stamp({"Id": tailwind_deal, "Name": "Tailwind Traders \u2013 FY26 platform renewal",
               "AccountId": tailwind, "StageName": "Closed Won", "Amount": 1140000.0, "CloseDate": "2026-06-30",
               "Type": RENEWAL, "LeadSource": "Other", "Competitor__c": "Fabrikam",
               "Description": "Renewed against Fabrikam, who offered 25% off our price. We didn't match it. We "
                              "held a 4% uplift, assigned a named engineer to their two open P1 incidents two "
                              "weeks before the renewal, and put the roadmap item they asked for in writing.",
               "LastStageChangeDate": _ts("2026-06-30", "19:00:00")},
              _ts("2026-03-02", "16:40:00")),
        stamp({"Id": adatum_deal, "Name": "Adatum Corporation \u2013 FY26 platform renewal",
               "AccountId": adatum, "StageName": "Closed Lost", "Amount": 1600000.0, "CloseDate": "2026-09-30",
               "Type": RENEWAL, "LeadSource": "Other", "Competitor__c": "Fabrikam",
               "Loss_Reason__c": "Competitor",
               "Description": "Lost to Fabrikam. Two P1 incidents sat unassigned for three weeks before the "
                              "renewal. We matched Fabrikam's 15% discount in the final week and Adatum left "
                              "anyway. Exit interview: support responsiveness, not price.",
               "LastStageChangeDate": _ts("2026-09-30", "21:00:00")},
              _ts("2026-05-04", "13:50:00")),
        stamp({"Id": pharma_deal, "Name": "Contoso Pharmaceuticals \u2013 compliance reporting pilot",
               "AccountId": pharma, "StageName": "Qualification", "Amount": 350000.0, "CloseDate": "2027-02-26",
               "Type": "New Customer", "LeadSource": "Web",
               "NextStep": "Security questionnaire due December 4.",
               "LastStageChangeDate": _ts("2026-10-14", "15:00:00")},
              _ts("2026-08-11", "16:40:00"), owner=lee),
    ]

    history_plan = {
        renewal: [("Qualification", "2026-09-15T15:00:00"), ("Value Proposition", "2026-10-08T17:00:00")],
        current: [("Qualification", "2024-09-02T14:30:00"), ("Proposal/Price Quote", "2024-10-21T15:00:00"),
                  ("Negotiation/Review", "2024-11-25T16:00:00"), ("Closed Won", "2024-12-16T20:00:00")],
        tailwind_deal: [("Qualification", "2026-03-02T16:40:00"), ("Proposal/Price Quote", "2026-05-12T15:30:00"),
                        ("Negotiation/Review", "2026-06-09T18:00:00"), ("Closed Won", "2026-06-30T19:00:00")],
        adatum_deal: [("Qualification", "2026-05-04T13:50:00"), ("Proposal/Price Quote", "2026-07-20T15:00:00"),
                      ("Negotiation/Review", "2026-09-08T17:00:00"), ("Closed Lost", "2026-09-30T21:00:00")],
        pharma_deal: [("Prospecting", "2026-08-11T16:40:00"), ("Qualification", "2026-10-14T15:00:00")],
    }
    by_id = {o["Id"]: o for o in opportunities}
    histories = []
    for opp_id, steps in history_plan.items():
        opp = by_id[opp_id]
        for stage, when in steps:
            probability, forecast = stage_info(stage)
            histories.append({"Id": new_id("008"), "OpportunityId": opp_id, "StageName": stage,
                              "Amount": opp["Amount"], "Probability": float(probability),
                              "CloseDate": opp["CloseDate"],
                              "ForecastCategory": {"Pipeline": "Pipeline", "Commit": "Forecast",
                                                   "Closed": "Closed"}.get(forecast, "Omitted"),
                              "CreatedDate": f"{when}.000Z", "CreatedById": opp["OwnerId"],
                              "SystemModstamp": f"{when}.000Z", "IsDeleted": False})

    events = [
        stamp({"Id": new_id("00U"), "Subject": "Contoso Ltd \u2013 Q3 QBR",
               "StartDateTime": "2026-09-29T13:00:00.000Z", "EndDateTime": "2026-09-29T14:00:00.000Z",
               "IsAllDayEvent": False, "Location": "Microsoft Teams meeting", "Type": "Meeting", "ShowAs": "Busy",
               "IsPrivate": False, "WhoId": lidia, "WhatId": renewal,
               "Description": "Attendees:\n"
                              f"- Lidia Holloway, CIO (lidia@{domain})\n"
                              f"- Daniel Okafor, Head of Procurement (daniel@{domain})\n"
                              f"- Isaiah Langer, Customer Success Manager (isaiah@{domain})\n\n"
                              "Agenda: Q3 usage, support, 2027 roadmap and the renewal timeline."},
              _ts("2026-09-16", "14:00:00")),
    ]
    tasks = [
        stamp({"Id": new_id("00T"), "Subject": "Renewal kickoff with Isaiah (CSM)", "ActivityDate": "2026-09-15",
               "Status": "Completed", "Priority": "Normal", "Type": "Meeting", "TaskSubtype": "Task",
               "WhatId": renewal, "CompletedDateTime": _ts("2026-09-15", "16:00:00"),
               "Description": "Agreed the renewal plan: QBR on September 29, pricing options to Daniel in early "
                              "October, formal proposal before the end of November."},
              _ts("2026-09-15", "16:00:00")),
        stamp({"Id": new_id("00T"), "Subject": "Send renewal pricing options to Daniel",
               "ActivityDate": "2026-10-06", "Status": "Completed", "Priority": "High", "Type": "Email",
               "TaskSubtype": "Email", "WhoId": daniel, "WhatId": renewal,
               "CompletedDateTime": _ts("2026-10-06", "14:30:00"),
               "Description": "Sent renewal pricing options to Daniel by email. Outcome is in the email thread."},
              _ts("2026-10-06", "14:30:00")),
    ]

    return {
        "domain": domain,
        "record_type_master": RECORD_TYPE_MASTER,
        "current_user": megan,
        "next_created": 1,
        "objects": {
            "User": users, "Organization": organization, "Account": accounts, "Contact": contacts,
            "Lead": [], "Opportunity": opportunities, "OpportunityHistory": histories, "Event": events,
            "Task": tasks,
        },
    }
