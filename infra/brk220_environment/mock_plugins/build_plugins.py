"""Build Microsoft 365 app package ZIPs for the mock plugins.

Every subfolder with a manifest.json is a plugin. Each builds to
<folder>_brk220.zip next to this script, with manifest.json at the root.

Usage:
    python build_plugins.py              # build all plugins
    python build_plugins.py lseg moodys  # build selected plugins
    python build_plugins.py --list       # list available plugins
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Fixed timestamp so rebuilding unchanged files gives an identical ZIP.
FIXED_DATE = (2026, 1, 1, 0, 0, 0)


def available_plugins() -> list[str]:
    return sorted(p.name for p in ROOT.iterdir() if (p / "manifest.json").is_file())


def validate(plugin_dir: Path) -> list[str]:
    errors = []
    try:
        manifest = json.loads((plugin_dir / "manifest.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"manifest.json is not valid JSON: {exc}"]
    for key in ("color", "outline"):
        icon = manifest.get("icons", {}).get(key)
        if not icon or not (plugin_dir / icon).is_file():
            errors.append(f"missing {key} icon: {icon}")
    for skill in manifest.get("agentSkills", []):
        if not (plugin_dir / skill["folder"] / "SKILL.md").is_file():
            errors.append(f"missing SKILL.md in {skill['folder']}")
    for connector in manifest.get("agentConnectors", []):
        url = connector.get("toolSource", {}).get("remoteMcpServer", {}).get("mcpServerUrl", "")
        if "REPLACE-WITH" in url:
            print(f"WARN {plugin_dir.name}: mcpServerUrl is still a placeholder ({url}). Set it to the deployed "
                  "mock server before uploading.", file=sys.stderr)
    return errors


def build(name: str) -> Path:
    plugin_dir = ROOT / name
    files = sorted(f for f in plugin_dir.rglob("*") if f.is_file())
    out = ROOT / f"{name}_brk220.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            info = zipfile.ZipInfo(f.relative_to(plugin_dir).as_posix(), FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, f.read_bytes())
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plugins", nargs="*", help="plugin folder names (default: all)")
    parser.add_argument("--list", action="store_true", help="list available plugins and exit")
    args = parser.parse_args()

    plugins = available_plugins()
    if args.list:
        print("\n".join(plugins))
        return 0

    selected = args.plugins or plugins
    unknown = [p for p in selected if p not in plugins]
    if unknown:
        print(f"Unknown plugin(s): {', '.join(unknown)}. Available: {', '.join(plugins)}", file=sys.stderr)
        return 1

    failed = False
    for name in selected:
        errors = validate(ROOT / name)
        if errors:
            failed = True
            print(f"FAIL {name}: " + "; ".join(errors), file=sys.stderr)
            continue
        out = build(name)
        print(f"OK   {name} -> {out.name} ({out.stat().st_size:,} bytes)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
