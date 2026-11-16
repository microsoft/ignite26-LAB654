"""Build the Connectors_BRK220_Demo COEP grounding-data package.

Usage (from the repo root):
    python infra/brk220_environment/tenant/tools/build_tenant.py
    python infra/brk220_environment/tenant/tools/validate_package.py

Writes infra/brk220_environment/tenant/Connectors_BRK220_Demo/ from scenario.py: config.json, a
<type>.config.json per Microsoft 365 type, the QBR transcript, the OneDrive documents and das.config.json, which
installs the Rovo and Salesforce mock connector packages (mock_plugins/*_brk220.zip) for Megan. Build the plugin
ZIPs first (mock_plugins/build_plugins.py). The package is rebuilt from scratch on every run.

To update the packages in an existing tenant, bump each manifest version, rebuild the plugins, run this with
--da-update 2 (then 3, ...), publish the package as a new evalset version and update the tenant to it. Tenant
updates are incremental: items whose IDs already exist are skipped.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import scenario  # noqa: E402

PACKAGE_DIR = HERE.parent / "Connectors_BRK220_Demo"
PLUGINS_DIR = HERE.parents[1] / "mock_plugins"
DA_PLUGINS = ("rovo", "salesforce")

CONFIG = {
    "Tenant": {
        "Ring": "SDFv2",
        "VirtualTenantName": "Connectors_BRK220_Demo",
        "Tags": "Ignite2026,BRK220",
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
    "onlinemeetings": "onlinemeetings.config.json",
    "das": "das.config.json",
}
GENERATED_DIRS = ["transcripts", "files", "DAConfig"]
EMAIL_ARRAYS = ("ToRecipients", "CcRecipients", "BccRecipients")


def _write(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _build_das(update_version: str | None = None) -> list[dict]:
    destination = PACKAGE_DIR / "DAConfig"
    destination.mkdir(parents=True, exist_ok=True)
    requests = []
    for plugin in DA_PLUGINS:
        source = PLUGINS_DIR / f"{plugin}_brk220.zip"
        if not source.is_file():
            raise SystemExit(f"{source} is missing. Run mock_plugins/build_plugins.py first.")
        with ZipFile(source) as archive:
            manifest = json.loads(archive.read("manifest.json"))
        shutil.copyfile(source, destination / source.name)
        requests.append({
            "Name": manifest["name"]["short"],
            "ManifestId": manifest["id"],
            "ManifestLocation": f"DAConfig/{source.name}",
            # COEP updates an installed package when ActionType is Update and Version is the update number (2, 3, ...).
            "ActionType": "Update" if update_version else "Install",
            "Version": update_version or manifest["version"],
        })
    return [{"UPN": upn, "DARequests": requests} for upn in scenario.das_users()]


def _check_cutoff() -> None:
    late = [t for t in scenario.all_timestamps() if t > scenario.EVIDENCE_CUTOFF.strftime("%Y-%m-%dT%H:%M:%SZ")]
    if late:
        raise SystemExit(f"Timestamps after EVIDENCE_CUTOFF: {late}")


def main(update_version: str | None = None) -> None:
    _check_cutoff()
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    for p in PACKAGE_DIR.glob("*.config.json"):
        p.unlink()
    for d in GENERATED_DIRS:
        shutil.rmtree(PACKAGE_DIR / d, ignore_errors=True)

    data = {k: getattr(scenario, k, lambda: [])() for k in ENTITY_FILES if k != "das"}
    data["emails"] = [{**e, **{k: e.get(k) or [] for k in EMAIL_ARRAYS}} for e in data["emails"]]
    data["das"] = _build_das(update_version)

    _write(PACKAGE_DIR / "config.json", CONFIG)
    for key, name in ENTITY_FILES.items():
        if data[key]:
            _write(PACKAGE_DIR / name, data[key])

    for rel, text in scenario.transcripts().items():
        path = PACKAGE_DIR / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")

    for p in scenario.build_documents(PACKAGE_DIR / "files"):
        print(f"wrote {p.relative_to(PACKAGE_DIR)}")
    for key in ENTITY_FILES:
        print(f"{key}: {len(data[key])}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--da-update", metavar="N", help="write the connector packages as ActionType Update, Version N "
                        "(2 for the first update), to update them in an existing tenant")
    main(parser.parse_args().da_update)
