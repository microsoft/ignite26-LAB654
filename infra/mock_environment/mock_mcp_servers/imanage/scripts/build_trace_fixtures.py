"""Turn the recorded Office (Word) trace of the live iManage Work connector into shape fixtures for the tests.

Each fixture is ``{"tool", "args", "summary", "items"}``: the live result with Office's wrapper keys removed, the
real host replaced, the CELA-approved fictitious names swapped in and long text trimmed. The tests compare key
sets/order and value types against the mock, not values (the seed is a newer copy of the matter).

    python scripts/build_trace_fixtures.py --trace <unzipped trace>/agent/conversations/<id>/workspace/search
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "tests" / "fixtures"
WRAPPER = {"entityKey", "citationKey", "title", "snippet", "type", "id", "displayName"}
CALLS = {  # result file suffix -> (fixture name, tool, args as the mock should be called)
    # The live connector returned nothing for this query even though its words all appear in the playbook; the
    # mock's word-AND search would hit, so the fixture asks for an absent term to check the empty-result shape.
    "1793358924317": ("01_search_no_match", "search",
                      {"query": "Contoso AI Procurement Playbook hard stops"}),
    "1793358934200": ("02_search_workspaces", "search_workspaces", {"searchParams": {"name": "Trey Research"},
                                                                    "limit": 100}),
    "1793358945145": ("03_get_container_children", "get_container_children",
                      {"container_id": "Dev!1870", "container_type": "workspace"}),
    "1793358952852": ("04_search_folders", "search_folders", {"container_id": "Dev!1870", "name": "Playbooks"}),
    "1793358968394": ("05_search", "search", {"query": "AI Procurement Playbook"}),
    "1793358976966": ("06_fetch", "fetch", {"id": "DEV!252567.1"}),
    "1793358986427": ("07_get_document_profile", "get_document_profile", {"documentId": "DEV!252567.1"}),
}
HOST = re.compile(r"[\w-]+\.cloudimanage\.com")
RENAMES = [
    ("Cognivault Nexus", "Trey Research – AI Platform Agreement"),
    ("Cognivault", "Trey Research"),
    ("Verdantis Technologies, Inc.", "Zava, Inc."),
    ("VERDANTIS TECHNOLOGIES, INC.", "ZAVA, INC."),
    ("Verdantis", "Zava"),
    ("VTI-LEGAL-PB-AI-2.1", "ZAVA-LEGAL-PB-AI-2.1"),
    ('"123"', '"EMIL"'),
    ('"hyi"', '"Emil Vanggaard"'),
    ('"02 Playbooks"', '"Playbooks"'),
    ('"04 Drafts"', '"Drafts"'),
]
# The recorded matter had four folders; the lab matter keeps only these two.
DROPPED_FOLDERS = {"01 Vendor Paper", "03 Research"}


def _clean(entry: dict) -> dict:
    out = {k: v for k, v in entry.items() if k not in WRAPPER}
    if "text" in out and len(out["text"]) > 400:
        out["text"] = out["text"][:400]
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--trace", type=Path, required=True, help="folder holding result_connector_imanage-*.json")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    for suffix, (name, tool, call_args) in CALLS.items():
        entries = json.loads((args.trace / f"result_connector_imanage-work-mcp_{suffix}.json")
                             .read_text(encoding="utf-8"))["imanage-work-mcp"]
        if tool in ("fetch", "get_document_profile"):
            summary, items = _clean(entries[0]), []
        else:
            summary = _clean(entries[0])
            items = [_clean(e) for e in entries[1:] if e.get("name") not in DROPPED_FOLDERS]
            if "cursor" in summary:
                summary["cursor"] = len(items)
        text = json.dumps({"tool": tool, "args": call_args, "summary": summary, "items": items},
                          ensure_ascii=False, indent=1)
        text = HOST.sub("imanage.example.com", text)
        for old, new in RENAMES:
            text = text.replace(old, new)
        (OUT / f"{name}.json").write_text(text + "\n", encoding="utf-8")
        print(f"{name}.json")


if __name__ == "__main__":
    main()
