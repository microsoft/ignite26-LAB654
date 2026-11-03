"""Validate a COEP grounding-data package against the local _schemas.

Usage (from repo root):
    python infra/mock_environment/tools/validate_package.py [package_dir] [--as-of 2026-11-09T14:00Z]

Checks each *.config.json (and config.json) against its JSON schema, then a
subset of the COEP cross-file rules (user references, file references, shared
links, placeholders, email chains, licences, timestamps, teams/channels,
online meetings and WebVTT transcripts). It doesn't replace COEP's own validation; it
catches the common mistakes before upload.
"""

from __future__ import annotations

import argparse
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


def schema_check(pkg: Path) -> dict[str, list | dict]:
    data = {}
    targets = {"config": [pkg / "config.json"]}
    for p in pkg.glob("*.config.json"):
        targets[p.name.split(".")[0].lower()] = [p]
    for type_name, paths in targets.items():
        schema_path = SCHEMAS / type_name / "schema.json"
        if not schema_path.exists():
            err(f"{paths[0].name}: no local schema for type '{type_name}'")
            continue
        doc = load(paths[0])
        data[type_name] = doc
        schema = load(schema_path)
        v = validator_for(schema)(schema, format_checker=validator_for(schema).FORMAT_CHECKER)
        for e in sorted(v.iter_errors(doc), key=lambda e: list(e.absolute_path)):
            loc = "/".join(str(x) for x in e.absolute_path)
            err(f"{paths[0].name}:{loc}: {e.message[:300]}")
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

    teams_m365_checks(data, users, teams_licensed, event_ids, chat_ids, user)
    online_meeting_checks(pkg, data, users, user)


def teams_m365_checks(data, users, teams_licensed, event_ids, chat_ids, user) -> None:
    teams = {}
    for t in data.get("teams", []):
        w = f"teams[{t['TeamId']}]"
        if t["TeamId"] in teams:
            err(f"{w}: duplicate TeamId")
        teams[t["TeamId"]] = t
        past(t["CreatedDateTime"], w)
        owners, members = set(t.get("Owners") or []), set(t.get("Members") or [])
        if owners & members:
            err(f"{w}: Owners and Members overlap {sorted(owners & members)}")
        for m in owners | members:
            user(m, f"{w}.Owners/Members")
    if len({t["Name"] for t in teams.values()}) != len(teams):
        err("teams: Name must be unique")

    channels = {}
    for c in data.get("channels", []):
        w = f"channels[{c['ChannelId']}]"
        if c["ChannelId"] in channels:
            err(f"{w}: duplicate ChannelId")
        channels[c["ChannelId"]] = c
        team = teams.get(c["TeamId"])
        if not team:
            err(f"{w}: TeamId {c['TeamId']} not in teams")
            continue
        if c["Name"].strip().lower() == "general":
            err(f"{w}: channel name must not be General")
        if c.get("CreatedDateTime"):
            past(c["CreatedDateTime"], w)
            if c["CreatedDateTime"] < team["CreatedDateTime"]:
                err(f"{w}: CreatedDateTime earlier than team CreatedDateTime")
        roster = set(team.get("Owners") or []) | set(team.get("Members") or [])
        for m in [*c["Members"], *([c["Creator"]] if c.get("Creator") else [])]:
            user(m, f"{w}.Members")
            if m not in roster:
                err(f"{w}: member {m} is not in team {c['TeamId']}")
            if m in users and m not in teams_licensed:
                err(f"{w}: member {m} lacks 'Microsoft Teams Enterprise' licence")
    names = [(c["TeamId"], c["Name"]) for c in channels.values()]
    if len(names) != len(set(names)):
        err("channels: Name must be unique within a team")

    msgs, sent = {}, {}
    for m in data.get("channelmessages", []):
        w = f"channelmessages[{m['ChannelMessageId']}]"
        if m["ChannelMessageId"] in msgs:
            err(f"{w}: duplicate ChannelMessageId")
        msgs[m["ChannelMessageId"]] = m
        ch = channels.get(m["ChannelId"])
        if not ch:
            err(f"{w}: ChannelId {m['ChannelId']} not in channels")
            continue
        past(m["SentDateTime"], w)
        if m["From"] not in ch["Members"]:
            err(f"{w}: From is not a member of the channel")
        if ch.get("CreatedDateTime") and m["SentDateTime"] < ch["CreatedDateTime"]:
            err(f"{w}: sent before the channel was created")
        sent.setdefault(m["ChannelId"], []).append(m["SentDateTime"])
    reply_ids = set()
    for r in data.get("channelmessagereplies", []):
        w = f"channelmessagereplies[{r['ChannelMessageReplyId']}]"
        if r["ChannelMessageReplyId"] in reply_ids:
            err(f"{w}: duplicate ChannelMessageReplyId")
        reply_ids.add(r["ChannelMessageReplyId"])
        parent = msgs.get(r["ChannelMessageId"])
        if not parent:
            err(f"{w}: ChannelMessageId {r['ChannelMessageId']} not in channelmessages")
            continue
        past(r["SentDateTime"], w)
        if r["SentDateTime"] < parent["SentDateTime"]:
            err(f"{w}: sent before its parent message")
        ch = channels.get(parent["ChannelId"])
        if ch and r["From"] not in ch["Members"]:
            err(f"{w}: From is not a member of the channel")
        sent.setdefault(parent["ChannelId"], []).append(r["SentDateTime"])
    for ch, times in sent.items():
        if len(times) != len(set(times)):
            err(f"channels[{ch}]: SentDateTime values must be unique across messages and replies")


