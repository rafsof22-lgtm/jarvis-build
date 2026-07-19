#!/usr/bin/env python3
"""Validate Jarvis requirement traceability CSVs without external dependencies."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

REQUIRED = [
    "requirement_id", "source_ids", "master_section", "module_id",
    "implementation_path", "test_ids", "evidence_ids", "status",
]
DONE = {"done", "complete", "implemented", "verified", "released", "done_verified"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--json", dest="json_path")
    args = parser.parse_args()
    path = Path(args.csv_path)
    if not path.exists():
        print(f"missing file: {path}", file=sys.stderr)
        return 2

    errors: list[dict] = []
    rows = 0
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        missing_cols = [column for column in REQUIRED if column not in fields]
        if missing_cols:
            errors.append({"row": 1, "error": "missing_columns", "fields": missing_cols})
        for line, row in enumerate(reader, start=2):
            rows += 1
            if not row.get("requirement_id", "").strip():
                errors.append({"row": line, "error": "missing_requirement_id"})
            status = row.get("status", "").strip().lower()
            if status in DONE:
                missing = [column for column in REQUIRED[1:-1] if not row.get(column, "").strip()]
                if missing:
                    errors.append({
                        "row": line,
                        "requirement_id": row.get("requirement_id"),
                        "error": "false_done_risk",
                        "fields": missing,
                    })

    result = {"file": str(path), "rows": rows, "passed": not errors, "errors": errors}
    text = json.dumps(result, indent=2)
    print(text)
    if args.json_path:
        Path(args.json_path).write_text(text + "\n", encoding="utf-8")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
