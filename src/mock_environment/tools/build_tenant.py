"""Build the Connectors_Ignite_EMP COEP grounding-data package.

Usage (from repo root):
    python src/mock_environment/tools/build_tenant.py [--anchor 2026-10-05]

``--anchor`` is the scenario's "today" (a Monday). Email and file timestamps
must be in the past when the package is provisioned, so pick an anchor on or
before the provisioning date. Re-run after changing any scenario module, then
run validate_package.py.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from scenarios import legal  # noqa: E402

PACKAGE_DIR = HERE.parent / "Connectors_Ignite_EMP"
DEFAULT_ANCHOR = "2026-10-05"

# Add finance / productivity modules here as they're authored.
SCENARIOS = [legal]

CONFIG = {
    "Tenant": {
        "Ring": "Production",
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


def _write(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--anchor", default=DEFAULT_ANCHOR, help="Scenario 'today' (YYYY-MM-DD, a Monday)")
    args = ap.parse_args()
    anchor = date.fromisoformat(args.anchor)
    if anchor.weekday() != 0:
        ap.error(f"--anchor {anchor} is not a Monday")

    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    files_dir = PACKAGE_DIR / "files"

    data = {
        "users": _merge_users(s.users() for s in SCENARIOS),
        "emails": [e for s in SCENARIOS for e in s.emails(anchor)],
        "chats": [c for s in SCENARIOS for c in s.chats(anchor)],
        "events": [e for s in SCENARIOS for e in s.events(anchor)],
        "files": [f for s in SCENARIOS for f in s.files(anchor)],
    }

    _write(PACKAGE_DIR / "config.json", CONFIG)
    for key, name in ENTITY_FILES.items():
        if data[key]:
            _write(PACKAGE_DIR / name, data[key])

    for s in SCENARIOS:
        for p in s.build_documents(files_dir):
            print(f"wrote {p.relative_to(PACKAGE_DIR)}")
    for key in ENTITY_FILES:
        print(f"{key}: {len(data[key])}")
    print(f"anchor (scenario 'today'): {anchor}")


if __name__ == "__main__":
    main()