VTT_TS = r"(\d{2}:)?\d{2}:\d{2}\.\d{3}"
VTT_TIMING = re.compile(rf"^({VTT_TS}) --> ({VTT_TS})(\s.*)?$")
VTT_SPEAKER = re.compile(r"<v(?:\.[^ >]+)* ([^>]+)>")


def _vtt_seconds(ts: str) -> float:
    parts = [float(x) for x in ts.split(":")]
    return sum(v * 60 ** i for i, v in enumerate(reversed(parts)))


def vtt_check(path: Path, allowed: set[str], where: str) -> None:
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    blocks = text.split("\n\n")
    if not blocks[0].startswith("WEBVTT") or "\n" in blocks[0].strip():
        err(f"{where}: must start with 'WEBVTT' followed by a blank line")
    if text.count("WEBVTT") > 1 and not all(b.startswith("NOTE") for b in blocks[1:] if "WEBVTT" in b):
        err(f"{where}: duplicate WEBVTT signature")
    cues, last = 0, -1.0
    for b in blocks[1:]:
        lines = [l for l in b.split("\n") if l != ""]
        if not lines or lines[0].startswith("NOTE"):
            continue
        idx = 0 if "-->" in lines[0] else 1
        if idx >= len(lines) or not (m := VTT_TIMING.match(lines[idx])):
            err(f"{where}: cue '{lines[0][:40]}' has no valid timing line")
            continue
        start, end = _vtt_seconds(m.group(1)), _vtt_seconds(m.group(3))
        if end <= start:
            err(f"{where}: cue '{lines[0][:40]}' end time must be after start time")
        if start < last:
            err(f"{where}: cue '{lines[0][:40]}' is out of order")
        last = start
        if len(lines) == idx + 1:
            err(f"{where}: cue '{lines[0][:40]}' has no text")
        for line in lines[idx + 1:]:
            for spk in VTT_SPEAKER.findall(line):
                if spk not in allowed:
                    err(f"{where}: speaker '{spk}' is not the event sender or an attendee")
        cues += 1
    if not cues:
        err(f"{where}: must contain at least one cue")


def online_meeting_checks(pkg: Path, data: dict, users: dict, user) -> None:
    events = {e["EventId"]: e for e in data.get("events", [])}
    seen = set()
    for om in data.get("onlinemeetings", []):
        w = f"onlinemeetings[{om['OnlineMeetingId']}]"
        if om["OnlineMeetingId"] in seen:
            err(f"{w}: duplicate OnlineMeetingId")
        seen.add(om["OnlineMeetingId"])
        if om.get("StartDateTime") and om.get("EndDateTime") and om["StartDateTime"] >= om["EndDateTime"]:
            err(f"{w}: StartDateTime must be earlier than EndDateTime")
        ev = events.get(om.get("EventId"))
        if not ev:
            err(f"{w}: EventId {om.get('EventId')} not in events")
            continue
        if not ev.get("IsOnlineMeeting"):
            err(f"{w}: referenced event is not an online meeting")
        if om.get("Owner") != ev["Sender"]:
            err(f"{w}: Owner must be the event Sender")
        parts = om.get("Participants") or []
        if len(parts) > 15:
            err(f"{w}: more than 15 participants")
        for p in parts:
            user(p, f"{w}.Participants")
        group = {ev["Sender"]} | {a["Email"] for f in ("RequiredAttendees", "OptionalAttendees") for a in ev.get(f) or []}
        names = {users[n]["DisplayName"] for n in group if n in users} | group
        for t in om.get("Transcripts") or []:
            f = pkg / t["TranscriptFile"]
            if not f.is_file():
                err(f"{w}: transcript {t['TranscriptFile']} missing")
            else:
                vtt_check(f, names, f"{w}:{t['TranscriptFile']}")


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
