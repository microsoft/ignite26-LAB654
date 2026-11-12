"""The 41 Atlassian Rovo MCP tools. Names, descriptions, input schemas and annotations are the real ones, captured
from the live server and loaded from ``seed_files/tool_schemas.json``.

Jira tools work against the Aurora project and Confluence tools against the Aurora Engineering (AUR) space. Compass
and the user-level Teamwork Graph calls fail the way they do for an account without those scopes.
"""

from __future__ import annotations

import base64
import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote, urlparse

from mockmcp import CallContext, InvalidParams, Tool, ToolError

from . import jql, render
from .render import api, site_url
from .store import Site, StateStore

SCHEMAS_PATH = Path(__file__).resolve().parent.parent / "seed_files" / "tool_schemas.json"
HINTS = ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint")
DONE_RESOLUTION = {"id": "10000", "description": "Work has been completed on this work item.", "name": "Done"}


def load_schemas(path: Path = SCHEMAS_PATH) -> dict[str, dict]:
    return {t["name"]: t for t in json.loads(path.read_text(encoding="utf-8"))}


def pretty(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False)


def compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def jira_stamp(now: datetime) -> str:
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}+0000"


# --- errors --------------------------------------------------------------------------------------------------------

class JiraError(ToolError):
    """An error whose rendered text is ``body`` as compact JSON."""

    def __init__(self, body: dict) -> None:
        super().__init__(body.get("message", "error") if isinstance(body.get("message"), str) else "error")
        self.body = body


def rest_error(status: int, messages: list[str] | None = None, errors: dict | None = None,
               limit: int = 400) -> JiraError:
    message = compact({"errorMessages": messages or [], "errors": errors or {}})
    return JiraError({"error": True, "message": message,
                      "rateLimit": {"limit": limit, "remaining": limit - 1,
                                    "headers": {"x-ratelimit-limit": str(limit),
                                                "x-ratelimit-remaining": str(limit - 1)}},
                      "statusCode": status})


def issue_not_found() -> JiraError:
    return rest_error(404, ["Issue does not exist or you do not have permission to see it."])


def project_not_found(ref: str) -> JiraError:
    return rest_error(404, [f"No project could be found with id or key '{ref}'."], limit=350)


def scope_error(tool: str) -> JiraError:
    scopes = ["offline_access", "read:me", "write:jira-work", "write:comment:confluence", "read:comment:confluence",
              "read:page:confluence", "read:confluence-user", "search:confluence", "read:jira-work",
              "write:page:confluence", "read:space:confluence", "read:hierarchical-content:confluence"]
    field = {"getCompassComponents": "searchComponents", "getCompassComponent": "component",
             "getCompassCustomFieldDefinitions": "customFieldDefinitions"}.get(tool, "createComponent")
    required = "read:component:compass" if tool.startswith("get") else "write:component:compass"
    detail = [{"message": "This request does not contain the right authorisation scopes to access this field",
               "locations": [], "path": ["compass", field],
               "extensions": {"requiredScopes": [required], "providedScopes": scopes,
                              "errorSource": "GRAPHQL_GATEWAY", "statusCode": 403,
                              "agg": {"severity": "NORMAL", "ugcPiiSafe": True},
                              "classification": "InsufficientOAuthScopes"}}]
    return JiraError({"error": True, "message": "GraphQL errors: " + compact(detail)})


# --- argument helpers ----------------------------------------------------------------------------------------------

def resolve_cloud(site: Site, value: Any) -> None:
    """Accept the cloud ID, the site name, its host name or its URL, as the real server does."""
    text = str(value or "").strip()
    meta = site.data["site"]
    host = urlparse(text).hostname if "://" in text else text.split("/")[0]
    accepted = {meta["cloudId"], meta["name"], f"{meta['name']}.atlassian.net",
                urlparse(site_url()).hostname or ""}
    if text in accepted or (host or "").lower() in {a.lower() for a in accepted}:
        return
    # Mock-defined wording: the live server's text for an unknown cloud ID wasn't captured.
    raise JiraError({"error": True,
                     "message": f"Cloud ID '{text}' is not accessible to this user. Call "
                                "getAccessibleAtlassianResources to find the cloud IDs you can use."})


def find_issue(site: Site, ref: Any) -> dict:
    issue = site.issue(str(ref or ""))
    if issue is None:
        raise issue_not_found()
    return issue


def find_project(site: Site, ref: Any) -> dict:
    p = site.project
    if str(ref).strip().upper() in (p["key"].upper(), p["id"]):
        return p
    raise project_not_found(str(ref))


def as_markdown(value: Any) -> str:
    """Body content arrives as markdown, an ADF object or an ADF JSON string."""
    if value is None:
        return ""
    if isinstance(value, dict):
        return render.from_adf(value)
    text = str(value)
    if text.lstrip().startswith("{"):
        try:
            doc = json.loads(text)
            if isinstance(doc, dict) and doc.get("type") == "doc":
                return render.from_adf(doc)
        except ValueError:
            pass
    return text


def ref_of(value: Any, *keys: str) -> str | None:
    if value is None:
        return None
    if isinstance(value, dict):
        for k in keys:
            if value.get(k) not in (None, ""):
                return str(value[k])
        return None
    return str(value)


def apply_fields(site: Site, issue: dict, fields: dict, now: datetime) -> None:
    errors: dict[str, str] = {}
    for name, value in fields.items():
        key = render.FIELD_ALIASES.get(name.lower(), name)
        if key == "summary":
            if not str(value or "").strip():
                errors["summary"] = "You must specify a summary of the issue."
            else:
                issue["summary"] = str(value)
        elif key == "description":
            issue["description"] = as_markdown(value) if value is not None else None
        elif key in ("assignee", "reporter"):
            ref = ref_of(value, "accountId", "id", "name", "emailAddress")
            if ref is None:
                if key == "reporter":
                    errors[key] = "Reporter is required."
                else:
                    issue[key] = None
                continue
            user = site.user(ref)
            if user is None:
                errors[key] = f"User '{ref}' does not exist."
            else:
                issue[key] = user["key"]
        elif key == "priority":
            ref = ref_of(value, "name", "id")
            match = next((p for p in site.data["priorities"]
                          if ref and ref.lower() in (p["name"].lower(), p["id"])), None)
            if match is None:
                errors["priority"] = "Specify the Priority (id or name) in the string format"
            else:
                issue["priority"] = match["name"]
        elif key == "labels":
            if not isinstance(value, list):
                errors["labels"] = "Labels must be an array of strings."
            elif any(" " in str(v) for v in value):
                errors["labels"] = "The label cannot contain spaces."
            else:
                issue["labels"] = [str(v) for v in value]
        elif key == "customfield_10020":
            if value is None:
                issue["sprint"] = None
                continue
            ref = ref_of(value[0] if isinstance(value, list) and value else value, "id", "name")
            sprint = next((s for s in site.data["sprints"]
                           if ref and ref.lower() in (str(s["id"]), s["name"].lower())), None)
            if sprint is None:
                errors["customfield_10020"] = f"Sprint with id {ref} does not exist."
            else:
                issue["sprint"] = sprint["id"]
        elif key == "timetracking":
            original = (value or {}).get("originalEstimate") if isinstance(value, dict) else None
            if original is None:
                issue["estimateHours"] = None
                continue
            seconds = render.parse_duration(str(original))
            if seconds is None:
                errors["timetracking"] = "Original Estimate is invalid."
            else:
                issue["estimateHours"] = seconds / 3600
        elif key in ("timeoriginalestimate",):
            issue["estimateHours"] = None if value is None else int(value) / 3600
        elif key == "parent":
            ref = ref_of(value, "key", "id")
            if ref is None:
                issue["parent"] = None
                continue
            parent = site.issue(ref)
            if parent is None or parent["key"] == issue.get("key"):
                errors["parent"] = "Could not find issue by id or key."
            else:
                issue["parent"] = parent["key"]
        elif key == "components":
            issue["components"] = [{"name": ref_of(c, "name", "id")} for c in (value or [])]
        elif key == "issuetype":
            ref = ref_of(value, "name", "id")
            t = site.types.get(ref or "") or site.types_by_id.get(ref or "")
            if t is None:
                errors["issuetype"] = "Specify a valid issue type"
            else:
                issue["type"] = t["name"]
        elif key == "resolution":
            ref = ref_of(value, "name", "id")
            issue["resolution"] = None if ref is None else dict(DONE_RESOLUTION, name=ref)
        elif key == "duedate":
            issue["duedate"] = value
        else:
            errors[name] = (f"Field '{name}' cannot be set. It is not on the appropriate screen, or unknown.")
    if errors:
        raise rest_error(400, [], errors)
    issue["updated"] = jira_stamp(now)


