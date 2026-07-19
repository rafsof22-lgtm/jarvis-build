#!/usr/bin/env python3
"""Create a deterministic source inventory for Jarvis ingestion planning."""
from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--no-hash", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        parser.error(f"root is not a directory: {root}")

    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and not path.is_symlink():
            stat = path.stat()
            rows.append({
                "relative_path": path.relative_to(root).as_posix(),
                "size_bytes": stat.st_size,
                "modified_ns": stat.st_mtime_ns,
                "extension": path.suffix.lower(),
                "sha256": "" if args.no_hash else sha256_file(path),
                "status": "NEW",
            })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "relative_path", "size_bytes", "modified_ns", "extension", "sha256", "status"
        ])
        writer.writeheader()
        writer.writerows(rows)
    print(f"inventoried_files={len(rows)} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
