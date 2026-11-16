"""Make the shared framework, domain models and every server package importable in tests."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for folder in (ROOT / "_framework", *sorted({p.parent for p in ROOT.glob("*/mock_*")})):
    if folder.is_dir() and str(folder.resolve()) not in sys.path:
        sys.path.insert(0, str(folder.resolve()))