def resolution_obj(site: Site, resolution: dict | None) -> dict | None:
    if not resolution:
        return None
    return {"self": f"{api(site)}/rest/api/3/resolution/{resolution['id']}", **resolution}


def decorate(site: Site, payload: dict) -> dict:
    """Swap the stored resolution for its REST shape wherever an issue was rendered."""
    fields = payload.get("fields") or {}
    if fields.get("resolution"):
        fields["resolution"] = resolution_obj(site, fields["resolution"])
    return payload


def issue_payload(site: Site, issue: dict, fields: list[str] | None = None, fmt: str | None = None,
                  expand: str | None = None) -> dict:
    return decorate(site, render.issue_obj(site, issue, fields, fmt, expand))


# --- tool base -----------------------------------------------------------------------------------------------------

class AtlassianTool(Tool):
    cloud_required = True

    def __init__(self, store: StateStore, schemas: dict[str, dict]) -> None:
        self.store = store
        spec = schemas[self.name]
        self.description = spec["description"]
        self.input_schema = spec["inputSchema"]
        hints = spec.get("annotations") or {}
        if hints:
            self.annotations = {k: hints[k] for k in HINTS if k in hints}
            if hints.get("title"):
                self.title = hints["title"]

    def site(self, args: dict, ctx: CallContext) -> Site:
        site = self.store.read(ctx.conversation_id)
        if self.cloud_required or args.get("cloudId"):
            resolve_cloud(site, args.get("cloudId"))
        return site

    def run(self, args: dict, ctx: CallContext) -> Any:
        scope = f"/v/{self.store.view_token(ctx.conversation_id)}" if ctx.conversation_id else ""
        token = render.VIEW_SCOPE.set(scope)
        try:
            return self.call(args, ctx)
        finally:
            render.VIEW_SCOPE.reset(token)

    def call(self, args: dict, ctx: CallContext) -> Any:
        return self.handle(self.site(args, ctx), args, ctx)

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        raise NotImplementedError


class WriteTool(AtlassianTool):
    def call(self, args: dict, ctx: CallContext) -> Any:
        resolve_cloud(self.store.read(ctx.conversation_id), args.get("cloudId"))
        with self.store.write(ctx.conversation_id) as site:
            return self.mutate(site, args, ctx)

    def mutate(self, site: Site, args: dict, ctx: CallContext) -> Any:
        raise NotImplementedError


# --- account and site ----------------------------------------------------------------------------------------------

class UserInfo(AtlassianTool):
    name = "atlassianUserInfo"
    cloud_required = False

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        u = site.current_user
        return compact({"account_id": u["accountId"], "account_status": "active", "name": u["displayName"],
                        "picture": render.avatar(u), "created_at": u["createdAt"], "last_updated": ctx.clock.iso(),
                        "email": u["email"], "characteristics": {"not_mentionable": False},
                        "extended_profile": {"phone_numbers": [], "team_type": u["teamType"]}, "locale": "en-US",
                        "nickname": u["displayName"], "account_type": "atlassian", "email_verified": True})


class AccessibleResources(AtlassianTool):
    name = "getAccessibleAtlassianResources"
    cloud_required = False

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        meta = site.data["site"]
        base = {"id": meta["cloudId"], "url": site_url(), "name": meta["name"]}
        return compact([{**base, "scopes": meta["confluenceScopes"], "avatarUrl": meta["avatarUrl"]},
                        {**base, "scopes": meta["jiraScopes"], "avatarUrl": meta["avatarUrl"]}])


class LookupAccount(AtlassianTool):
    name = "lookupJiraAccountId"

    @staticmethod
    def highlight(text: str, needle: str) -> str:
        m = re.search(r"(?i)(?<![\w])" + re.escape(needle), text)
        if not m:
            return text
        return f"{text[:m.start()]}<strong>{m.group(0)}</strong>{text[m.end():]}"

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        needle = str(args.get("searchString") or "").strip()
        users = []
        if needle:
            low = needle.lower()
            for u in site.data["users"]:
                words = [w.lower() for w in u["displayName"].split()]
                if any(w.startswith(low) for w in words) or u["displayName"].lower().startswith(low) or \
                        u["email"].lower().startswith(low) or low == u["accountId"].lower():
                    html = f"{self.highlight(u['displayName'], needle)} - {self.highlight(u['email'], needle)}"
                    users.append({"accountId": u["accountId"], "accountType": "atlassian", "html": html,
                                  "displayName": u["displayName"]})
        n = len(users)
        return pretty({"data": {"users": {"users": users, "total": n, "header": f"Showing {n} of {n} matching users"},
                                "groups": {"header": "Showing 0 of 0 matching groups", "total": 0, "groups": []}},
                       "statusCode": 200})


# --- Jira reads ----------------------------------------------------------------------------------------------------

class GetIssue(AtlassianTool):
    name = "getJiraIssue"

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        issue = find_issue(site, args["issueIdOrKey"])
        return pretty(issue_payload(site, issue, args.get("fields"), args.get("responseContentFormat"),
                                    args.get("expand")))


class SearchJql(AtlassianTool):
    name = "searchJiraIssuesUsingJql"

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        mode = args.get("searchResultMode") or "issues"
        try:
            found = jql.search(site, str(args.get("jql") or ""), ctx.clock.now)
        except (jql.JqlError, KeyError, ValueError):
            # The live server answers an invalid query or unknown field with an empty, final page.
            return pretty({"issues": [], "isLast": True} if mode != "count" else {"issues": [], "totalCount": 0})
        if mode == "count":
            return pretty({"issues": [], "totalCount": len(found)})
        size = max(1, min(int(args.get("maxResults") or 50), 100))
        start = 0
        token = args.get("nextPageToken")
        if token:
            try:
                start = int(base64.urlsafe_b64decode(token.encode() + b"==").decode().split(":")[1])
            except (ValueError, IndexError):
                raise rest_error(400, ["The provided next page token is invalid or expired."])
        page = found[start:start + size]
        out: dict[str, Any] = {"issues": [issue_payload(site, i, args.get("fields"),
                                                        args.get("responseContentFormat")) for i in page]}
        if start + size < len(found):
            out["nextPageToken"] = base64.urlsafe_b64encode(f"offset:{start + size}".encode()).decode().rstrip("=")
            out["isLast"] = False
        else:
            out["isLast"] = True
        if mode == "all":
            out["totalCount"] = len(found)
        return pretty(out)


class GetTransitions(AtlassianTool):
    name = "getTransitionsForJiraIssue"

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        find_issue(site, args["issueIdOrKey"])
        transitions = render.transitions_list(site)
        if args.get("transitionId"):
            transitions = [t for t in transitions if t["id"] == str(args["transitionId"])]
        return pretty({"expand": "transitions", "transitions": transitions})


class RemoteLinks(AtlassianTool):
    name = "getJiraIssueRemoteIssueLinks"

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        issue = find_issue(site, args["issueIdOrKey"])
        links = site.data["remoteLinks"].get(issue["key"], [])
        if args.get("globalId"):
            links = [x for x in links if x.get("globalId") == args["globalId"]]
        return pretty(links)


