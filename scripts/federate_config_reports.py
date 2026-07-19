#!/usr/bin/env python3
"""Merge redacted configuration-readiness reports into one Jarvis evidence pack.

Input reports must already be redacted. This script never reads or emits secret
values, never contacts providers, and never mutates external systems.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path


def load_reports(folder: Path) -> list[dict]:
    reports: list[dict] = []
    for path in sorted(folder.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        safety = payload.get("safety", {})
        if safety.get("values_emitted") is not False:
            raise ValueError(f"unsafe report rejected: {path}")
        payload["report_file"] = path.name
        reports.append(payload)
    return reports


def merge(reports: list[dict]) -> dict:
    by_name: dict[str, dict] = {}
    repo_summaries = []
    tracked_files = []
    for report in reports:
        repo_id = report.get("repository_id") or Path(report.get("scope", "unknown")).name
        repo_summaries.append({"repository_id": repo_id, **report.get("summary", {})})
        for item in report.get("configuration", []):
            name = item["name"]
            row = by_name.setdefault(name, {
                "name": name,
                "class": item.get("class", "configuration"),
                "repositories": set(),
                "referenced_in": defaultdict(set),
                "declared_in_template": defaultdict(set),
                "template_status": "declared",
                "value_status": "not_inspected",
            })
            row["repositories"].add(repo_id)
            row["referenced_in"][repo_id].update(item.get("referenced_in", []))
            row["declared_in_template"][repo_id].update(item.get("declared_in_template", []))
            if item.get("template_status") != "declared":
                row["template_status"] = "missing_in_one_or_more_repositories"
        for path in report.get("tracked_environment_files_for_review", []):
            tracked_files.append({"repository_id": repo_id, "path": path, "action": "manual_security_review"})

    configuration = []
    for row in sorted(by_name.values(), key=lambda value: value["name"]):
        configuration.append({
            "name": row["name"],
            "class": row["class"],
            "repositories": sorted(row["repositories"]),
            "referenced_in": {k: sorted(v) for k, v in sorted(row["referenced_in"].items())},
            "declared_in_template": {k: sorted(v) for k, v in sorted(row["declared_in_template"].items())},
            "template_status": row["template_status"],
            "value_status": row["value_status"],
            "setup_action": "Open the owning platform settings, add the named value directly, then run the bounded connection test.",
        })

    duplicate_candidates = [
        {"name": item["name"], "repositories": item["repositories"], "decision": "shared_service_review"}
        for item in configuration if len(item["repositories"]) > 1
    ]
    stale_candidates = [
        {"name": item["name"], "reason": "declared_or_discovered_but_not_proven_active", "decision": "do_not_delete_without_proof"}
        for item in configuration if not any(item["referenced_in"].values())
    ]
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "safety": {"values_emitted": False, "external_connections_attempted": False, "automatic_deletions": False},
        "summary": {
            "repositories_scanned": len(reports),
            "configuration_names": len(configuration),
            "duplicate_candidates": len(duplicate_candidates),
            "stale_candidates": len(stale_candidates),
            "tracked_environment_files_for_review": len(tracked_files),
        },
        "repositories": repo_summaries,
        "configuration": configuration,
        "duplicate_candidates": duplicate_candidates,
        "stale_candidates": stale_candidates,
        "tracked_environment_files_for_review": tracked_files,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("evidence/federated-config-readiness.json"))
    args = parser.parse_args()
    report = merge(load_reports(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
