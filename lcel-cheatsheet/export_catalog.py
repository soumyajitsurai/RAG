"""Write space-static/catalog_data.json from catalog.py."""

from __future__ import annotations

import json
from pathlib import Path

from catalog import CATEGORIES, ENTRIES, QUICK_REF

OUT = Path(__file__).parent / "space-static" / "catalog_data.json"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(
            {"categories": CATEGORIES, "entries": ENTRIES, "quickRef": QUICK_REF},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT} ({len(ENTRIES)} entries)")


if __name__ == "__main__":
    main()
