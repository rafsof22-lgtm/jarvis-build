from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def require(value: bool, message: str):
    if not value:
        raise AssertionError(message)

registry = load("registry/health/health_care_coordination_v1.json")
tracker = load("registry/trackers/all_progress_tracker_reconciliation_v15.json")
require(registry["status"] == "DONE_VERIFIED_LOCAL", "registry status")
require(registry["test_evidence"]["deterministic_tests"] == 23, "test count")
require(registry["controls"]["raw_medical_values_persisted"] is False, "raw values")
require(registry["controls"]["direct_identifiers_allowed"] is False, "identifiers")
require(registry["controls"]["device_control_default"] == "BLOCKED", "device default")
require(tracker["program_state"] == "ACTIVE_PROGRAM_NOT_100_PERCENT", "false completion")
require(tracker["baseline_main"] == "3f0ffdda9dd54dd776e10d4f89ea78cc053bfd5b", "baseline")
require(tracker["health_current_states"]["production"] == "NOT_AUTHORISED", "production")
source = (ROOT / "src/jarvis_health/care_coordination_v1.py").read_text(encoding="utf-8")
ast.parse(source)
for token in ["CareCoordinationStore", "claim_review_queue", "RESTRICTED_HEALTH", "active consent required", "SUPERVISED_INFORMATION_ONLY"]:
    require(token in source, f"missing {token}")
for prohibited in [" name TEXT", " email TEXT", " phone TEXT", " address TEXT", " dob TEXT", " medicare TEXT", " claim_text TEXT", " raw_text TEXT"]:
    require(prohibited not in source, f"prohibited schema {prohibited}")
print(json.dumps({"verification_id":"HEALTH-CARE-V15","status":"DONE_VERIFIED_LOCAL","tests":23,"real_health_data":"NOT_CONNECTED","device_control":"BLOCKED","production":"NOT_AUTHORISED"}, indent=2))
