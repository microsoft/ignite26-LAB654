"""Build the Jira direct-ingestion JSONL for the engineering scenario.

Source of truth: the Aurora (AUR) work items in
``Connectors_Ignite_EMP/customconnectors/customconnectors_engineering.jsonl``.
Output mirrors the record shape of the Jira Cloud direct-ingestion sample
(one Graph-connector external item per line).

Usage:
    python build_jira_jsonl.py [--domain <tenant>.onmicrosoft.com]
"""

import argparse
import base64
import hashlib
import html
import json
import re
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENV = HERE.parents[1]
SOURCE = ENV / "Connectors_Ignite_EMP" / "customconnectors" / "customconnectors_engineering.jsonl"
USERS = ENV / "Connectors_Ignite_EMP" / "users.config.json"
OUTPUT = HERE / "jira_engineering.jsonl"

DEFAULT_DOMAIN = "a830edad9050849coeplTx9Ux16.onmicrosoft.com"
SITE = "https://mock-atlassian.yellowsand-9530f5dc.eastus.azurecontainerapps.io"
PROJECT_KEY = "AUR"
PROJECT_NAME = "Aurora"
ORG_NAME = "Zava"
NS = uuid.UUID("6f1c2a4e-9b7d-4c3a-8e21-5d0f7a6b3c91")
ZERO_GUID = "00000000-0000-0000-0000-000000000000"

STATUS_ICON = {"To Do": "open", "In Progress": "inprogress", "Done": "closed"}
TYPE_AVATAR = {"Bug": 10303, "Task": 10318, "Story": 10315, "Epic": 10307}

# Search-enrichment fields, authored per issue from its title, description and comments.
ENRICHMENT = {
    "AUR-133": {
        "title_keywords": ["device heartbeat events", "event-driven status service", "publish heartbeat"],
        "title_topic": "heartbeat events for status service",
        "content_keywords": ["hub heartbeat events", "derive Online and Offline", "without polling"],
        "content_topics": ["device heartbeat publishing", "event-driven status derivation", "polling removal", "aurora-status service", "production rollout"],
        "title_exact_phrases": ["device heartbeat", "heartbeat events", "event-driven status", "status service"],
        "content_exact_phrases": ["hub heartbeat events", "derive Online and Offline", "without polling", "heartbeat publisher"],
        "label_keyword": "status-service-cutover",
        "comment_keywords": ["heartbeat", "publisher", "staging", "production", "closing"],
        "topics": ("Device heartbeat publishing", "event-driven status derivation"),
    },
    "AUR-136": {
        "title_keywords": ["status-service cutover runbook", "pilot stores", "cutover"],
        "title_topic": "pilot store cutover runbook",
        "content_keywords": ["November 20 cutover runbook", "rollback trigger", "owner on call"],
        "content_topics": ["cutover runbook", "switch order", "health checks", "rollback planning", "dry run"],
        "title_exact_phrases": ["cutover runbook", "status-service cutover", "pilot stores"],
        "content_exact_phrases": ["switch order", "health checks", "rollback trigger", "owner on call", "Aurora Engineering Confluence space"],
        "label_keyword": "status-service-cutover",
        "comment_keywords": ["Confluence", "rollback", "switch order", "dry run", "Nov 18"],
        "topics": ("Cutover runbook", "rollback planning"),
    },
    "AUR-137": {
        "title_keywords": ["telemetry gaps", "Lakeshore Retail pilot hubs", "firmware 4.2"],
        "title_topic": "pilot hub telemetry gaps",
        "content_keywords": ["drop telemetry", "nightly network restart", "heartbeat interval"],
        "content_topics": ["telemetry loss", "firmware 4.2 regression", "network restart behaviour", "firmware 4.2.1 rollout", "device team escalation"],
        "title_exact_phrases": ["telemetry gaps", "Lakeshore Retail", "pilot hubs", "firmware 4.2"],
        "content_exact_phrases": ["drop telemetry", "nightly network restart", "one heartbeat interval", "4.2.1 firmware build"],
        "label_keyword": "lakeshore-retail-pilot",
        "comment_keywords": ["blocked", "firmware", "4.2.1", "device team", "escalated", "resolving"],
        "topics": ("Telemetry loss", "firmware 4.2.1 rollout"),
    },
    "AUR-139": {
        "title_keywords": ["rollout regression checks", "status-service cutover", "regression"],
        "title_topic": "cutover regression checks",
        "content_keywords": ["rollout regression checks", "event-driven status service", "safe cutover"],
        "content_topics": ["regression testing", "cutover readiness", "staging validation", "dry run scheduling", "event-driven status service"],
        "title_exact_phrases": ["rollout regression", "regression checks", "status-service cutover"],
        "content_exact_phrases": ["rollout regression checks", "November 20 cutover", "safe cutover"],
        "label_keyword": "status-service-cutover",
        "comment_keywords": ["regression", "staging", "green", "dry run", "Nov 18"],
        "topics": ("Regression testing", "cutover readiness"),
    },
    "AUR-142": {
        "title_keywords": ["Aurora hubs", "remain offline", "after reconnect"],
        "title_topic": "stale offline state after reconnect",
        "content_keywords": ["remain Offline in the dashboard", "network reconnect", "pilot expansion"],
        "content_topics": ["stale device status", "reconnect handling", "event-driven status service", "reconnect-state design decision", "pilot expansion risk"],
        "title_exact_phrases": ["Aurora hubs", "remain offline", "after reconnect"],
        "content_exact_phrases": ["remain Offline", "successful network reconnect", "visible state is stale", "reconnect coverage"],
        "label_keyword": "at-risk",
        "comment_keywords": ["fix", "legacy path", "review", "design decision", "platform sign-off", "at risk", "Sprint 24", "Nov 23"],
        "topics": ("Stale device status", "reconnect-state design decision"),
    },
    "AUR-151": {
        "title_keywords": ["custom dashboard filters", "store status view", "filters"],
        "title_topic": "saved dashboard filters",
        "content_keywords": ["save custom filters", "device status dashboard", "lower-priority enhancement"],
        "content_topics": ["dashboard customisation", "saved filters", "store operations", "device status dashboard", "backlog enhancement"],
        "title_exact_phrases": ["custom dashboard", "dashboard filters", "store status view"],
        "content_exact_phrases": ["save custom filters", "device status dashboard", "no contractual or pilot dependency"],
        "label_keyword": "dashboard",
        "comment_keywords": [],
        "topics": ("Dashboard customisation", "saved filters"),
    },
}


