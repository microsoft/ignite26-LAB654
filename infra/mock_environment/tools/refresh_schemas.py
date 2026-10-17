"""Refresh infra/mock_environment/_schemas from the COEP Schema Master API.

Usage (from repo root):
    $env:COEP_TOKEN = "<bearer token>"
    python infra/mock_environment/tools/refresh_schemas.py

Getting a token: sign in to https://coep.microsoft.com/schema/portal, open the
browser dev tools, and copy the ``Authorization: Bearer ...`` value from any
request to ``/schema/api/v1`` (or the access token from MSAL session storage).

For each type it writes the "Latest" schema, plus rules and examples for that
version, to ``_schemas/<Category>/<typeName>/`` and rewrites manifest.json.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://coep.microsoft.com/schema/api/v1"
PORTAL = "https://coep.microsoft.com/schema/portal"
OUT = Path(__file__).resolve().parent.parent / "_schemas"
EXCLUDE = {"andy_test"}  # test types on the portal


def get(token: str, path: str, **params):
    url = f"{API}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def dump(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    token = os.environ.get("COEP_TOKEN", "").removeprefix("Bearer ").strip()
    if not token:
        print("Set COEP_TOKEN to a bearer token for the COEP schema API.", file=sys.stderr)
        return 2

    types = get(token, "/types")
    if isinstance(types, dict):
        types = types.get("items") or types.get("types") or types.get("value") or []
    manifest = []
    staging = OUT.with_name("_schemas.tmp")
    shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir()

    for t in sorted(types, key=lambda x: (x["category"], x["typeName"])):
        name, cat = t["typeName"], t["category"]
        if name in EXCLUDE:
            continue
        info = get(token, f"/types/{name}", category=cat)
        tags = info.get("tags") or {}
        version = tags.get("Latest") or (info.get("availableVersions") or [None])[-1]
        d = staging / cat / name
        d.mkdir(parents=True)

        schemas = get(token, f"/types/{name}/schemas", category=cat, tag="Latest")
        if schemas:
            content = schemas[0]["content"]
            try:
                dump(d / "schema.json", json.loads(content))
            except (TypeError, json.JSONDecodeError):
                (d / "schema.txt").write_text(str(content), encoding="utf-8")
        for kind in ("rules", "examples"):
            try:
                res = get(token, f"/types/{name}/{kind}", category=cat, version=version)
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    continue
                raise
            if res:
                dump(d / f"{kind}.json", res)

        manifest.append({
            "typeName": name,
            "displayName": t.get("displayName"),
            "category": cat,
            "dataFormat": t.get("dataFormat"),
            "dataSourceType": t.get("dataSourceType"),
            "version": version,
            "tags": tags,
            "description": t.get("description"),
            "path": f"{cat}/{name}",
        })
        print(f"{cat}/{name} {version}")

    dump(staging / "manifest.json", {
        "source": PORTAL,
        "api": API,
        "fetchedAt": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "types": manifest,
    })
    shutil.rmtree(OUT, ignore_errors=True)
    staging.rename(OUT)
    print(f"Refreshed {len(manifest)} types into {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
