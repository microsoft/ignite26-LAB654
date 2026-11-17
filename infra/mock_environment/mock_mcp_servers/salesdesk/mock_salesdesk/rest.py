"""The REST surface behind ``dispatch`` and ``dispatch_readonly``.

Responses use the envelopes the real tools return (recorded in SEVAL traces):

* success: ``{"status_code": 200, "body": <json>, "url": "<instance>/services/data/vNN.0/<route>"}``
* failure: ``{"error_code": "API_ERROR", "message": "API call failed with status N", "status_code": N,
  "body": "[{\\"message\\": ..., \\"errorCode\\": ...}]"}`` (the body is a JSON *string*)

Routes the traces exercise are implemented against the mock org (graphql, query, search, result-groups,
object-schema, sobjects, limits, tooling/query). Routes the traces show failing on a real org (Tableau, Einstein
search answers, virtual activity IDs) fail here with the same status and message.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlsplit

from . import graphql, soql
from .engine import Ctx, display_value
from .ids import normalize
from .schema import OBJECTS, READ_ONLY_FIELDS, SEARCHABLE, WRITABLE, find_field, find_object, stage_info
from .store import Org, StateStore
from .timeutil import iso_ms, parse_date, parse_dt

SEED_DIR = Path(__file__).resolve().parent.parent / "seed_files"
_VERSION = re.compile(r"^/services/data/(v\d+\.\d+)(/.*)?$")
_NOT_FOUND = "The requested resource does not exist"


def base_url() -> str:
    return (os.environ.get("PUBLIC_BASE_URL") or "http://localhost:8000").rstrip("/")


def _ok(body: Any, path: str, status: int = 200) -> dict:
    return {"status_code": status, "body": body, "url": base_url() + path}


def _err(status: int, message: str, code: str, fields: list[str] | None = None) -> dict:
    item: dict = {"message": message, "errorCode": code}
    if fields is not None:
        item["fields"] = fields
    return {"error_code": "API_ERROR", "message": f"API call failed with status {status}", "status_code": status,
            "body": json.dumps([item], separators=(",", ":"))}


def _public(rec: dict) -> dict:
    return {k: v for k, v in rec.items() if not k.startswith("_")}


# --- entry point --------------------------------------------------------------------------------------------------

def dispatch(store: StateStore, conversation_id: str | None, method: str, url: str,
             query_params: dict | None = None, body: Any = None, readonly: bool = False,
             now: datetime | None = None) -> dict:
    method = (method or "GET").upper()
    now = now or datetime.now(timezone.utc)
    if readonly and method != "GET":
        return _err(405, f"HTTP Method '{method}' not allowed. Allowed are GET", "METHOD_NOT_ALLOWED")
    parts = urlsplit(url or "")
    path = parts.path or "/"
    params: dict[str, Any] = dict(parse_qsl(parts.query, keep_blank_values=True))
    params.update(query_params or {})
    if isinstance(body, str) and body.strip():
        try:
            body = json.loads(body)
        except ValueError:
            return _err(400, "Unexpected character: was expecting a JSON value", "JSON_PARSER_ERROR")

    match = _VERSION.match(path.rstrip("/") or "/")
    if not match:
        return _err(404, _NOT_FOUND, "NOT_FOUND")
    version, route = match.group(1), (match.group(2) or "/").rstrip("/") or "/"
    full = f"/services/data/{version}{'' if route == '/' else route}"

    if method in ("POST", "PATCH", "PUT", "DELETE") and route.startswith("/sobjects/"):
        with store.write(conversation_id) as org:
            return _sobjects_write(Ctx(org, now), method, route, body, version, full, conversation_id)
    ctx = Ctx(store.read(conversation_id), now)
    return _route(ctx, method, route, params, body, version, full)


def _route(ctx: Ctx, method: str, route: str, params: dict, body: Any, version: str, full: str) -> dict:
    if route == "/":
        return _ok(_resources(version), full) if method == "GET" else _err(405, "Method not allowed", "METHOD_NOT_ALLOWED")
    if route == "/graphql":
        return _graphql(ctx, method, params, body, full)
    if route in ("/query", "/queryAll"):
        return _query(ctx, params.get("q"), version, full)
    if route == "/search":
        return _search(ctx, params.get("q"), version, full)
    if route == "/tooling/query":
        return _ok({"size": 0, "totalSize": 0, "done": True, "queryLocator": None, "entityTypeName": None,
                    "records": []}, full)
    if route == "/limits":
        return _ok(json.loads((SEED_DIR / "limits.json").read_text(encoding="utf-8")), full)
    if route == "/connect/search/sobjects/result-groups":
        return _ok(_result_groups(ctx, str(params.get("q") or "")), full)
    if route in ("/connect/search/sources", "/connect/search/sobjects/answer"):
        return _err(403, "This feature is not currently enabled for this user.", "FUNCTIONALITY_NOT_ENABLED")
    if route.startswith("/tableau/"):
        name = route.split("/", 2)[2]
        return _err(400, f"An unexpected error occurred: Post to /v1/{name} status failed. status code: 404, "
                         "status message: Not Found", "UNKNOWN_EXCEPTION")
    if route == "/platform-mcp-context/object-schema":
        return _object_schema(params.get("objects"), full)
    if route == "/sobjects" or route.startswith("/sobjects/"):
        return _sobjects_read(ctx, route, params, version, full)
    return _err(404, _NOT_FOUND, "NOT_FOUND")


def _resources(version: str) -> dict:
    names = ["graphql", "limits", "query", "queryAll", "search", "sobjects", "tooling"]
    return {n: f"/services/data/{version}/{n}" for n in names}


# --- graphql / query / search -------------------------------------------------------------------------------------

def _graphql(ctx: Ctx, method: str, params: dict, body: Any, full: str) -> dict:
    if method == "GET":
        raw = params.get("queryInput")
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except ValueError:
                return _err(400, "Invalid queryInput: not valid JSON", "INVALID_INPUT")
        payload = raw if isinstance(raw, dict) else {"query": params.get("query"),
                                                     "variables": params.get("variables")}
    elif method == "POST":
        payload = body if isinstance(body, dict) else {}
    else:
        return _err(405, f"HTTP Method '{method}' not allowed. Allowed are GET,POST", "METHOD_NOT_ALLOWED")
    variables = payload.get("variables")
    if isinstance(variables, str):
        try:
            variables = json.loads(variables) if variables.strip() else None
        except ValueError:
            variables = None
    if not payload.get("query"):
        return _err(400, "Query is required.", "INVALID_INPUT")
    return _ok(graphql.execute(ctx, payload["query"], variables, payload.get("operationName")), full)


def _query(ctx: Ctx, q: Any, version: str, full: str) -> dict:
    if not q:
        return _err(400, "A query string has to be specified", "MALFORMED_QUERY")
    try:
        return _ok(soql.query(ctx, str(q), version), full)
    except soql.SoqlError as err:
        return _err(400, err.render(str(q)), err.code)


def _search(ctx: Ctx, q: Any, version: str, full: str) -> dict:
    if not q:
        return _err(400, "A search string has to be specified", "MALFORMED_SEARCH")
    try:
        return _ok(soql.search(ctx, str(q), version), full)
    except soql.SoqlError as err:
        return _err(400, err.render(str(q)), err.code)


# --- connect/search/sobjects/result-groups ------------------------------------------------------------------------

_THEME = {"Account": ("5867E8", "account"), "Contact": ("A094ED", "contact"), "Opportunity": ("FF5D2D", "opportunity"),
          "Lead": ("F88962", "lead"), "Event": ("CB65FF", "event"), "Task": ("3BA755", "task"),
          "User": ("1B96FF", "user")}
_DISPLAY = {
    "Account": ["Name", "Type", "BillingCity", "Owner.Alias"],
    "Contact": ["Name", "Title", "Account.Name", "Email", "Owner.Alias"],
    "Opportunity": ["Name", "Account.Name", "StageName", "CloseDate", "Owner.Alias"],
    "Lead": ["Name", "Company", "Email", "Status", "Owner.Alias"],
    "Event": ["StartDateTime", "EndDateTime", "Subject", "Who.Name", "What.Name", "Owner.Alias"],
    "Task": ["Subject", "Who.Name", "What.Name", "ActivityDate", "Status", "Owner.Alias"],
    "User": ["Name", "Title", "Email"],
}


def _alias(user: dict | None) -> str | None:
    if not user:
        return None
    return ((user.get("FirstName") or "")[:1] + (user.get("LastName") or "")[:4]).lower() or None


def _rg_value(ctx: Ctx, obj: str, rec: dict, path: str) -> tuple[Any, Any]:
    if "." in path:
        rel, leaf = path.split(".", 1)
        fk = next((f[0] for f in OBJECTS[obj]["fields"] if f[2] == "REFERENCE" and f[3] and f[3][0] == rel), None)
        hit = ctx.org.get(rec.get(fk)) if fk else None
        if not hit:
            return None, None
        return (_alias(hit[1]) if leaf == "Alias" else hit[1].get(leaf)), None
    meta = find_field(obj, path)
    raw = rec.get(path)
    if path == "Id" or meta is None:
        return raw, None
    shown = display_value(meta[2], raw)
    return raw, shown if shown is not None else raw


def _result_groups(ctx: Ctx, q: str) -> dict:
    cleaned = re.sub(r"[{}\[\]()^~:\\\"'+\-!&|]", " ", q).strip()
    hit = soql._matcher(cleaned) if len(cleaned.replace("*", "")) >= 2 else (lambda _t: False)
    groups, counts = [], {}
    for obj in SEARCHABLE:
        results = []
        for rec in ctx.org.records(obj):
            if hit(soql._search_text(obj, rec, None)):
                fields = {}
                for path in _DISPLAY[obj] + ["Id"]:
                    value, shown = _rg_value(ctx, obj, rec, path)
                    fields[path] = {"value": value, "displayValue": shown}
                results.append({"id": rec["Id"], "apiName": obj, "fields": fields})
        counts[obj] = len(results)
        if results:
            groups.append({"objectApiName": obj, "results": results})
    metadata, sobjects = {}, {}
    for obj in SEARCHABLE:
        color, icon = _THEME[obj]
        fields = {}
        if counts[obj]:
            for path in _DISPLAY[obj] + ["Id"]:
                leaf = path.split(".")[-1]
                domain = obj if "." not in path else ("Name" if leaf == "Name" else "User")
                meta = find_field(obj, path) if "." not in path else None
                fields[path] = {"field": path, "fieldApiName": leaf, "domain": domain,
                                "label": (meta[1] if meta else leaf).replace("&", "&amp;"),
                                "fieldType": (meta[2].title() if meta else "String"), "sortable": True,
                                "filterable": True, "highlightable": False}
        metadata[obj] = {"objectApiName": obj, "label": OBJECTS[obj]["label"],
                         "labelPlural": "People" if obj == "User" else OBJECTS[obj]["plural"],
                         "themeInfo": {"color": color,
                                       "iconUrl": f"{base_url()}/img/icon/t4v35/standard/{icon}.svg"},
                         "fields": fields}
        entry = {"nameField": OBJECTS[obj]["name"][0], "source": "__CRM__", "numberOfMatches": counts[obj],
                 "hasMoreResults": False}
        if counts[obj]:
            entry = {"nameField": entry["nameField"], "displayFields": _DISPLAY[obj], **{k: v for k, v in
                     entry.items() if k != "nameField"}}
        sobjects[obj] = entry
    return {"resultGroups": groups, "parameters": {"q": q}, "metadata": metadata,
            "queryInfo": {"queryId": hashlib.sha1(q.encode()).hexdigest()[:13],
                          "status": {"code": "Success", "message": "Successful query"}, "sobjects": sobjects}}


# --- object schema / describe -------------------------------------------------------------------------------------

_REQUIRED = {"Account": {"Name"}, "Contact": {"LastName"}, "Lead": {"LastName", "Company", "Status"},
             "Opportunity": {"Name", "StageName", "CloseDate"}, "Event": {"StartDateTime", "EndDateTime"},
             "Task": {"Status", "Priority"}, "User": {"LastName", "Username", "Email"}}
_LENGTH = {"ID": 18, "REFERENCE": 18, "STRING": 255, "EMAIL": 80, "PHONE": 40, "URL": 255, "PICKLIST": 255,
           "COMBOBOX": 255, "TEXTAREA": 32000}


def _picklist(meta: tuple) -> list:
    if meta[2] in ("PICKLIST", "COMBOBOX", "MULTIPICKLIST") and isinstance(meta[3], list):
        return list(meta[3])
    return []


def _object_schema(objects: Any, full: str) -> dict:
    names = [n.strip() for n in str(objects or "").split(",") if n.strip()]
    if not names:
        return _err(400, "The objects parameter is required.", "INVALID_INPUT")
    details = []
    for name in names:
        obj = find_object(name)
        if not obj or OBJECTS[obj].get("virtual"):
            continue
        fields = []
        for meta in OBJECTS[obj]["fields"]:
            item: dict = {"label": meta[1]}
            if meta[2] in _LENGTH:
                item["length"] = _LENGTH[meta[2]]
            item["name"] = meta[0]
            item["picklistValues"] = [{"defaultValue": False, "label": v, "value": v} for v in _picklist(meta)]
            item["referenceTo"] = list(meta[3][1]) if meta[2] == "REFERENCE" and meta[3] else []
            if meta[2] == "REFERENCE" and meta[3]:
                item["relationshipName"] = meta[3][0]
            item["required"] = meta[0] in _REQUIRED.get(obj, set())
            item["type"] = meta[2].lower()
            fields.append(item)
        details.append({"childRelationships": [{"childObject": c, "field": f, "relationshipName": r}
                                               for c, r, f in OBJECTS[obj]["children"]],
                        "fields": fields, "label": OBJECTS[obj]["label"], "name": obj})
    return _ok({"details": details}, full)


def _urls(obj: str, version: str) -> dict:
    root = f"/services/data/{version}/sobjects/{obj}"
    return {"sobject": root, "describe": f"{root}/describe", "rowTemplate": f"{root}/{{ID}}"}


def _sobject_summary(obj: str, version: str) -> dict:
    meta = OBJECTS[obj]
    writable = obj in WRITABLE
    return {"name": obj, "label": meta["label"], "labelPlural": meta["plural"], "keyPrefix": meta.get("prefix"),
            "custom": False, "queryable": True, "searchable": obj in SEARCHABLE, "createable": writable,
            "updateable": writable, "deletable": writable, "retrieveable": not meta.get("virtual"),
            "urls": _urls(obj, version)}


def _describe(obj: str, version: str) -> dict:
    ro = _read_only(obj)
    fields = []
    for meta in OBJECTS[obj]["fields"]:
        writable = obj in WRITABLE and meta[0] not in ro
        fields.append({
            "name": meta[0], "label": meta[1], "type": "id" if meta[2] == "ID" else meta[2].lower(),
            "length": _LENGTH.get(meta[2], 0), "nillable": meta[0] not in _REQUIRED.get(obj, set()) and meta[0] != "Id",
            "createable": writable, "updateable": writable,
            "referenceTo": list(meta[3][1]) if meta[2] == "REFERENCE" and meta[3] else [],
            "relationshipName": meta[3][0] if meta[2] == "REFERENCE" and meta[3] else None,
            "picklistValues": [{"active": True, "defaultValue": False, "label": v, "validFor": None, "value": v}
                               for v in _picklist(meta)],
        })
    out = _sobject_summary(obj, version)
    out["fields"] = fields
    out["childRelationships"] = [{"childSObject": c, "field": f, "relationshipName": r, "cascadeDelete": False}
                                 for c, r, f in OBJECTS[obj]["children"]]
    return out


# --- sobjects -----------------------------------------------------------------------------------------------------

def _read_only(obj: str) -> set[str]:
    ro = set(READ_ONLY_FIELDS)
    if obj in ("Contact", "Opportunity"):
        ro.discard("AccountId")
    if obj in ("Account", "Opportunity"):
        ro.discard("Name")
    return ro


def _resolve(route: str) -> tuple[str | None, list[str]]:
    segments = [s for s in route.split("/") if s][1:]
    if not segments:
        return None, []
    return find_object(segments[0]), segments[1:]


def _sobjects_read(ctx: Ctx, route: str, params: dict, version: str, full: str) -> dict:
    if route == "/sobjects":
        return _ok({"encoding": "UTF-8", "maxBatchSize": 200,
                    "sobjects": [_sobject_summary(o, version) for o in OBJECTS if not OBJECTS[o].get("virtual")]},
                   full)
    obj, rest = _resolve(route)
    if not obj or OBJECTS[obj].get("virtual"):
        return _err(404, _NOT_FOUND, "NOT_FOUND")
    if not rest:
        recent = [{"attributes": {"type": obj, "url": f"/services/data/{version}/sobjects/{obj}/{r['Id']}"},
                   "Id": r["Id"], OBJECTS[obj]["name"][0]: r.get(OBJECTS[obj]["name"][0])}
                  for r in ctx.org.records(obj)[:5]]
        return _ok({"objectDescribe": _sobject_summary(obj, version), "recentItems": recent}, full)
    if rest == ["describe"]:
        return _ok(_describe(obj, version), full)
    if len(rest) == 1:
        hit = ctx.org.get(rest[0])
        if not hit or hit[0] != obj:
            return _err(404, _NOT_FOUND, "NOT_FOUND")
        rec = _public(hit[1])
        wanted = [f.strip() for f in str(params.get("fields") or "").split(",") if f.strip()]
        if wanted:
            bad = [f for f in wanted if not find_field(obj, f)]
            if bad:
                return _err(400, f"No such column '{bad[0]}' on sobject of type {obj}", "INVALID_FIELD")
            names = [find_field(obj, f)[0] for f in wanted]
        else:
            names = [f[0] for f in OBJECTS[obj]["fields"]]
        out = {"attributes": {"type": obj, "url": f"/services/data/{version}/sobjects/{obj}/{rec['Id']}"}}
        for name in names:
            out[name] = rec.get(name)
        return _ok(out, full)
    return _err(404, _NOT_FOUND, "NOT_FOUND")


def _check_fields(ctx: Ctx, obj: str, body: dict) -> dict | None:
    ro = _read_only(obj)
    for key in body:
        if key == "attributes":
            continue
        meta = find_field(obj, key)
        if not meta:
            return _err(400, f"No such column '{key}' on sobject of type {obj}", "INVALID_FIELD")
        if meta[0] in ro:
            return _err(400, f"Unable to create/update fields: {meta[0]}. Please check the security settings of "
                             "this field and verify that it is read/write for your user or administrator.",
                        "INVALID_FIELD_FOR_INSERT_UPDATE", [meta[0]])
    for key, value in body.items():
        meta = find_field(obj, key) if key != "attributes" else None
        if not meta or value in (None, ""):
            continue
        if meta[2] == "REFERENCE":
            if not isinstance(value, str) or len(value) not in (15, 18):
                return _err(400, f"{meta[1]}: id value of incorrect type: {value}", "MALFORMED_ID", [meta[0]])
            target = ctx.org.get(value)
            if not target or target[0] not in meta[3][1]:
                return _err(400, "invalid cross reference id", "INVALID_CROSS_REFERENCE_KEY", [meta[0]])
        elif meta[2] == "DATE" and not parse_date(str(value)):
            return _err(400, f"{meta[1]}: value not of required type: {value}", "INVALID_TYPE_ON_FIELD_IN_RECORD",
                        [meta[0]])
        elif meta[2] == "DATETIME" and not parse_dt(str(value)):
            return _err(400, f"{meta[1]}: value not of required type: {value}", "INVALID_TYPE_ON_FIELD_IN_RECORD",
                        [meta[0]])
    return None


def _normalize_values(obj: str, body: dict) -> dict:
    out = {}
    for key, value in body.items():
        if key == "attributes":
            continue
        meta = find_field(obj, key)
        if meta[2] == "REFERENCE" and isinstance(value, str) and value:
            value = normalize(value)
        elif meta[2] == "DATETIME" and value:
            value = iso_ms(parse_dt(str(value)))
        elif meta[2] == "DATE" and value:
            value = parse_date(str(value)).isoformat()
        out[meta[0]] = value
    return out


def _stage_history(org: Org, opp: dict, stamp: str, conv: str | None) -> None:
    probability, forecast = stage_info(opp.get("StageName"))
    org.records("OpportunityHistory").append({
        "Id": org.take_id("OpportunityHistory", conv), "OpportunityId": opp["Id"], "StageName": opp.get("StageName"),
        "Amount": opp.get("Amount"), "Probability": float(probability), "CloseDate": opp.get("CloseDate"),
        "ForecastCategory": {"Pipeline": "Pipeline", "Commit": "Forecast", "Closed": "Closed"}.get(forecast, "Omitted"),
        "CreatedDate": stamp, "CreatedById": org.current_user_id, "SystemModstamp": stamp, "IsDeleted": False})
    opp["LastStageChangeDate"] = stamp


_DEFAULTS = {"Task": {"Status": "Not Started", "Priority": "Normal", "TaskSubtype": "Task"},
             "Lead": {"Status": "Open - Not Contacted"}, "Event": {"IsAllDayEvent": False, "ShowAs": "Busy"}}


def _sobjects_write(ctx: Ctx, method: str, route: str, body: Any, version: str, full: str,
                    conv: str | None = None) -> dict:
    obj, rest = _resolve(route)
    if not obj or OBJECTS[obj].get("virtual"):
        return _err(404, _NOT_FOUND, "NOT_FOUND")
    org, stamp = ctx.org, iso_ms(ctx.now)
    if obj not in WRITABLE:
        verb = {"POST": "inserted", "DELETE": "deleted"}.get(method, "updated")
        return _err(400, f"entity type cannot be {verb}: {OBJECTS[obj]['label']}",
                    "CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY")
    if method == "POST" and not rest:
        if not isinstance(body, dict):
            return _err(400, "Request body is required.", "JSON_PARSER_ERROR")
        problem = _check_fields(ctx, obj, body)
        if problem:
            return problem
        values = _normalize_values(obj, body)
        rec = {**_DEFAULTS.get(obj, {}), **values}
        missing = [f for f in sorted(_REQUIRED.get(obj, set())) if rec.get(f) in (None, "")]
        if missing:
            return _err(400, f"Required fields are missing: [{', '.join(missing)}]", "REQUIRED_FIELD_MISSING",
                        missing)
        if "Probability" in values:
            rec["_probability_set"] = True
        rec.update({"Id": org.take_id(obj, conv), "CreatedDate": stamp, "CreatedById": org.current_user_id,
                    "LastModifiedDate": stamp, "LastModifiedById": org.current_user_id, "SystemModstamp": stamp,
                    "IsDeleted": False})
        rec.setdefault("OwnerId", org.current_user_id)
        if obj == "Task" and rec.get("Status") == "Completed":
            rec.setdefault("CompletedDateTime", stamp)
        org.records(obj).append(rec)
        if obj == "Opportunity":
            _stage_history(org, rec, stamp, conv)
        return _ok({"id": rec["Id"], "success": True, "errors": []}, full, 201)
    if len(rest) != 1:
        return _err(404, _NOT_FOUND, "NOT_FOUND")
    hit = org.get(rest[0])
    if not hit or hit[0] != obj:
        return _err(404, _NOT_FOUND, "NOT_FOUND")
    rec = hit[1]
    if method == "DELETE":
        org.data["objects"][obj] = [r for r in org.records(obj) if r is not rec]
        return _ok(None, full, 204)
    if method in ("PATCH", "PUT"):
        if not isinstance(body, dict):
            return _err(400, "Request body is required.", "JSON_PARSER_ERROR")
        problem = _check_fields(ctx, obj, body)
        if problem:
            return problem
        values = _normalize_values(obj, body)
        missing = [f for f in sorted(_REQUIRED.get(obj, set())) if f in values and values[f] in (None, "")]
        if missing:
            return _err(400, f"Required fields are missing: [{', '.join(missing)}]", "REQUIRED_FIELD_MISSING",
                        missing)
        stage_changed = obj == "Opportunity" and "StageName" in values and values["StageName"] != rec.get("StageName")
        rec.update(values)
        if "Probability" in values:
            rec["_probability_set"] = True
        elif stage_changed:
            rec.pop("_probability_set", None)
        if obj == "Task" and values.get("Status") == "Completed":
            rec.setdefault("CompletedDateTime", stamp)
        rec.update({"LastModifiedDate": stamp, "LastModifiedById": org.current_user_id, "SystemModstamp": stamp})
        if stage_changed:
            _stage_history(org, rec, stamp, conv)
        return _ok(None, full, 204)
    return _err(405, f"HTTP Method '{method}' not allowed. Allowed are GET,PATCH,DELETE", "METHOD_NOT_ALLOWED")
