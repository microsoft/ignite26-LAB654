"""Build the Connectors_Ignite_EMP COEP grounding-data package.

Usage (from repo root):
    python infra/mock_environment/tools/build_tenant.py

Each scenario module in tools/scenarios may expose any of the M365 entity hooks
(users, emails, chats, events, files, teams, channels, channelmessages,
channelmessagereplies, onlinemeetings); missing hooks count as empty. Optional
extras:

- build_documents(files_dir): generate documents into Connectors_Ignite_EMP/files
- transcripts(): {"transcripts/<name>.vtt": text} meeting transcripts
- confluencepages(): Confluence synced-connector pages (confluence/confluence_<scenario>.jsonl)
- customconnectors(): custom synced connections such as the Jira connector
  (customconnectors/customconnectors_<scenario>.jsonl, one connection per line)

The package is rebuilt from scratch on every run. Then run validate_package.py.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from scenarios import engineering, expense, finance, legal, productivity  # noqa: E402

PACKAGE_DIR = HERE.parent / "Connectors_Ignite_EMP"

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
}

# Connector (3P) types use a different layout: <type>/<type>_<name>.jsonl, one
# searchable item per line (COEP Connector Entity Guide). One file per scenario.
CONNECTOR_TYPES = {"confluence": "confluencepages", "customconnectors": "customconnectors"}

# Generated directories cleared on every rebuild.
GENERATED_DIRS = [*CONNECTOR_TYPES, "transcripts"]


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


def _write_jsonl(path: Path, items) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in items), encoding="utf-8")


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

    _write(PACKAGE_DIR / "config.json", CONFIG)
    for key, name in ENTITY_FILES.items():
        if data[key]:
            _write(PACKAGE_DIR / name, data[key])

    for t, fn in CONNECTOR_TYPES.items():
        data[t] = []
        for s in SCENARIOS:
            items = hook(s, fn)
            if items:
                _write_jsonl(PACKAGE_DIR / t / f"{t}_{s.__name__.rsplit('.', 1)[-1]}.jsonl", items)
                data[t] += items

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
    for key in [*ENTITY_FILES, *CONNECTOR_TYPES, "transcripts"]:
        print(f"{key}: {len(data[key])}")


if __name__ == "__main__":
    main()