def multi_topics(a: str, b: str) -> dict:
    lb = b[0].lower() + b[1:]
    return {
        "multi_topics_compare": f"{a} versus {lb}.",
        "multi_topics_conjunction": f"{a} and {lb}.",
        "multi_topics_disjunction": f"{a} or {lb}.",
        "multi_topics_purpose": f"{a} enables {lb}.",
        "multi_topics_sequence": f"{a} followed by {lb}.",
        "multi_topics_causation": f"{a} impacts {lb}.",
        "multi_topics_part_whole": f"{a} is a component of {lb}.",
        "multi_topics_condition": f"{a} under {lb}.",
        "multi_topics_contrast": f"{a} and {lb} have different tradeoffs.",
        "topic_long_1": f"{a} for the Aurora pilot.",
        "topic_long_2": f"{b} for the Aurora pilot.",
        "topic_med_1": f"{a}.",
        "topic_med_2": f"{b}.",
    }


def load_people(domain: str) -> dict:
    users = json.loads(USERS.read_text(encoding="utf-8"))
    return {u["DisplayName"]: f"{u['MailNickName']}@{domain}" for u in users}


def identity(name: str, email: str) -> dict:
    return {
        "userSyncAction": 0,
        "identitySourceProperties": {},
        "metadata": None,
        "ExternalId": email,
        "EntraId": ZERO_GUID,
        "Email": email,
        "ExternalName": name,
        "PrincipalType": "user",
        "identitySource": None,
        "displayName": name,
        "identityType": 0,
        "id": hashlib.md5(email.lower().encode()).hexdigest(),
    }


def person_ref(name: str, email: str) -> dict:
    return {
        "ExternalId": str(uuid.uuid5(NS, "person:" + email)),
        "Email": email,
        "ExternalName": name,
        "PrincipalType": "user",
        "id": email,
    }


def to_html(text: str) -> str:
    out = []
    for block in text.split("\n\n"):
        lines = [ln for ln in block.split("\n") if ln.strip()]
        if lines and all(ln.startswith("- ") for ln in lines):
            out.append("<ul>" + "".join(f"<li>{html.escape(ln[2:])}</li>" for ln in lines) + "</ul>")
            continue
        m = re.fullmatch(r"\*\*(.+)\*\*", block.strip())
        if m:
            out.append(f"<h3>{html.escape(m.group(1))}</h3>")
        else:
            out.append("<p>" + "<br/>".join(html.escape(ln) for ln in lines) + "</p>")
    return "\n".join(out)


def b64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def parse_comments(raw: list, people: dict) -> list:
    comments = []
    for i, c in enumerate(raw or []):
        date, rest = c.split(" - ", 1)
        author, text = rest.split(": ", 1)
        ts = f"{date}T08:{15 + 10 * i:02d}:00Z"
        comments.append((author, people[author], ts, text))
    return comments


