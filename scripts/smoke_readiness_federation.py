#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import tempfile

from federate_config_reports import load_reports, merge

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        sample_a = {
            "repository_id": "alpha",
            "scope": "alpha",
            "safety": {"values_emitted": False},
            "summary": {"configuration_names": 2},
            "configuration": [
                {"name": "SERVICE_URL", "class": "connection_metadata", "referenced_in": ["app.py"], "declared_in_template": [".env.example"], "template_status": "declared"},
                {"name": "SHARED_TOKEN", "class": "sensitive_value", "referenced_in": ["app.py"], "declared_in_template": [], "template_status": "missing_template_entry"},
            ],
            "tracked_environment_files_for_review": [],
        }
        sample_b = {
            "repository_id": "beta",
            "scope": "beta",
            "safety": {"values_emitted": False},
            "summary": {"configuration_names": 1},
            "configuration": [
                {"name": "SHARED_TOKEN", "class": "sensitive_value", "referenced_in": ["worker.py"], "declared_in_template": [".env.example"], "template_status": "declared"},
            ],
            "tracked_environment_files_for_review": [".env"],
        }
        (folder / "alpha.json").write_text(json.dumps(sample_a), encoding="utf-8")
        (folder / "beta.json").write_text(json.dumps(sample_b), encoding="utf-8")
        report = merge(load_reports(folder))
        assert report["safety"]["values_emitted"] is False
        assert report["summary"]["repositories_scanned"] == 2
        assert report["summary"]["duplicate_candidates"] == 1
        assert report["tracked_environment_files_for_review"][0]["path"] == ".env"
        serialized = json.dumps(report)
        assert "example-secret-value" not in serialized

    setup = json.loads((ROOT / "registry" / "setup-actions.json").read_text(encoding="utf-8"))
    assert setup["rules"]["values_never_stored_here"] is True
    assert {item["platform_id"] for item in setup["platforms"]} >= {"github-actions", "vercel", "railway"}
    print("Readiness federation smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