class VisibleProjects(AtlassianTool):
    name = "getVisibleJiraProjects"

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        size = int(args.get("maxResults") or 50)
        start = int(args.get("startAt") or 0)
        needle = str(args.get("searchString") or "").lower()
        p = site.project
        values = [render.project_value(site)] if not needle or needle in p["key"].lower() or \
            needle in p["name"].lower() else []
        if args.get("expandIssueTypes") is False:
            for v in values:
                v.pop("issueTypes", None)
        page = values[start:start + size]
        action = args.get("action") or "create"
        out = {"self": f"{api(site)}/rest/api/3/project/search?expand=issueTypes&maxResults={size}"
                       f"&action={action}&startAt={start}",
               "maxResults": size, "startAt": start, "total": len(values),
               "isLast": start + size >= len(values), "values": page}
        return pretty(out)


class IssueTypesMetadata(AtlassianTool):
    name = "getJiraProjectIssueTypesMetadata"

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        p = find_project(site, args["projectIdOrKey"])
        types = []
        for t in site.data["issueTypes"]:
            obj = render.issuetype_obj(site, t, entity=True)
            obj.pop("avatarId")
            obj["untranslatedName"] = t["name"]
            obj["scope"] = {"type": "PROJECT", "project": {"id": p["id"]}}
            types.append(obj)
        start = int(args.get("startAt") or 0)
        size = int(args.get("maxResults") or 50)
        return pretty({"startAt": start, "maxResults": size, "total": len(types),
                       "issueTypes": types[start:start + size]})


class IssueTypeFields(AtlassianTool):
    name = "getJiraIssueTypeMetaWithFields"

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        find_project(site, args["projectIdOrKey"])
        t = site.types_by_id.get(str(args["issueTypeId"]))
        if t is None:
            raise rest_error(404, ["The issue type selected is invalid."])
        user_url = f"{api(site)}/rest/api/3/user/recommend?context="

        def field(fid, name, schema, required=False, ops=("set",), **extra):
            out = {"required": required, "schema": schema, "name": name, "key": fid}
            if "autoCompleteUrl" in extra:
                out["autoCompleteUrl"] = extra.pop("autoCompleteUrl")
            out["hasDefaultValue"] = extra.pop("hasDefaultValue", False)
            out["operations"] = list(ops)
            if "allowedValues" in extra:
                out["allowedValues"] = extra.pop("allowedValues")
            out["fieldId"] = fid
            return out

        fields = [
            field("issuetype", "Issue Type", {"type": "issuetype", "system": "issuetype"}, True, (),
                  allowedValues=[render.issuetype_obj(site, t)]),
            field("project", "Project", {"type": "project", "system": "project"}, True,
                  allowedValues=[render.project_obj(site)]),
            field("reporter", "Reporter", {"type": "user", "system": "reporter"}, True,
                  autoCompleteUrl=f"{user_url}Reporter&issueKey=", hasDefaultValue=True),
            field("summary", "Summary", {"type": "string", "system": "summary"}, True),
            field("description", "Description", {"type": "string", "system": "description"}),
            field("assignee", "Assignee", {"type": "user", "system": "assignee"},
                  autoCompleteUrl=f"{user_url}Assignee&issueKey="),
            field("priority", "Priority", {"type": "priority", "system": "priority"}, hasDefaultValue=True,
                  allowedValues=[render.priority_obj(site, p["name"]) for p in site.data["priorities"]]),
            field("labels", "Labels", {"type": "array", "items": "string", "system": "labels"},
                  ops=("add", "set", "remove"),
                  autoCompleteUrl=f"{api(site)}/rest/api/1.0/labels/suggest?query="),
            field("parent", "Parent", {"type": "issuelink", "system": "parent"}),
            field("customfield_10020", "Sprint",
                  {"type": "array", "items": "json", "custom": "com.pyxis.greenhopper.jira:gh-sprint",
                   "customId": 10020}),
            field("timetracking", "Time tracking", {"type": "timetracking", "system": "timetracking"},
                  ops=("set", "edit")),
            field("duedate", "Due date", {"type": "date", "system": "duedate"}),
            field("components", "Components", {"type": "array", "items": "component", "system": "components"},
                  ops=("add", "set", "remove"), allowedValues=[]),
            field("issuelinks", "Linked Issues", {"type": "array", "items": "issuelinks", "system": "issuelinks"},
                  ops=("add",), autoCompleteUrl=f"{api(site)}/rest/api/2/issue/picker?currentProjectId="
                                                f"&showSubTaskParent=true&showSubTasks=true&currentIssueKey=null"
                                                f"&currentProjectId={site.project['id']}&query="),
        ]
        if t["subtask"]:
            fields[8]["required"] = True
        if args.get("requiredFieldsOnly"):
            fields = [f for f in fields if f["required"]]
        start = int(args.get("startAt") or 0)
        size = int(args.get("maxResults") or 50)
        return pretty({"startAt": start, "maxResults": size, "total": len(fields),
                       "fields": fields[start:start + size]})


class LinkTypes(AtlassianTool):
    name = "getIssueLinkTypes"

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        return pretty({"issueLinkTypes": [render.link_type_obj(site, t["name"]) for t in site.data["linkTypes"]]})


# --- Jira writes ---------------------------------------------------------------------------------------------------

class CreateIssue(WriteTool):
    name = "createJiraIssue"

    def mutate(self, site: Site, args: dict, ctx: CallContext) -> Any:
        find_project(site, args["projectKey"])
        t = site.types.get(str(args["issueTypeName"]).strip().title()) or next(
            (x for x in site.data["issueTypes"] if x["name"].lower() == str(args["issueTypeName"]).lower()), None)
        if t is None:
            raise rest_error(400, [], {"issuetype": "Specify a valid issue type"})
        issue_id, key = site.next_issue()
        now = jira_stamp(ctx.clock.now)
        issue = {"id": issue_id, "key": key, "type": t["name"], "summary": "", "description": None,
                 "status": "To Do", "priority": site.data.get("defaultPriority", "Medium"), "assignee": None,
                 "reporter": site.current_user["key"],
                 "labels": [], "sprint": None, "estimateHours": None, "created": now, "updated": now,
                 "comments": [], "links": [], "worklogs": [], "resolution": None, "parent": None, "components": []}
        fields: dict[str, Any] = {"summary": args["summary"]}
        if args.get("description") is not None:
            fields["description"] = args["description"]
        if args.get("assignee_account_id"):
            fields["assignee"] = args["assignee_account_id"]
        if args.get("parent"):
            fields["parent"] = args["parent"]
        fields.update(args.get("additional_fields") or {})
        apply_fields(site, issue, fields, ctx.clock.now)
        if t["subtask"] and not issue["parent"]:
            raise rest_error(400, [], {"parent": "Given parent work item does not belong to appropriate hierarchy."})
        if args.get("transition"):
            move(site, issue, str(args["transition"]["id"]))
        site.data["issues"].append(issue)
        site.data["created"].append(key)
        site.derive()
        return pretty({"id": issue_id, "key": key, "self": f"{api(site)}/rest/api/3/issue/{issue_id}"})


def move(site: Site, issue: dict, transition_id: str) -> None:
    t = next((x for x in site.data["transitions"] if x["id"] == transition_id), None)
    if t is None:
        raise rest_error(400, [f"Transition id '{transition_id}' is not valid for this issue."])
    status = site.statuses_by_id[t["to"]]
    issue["status"] = status["name"]
    issue["resolution"] = dict(DONE_RESOLUTION) if status["category"] == 3 else None


class EditIssue(WriteTool):
    name = "editJiraIssue"

    def mutate(self, site: Site, args: dict, ctx: CallContext) -> Any:
        issue = find_issue(site, args["issueIdOrKey"])
        fields = args.get("fields") or {}
        if "status" in fields:
            raise rest_error(400, [], {"status": "Field 'status' cannot be set. Use transitionJiraIssue to "
                                                 "change the status."})
        apply_fields(site, issue, fields, ctx.clock.now)
        site.derive()
        return pretty(issue_payload(site, issue, None, args.get("responseContentFormat")))