def build_record(item: dict, people: dict) -> dict:
    p = item["properties"]
    key = p["Key"]
    issue_id = 10000 + int(key.split("-")[1])
    status, priority, itype = p["Status"], p["Priority"], p["Type"]
    desc_html = to_html(p["Description"])

    reporter_email = people[p["Reporter"]]
    comments = parse_comments(p.get("Comments"), people)
    last_actor = comments[-1][0] if comments else p["Assignee"][0]
    created_by = {"Id": str(uuid.uuid5(NS, "person:" + reporter_email)), "Email": reporter_email, "Name": p["Reporter"]}
    author_names = [n for n in dict.fromkeys([*p["Assignee"], *(c[0] for c in comments)]) if n != p["Reporter"]]

    est = float(p["OriginalEstimateHours"])
    done = status == "Done"
    props = {
        "Title": p["Title"],
        "IssueSummary": p["Title"],
        "IssueDescription": desc_html,
        "Created": p["CreatedAt"],
        "Updated": p["UpdatedAt"],
        "DueDate": "2026-11-20T17:00:00Z",
        "ProjectName": PROJECT_NAME,
        "IssueType": itype,
        "IssueStatus": status,
        "IssuePriority": priority,
        "Labels": p["Labels"],
        "OrganizationName": ORG_NAME,
        "OrganizationUrl": SITE + "/",
        "IssueKey": key,
        "IssueId": issue_id,
        "ItemPath": PROJECT_KEY,
        "IssueLink": f"{SITE}/browse/{key}",
        "ProjectUrl": f"{SITE}/jira/software/projects/{PROJECT_KEY}/boards/57",
        "IssueStatusIconUrl": f"{SITE}/images/icons/statuses/{STATUS_ICON[status]}.png",
        "IssueIconUrl": f"{SITE}/rest/api/2/universal_avatar/view/type/issuetype/avatar/{TYPE_AVATAR[itype]}?size=small",
        "IssuePriorityIconUrl": f"{SITE}/images/icons/priorities/{priority.lower()}.svg",
        "CompletedWork": str(est if done else 0.0),
        "EstimatedWork": str(est),
        "RemainingWork": str(0.0 if done else est),
        "PercentWorkCompleted": 100 if done else -1,
        "ReporterName": identity(p["Reporter"], reporter_email),
        "AssigneeName": [identity(a, people[a]) for a in p["Assignee"]],
        "ChangedBy": identity(last_actor, people[last_actor]),
        "CreatedBy": created_by,
        "Authors": [created_by] + [identity(n, people[n]) for n in author_names],
    }
    if done:
        props["ClosedDate"] = p["ResolvedAt"]

    record = {
        "ObjectId": str(uuid.uuid5(NS, "issue:" + key)),
        "id": issue_id,
        "displayName": p["Title"],
        "shouldHashId": False,
        "hashedId": None,
        "isContainer": False,
        "containerId": None,
        "isAssociatedItem": False,
        "associatedItemsMetadata": None,
        "accessControlList": [{
            "principal": {
                "type": "everyone", "value": "EVERYONE", "identitySource": None,
                "identitySourceEnum": "azureActiveDirectory", "identityType": 3,
                "identitySourceProperties": None, "metadata": None, "displayName": None,
            },
            "ruleNode": None, "accessType": "grant", "transformedIdentity": None,
        }],
        "UniversalAccessControlBlock": None,
        "activityList": None,
        "itemVersion": None,
        "contentDomainCategoryName": None,
        "dataSourceResponse": None,
        "properties": props,
        "content": {"type": "html", "annotation": None, "semanticContent": None, "parsedData": desc_html},
        "comments": [
            {
                "entitySemanticType": "comment",
                "parentCommentId": None,
                "mentionedUsers": [],
                "commentId": str(uuid.uuid5(NS, f"comment:{key}:{i}")),
                "creator": person_ref(name, email),
                "modifier": person_ref(name, email),
                "createdDateTime": ts,
                "modifiedDateTime": ts,
                "commentText": text,
                "entityContent": b64(text),
                "entityEncoding": "b64",
                "entityFormat": "txt",
                "CommentId": issue_id * 100 + i + 1,
            }
            for i, (name, email, ts, text) in enumerate(comments)
        ],
        "attachments": [],
    }
    enr = dict(ENRICHMENT[key])
    topics = enr.pop("topics")
    record.update(enr)
    record.update(multi_topics(*topics))
    return record


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--domain", default=DEFAULT_DOMAIN, help="Tenant email domain for Zava users")
    args = ap.parse_args()

    people = load_people(args.domain)
    items = []
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        if line.strip():
            conn = json.loads(line)
            if conn.get("ConnectionId") == "jiraaurora":
                items = conn["Items"]
    records = [build_record(it, people) for it in items]
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Wrote {len(records)} issues to {OUTPUT}")


if __name__ == "__main__":
    main()
