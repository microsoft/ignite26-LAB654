"""Validate a COEP grounding-data package against the local _schemas.

Usage (from repo root):
    python src/mock_environment/tools/validate_package.py [package_dir] [--as-of 2026-11-09T14:00Z]

Checks each *.config.json (and config.json), and each connector folder's
<type>/<type>_*.jsonl, against its JSON schema, then a
subset of the COEP cross-file rules (user references, file references, shared
links, placeholders, email chains, licences, timestamps, intranet page ids). It doesn't replace
COEP's own validation; it catches the common mistakes before upload.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from jsonschema.validators import validator_for

HERE = Path(__file__).resolve().parent
SCHEMAS = HERE.parent / "_schemas" / "Grounding"
DEFAULT_PACKAGE = HERE.parent / "Connectors_Ignite_EMP"
PLACEHOLDER = re.compile(r"\{placeholder:([^}]+)\}")

errors: list[str] = []
AS_OF = datetime.now(timezone.utc)


def err(msg: str) -> None:
    errors.append(msg)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list:
    items = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            err(f"{path.name}:{n}: not valid JSON ({e.msg})")
            continue
        if not isinstance(obj, dict):
            err(f"{path.name}:{n}: each line must be one JSON object, not an array")
            continue
        items.append(obj)
    return items


def schema_check(pkg: Path) -> dict[str, list | dict]:
    data = {}
    targets = {"config": [pkg / "config.json"]}
    for p in pkg.glob("*.config.json"):
        targets[p.name.split(".")[0].lower()] = [p]
    # Connector types: <type>/<type>_*.jsonl (COEP Connector Entity Guide).
    for d in pkg.iterdir():
        if d.is_dir() and d.name != "files":
            files = sorted(d.glob("*.jsonl"))
            for p in files:
                if p.name.split("_")[0] != d.name or d.name != d.name.lower():
                    err(f"{d.name}/{p.name}: folder and file prefix must both be the lowercase type name")
            if files:
                targets[d.name] = files
    for type_name, paths in targets.items():
        schema_path = SCHEMAS / type_name / "schema.json"
        if not schema_path.exists():
            err(f"{paths[0].name}: no local schema for type '{type_name}'")
            continue
        if paths[0].suffix == ".jsonl":
            doc = [i for p in paths for i in load_jsonl(p)]
        else:
            doc = load(paths[0])
        data[type_name] = doc
        schema = load(schema_path)
        v = validator_for(schema)(schema, format_checker=validator_for(schema).FORMAT_CHECKER)
        label = paths[0].name if len(paths) == 1 else f"{type_name}/*.jsonl"
        for e in sorted(v.iter_errors(doc), key=lambda e: list(e.absolute_path)):
            loc = "/".join(str(x) for x in e.absolute_path)
            err(f"{label}:{loc}: {e.message[:300]}")
    return data


def past(ts: str, what: str) -> None:
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if dt > AS_OF:
        err(f"{what}: timestamp {ts} is after {AS_OF:%Y-%m-%dT%H:%MZ} (COEP requires past timestamps)")


def cross_checks(pkg: Path, data: dict) -> None:
    if "users" not in data:
        err("users.config.json is required")
        return
    users = {u["MailNickName"]: u for u in data["users"]}
    teams_licensed = {n for n, u in users.items() if "Microsoft Teams Enterprise" in (u.get("Licenses") or [])}

    def user(n, where):
        if n not in users:
            err(f"{where}: '{n}' not in users.config.json")

    for n, u in users.items():
        if u.get("Manager"):
            user(u["Manager"], f"users[{n}].Manager")
    phones = [u.get("PhoneNumber") for u in users.values() if u.get("PhoneNumber")]
    if len(phones) != len(set(phones)):
        err("users: PhoneNumber values must be unique")

    files = {f["FileId"]: f for f in data.get("files", [])}
    for fid, f in files.items():
        user(f["Owner"], f"files[{fid}].Owner")
        for s in f.get("SharedWith") or []:
            user(s["Email"], f"files[{fid}].SharedWith")
        loc = pkg / f["FileLocation"]
        if not loc.is_file() or loc.stat().st_size == 0:
            err(f"files[{fid}]: FileLocation {f['FileLocation']} missing or empty")
        if Path(f["FileLocation"]).name != Path(f["FileName"]).name:
            err(f"files[{fid}]: FileName and FileLocation file names differ")
        past(f["CreatedDate"], f"files[{fid}].CreatedDate")
        if f.get("LastModifiedDate") and f["LastModifiedDate"] <= f["CreatedDate"]:
            err(f"files[{fid}]: LastModifiedDate must be later than CreatedDate")

    def file_link(hl, where):
        if "FileId" not in hl:
            return
        f = files.get(hl["FileId"])
        if not f:
            err(f"{where}: FileId {hl['FileId']} not in files.config.json")
            return
        if hl.get("FileOwner") != f["Owner"]:
            err(f"{where}: FileOwner doesn't match file Owner")
        links = {l["SharedLinkId"] for l in f.get("FileSharedLinks") or []}
        if hl.get("SharedLinkId") not in links:
            err(f"{where}: SharedLinkId {hl.get('SharedLinkId')} not defined on file {hl['FileId']}")

    def placeholders(text, phs, where):
        used = set(PLACEHOLDER.findall(text or ""))
        defined = [p["PlaceholderId"] for p in phs or []]
        if len(defined) != len(set(defined)):
            err(f"{where}: duplicate PlaceholderId")
        if used != set(defined):
            err(f"{where}: placeholders used {sorted(used)} != defined {sorted(defined)}")
        for p in phs or []:
            file_link(p.get("HyperLinkContent", {}), f"{where}.Placeholders[{p['PlaceholderId']}]")

    emails = {e["EmailId"]: e for e in data.get("emails", [])}
    if len(emails) != len(data.get("emails", [])):
        err("emails: duplicate EmailId")
    for eid, e in emails.items():
        w = f"emails[{eid}]"
        user(e["Sender"], f"{w}.Sender")
        for fld in ("ToRecipients", "CcRecipients", "BccRecipients"):
            for r in e.get(fld) or []:
                user(r["Recipient"], f"{w}.{fld}")
        for a in e.get("Attachments") or []:
            if not (pkg / a).is_file():
                err(f"{w}: attachment {a} missing")
        past(e["Timestamp"], w)
        placeholders(e.get("Body"), e.get("Placeholders"), w)
        ref = e.get("ReferenceEmailId")
        if ref:
            parent = emails.get(ref)
            if not parent:
                err(f"{w}: ReferenceEmailId {ref} not found")
            else:
                participants = {parent["Sender"]} | {
                    r["Recipient"] for f in ("ToRecipients", "CcRecipients", "BccRecipients") for r in parent.get(f) or []
                }
                if e["Sender"] not in participants:
                    err(f"{w}: Sender not a participant of referenced email {ref}")
                if parent["Timestamp"] >= e["Timestamp"]:
                    err(f"{w}: reply is not later than referenced email {ref}")
    for eid in emails:  # cycle check
        seen, cur = set(), eid
        while cur:
            if cur in seen:
                err(f"emails: ReferenceEmailId cycle involving {eid}")
                break
            seen.add(cur)
            cur = emails.get(cur, {}).get("ReferenceEmailId")

    event_ids = set()
    for ev in data.get("events", []):
        w = f"events[{ev['EventId']}]"
        if ev["EventId"] in event_ids:
            err(f"{w}: duplicate EventId")
        event_ids.add(ev["EventId"])
        user(ev["Sender"], f"{w}.Sender")
        for fld in ("RequiredAttendees", "OptionalAttendees"):
            for a in ev.get(fld) or []:
                user(a["Email"], f"{w}.{fld}")
        if ev["StartDateTime"] > ev["EndDateTime"]:
            err(f"{w}: StartDateTime after EndDateTime")
        placeholders(ev.get("Body"), ev.get("Placeholders"), w)

    chat_ids = set()
    for c in data.get("chats", []):
        w = f"chats[{c['ChatId']}]"
        if c["ChatId"] in chat_ids:
            err(f"{w}: duplicate ChatId")
        chat_ids.add(c["ChatId"])
        members = set(c["Members"])
        for m in members:
            user(m, f"{w}.Members")
            if m in users and m not in teams_licensed:
                err(f"{w}: member {m} lacks 'Microsoft Teams Enterprise' licence")
        msg_ids, prior = set(), set()
        for m in c["ChatMessages"]:
            mw = f"{w}.ChatMessages[{m['ChatMessageId']}]"
            if m["ChatMessageId"] in msg_ids:
                err(f"{mw}: duplicate ChatMessageId")
            msg_ids.add(m["ChatMessageId"])
            if m["From"] not in members:
                err(f"{mw}: From not in Members")
            if m.get("SentDateTime"):
                past(m["SentDateTime"], mw)
                if c.get("CreatedDateTime") and c["CreatedDateTime"] >= m["SentDateTime"]:
                    err(f"{mw}: CreatedDateTime must be earlier than SentDateTime")
            q = m.get("QuoteChatMessageId")
            if q and q not in prior:
                err(f"{mw}: QuoteChatMessageId must reference an earlier message")
            prior.add(m["ChatMessageId"])
            placeholders(m.get("Content"), m.get("Placeholders"), mw)
        if c["ChatType"] == "Meeting" and c.get("EventId") not in event_ids:
            err(f"{w}: Meeting chat EventId not in events")

    connector_ids: set[str] = set()
    for p in data.get("intranetwebsite", []):
        props = p["properties"]
        w = f"intranetwebsite[{props['URL']}]"
        if not re.fullmatch(r"[A-Za-z0-9]+", p["id"]):
            err(f"{w}: id must contain only letters and digits")
        if p["id"] in connector_ids:
            err(f"{w}: duplicate id")
        connector_ids.add(p["id"])
        if p["displayName"] != props["URL"]:
            err(f"{w}: displayName must equal properties.URL")
        if p["id"] != hashlib.sha512(props["URL"].encode("utf-16-le")).hexdigest().upper():
            err(f"{w}: id must be the uppercase SHA-512 of the URL (UTF-16LE)")
        if props["LastModifiedBy"] not in props["Authors"]:
            err(f"{w}: LastModifiedBy must be one of Authors")
        if props["CreatedDateTime"] > props["LastModifiedDateTime"]:
            err(f"{w}: CreatedDateTime after LastModifiedDateTime")
        past(props["LastModifiedDateTime"], w)
        acts = p["activityList"]
        created = [a for a in acts if a["ActivityType"] == "created"]
        if len(created) != 1 or created[0]["ActivityDateTime"] != props["CreatedDateTime"]:
            err(f"{w}: needs one 'created' activity matching CreatedDateTime")
        for a in acts:
            past(a["ActivityDateTime"], f"{w}.activity[{a['id']}]")
            if created and a["ActivityDateTime"] < created[0]["ActivityDateTime"]:
                err(f"{w}: activity {a['id']} is earlier than 'created'")


def array_scope_checks(data: dict) -> None:
    """COEP fails an "arrayScope" rule outright when that array is absent on every
    record of the type, even if the schema makes the field optional."""
    for type_name, records in data.items():
        rules_path = SCHEMAS / type_name / "rules.json"
        if not isinstance(records, list) or not records or not rules_path.exists():
            continue
        scopes = set(re.findall(r'"arrayScope":\s*"([^"]+)"', rules_path.read_text(encoding="utf-8")))
        for scope in sorted(scopes):
            def resolve(obj, parts=scope.split(".")):
                for p in parts:
                    obj = obj.get(p) if isinstance(obj, dict) else None
                return obj
            if not any(isinstance(resolve(r), list) for r in records):
                err(f"{type_name}: '{scope}' must be an array (use [] if unused) on at least one record; "
                    f"COEP rule arrayScope '{scope}' can't be evaluated otherwise")


def main() -> int:
    global AS_OF
    ap = argparse.ArgumentParser(description="Validate a COEP grounding-data package.")
    ap.add_argument("package", nargs="?", default=str(DEFAULT_PACKAGE))
    ap.add_argument("--as-of", help="Planned provisioning time (ISO, e.g. 2026-11-09T14:00Z) for the past-timestamp check; default now")
    args = ap.parse_args()
    if args.as_of:
        AS_OF = datetime.fromisoformat(args.as_of.replace("Z", "+00:00"))
        if AS_OF.tzinfo is None:
            AS_OF = AS_OF.replace(tzinfo=timezone.utc)
    pkg = Path(args.package).resolve()
    if not (pkg / "config.json").exists():
        err("config.json is required")
    data = schema_check(pkg)
    cross_checks(pkg, data)
    array_scope_checks(data)
    counts = ", ".join(f"{k}={len(v) if isinstance(v, list) else 1}" for k, v in sorted(data.items()))
    print(f"Package: {pkg}\nLoaded: {counts}")
    if errors:
        print(f"\n{len(errors)} problem(s):")
        for e in errors:
            print(f" - {e}")
        return 1
    print("OK: schema and cross-file checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
