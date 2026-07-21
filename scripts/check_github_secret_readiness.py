#!/usr/bin/env python3
"""Create a redacted GitHub Actions secret-readiness report.

The script checks presence only. It never prints, hashes, stores, compares, or uploads
secret values. Missing secrets are reported by name and task ID so the owner can add
them through GitHub Actions Secrets or an approved provider vault.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registry/platform/github_actions_secret_manifest_v1.json"
OUTPUT = ROOT / "evidence/github-actions-secret-readiness-v1.json"


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    groups = []
    total = 0
    present = 0

    for group in manifest["secret_groups"]:
        checks = []
        for item in group["secrets"]:
            name = item["name"]
            is_present = bool(os.getenv(name))
            total += 1
            present += int(is_present)
            checks.append(
                {
                    "name": name,
                    "present": is_present,
                    "required": item.get("required", True),
                    "purpose": item["purpose"],
                    "add_at": item["add_at"],
                    "value_exposed": False,
                }
            )
        required_missing = [c["name"] for c in checks if c["required"] and not c["present"]]
        groups.append(
            {
                "group_id": group["group_id"],
                "task_ids": group["task_ids"],
                "state": "READY" if not required_missing else "MISSING_REQUIRED_SECRETS",
                "required_missing": required_missing,
                "checks": checks,
            }
        )

    report = {
        "id": "EVIDENCE-GITHUB-ACTIONS-SECRET-READINESS-V1",
        "status": "READY" if all(g["state"] == "READY" for g in groups) else "ACTION_REQUIRED",
        "summary": {"total_secret_names": total, "present": present, "missing": total - present},
        "groups": groups,
        "security": {
            "values_read_only_for_presence": True,
            "values_printed": False,
            "values_hashed": False,
            "values_written": False,
            "values_uploaded": False,
        },
        "next_action": "Add each missing name in repository Settings -> Secrets and variables -> Actions, or in the named provider vault. Never paste values into issues, commits, logs or chat.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