class TransitionIssue(WriteTool):
    name = "transitionJiraIssue"

    def mutate(self, site: Site, args: dict, ctx: CallContext) -> Any:
        issue = find_issue(site, args["issueIdOrKey"])
        move(site, issue, str(args["transition"]["id"]))
        if args.get("fields"):
            apply_fields(site, issue, args["fields"], ctx.clock.now)
        for op in (args.get("update") or {}).get("comment", []):
            text = as_markdown((op.get("add") or {}).get("body"))
            if text:
                add_comment(site, issue, text, ctx.clock.now)
        issue["updated"] = jira_stamp(ctx.clock.now)
        site.derive()
        return pretty(issue_payload(site, issue))


def add_comment(site: Site, issue: dict, text: str, now: datetime) -> dict:
    stamp = jira_stamp(now)
    comment = {"id": site.next_id("comment", 10500), "author": site.current_user["key"], "body": text,
               "created": stamp, "updated": stamp}
    issue["comments"].append(comment)
    issue["updated"] = stamp
    return comment


class AddComment(WriteTool):
    name = "addCommentToJiraIssue"

    def mutate(self, site: Site, args: dict, ctx: CallContext) -> Any:
        issue = find_issue(site, args["issueIdOrKey"])
        text = as_markdown(args["commentBody"])
        if not text.strip():
            raise rest_error(400, [], {"comment": "Comment body can not be empty!"})
        if args.get("commentId"):
            comment = next((c for c in issue["comments"] if c["id"] == str(args["commentId"])), None)
            if comment is None:
                raise rest_error(404, ["Can not find a comment for the id: " + str(args["commentId"]) + "."])
            comment["body"] = text
            comment["updated"] = jira_stamp(ctx.clock.now)
        else:
            comment = add_comment(site, issue, text, ctx.clock.now)
        out = render.comment_obj(site, issue, comment, args.get("responseContentFormat"), full=True)
        if args.get("commentVisibility"):
            out["visibility"] = dict(args["commentVisibility"], identifier=args["commentVisibility"]["value"])
        return pretty(out)


class AddWorklog(WriteTool):
    name = "addWorklogToJiraIssue"

    def mutate(self, site: Site, args: dict, ctx: CallContext) -> Any:
        issue = find_issue(site, args["issueIdOrKey"])
        stamp = jira_stamp(ctx.clock.now)
        seconds = render.parse_duration(str(args.get("timeSpent") or "")) if args.get("timeSpent") else None
        if args.get("timeSpent") and not seconds:
            raise rest_error(400, [], {"timeLogged": "Invalid time duration entered."})
        if args.get("worklogId"):
            log = next((w for w in issue["worklogs"] if w["id"] == str(args["worklogId"])), None)
            if log is None:
                raise rest_error(404, ["Cannot find worklog with id: " + str(args["worklogId"])])
            if seconds:
                log["timeSpentSeconds"] = seconds
        else:
            if not seconds:
                raise rest_error(400, [], {"timeLogged": "You must indicate the time spent working."})
            log = {"id": site.next_id("worklog", 10700), "author": site.current_user["key"],
                   "timeSpentSeconds": seconds, "started": args.get("started") or stamp, "created": stamp}
            issue["worklogs"].append(log)
        if args.get("commentBody"):
            log["comment"] = as_markdown(args["commentBody"])
        if args.get("started"):
            log["started"] = args["started"]
        log["updated"] = stamp
        issue["updated"] = stamp
        return pretty(render.worklog_obj(site, issue, log))


def link_issues(site: Site, inward: dict, outward: dict, type_name: str) -> dict:
    t = next((x for x in site.data["linkTypes"] if type_name.lower() in
              (x["name"].lower(), x["inward"].lower(), x["outward"].lower())), None)
    if t is None and type_name.lower() in ("clones", "clone"):
        t = site.link_types["Cloners"]
    if t is None:
        raise rest_error(404, [f"No issue link type with name '{type_name}' found."])
    link = {"id": site.next_id("link", 10600), "type": t["name"], "outward": outward["key"]}
    inward["links"].append(link)
    return link


class CreateLink(WriteTool):
    name = "createIssueLink"

    def mutate(self, site: Site, args: dict, ctx: CallContext) -> Any:
        inward = find_issue(site, args["inwardIssue"])
        outward = find_issue(site, args["outwardIssue"])
        link = link_issues(site, inward, outward, str(args["type"]))
        if args.get("comment"):
            add_comment(site, outward, as_markdown(args["comment"]), ctx.clock.now)
        site.derive()
        # The REST call answers 201 with no body; the mock describes the link it made instead.
        rendered = next(x for x in render.issue_links(site, inward) if x["id"] == link["id"])
        return pretty({"success": True, "message": f"Linked {inward['key']} {rendered['type']['outward']} "
                                                   f"{outward['key']}.", "link": rendered})


# --- Teamwork Graph ------------------------------------------------------------------------------------------------

def issue_from_identifier(site: Site, text: str) -> dict | None:
    text = str(text or "").strip()
    m = re.search(r"issue/([^/?#]+)$", text) or re.search(r"/browse/([A-Za-z]+-\d+)", text)
    return site.issue(m.group(1) if m else text)


def graph_target(site: Site, issue: dict) -> dict:
    return {"ari": render.issue_ari(site, issue), "type": "JiraWorkItem", "__typename": "JiraWorkItem",
            "summary": issue["summary"], "webUrl": render.browse_url(issue["key"])}


def graph_user(user: dict) -> dict:
    return {"ari": render.user_ari(user), "type": "AtlassianUser", "__typename": "AtlassianUser",
            "userName": user["displayName"]}


TTL_WARNING = ("The following relationships are TTL-limited and were truncated to the retention window of 90 days: "
               "atlassian_user_created_jira_work_item, atlassian_user_updated_jira_work_item, "
               "jira_work_item_has_changed_jira_priority, jira_work_item_has_changed_jira_status, "
               "jira_work_item_shared_with_atlassian_user")


