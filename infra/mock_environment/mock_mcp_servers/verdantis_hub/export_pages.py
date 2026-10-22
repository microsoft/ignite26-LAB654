"""Write seed_files/pages.json from the COEP tenant generator, so the site and the tenant's indexed pages match.

Run after changing the pages in tools/scenarios/productivity/__init__.py:

    python verdantis_hub/export_pages.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[1] / "tools"
OUT = HERE / "seed_files" / "pages.json"


def build() -> list[dict]:
    sys.path.insert(0, str(TOOLS))
    from scenarios import productivity

    pages = productivity.hub_pages()
    for page in pages:
        # Links become site-relative so the site works on any host, locally included.
        page["html"] = page["html"].replace(productivity.HUB, "")
    return pages


def main() -> None:
    OUT.write_text(json.dumps(build(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
