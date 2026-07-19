#!/usr/bin/env python3
"""Create a redacted configuration-readiness report.

Only variable names, file paths, counts, and readiness states are written.
Values are never included. The scanner performs no external connection,
mutation, deletion, rotation, or account action.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re

NAME = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b")
ENV_ASSIGN = re.compile(r"^\s*([A-Z][A-Z0-9_]{2,})\s*=", re.MULTILINE)
INTERESTING = ("KEY", "TOKEN", "SECRET", "PASSWORD", "CLIENT_ID", "CLIENT_SECRET", "URL", "URI", "HOST", "PORT", "DATABASE", "POSTGRES", "REDIS", "WEBHOOK", "PROJECT_ID", "ORG_ID", "SHEET_ID", "BUCKET", "REGION")
TEXT_SUFFIXES = {".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yml", ".yaml", ".md", ".txt", ".sh", ".toml", ".ini", ".example"}
SKIP_PARTS = {".git", "node_modules", ".next", "dist", "build", "coverage", "vendor", "__pycache__"}


def is_text_candidate(path: Path) -> bool:
    if any(part in SKIP_PARTS for part in path.parts):
        return False
    return path.name.startswith(".env") or path.suffix.lower() in TEXT_SUFFIXES


def classify_name(name: str) -> str:
    if any(word in name for word in ("KEY", "TOKEN", "SECRET", "PASSWORD")):
        return "sensitive_value"
    if any(word in name for word in ("URL", "URI", "HOST", "PORT", "REGION")):
        return "connection_metadata"
    return "configuration"


def scan(root: Path) -> dict:
    references: dict[str, set[str]] = defaultdict(set)
    templates: dict[str, set[str]] = defaultdict(set)
    tracked_env_files: list[str] = []
    unreadable: list[str] = []

    for path in root.rglob("*"):
        if not path.is_file() or not is_text_candidate(path):
            continue
        rel = path.relative_to(root).as_posix()
        if path.name.startswith(".env") and path.name not in {".env.example", ".env.template", ".env.sample"}:
            tracked_env_files.append(rel)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            unreadable.append(rel)
            continue
        for name in NAME.findall(text):
            if any(marker in name for marker in INTERESTING):
                references[name].add(rel)
        if path.name in {".env.example", ".env.template", ".env.sample"}:
            for name in ENV_ASSIGN.findall(text):
                templates[name].add(rel)

    names = sorted(set(references) | set(templates))
    records = []
    for name in names:
        records.append({
            "name": name,
            "class": classify_name(name),
            "referenced_in": sorted(references.get(name, set())),
            "declared_in_template": sorted(templates.get(name, set())),
            "template_status": "declared" if templates.get(name) else "missing_template_entry",
            "value_status": "not_inspected",
            "owner_action": "Add or verify this name in the approved platform configuration only when its owning module requires it.",
        })

    return {
        "schema_version": "1.0.0",
        "scope": str(root),
        "safety": {
            "values_emitted": False,
            "external_connections_attempted": False,
            "mutations_performed": False,
            "deletions_performed": False,
        },
        "summary": {
            "configuration_names": len(records),
            "missing_template_entries": sum(r["template_status"] == "missing_template_entry" for r in records),
            "tracked_environment_files_for_review": len(tracked_env_files),
            "unreadable_files": len(unreadable),
        },
        "configuration": records,
        "tracked_environment_files_for_review": sorted(tracked_env_files),
        "unreadable_files": sorted(unreadable),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=Path("evidence/config-readiness.json"))
    args = parser.parse_args()
    report = scan(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