class GraphContext(AtlassianTool):
    name = "getTeamworkGraphContext"

    def relationships(self, site: Site, issue: dict) -> list[dict]:
        rels: list[dict] = []

        def add(name: str, kind: str, targets: list[dict]) -> None:
            if targets:
                rels.append({"relationshipName": name, "targetObjectType": kind, "targets": targets})

        assignee = site.users.get(issue.get("assignee") or "")
        reporter = site.users.get(issue.get("reporter") or "")
        if assignee:
            add("atlassian_user_assigned_jira_work_item", "AtlassianUser", [graph_user(assignee)])
            add("atlassian_user_assigned_work_items", "AtlassianUser", [graph_user(assignee)])
        if reporter:
            add("atlassian_user_reported_jira_work_item", "AtlassianUser", [graph_user(reporter)])
        children = [i for i in site.data["issues"] if i.get("parent") == issue["key"]]
        add("jira_work_item_has_child_jira_work_item", "JiraWorkItem", [graph_target(site, c) for c in children])
        parent = site.issue(issue.get("parent"))
        add("jira_work_item_has_parent_jira_work_item", "JiraWorkItem", [graph_target(site, parent)] if parent else [])
        blocks, linked = [], []
        for link in render.issue_links(site, issue):
            other = site.issue((link.get("outwardIssue") or link.get("inwardIssue"))["key"])
            if link["type"]["name"] == "Blocks" and "outwardIssue" in link:
                blocks.append(graph_target(site, other))
            else:
                linked.append(graph_target(site, other))
        add("jira_work_item_blocks_jira_work_item", "JiraWorkItem", blocks)
        add("jira_work_item_links_jira_work_item", "JiraWorkItem", linked)
        return rels

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        kind = args["objectType"]
        ident = str(args["objectIdentifier"])
        cid = site.data["site"]["cloudId"]
        if kind == "JiraWorkItem":
            issue = issue_from_identifier(site, ident)
            if issue is None:
                raise JiraError({"error": True, "message": f"Could not resolve JiraWorkItem '{ident}'."})
            rels = self.relationships(site, issue)
            if args.get("relationshipTypes"):
                wanted = {r.replace("-", "_") for r in args["relationshipTypes"]}
                rels = [r for r in rels if r["relationshipName"] in wanted]
            if args.get("targetObjectTypes"):
                rels = [r for r in rels if r["targetObjectType"] in set(args["targetObjectTypes"])]
            obj = {"ari": render.issue_ari(site, issue), "type": "JiraWorkItem", "key": issue["key"],
                   "summary": issue["summary"], "webUrl": render.browse_url(issue["key"])}
            if (args.get("detailLevel") or "summary") == "summary":
                summary = [{"relationshipName": r["relationshipName"], "targetObjectType": r["targetObjectType"],
                            "count": len(r["targets"])} for r in rels]
                return compact({"data": {"data": {"object": obj, "relationshipSummary": summary},
                                         "hints": ["Call getTeamworkGraphContext with detailLevel \"full\" to get "
                                                   "the related objects."],
                                         "warnings": [TTL_WARNING]}})
            first = int(args.get("first") or 50)
            for r in rels:
                r["targets"] = r["targets"][:first]
            return compact({"data": {"data": {"object": obj, "relationships": rels,
                                              "pagination": {"hasNextPage": False, "endCursor": None}},
                                     "hints": ["Call getTeamworkGraphObject with the ARIs from this response to get "
                                               "full object content."],
                                     "warnings": [TTL_WARNING]}})
        if kind == "JiraSprint":
            m = re.search(r"(\d+)$", ident)
            semantic = "Semantic Error: Node type for ATI 'ati:cloud:jira-software:sprint' not found."
            return compact({"data": {"data": {"object": {"ari": render.sprint_ari(site, m.group(1) if m else ident),
                                                         "type": "JiraSprint"}, "relationshipSummary": []},
                                     "errors": ["\n".join([semantic] * 5),
                                                "The field at path '/graphStore/cypherQueryV2' was declared as a non "
                                                "null type, but the code involved in retrieving data has wrongly "
                                                "returned a null value.  The graphql specification requires that the "
                                                "parent field be set to null, or if that is non nullable that it "
                                                "bubble up null to its parent and so on. The non-nullable type is "
                                                "'GraphStoreCypherQueryV2Connection' within parent type "
                                                "'GraphStore'"]}})
        if kind == "JiraSpace":
            p = site.project
            if ident.upper() not in (p["key"], p["id"]) and not ident.endswith(f"project/{p['id']}"):
                raise project_not_found(ident)
            return compact({"data": {"data": {"object": {"ari": f"ari:cloud:jira:{cid}:project/{p['id']}",
                                                         "type": "JiraSpace"}, "relationshipSummary": []}}})
        raise JiraError({"error": True, "message": "TWG request failed: 403 Forbidden. "
                                                   "{\"errors\":[\"Insufficient OAuth scopes. Required scope: "
                                                   "read:all:twg\"]}"})


class GraphObject(AtlassianTool):
    name = "getTeamworkGraphObject"

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        objects, errors = [], []
        for ident in args.get("objects") or []:
            issue = issue_from_identifier(site, ident)
            if issue is None:
                errors.append(f"Could not hydrate object '{ident}'.")
                continue
            objects.append({"ari": render.issue_ari(site, issue), "type": "JiraWorkItem",
                            "raw": render.graph_issue_raw(site, issue)})
        data: dict[str, Any] = {"data": {"objects": objects}}
        if errors:
            data["errors"] = errors
        return compact({"data": data})


class AddGraphContext(WriteTool):
    name = "addTeamworkGraphContext"

    def mutate(self, site: Site, args: dict, ctx: CallContext) -> Any:
        kind = args["relationshipType"]
        if kind not in ("jira-work-item-links-jira-work-item", "jira-work-item-blocks-jira-work-item"):
            raise JiraError({"error": True, "message": f"Relationship type '{kind}' needs objects this site "
                                                       "doesn't have (Atlas projects, goals or remote links)."})
        source = issue_from_identifier(site, args["objectIdentifier"])
        target = issue_from_identifier(site, args["targetObjectIdentifier"])
        if source is None or target is None:
            raise issue_not_found()
        link_issues(site, source, target, "Blocks" if kind.endswith("blocks-jira-work-item") else "Relates")
        site.derive()
        # Inferred response: the live server's success shape wasn't captured.
        return compact({"data": {"success": True, "relationshipType": kind,
                                 "from": render.issue_ari(site, source), "to": render.issue_ari(site, target)}})


# --- Rovo search and fetch -----------------------------------------------------------------------------------------

class RovoSearch(AtlassianTool):
    name = "search"
    cloud_required = False

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        terms = [t for t in re.findall(r"[\w-]+", str(args["query"]).lower()) if len(t) > 1]
        scored = []
        for issue in site.data["issues"]:
            title = f"{issue['key']} {issue['summary']}".lower()
            text = " ".join([issue.get("description") or ""] + [c["body"] for c in issue.get("comments", [])] +
                            issue.get("labels", [])).lower()
            score = sum(3 for t in terms if t in title) + sum(1 for t in terms if t in text)
            if score:
                scored.append((score, -int(issue["id"]), "issue", issue))
        for page in site.data["confluence"]["pages"]:
            if page["status"] != "current":
                continue
            title, text = page["title"].lower(), page_text(site, page)
            score = sum(3 for t in terms if t in title) + sum(1 for t in terms if t in text)
            if score:
                scored.append((score, -int(page["id"]), "page", page))
        scored.sort(key=lambda x: (-x[0], x[1]))
        cid = site.data["site"]["cloudId"]
        results = []
        for _, _, kind, item in scored[:10]:
            if kind == "issue":
                results.append({"id": render.issue_ari(site, item), "title": f"{item['key']}: {item['summary']}",
                                "text": render.snippet(item.get("description")), "url": render.browse_url(item["key"]),
                                "type": "issue", "metadata": {"cloudId": cid, "searchScope": "generic"}})
            else:
                results.append({"id": render.page_ari(site, item), "title": item["title"],
                                "text": render.snippet(item.get("body")), "url": render.page_url(site, item),
                                "type": "page", "metadata": {"cloudId": cid, "searchScope": "generic"}})
        return compact({"results": results})


class RovoFetch(AtlassianTool):
    name = "fetch"
    cloud_required = False

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        ident = str(args["id"]).strip()
        if ":confluence:" in ident:
            page = site.pages.get(ident.rsplit("/", 1)[-1])
            if page is None or page["status"] != "current":
                raise JiraError({"error": True, "message": "Confluence page not found."})
            space = site.spaces.get(page["spaceId"]) or {}
            return pretty({"id": render.page_ari(site, page), "title": page["title"], "text": page.get("body") or "",
                           "url": render.page_url(site, page), "type": "confluence-page",
                           "metadata": {"cloudId": site.data["site"]["cloudId"], "spaceKey": space.get("key"),
                                        "spaceName": space.get("name"),
                                        "author": site.users[page["author"]]["displayName"],
                                        "lastModifiedBy": site.users[page.get("updatedBy") or page["author"]][
                                            "displayName"],
                                        "created": page["created"], "lastModified": page["updated"],
                                        "version": page["version"]}})
        issue = issue_from_identifier(site, ident)
        if issue is None:
            raise issue_not_found()
        cid = site.data["site"]["cloudId"]

        def name(key):
            u = site.users.get(key or "")
            return u["displayName"] if u else None

        return pretty({"id": f"ari:cloud:jira:{cid}:issue/{issue['key']}", "title": issue["summary"],
                       "text": issue.get("description") or "", "url": f"{api(site)}/rest/api/3/issue/{issue['id']}",
                       "type": "jira-issue",
                       "metadata": {"cloudId": cid, "status": issue["status"], "assignee": name(issue.get("assignee")),
                                    "priority": issue.get("priority"), "issueType": issue["type"],
                                    "reporter": name(issue.get("reporter")), "created": issue["created"],
                                    "updated": issue["updated"]}})


# --- Confluence ----------------------------------------------------------------------------------------------------

FORMAT_TOOLS = ("createConfluencePage", "updateConfluencePage")
# Mock-authored guidance: the live server's HTML guide wasn't captured.
FORMAT_GUIDE = (
    "# Confluence page body format (HTML)\n\n"
    "When contentFormat is \"html\" (the default), write the body as structured HTML. Use <h1>-<h6> for headings, "
    "<p> for paragraphs, <strong> for bold, <ul>/<ol> with <li> for lists, <table> with <tr>, <th> and <td> for "
    "tables, and <a href=\"...\"> for links. Don't wrap the body in <html> or <body>. To write Markdown instead, pass "
    "contentFormat \"markdown\". Write real content: don't create blank or placeholder pages."
)


