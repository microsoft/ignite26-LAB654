"""Build the Connectors_Ignite_EMP COEP grounding-data package.

Usage (from repo root):
    python src/mock_environment/tools/build_tenant.py

Each scenario module in tools/scenarios exposes users(), emails(), chats(),
events() and files(), and optionally build_documents(files_dir) for documents
that must be generated into Connectors_Ignite_EMP/files. The package is
rebuilt from scratch on every run. Then run validate_package.py.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from scenarios import legal  # noqa: E402

PACKAGE_DIR = HERE.parent / "Connectors_Ignite_EMP"

# Add finance / productivity modules here as they're authored.
SCENARIOS = [legal]

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
}


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


def main() -> None:
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    for p in PACKAGE_DIR.glob("*.config.json"):
        p.unlink()

    data = {
        "users": _merge_users(s.users() for s in SCENARIOS),
        "emails": [_normalize_email(e) for s in SCENARIOS for e in s.emails()],
        "chats": [c for s in SCENARIOS for c in s.chats()],
        "events": [e for s in SCENARIOS for e in s.events()],
        "files": [f for s in SCENARIOS for f in s.files()],
    }

    _write(PACKAGE_DIR / "config.json", CONFIG)
    for key, name in ENTITY_FILES.items():
        if data[key]:
            _write(PACKAGE_DIR / name, data[key])

    files_dir = PACKAGE_DIR / "files"
    for s in SCENARIOS:
        build = getattr(s, "build_documents", None)
        for p in build(files_dir) if build else []:
            print(f"wrote {p.relative_to(PACKAGE_DIR)}")
    for key in ENTITY_FILES:
        print(f"{key}: {len(data[key])}")


if __name__ == "__main__":
    main()
