"""Validate a COEP grounding-data package against the local _schemas.

Usage (from repo root):
    python src/mock_environment/tools/validate_package.py [package_dir]

Checks each *.config.json (and config.json) against its JSON schema, then a
subset of the COEP cross-file rules (user references, file references, shared
links, placeholders, email chains, licences, timestamps). It doesn't replace
COEP's own validation; it catches the common mistakes before upload.
"""

from __future__ import annotations

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


def err(msg: str) -> None:
    errors.append(msg)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def schema_check(pkg: Path) -> dict[str, list | dict]:
    data = {}
    targets = {"config": pkg / "config.json"}
    for p in pkg.glob("*.config.json"):
        targets[p.name.split(".")[0].lower()] = p
    for type_name, path in targets.items():
        schema_path = SCHEMAS / type_name / "schema.json"
        if not schema_path.exists():
            err(f"{path.name}: no local schema for type '{type_name}'")
            continue
        doc = load(path)
        data[type_name] = doc
        schema = load(schema_path)
        v = validator_for(schema)(schema, format_checker=validator_for(schema).FORMAT_CHECKER)
        for e in sorted(v.iter_errors(doc), key=lambda e: list(e.absolute_path)):
            loc = "/".join(str(x) for x in e.absolute_path)
            err(f"{path.name}:{loc}: {e.message[:300]}")
    return data


def past(ts: str, what: str) -> None:
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if dt > datetime.now(timezone.utc):
        err(f"{what}: timestamp {ts} is in the future (COEP requires past timestamps)")


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


def main() -> int:
    pkg = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_PACKAGE
    if not (pkg / "config.json").exists():
        err("config.json is required")
    data = schema_check(pkg)
    cross_checks(pkg, data)
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