class FormatGuide(AtlassianTool):
    name = "getContentFormatGuide"
    cloud_required = False

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        tool = str(args["toolName"])
        if tool in FORMAT_TOOLS:
            return FORMAT_GUIDE
        return pretty({"error": True, "toolName": tool,
                       "message": f"No description registered for tool \"{tool}\". Supported tools: "
                                  f"{', '.join(FORMAT_TOOLS)}.",
                       "supportedToolNames": list(FORMAT_TOOLS),
                       "howToFix": "Retry this exact call with toolName: \"createConfluencePage\". Do not proceed "
                                   "without this guidance, and do not create blank or placeholder content as a "
                                   "fallback."})


def confluence_missing(what: str, ident: Any) -> JiraError:
    # Mock-defined wording, modelled on the Confluence v2 REST error body.
    return JiraError({"error": True, "message": compact({"errors": [{"status": 404, "code": "NOT_FOUND",
                                                                     "title": f"{what} {ident} not found",
                                                                     "detail": None}]}), "statusCode": 404})


def confluence_bad_request(title: str) -> JiraError:
    return JiraError({"error": True, "message": compact({"errors": [{"status": 400, "code": "INVALID_REQUEST_PARAMETER",
                                                                     "title": title, "detail": None}]}),
                      "statusCode": 400})


def wiki_stamp(now: datetime) -> str:
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


def account(site: Site, key: str | None) -> str | None:
    u = site.users.get(key or "")
    return u["accountId"] if u else None


def find_page(site: Site, ref: Any) -> dict:
    page = site.pages.get(str(ref or "").strip())
    if page is None or page["status"] == "deleted":
        raise confluence_missing("Page", ref)
    return page


def find_space(site: Site, ref: Any) -> dict:
    space = site.space(str(ref or ""))
    if space is None:
        raise confluence_missing("Space", ref)
    return space


def stored_body(value: Any, fmt: str | None) -> str:
    """Page and comment bodies are stored as markdown, whatever format they arrive in."""
    if fmt == "adf" or isinstance(value, dict):
        return as_markdown(value)
    if fmt == "markdown":
        return str(value or "")
    return render.from_html(str(value or ""))


def body_obj(text: str, fmt: str | None) -> dict:
    if fmt == "adf":
        return {"atlas_doc_format": {"value": compact(render.to_adf(text)), "representation": "atlas_doc_format"}}
    if fmt == "html":
        return {"storage": {"value": render.to_html(text), "representation": "storage"}}
    return {"markdown": {"value": text, "representation": "markdown"}}


def space_obj(site: Site, space: dict) -> dict:
    return {"spaceOwnerId": account(site, space.get("owner")), "authorId": account(site, space.get("author")),
            "homepageId": space.get("homepageId"), "createdAt": space["created"], "icon": None,
            "name": space["name"], "key": space["key"], "id": space["id"], "type": space["type"],
            "description": {"plain": {"value": space.get("description") or "", "representation": "plain"}},
            "status": space["status"], "_links": {"webui": f"/spaces/{space['key']}"},
            "currentActiveAlias": space["key"]}


def page_obj(site: Site, page: dict, fmt: str | None = "markdown", with_body: bool = True) -> dict:
    out = {"parentType": "page" if page.get("parentId") else None, "parentId": page.get("parentId"),
           "spaceId": page["spaceId"], "ownerId": account(site, page["author"]),
           "lastOwnerId": None, "createdAt": page["created"], "authorId": account(site, page["author"]),
           "position": int(page["id"]) % 1000, "version": {
               "number": page["version"], "message": page.get("versionMessage") or "", "minorEdit": False,
               "authorId": account(site, page.get("updatedBy") or page["author"]), "createdAt": page["updated"]},
           "title": page["title"], "status": page["status"], "id": page["id"]}
    if with_body:
        out["body"] = body_obj(page.get("body") or "", fmt)
    out["labels"] = {"results": [{"id": str(9000 + i), "name": x, "prefix": "global"}
                                 for i, x in enumerate(page.get("labels", []))]}
    path = render.page_path(site, page)
    out["_links"] = {"editui": f"/pages/resumedraft.action?draftId={page['id']}", "webui": path,
                     "edituiv2": f"/spaces/{path.split('/')[2]}/pages/edit-v2/{page['id']}",
                     "tinyui": f"/x/{base64.urlsafe_b64encode(int(page['id']).to_bytes(4, 'little')).decode().rstrip('=')}",
                     "base": render.wiki_base()}
    return out


def wiki_comment_obj(site: Site, c: dict, fmt: str | None) -> dict:
    page = site.pages.get(c["pageId"])
    out = {"id": c["id"], "status": "current", "title": f"Re: {page['title'] if page else ''}",
           "pageId": c["pageId"], "version": {"createdAt": c.get("updated") or c["created"], "message": "",
                                              "number": c.get("version", 1), "minorEdit": False,
                                              "authorId": account(site, c["author"])},
           "body": body_obj(c["body"], fmt)}
    if c.get("parentId"):
        out["parentCommentId"] = c["parentId"]
    if c["type"] == "inline":
        out["resolutionStatus"] = c.get("resolutionStatus", "open")
        out["properties"] = {"inlineMarkerRef": c.get("markerRef", ""),
                             "inlineOriginalSelection": c.get("selection", "")}
    out["_links"] = {"webui": f"{render.page_path(site, page) if page else ''}?focusedCommentId={c['id']}"}
    return out


def visible_pages(site: Site, space: dict | None = None) -> list[dict]:
    return [p for p in site.data["confluence"]["pages"]
            if p["status"] == "current" and (space is None or p["spaceId"] == space["id"])]


def paged(results: list, args: dict, default: int = 25, cap: int = 250) -> list:
    return results[:max(1, min(int(args.get("limit") or default), cap))]


class ConfluenceSpaces(AtlassianTool):
    name = "getConfluenceSpaces"

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        def as_list(value):
            if value is None:
                return None
            return [str(x).strip() for x in (value if isinstance(value, list) else str(value).split(","))]

        ids, keys = as_list(args.get("ids")), as_list(args.get("keys"))
        labels = as_list(args.get("labels"))
        spaces = []
        for space in site.data["confluence"]["spaces"]:
            if ids and space["id"] not in ids:
                continue
            if keys and space["key"].upper() not in {k.upper() for k in keys}:
                continue
            if args.get("type") and space["type"] != args["type"]:
                continue
            if args.get("status") and space["status"] != args["status"]:
                continue
            if labels and not set(labels) & set(space.get("labels", [])):
                continue
            spaces.append(space_obj(site, space))
        return pretty({"results": paged(spaces, args), "_links": {"base": render.wiki_base()}})


# --- CQL -------------------------------------------------------------------------------------------------------------

_CQL_CLAUSE = re.compile(r"""\s*(?P<field>[\w.]+)\s*(?P<op>!=|!~|~|=|<=|>=|<|>|\bnot\s+in\b|\bin\b)\s*
                             (?P<value>"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\([^)]*\)|[\w.\-()]+)""", re.I | re.X)
_STOP = {"the", "and", "or", "of", "to", "for", "a", "an", "in", "on", "is", "what", "with"}


def _cql_values(raw: str) -> list[str]:
    raw = raw.strip()
    if raw.startswith("("):
        return [v.strip().strip("\"'") for v in raw[1:-1].split(",") if v.strip()]
    return [raw.strip("\"'")]


def _terms(text: str) -> list[str]:
    return [t for t in re.findall(r"[\w-]+", text.lower()) if t not in _STOP and len(t) > 1]


def page_text(site: Site, page: dict) -> str:
    comments = [c["body"] for c in site.data["confluence"]["comments"] if c["pageId"] == page["id"]]
    return " ".join([page["title"], page.get("body") or "", " ".join(page.get("labels", []))] + comments).lower()


