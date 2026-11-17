"""Build the Connectors_Ignite_EMP COEP grounding-data package.

Usage (from repo root):
    python infra/mock_environment/tools/build_tenant.py

Each scenario module in tools/scenarios may expose any of the M365 entity hooks
(users, emails, chats, events, files, teams, channels, channelmessages,
channelmessagereplies, onlinemeetings); missing hooks count as empty. Optional
extras:

- build_documents(files_dir): generate documents into Connectors_Ignite_EMP/files
- transcripts(): {"transcripts/<name>.vtt": text} meeting transcripts

The seven preinstalled mock connector packages are copied from mock_plugins
to DAConfig and assigned to Emil through das.config.json. Zava Expense is
excluded so attendees can install it in the custom MCP exercise.

Scenarios are written for a single attendee account, "emil". _expand_emils keeps
every original record unchanged and adds EMIL_COUNT extra lab accounts
(emil001...): every email, chat, event, online meeting, file and plugin set
involving Emil is copied per account with an ID suffix (-e001...), and the extra
accounts join the shared team (still owned by "emil") and its channels as members.

The package is rebuilt from scratch on every run. Then run validate_package.py.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from scenarios import engineering, expense, finance, legal, productivity  # noqa: E402

PACKAGE_DIR = HERE.parent / "Connectors_Ignite_EMP"
PLUGINS_DIR = HERE.parent / "mock_plugins"
DA_PLUGINS = ("github", "enghub", "imanage", "factset", "lseg", "salesdesk", "moodys")

SCENARIOS = [legal, finance, productivity, engineering, expense]

CONFIG = {
    "Tenant": {
        "Ring": "SDFv2",
        "VirtualTenantName": "Connectors_Ignite_EMP",
        "Tags": "Ignite2026,LAB654",
        "IsShared": False,
    },
    "TenantCount": 1,
}

ENTITY_FILES = {
    "users": "users.config.json",
    "emails": "emails.config.json",
    "chats": "chats.config.json",
    "events": "events.config.json",
    "files": "files.config.json",
    "teams": "teams.config.json",
    "channels": "channels.config.json",
    "channelmessages": "channelmessages.config.json",
    "channelmessagereplies": "channelmessagereplies.config.json",
    "onlinemeetings": "onlinemeetings.config.json",
    "das": "das.config.json",
}

# Generated directories cleared on every rebuild.
GENERATED_DIRS = ["transcripts", "files", "DAConfig"]


def _merge_users(lists):
    seen: dict[str, dict] = {}
    for lst in lists:
        for u in lst:
            if u["MailNickName"] in seen and seen[u["MailNickName"]] != u:
                raise ValueError(f"Conflicting definitions for user {u['MailNickName']}")
            seen[u["MailNickName"]] = u
    return list(seen.values())


# COEP's "arrayScope" rules (e.g. "BccRecipient should not have Flag... when it is
# group") fail when the array is absent on every record, even though the schema
# makes it optional. Always emit the recipient arrays, empty if unused.
EMAIL_ARRAYS = ("ToRecipients", "CcRecipients", "BccRecipients")


def _normalize_email(e: dict) -> dict:
    return {**e, **{k: e.get(k) or [] for k in EMAIL_ARRAYS}}


def _write(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


EMIL_COUNT = 114
# Per-Emil copies get these ID fields suffixed; references to them are remapped.
COPIED_IDS = {
    "emails": "EmailId",
    "chats": "ChatId",
    "events": "EventId",
    "onlinemeetings": "OnlineMeetingId",
    "files": "FileId",
}


def _emil(n: int) -> str:
    return f"{legal.EMIL}{n:03d}"


def _replace(o, mapping: dict[str, str]):
    if isinstance(o, dict):
        return {k: _replace(v, mapping) for k, v in o.items()}
    if isinstance(o, list):
        return [_replace(v, mapping) for v in o]
    return mapping.get(o, o) if isinstance(o, str) else o


def _involves_emil(o) -> bool:
    if isinstance(o, dict):
        return any(_involves_emil(v) for v in o.values())
    if isinstance(o, list):
        return any(_involves_emil(v) for v in o)
    return o == legal.EMIL


def _expand_emils(data: dict) -> None:
    emils = [_emil(n) for n in range(1, EMIL_COUNT + 1)]
    template = next(u for u in data["users"] if u["MailNickName"] == legal.EMIL)
    copy = {k: v for k, v in template.items() if k != "PhoneNumber"}
    data["users"] += [{**copy, "MailNickName": e} for e in emils]

    per_emil = {k: [r for r in data[k] if _involves_emil(r)] for k in COPIED_IDS}
    ids = [r[COPIED_IDS[k]] for k, rows in per_emil.items() for r in rows]
    # COEP rejects a transcript shared by several meetings, so each Emil gets his own copy.
    paths = [t["TranscriptFile"] for m in per_emil["onlinemeetings"] for t in m.get("Transcripts") or []]
    data["copies"] = []
    for n, e in enumerate(emils, 1):
        mapping = {legal.EMIL: e, **{i: f"{i}-e{n:03d}" for i in ids}}
        for p in paths:
            src = PurePosixPath(p)
            dst = src.with_stem(f"{src.stem}-e{n:03d}")
            mapping[p] = str(dst)
            data["copies"].append((p, str(dst)))
        for k, rows in per_emil.items():
            data[k] += [_replace(r, mapping) for r in rows]

    for t in data["teams"]:
        if _involves_emil(t):
            t["Members"] = (t.get("Members") or []) + emils
    for c in data["channels"]:
        if legal.EMIL in c.get("Members", []):
            c["Members"] = c["Members"] + emils
    if _involves_emil([data[k] for k in ("channelmessages", "channelmessagereplies")]):
        raise ValueError("Emil must not post channel messages; channels are shared by all Emils")
    data["das"] += [{**d, "UPN": e} for d in data["das"] for e in emils]


def _build_das() -> list[dict]:
    destination = PACKAGE_DIR / "DAConfig"
    destination.mkdir(parents=True, exist_ok=True)
    requests = []
    for plugin in DA_PLUGINS:
        source = PLUGINS_DIR / f"{plugin}_lab.zip"
        with ZipFile(source) as archive:
            manifest = json.loads(archive.read("manifest.json"))
        shutil.copyfile(source, destination / source.name)
        requests.append({
            "Name": manifest["name"]["short"],
            "ManifestId": manifest["id"],
            "ManifestLocation": f"DAConfig/{source.name}",
            "ActionType": "Install",
            "Version": manifest["version"],
        })
    return [{"UPN": legal.EMIL, "DARequests": requests}]


def main() -> None:
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    for p in PACKAGE_DIR.glob("*.config.json"):
        p.unlink()
    for d in GENERATED_DIRS:
        shutil.rmtree(PACKAGE_DIR / d, ignore_errors=True)

    def hook(s, name):
        return getattr(s, name, lambda: [])()

    data = {k: [x for s in SCENARIOS for x in hook(s, k)] for k in ENTITY_FILES}
    data["users"] = _merge_users(hook(s, "users") for s in SCENARIOS)
    # Bring your own app step 3a: "submit the report to my manager" -> Hannes Niemi.
    for u in data["users"]:
        if u["MailNickName"] == "emil":
            u["Manager"] = "hannes"
    data["emails"] = [_normalize_email(e) for e in data["emails"]]
    data["das"] = _build_das()
    _expand_emils(data)

    _write(PACKAGE_DIR / "config.json", CONFIG)
    for key, name in ENTITY_FILES.items():
        if data[key]:
            _write(PACKAGE_DIR / name, data[key])

    data["transcripts"] = []
    for s in SCENARIOS:
        for rel, text in getattr(s, "transcripts", dict)().items():
            path = PACKAGE_DIR / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
            data["transcripts"].append(rel)

    files_dir = PACKAGE_DIR / "files"
    for s in SCENARIOS:
        build = getattr(s, "build_documents", None)
        for p in build(files_dir) if build else []:
            print(f"wrote {p.relative_to(PACKAGE_DIR)}")
    for src, dst in data["copies"]:
        (PACKAGE_DIR / dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PACKAGE_DIR / src, PACKAGE_DIR / dst)
    print(f"per-Emil transcript copies: {len(data['copies'])}")
    for key in [*ENTITY_FILES, "transcripts"]:
        print(f"{key}: {len(data[key])}")


if __name__ == "__main__":
    main()
