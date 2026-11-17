"""The lab's SalesDesk org (scenario.md §5.1): one rep (Emil) who owns the Lakeshore Retail account, its open
400-store rollout and the closed pilot, two closed Aurora deals against Boulder Innovations for win/loss history,
two Lakeshore contacts, the Nov 20 pitch Event and two completed Tasks.

Company names and domains come from CELA's approved fictitious names list (see infra/mock_environment/README.md).
The people are the tenant users with the tenant email domain, so ``call-prep`` matches attendees to contacts by
exact email. Set ``SF_EMAIL_DOMAIN`` if the tenant domain changes.
"""

from __future__ import annotations

import os

from .ids import seed_id
from .schema import RECORD_TYPE_MASTER, stage_info

DEFAULT_EMAIL_DOMAIN = "a830edad9050849coeplTx9Ux16.onmicrosoft.com"


def _ts(day: str, time: str = "15:00:00") -> str:
    return f"{day}T{time}.000Z"


def build_seed(email_domain: str | None = None) -> dict:
    domain = email_domain or os.environ.get("SF_EMAIL_DOMAIN") or DEFAULT_EMAIL_DOMAIN
    counters: dict[str, int] = {}

    def new_id(prefix: str) -> str:
        counters[prefix] = counters.get(prefix, 0) + 1
        return seed_id(prefix, counters[prefix])

    org_id = new_id("00D")
    emil, zoe = new_id("005"), new_id("005")
    lakeshore, wwi, tailspin = new_id("001"), new_id("001"), new_id("001")
    atul, jahidi = new_id("003"), new_id("003")
    rollout, pilot, wwi_deal, tailspin_deal = new_id("006"), new_id("006"), new_id("006"), new_id("006")

    def stamp(rec: dict, created: str, owner: str | None = emil) -> dict:
        rec.setdefault("CreatedDate", created)
        rec.setdefault("CreatedById", emil)
        rec.setdefault("LastModifiedDate", rec["CreatedDate"])
        rec.setdefault("LastModifiedById", emil)
        rec.setdefault("SystemModstamp", rec["LastModifiedDate"])
        rec.setdefault("IsDeleted", False)
        if owner:
            rec.setdefault("OwnerId", owner)
        return rec

    users = [
        stamp({"Id": emil, "FirstName": "Emil", "LastName": "Vanggaard", "Username": f"emil@{domain}",
               "Email": f"emil@{domain}", "CompanyName": "Zava", "IsActive": True,
               "TimeZoneSidKey": "America/New_York", "LocaleSidKey": "en_US", "ManagerId": zoe},
              _ts("2026-01-12"), owner=None),
        stamp({"Id": zoe, "FirstName": "Zoe", "LastName": "Armstrong", "Username": f"zoe@{domain}",
               "Email": f"zoe@{domain}", "Title": "Director of Retail Sales", "Department": "Sales",
               "CompanyName": "Zava", "IsActive": True, "TimeZoneSidKey": "America/New_York",
               "LocaleSidKey": "en_US"},
              _ts("2026-01-12"), owner=None),
    ]
    organization = [{"Id": org_id, "Name": "Zava", "OrganizationType": "Enterprise Edition",
                     "InstanceName": "USA1000", "IsSandbox": False, "DefaultLocaleSidKey": "en_US",
                     "TimeZoneSidKey": "America/New_York", "Country": "United States",
                     "CreatedDate": _ts("2026-01-12")}]

    accounts = [
        stamp({"Id": lakeshore, "Name": "Lakeshore Retail", "Type": "Customer", "Industry": "Retail",
               "NumberOfEmployees": 12000, "Website": "lakeshore-retail.com", "AccountSource": "Partner Referral",
               "BillingCity": "Minneapolis", "BillingState": "MN", "BillingCountry": "United States",
               "Description": "Retailer with about 400 stores. Ran a 50-store Aurora smart-home hub pilot in 2026; "
                              "the full 400-store rollout is in proposal."},
              _ts("2026-06-02", "14:10:00")),
        stamp({"Id": wwi, "Name": "Wide World Importers", "Type": "Customer", "Industry": "Retail",
               "NumberOfEmployees": 8500, "Website": "wideworldimporters.com", "BillingCountry": "United States",
               "Description": "Aurora customer since September 2026 (320 stores)."},
              _ts("2026-06-15", "16:30:00")),
        stamp({"Id": tailspin, "Name": "Tailspin Toys", "Type": "Prospect", "Industry": "Retail",
               "NumberOfEmployees": 3200, "Website": "tailspintoys.com", "BillingCountry": "United States",
               "Description": "Evaluated Aurora for 120 stores in 2026; chose Boulder Innovations."},
              _ts("2026-07-20", "13:45:00")),
    ]
    contacts = [
        stamp({"Id": atul, "FirstName": "Atul", "LastName": "Manohar", "AccountId": lakeshore,
               "Title": "Director of Store Operations", "Department": "Store Operations",
               "Email": f"atul@{domain}", "MailingCity": "Minneapolis", "MailingState": "MN",
               "MailingCountry": "United States"},
              _ts("2026-06-02", "14:20:00")),
        stamp({"Id": jahidi, "FirstName": "Jahidi", "LastName": "Juma", "AccountId": lakeshore,
               "Title": "IT Security Lead", "Department": "IT", "Email": f"jahidi@{domain}",
               "MailingCity": "Minneapolis", "MailingState": "MN", "MailingCountry": "United States"},
              _ts("2026-06-02", "14:25:00")),
    ]

    opportunities = [
        stamp({"Id": rollout, "Name": "Lakeshore Retail \u2013 Aurora 400-store rollout", "AccountId": lakeshore,
               "ContactId": atul, "StageName": "Proposal/Price Quote", "Amount": 1200000.0,
               "CloseDate": "2026-12-31", "Type": "Existing Customer - Upgrade", "LeadSource": "Partner Referral",
               "NextStep": "Expansion pitch Fri Nov 20 with Atul, Nanami (CFO) and Jahidi: bring the all-in "
                           "per-store and total cost.",
               "Description": "Roll Aurora out to all 400 Lakeshore Retail stores ahead of the holiday season, "
                              "following the 50-store pilot. List price $3,000 per store.",
               "LastStageChangeDate": _ts("2026-11-02", "17:00:00")},
              _ts("2026-10-23", "18:00:00")),
        stamp({"Id": pilot, "Name": "Lakeshore Retail \u2013 Aurora pilot (50 stores)", "AccountId": lakeshore,
               "ContactId": atul, "StageName": "Closed Won", "Amount": 150000.0, "CloseDate": "2026-08-28",
               "Type": "New Customer", "LeadSource": "Partner Referral",
               "Description": "50-store Aurora pilot at list price ($3,000 per store). Success metric: attach "
                              "rate on smart-home bundles versus control stores.",
               "LastStageChangeDate": _ts("2026-08-28", "20:00:00")},
              _ts("2026-06-02", "14:30:00")),
        stamp({"Id": wwi_deal, "Name": "Wide World Importers \u2013 Aurora 320-store rollout", "AccountId": wwi,
               "StageName": "Closed Won", "Amount": 844800.0, "CloseDate": "2026-09-18", "Type": "New Customer",
               "LeadSource": "Web", "Competitor__c": "Boulder Innovations",
               "Description": "Won against Boulder Innovations on all-in TCO, not on sticker price. We showed "
                              "the all-in per-store cost instead of matching their discount.",
               "LastStageChangeDate": _ts("2026-09-18", "19:00:00")},
              _ts("2026-06-15", "16:40:00")),
        stamp({"Id": tailspin_deal, "Name": "Tailspin Toys \u2013 Aurora 120-store rollout", "AccountId": tailspin,
               "StageName": "Closed Lost", "Amount": 360000.0, "CloseDate": "2026-10-09", "Type": "New Customer",
               "LeadSource": "Web", "Competitor__c": "Boulder Innovations", "Loss_Reason__c": "Price",
               "Description": "Lost to Boulder Innovations on price. We led with a discount and never showed the "
                              "all-in TCO.",
               "LastStageChangeDate": _ts("2026-10-09", "21:00:00")},
              _ts("2026-07-20", "13:50:00")),
    ]

    history_plan = {
        rollout: [("Qualification", "2026-10-23T18:00:00"), ("Proposal/Price Quote", "2026-11-02T17:00:00")],
        pilot: [("Qualification", "2026-06-02T14:30:00"), ("Proposal/Price Quote", "2026-07-10T15:00:00"),
                ("Negotiation/Review", "2026-08-05T16:00:00"), ("Closed Won", "2026-08-28T20:00:00")],
        wwi_deal: [("Qualification", "2026-06-15T16:40:00"), ("Value Proposition", "2026-07-08T14:00:00"),
                   ("Proposal/Price Quote", "2026-08-04T15:30:00"), ("Negotiation/Review", "2026-08-27T18:00:00"),
                   ("Closed Won", "2026-09-18T19:00:00")],
        tailspin_deal: [("Qualification", "2026-07-20T13:50:00"), ("Proposal/Price Quote", "2026-08-24T15:00:00"),
                        ("Negotiation/Review", "2026-09-21T17:00:00"), ("Closed Lost", "2026-10-09T21:00:00")],
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
                              "CreatedDate": f"{when}.000Z", "CreatedById": emil,
                              "SystemModstamp": f"{when}.000Z", "IsDeleted": False})

    events = [
        stamp({"Id": new_id("00U"), "Subject": "Lakeshore Retail \u2013 Aurora expansion pitch",
               "StartDateTime": "2026-11-20T15:00:00.000Z", "EndDateTime": "2026-11-20T16:00:00.000Z",
               "IsAllDayEvent": False, "Location": "Microsoft Teams meeting", "Type": "Meeting", "ShowAs": "Busy",
               "IsPrivate": False, "WhoId": atul, "WhatId": rollout,
               "Description": "Attendees:\n"
                              f"- Atul Manohar, Director of Store Operations (atul@{domain})\n"
                              f"- Nanami Nakayama, CFO (nanami@{domain})\n"
                              f"- Jahidi Juma, IT Security Lead (jahidi@{domain})\n\n"
                              "Agenda: pilot results, the 400-store rollout proposal and pricing."},
              _ts("2026-11-03", "14:00:00")),
    ]
    tasks = [
        stamp({"Id": new_id("00T"), "Subject": "Pilot kickoff", "ActivityDate": "2026-09-01",
               "Status": "Completed", "Priority": "Normal", "Type": "Meeting", "TaskSubtype": "Task",
               "WhoId": atul, "WhatId": pilot, "CompletedDateTime": _ts("2026-09-01", "16:00:00"),
               "Description": "Kicked off the 50-store Aurora pilot with Atul. Success metric: attach rate on "
                              "smart-home bundles versus control stores."},
              _ts("2026-09-01", "16:00:00")),
        stamp({"Id": new_id("00T"), "Subject": "30-day pilot check-in", "ActivityDate": "2026-10-01",
               "Status": "Completed", "Priority": "Normal", "Type": "Call", "TaskSubtype": "Call",
               "WhoId": atul, "WhatId": pilot, "CompletedDateTime": _ts("2026-10-01", "15:30:00"),
               "Description": "All 50 pilot stores are live. Atul says the early attach-rate trend is positive; "
                              "full results at the pilot review."},
              _ts("2026-10-01", "15:30:00")),
    ]

    return {
        "domain": domain,
        "record_type_master": RECORD_TYPE_MASTER,
        "current_user": emil,
        "next_created": 1,
        "objects": {
            "User": users, "Organization": organization, "Account": accounts, "Contact": contacts,
            "Lead": [], "Opportunity": opportunities, "OpportunityHistory": histories, "Event": events,
            "Task": tasks,
        },
    }