def _ancestors(site: Site, page: dict) -> list[str]:
    out, cur = [], page.get("parentId")
    while cur and cur in site.pages and cur not in out:
        out.append(cur)
        cur = site.pages[cur].get("parentId")
    return out


def _clause(site: Site, page: dict, field: str, op: str, values: list[str]) -> tuple[bool, int]:
    """Whether one CQL clause matches a page, and a relevance score for text clauses."""
    field, op = field.lower(), op.lower()
    negate = op in ("!=", "!~") or op.startswith("not")
    space = site.spaces.get(page["spaceId"]) or {}
    users = {page["author"], page.get("updatedBy")}
    score = 0
    if field == "type":
        hit = "page" in [v.lower() for v in values]
    elif field in ("space", "space.key"):
        hit = space.get("key", "").upper() in [v.upper() for v in values]
    elif field == "space.id":
        hit = space.get("id") in values
    elif field in ("space.title", "space.name"):
        hit = any(v.lower() in space.get("name", "").lower() for v in values)
    elif field in ("id", "content", "content.id"):
        hit = page["id"] in values
    elif field == "parent":
        hit = page.get("parentId") in values
    elif field == "ancestor":
        hit = bool(set(_ancestors(site, page)) & set(values))
    elif field in ("label", "labels"):
        hit = bool({v.lower() for v in values} & {x.lower() for x in page.get("labels", [])})
    elif field in ("creator", "contributor", "mention", "watcher", "favourite", "favorite"):
        wanted = set()
        for v in values:
            u = site.current_user if v.lower() == "currentuser()" else site.user(v)
            if u:
                wanted.add(u["key"])
        hit = bool(wanted & ({page["author"]} if field == "creator" else users))
    elif field == "title":
        title = page["title"].lower()
        if op in ("=", "!=", "in", "not in"):
            hit = title in [v.lower() for v in values]
        else:
            terms = _terms(" ".join(values))
            score = sum(3 for t in terms if t in title)
            hit = bool(terms) and all(t in title for t in terms)
    elif field in ("text", "sitesearch"):
        text = page_text(site, page)
        terms = _terms(" ".join(values))
        found = [t for t in terms if t in text]
        score = len(found) + sum(2 for t in found if t in page["title"].lower())
        hit = bool(terms) and len(found) * 2 >= len(terms)
    else:
        hit = True  # created, lastmodified and other fields the mock doesn't model don't filter
    return (not hit if negate else hit), score


def run_cql(site: Site, cql: str) -> list[dict]:
    text = cql.strip()
    order = None
    m = re.search(r"\border\s+by\s+([\w.]+)(\s+(asc|desc))?\s*$", text, re.I)
    if m:
        order = (m.group(1).lower(), (m.group(3) or "asc").lower())
        text = text[:m.start()].strip()
    groups = [g for g in re.split(r"\s+OR\s+", text, flags=re.I) if g.strip()]
    parsed = []
    for g in groups:
        clauses = []
        for part in re.split(r"\s+AND\s+", g.strip().strip("()"), flags=re.I):
            cm = _CQL_CLAUSE.fullmatch(part.strip())
            if not cm:
                raise confluence_bad_request(f"Could not parse cql : {cql}")
            clauses.append((cm.group("field"), re.sub(r"\s+", " ", cm.group("op")), _cql_values(cm.group("value"))))
        parsed.append(clauses)
    scored = []
    for page in visible_pages(site):
        best = None
        for clauses in parsed:
            results = [_clause(site, page, *c) for c in clauses]
            if all(ok for ok, _ in results):
                best = max(best or 0, sum(s for _, s in results))
        if best is not None:
            scored.append((best, page))
    if order:
        key = {"created": "created", "lastmodified": "updated", "title": "title"}.get(order[0], "updated")
        scored.sort(key=lambda x: x[1][key], reverse=order[1] == "desc")
    else:
        scored.sort(key=lambda x: (-x[0], x[1]["updated"]), reverse=False)
        scored.sort(key=lambda x: -x[0])
    return [p for _, p in scored]


def friendly(stamp: str) -> str:
    moment = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    return f"{moment:%b} {moment.day}, {moment.year}"


class ConfluenceCql(AtlassianTool):
    name = "searchConfluenceUsingCql"

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        cql = str(args["cql"])
        limit = max(1, min(int(args.get("limit") or 25), 250))
        pages = run_cql(site, cql)
        results = []
        for page in pages[:limit]:
            space = site.spaces[page["spaceId"]]
            author = site.users.get(page["author"])
            path = render.page_path(site, page)
            results.append({
                "content": {"id": page["id"], "type": "page", "status": page["status"], "title": page["title"],
                            "history": {"latest": True, "createdBy": {
                                "type": "known", "accountId": author["accountId"], "accountType": "atlassian",
                                "email": author["email"], "publicName": author["displayName"],
                                "displayName": author["displayName"], "isExternalCollaborator": False},
                                "createdDate": page["created"]},
                            "_links": {"webui": path, "self": f"{render.wiki_base()}/rest/api/content/{page['id']}",
                                       "tinyui": page_obj(site, page, with_body=False)["_links"]["tinyui"]}},
                "title": page["title"], "excerpt": render.snippet(page.get("body"), 200),
                "url": path, "resultGlobalContainer": {"title": space["name"], "displayUrl": f"/spaces/{space['key']}"},
                "breadcrumbs": [], "entityType": "content", "iconCssClass": "aui-icon content-type-page",
                "lastModified": page["updated"], "friendlyLastModified": friendly(page["updated"]), "score": 0.0})
        return pretty({"results": results, "start": 0, "limit": limit, "size": len(results),
                       "totalSize": len(pages), "cqlQuery": cql, "searchDuration": 41, "archivedResultCount": 0,
                       "_links": {"base": render.wiki_base(), "context": "/wiki",
                                  "self": f"{render.wiki_base()}/rest/api/search?expand=content%2Ccontent.history"
                                          f"&cql={quote(cql, safe='').replace('%20', '+')}"}})


class ConfluencePage(AtlassianTool):
    name = "getConfluencePage"

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        page = find_page(site, args["pageId"])
        return pretty(page_obj(site, page, args.get("contentFormat") or "markdown"))


SORTS = {"id": lambda p: int(p["id"]), "created-date": lambda p: p["created"],
         "modified-date": lambda p: p["updated"], "title": lambda p: p["title"].lower()}


class PagesInSpace(AtlassianTool):
    name = "getPagesInConfluenceSpace"

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        space = find_space(site, args["spaceId"])
        status = args.get("status") or "current"
        pages = [p for p in site.data["confluence"]["pages"] if p["spaceId"] == space["id"] and p["status"] == status]
        if args.get("title"):
            pages = [p for p in pages if str(args["title"]).lower() in p["title"].lower()]
        sort = str(args.get("sort") or "id")
        pages.sort(key=SORTS.get(sort.lstrip("-"), SORTS["id"]), reverse=sort.startswith("-"))
        fmt = args.get("contentFormat")
        results = [page_obj(site, p, fmt, with_body=bool(fmt)) for p in paged(pages, args)]
        return pretty({"results": results, "_links": {"base": render.wiki_base()}})


class PageDescendants(AtlassianTool):
    name = "getConfluencePageDescendants"

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        root = find_page(site, args["pageId"])
        max_depth = int(args.get("depth") or 5)
        out: list[dict] = []

        def walk(parent: dict, depth: int) -> None:
            children = sorted((p for p in visible_pages(site) if p.get("parentId") == parent["id"]),
                              key=lambda p: int(p["id"]))
            for i, child in enumerate(children):
                out.append({"id": child["id"], "status": child["status"], "title": child["title"], "type": "page",
                            "parentId": parent["id"], "depth": depth, "childPosition": i})
                if depth < max_depth:
                    walk(child, depth + 1)

        walk(root, 1)
        return pretty({"results": paged(out, args), "_links": {"base": render.wiki_base()}})


def comments_for(site: Site, page_id: str, kind: str) -> list[dict]:
    return [c for c in site.data["confluence"]["comments"] if c["pageId"] == page_id and c["type"] == kind]


class PageComments(AtlassianTool):
    kind = "footer"

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        page = find_page(site, args["pageId"])
        fmt = args.get("contentFormat") or "markdown"
        all_comments = comments_for(site, page["id"], self.kind)
        top = [c for c in all_comments if not c.get("parentId")]
        if self.kind == "inline" and args.get("resolutionStatus"):
            top = [c for c in top if c.get("resolutionStatus", "open") == args["resolutionStatus"]]
        sort = str(args.get("sort") or "created-date")
        top.sort(key=lambda c: c["created"] if "created" in sort else int(c["id"]), reverse=sort.startswith("-"))
        results = []
        for c in paged(top, args):
            item = wiki_comment_obj(site, c, fmt)
            if args.get("includeReplies"):
                replies = [r for r in all_comments if r.get("parentId") == c["id"]]
                item["replies"] = [wiki_comment_obj(site, r, fmt)
                                   for r in replies[:int(args.get("repliesPerComment") or 25)]]
            results.append(item)
        return pretty({"results": results, "_links": {"base": render.wiki_base()}})


class FooterComments(PageComments):
    name = "getConfluencePageFooterComments"
    kind = "footer"


class InlineComments(PageComments):
    name = "getConfluencePageInlineComments"
    kind = "inline"


class CommentChildren(AtlassianTool):
    name = "getConfluenceCommentChildren"

    def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
        parent = site.wiki_comments.get(str(args["commentId"]))
        if parent is None or parent["type"] != args.get("commentType", parent["type"]):
            raise confluence_missing("Comment", args["commentId"])
        children = [c for c in site.data["confluence"]["comments"] if c.get("parentId") == parent["id"]]
        return pretty({"results": [wiki_comment_obj(site, c, "markdown") for c in children],
                       "_links": {"base": render.wiki_base()}})


class CreatePage(WriteTool):
    name = "createConfluencePage"

    def mutate(self, site: Site, args: dict, ctx: CallContext) -> Any:
        space = find_space(site, args["spaceId"])
        title = str(args.get("title") or "").strip()
        if not title:
            raise confluence_bad_request("A page title is required.")
        if any(p["title"].lower() == title.lower() and p["spaceId"] == space["id"] for p in visible_pages(site)):
            raise confluence_bad_request("A page with this title already exists: A page already exists with the same "
                                         "TITLE in this space")
        parent = find_page(site, args["parentId"]) if args.get("parentId") else site.pages.get(space["homepageId"])
        text = stored_body(args["body"], args.get("contentFormat"))
        if not text.strip():
            raise confluence_bad_request("The page body can't be empty.")
        stamp = wiki_stamp(ctx.clock.now)
        me = site.current_user["key"]
        page = {"id": site.next_id("page", 131500), "parentId": parent["id"] if parent else None, "title": title,
                "author": me, "created": stamp, "updatedBy": me, "updated": stamp, "version": 1, "labels": [],
                "spaceId": space["id"], "status": args.get("status") or "current", "versionMessage": "",
                "body": text}
        site.data["confluence"]["pages"].append(page)
        site.data["created"].append("PAGE:" + page["id"])
        site.derive()
        return pretty(page_obj(site, page, args.get("contentFormat") or "html"))


class UpdatePage(WriteTool):
    name = "updateConfluencePage"

    def mutate(self, site: Site, args: dict, ctx: CallContext) -> Any:
        page = find_page(site, args["pageId"])
        text = stored_body(args["body"], args.get("contentFormat"))
        if not text.strip():
            raise confluence_bad_request("The page body can't be empty.")
        if args.get("spaceId"):
            page["spaceId"] = find_space(site, args["spaceId"])["id"]
        if args.get("parentId"):
            page["parentId"] = find_page(site, args["parentId"])["id"]
        if args.get("title"):
            page["title"] = str(args["title"]).strip()
        page["body"] = text
        page["status"] = args.get("status") or "current"
        page["version"] += 1
        page["versionMessage"] = str(args.get("versionMessage") or "")
        page["updated"] = wiki_stamp(ctx.clock.now)
        page["updatedBy"] = site.current_user["key"]
        site.derive()
        return pretty(page_obj(site, page, args.get("contentFormat") or "html", with_body=bool(args.get("includeBody"))))


def new_comment(site: Site, args: dict, ctx: CallContext, kind: str) -> dict:
    parent = None
    if args.get("parentCommentId"):
        parent = site.wiki_comments.get(str(args["parentCommentId"]))
        if parent is None or parent["type"] != kind:
            raise confluence_missing("Comment", args["parentCommentId"])
        page = find_page(site, parent["pageId"])
    elif args.get("pageId"):
        page = find_page(site, args["pageId"])
    else:
        raise confluence_bad_request("Provide pageId for a new comment or parentCommentId for a reply.")
    text = stored_body(args["body"], args.get("contentFormat"))
    if not text.strip():
        raise confluence_bad_request("The comment body can't be empty.")
    stamp = wiki_stamp(ctx.clock.now)
    return {"id": site.next_id("wikiComment", 99100), "pageId": page["id"], "type": kind,
            "parentId": parent["id"] if parent else None, "author": site.current_user["key"], "created": stamp,
            "updated": stamp, "version": 1, "body": text}


class CreateFooterComment(WriteTool):
    name = "createConfluenceFooterComment"

    def mutate(self, site: Site, args: dict, ctx: CallContext) -> Any:
        comment = new_comment(site, args, ctx, "footer")
        site.data["confluence"]["comments"].append(comment)
        site.derive()
        return pretty(wiki_comment_obj(site, comment, args.get("contentFormat") or "markdown"))


class CreateInlineComment(WriteTool):
    name = "createConfluenceInlineComment"

    def mutate(self, site: Site, args: dict, ctx: CallContext) -> Any:
        comment = new_comment(site, args, ctx, "inline")
        if not comment["parentId"]:
            props = args.get("inlineCommentProperties") or {}
            selection = str(props.get("textSelection") or "")
            if not selection:
                raise confluence_bad_request("inlineCommentProperties.textSelection is required for a new inline "
                                             "comment.")
            if selection not in render.plain_text(site.pages[comment["pageId"]].get("body")):
                raise confluence_bad_request("The selected text wasn't found in the page. Fetch the page and copy "
                                             "the text exactly.")
            comment.update(selection=selection, markerRef=str(uuid.uuid4()), resolutionStatus="open")
        site.data["confluence"]["comments"].append(comment)
        site.derive()
        return pretty(wiki_comment_obj(site, comment, args.get("contentFormat") or "markdown"))


# --- Compass (no scope) --------------------------------------------------------------------------------------------

def compass_tool(tool_name: str, write: bool = False) -> type:
    base = WriteTool if write else AtlassianTool

    class CompassTool(base):  # type: ignore[valid-type, misc]
        name = tool_name

        def handle(self, site: Site, args: dict, ctx: CallContext) -> Any:
            raise scope_error(tool_name)

        def mutate(self, site: Site, args: dict, ctx: CallContext) -> Any:
            raise scope_error(tool_name)

    CompassTool.__name__ = tool_name
    return CompassTool


TOOLS = (
    UserInfo, AccessibleResources, FormatGuide,
    ConfluencePage, ConfluenceCql, ConfluenceSpaces, PagesInSpace, FooterComments, InlineComments,
    CommentChildren, PageDescendants, CreatePage, UpdatePage, CreateFooterComment, CreateInlineComment,
    GetIssue, EditIssue, CreateIssue, GetTransitions, RemoteLinks, VisibleProjects, IssueTypesMetadata,
    IssueTypeFields, AddComment, TransitionIssue, SearchJql, LookupAccount, AddWorklog, LinkTypes, CreateLink,
    compass_tool("getCompassComponents"), compass_tool("getCompassComponent"),
    compass_tool("getCompassCustomFieldDefinitions"),
    compass_tool("createCompassCustomFieldDefinition", write=True), compass_tool("createCompassComponent", write=True),
    compass_tool("createCompassComponentRelationship", write=True),
    GraphContext, GraphObject, AddGraphContext, RovoSearch, RovoFetch,
)
