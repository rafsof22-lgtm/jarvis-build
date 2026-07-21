from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)

source = load("registry/sources/health_spooky2_psychology_full_reconstruction_v14.json")
aliases = load("registry/sources/upload_alias_dedupe_v14.json")
requirements = load("registry/requirements/health_spooky2_psychology_requirements_v14.json")
safety = load("registry/health/health_evidence_and_safety_controls_v2.json")
gaps = load("registry/health/health_spooky2_psychology_gap_decision_register_v14.json")
tracker = load("registry/trackers/all_progress_tracker_reconciliation_v14.json")

require(source["state"] == "FULL_MACHINE_RECONSTRUCTION_VERIFIED_PRIVACY_SAFE", "wrong source state")
latest = source["latest_unique_project_denominator"]
require(latest["unique_conversations"] == 156, "unique conversation denominator drift")
require(latest["canonical_messages"] == 27153, "canonical message denominator drift")
require(sum(p["conversations"] for p in latest["projects"]) == 156, "project conversation total mismatch")
require(sum(p["canonical_messages"] for p in latest["projects"]) == 27153, "project message total mismatch")
require(source["denominator_conflict"]["prior_v12_envelopes"] == 157, "prior conflict not preserved")
require(source["older_handover_comparison"]["latest_target_conversations_missing_from_older_handover"] == 79, "older handover delta drift")
require(source["message_semantic_pass"]["all_canonical_messages_machine_read"] is True, "message pass not proven")
require(source["bundled_source_file_pass"]["files"] == 52, "source-file count drift")
require(source["bundled_source_file_pass"]["xlsx"]["workbooks"] == 7, "xlsx count drift")
require(source["bundled_source_file_pass"]["pdf"]["files"] == 4, "pdf count drift")
require(sum(row["count"] for row in source["bundled_source_file_pass"]["images"]) == 4, "image classification count drift")
require(source["privacy_boundary"], "privacy boundary missing")
require("clinically validate" in source["truth_boundary"], "truth boundary weakened")

require(aliases["new_source_bytes"] == 0, "duplicate aliases incorrectly counted as new bytes")
require(len(aliases["aliases"]) == 5, "current upload alias count drift")
require(all(row["canonical_relationship"] == "EXACT_DUPLICATE_ALIAS" for row in aliases["aliases"]), "non-exact alias present")

require(requirements["requirement_count"] == 32, "requirement count drift")
require(len({r["requirement_id"] for r in requirements["requirements"]}) == 32, "duplicate requirement IDs")
required_ids = {f"HLTH-REQ-{n:03d}" for n in range(1, 33)}
require({r["requirement_id"] for r in requirements["requirements"]} == required_ids, "requirement ID gap")
require(safety["runtime"]["claim_text_persisted"] is False, "raw claim persistence enabled")
require(safety["runtime"]["medical_device_control"] is False, "device control enabled")
require(safety["runtime"]["diagnosis_or_treatment_execution"] is False, "clinical execution enabled")
require(safety["test_evidence"]["deterministic_tests"] == 19, "test count drift")
require(len(gaps["gaps"]) >= 8, "gap register incomplete")
require(tracker["program_state"] == "ACTIVE_PROGRAM_NOT_100_PERCENT", "false whole-program completion")
require(tracker["baseline_main"] == "1284593de79e1a264d8cb6d3c2ab64cadd64450e", "baseline main drift")
require(tracker["health_current_states"]["device_control"] == "BLOCKED", "tracker device control not blocked")
require(tracker["health_current_states"]["production"] == "NOT_AUTHORISED", "tracker production truth weakened")

module_path = ROOT / "src/jarvis_health/evidence_gate_v1.py"
source_text = module_path.read_text(encoding="utf-8")
ast.parse(source_text)
for token in ["GUARANTEED_CURE_OR_INEVITABILITY","PRESCRIPTION_OR_MEDICATION_CHANGE","PSYCHEDELIC_OR_CONTROLLED_DOSING","INVASIVE_OR_EXPERIMENTAL_INTERVENTION","MEDICAL_DEVICE_SETTINGS","FREQUENCY_AS_CURE_OR_DRUG_SIMULATION","PrivacySafeHealthLedger"]:
    require(token in source_text, f"missing runtime control: {token}")
require("claim_text TEXT" not in source_text, "raw claim text database column detected")
require("execution_allowed=False" in source_text, "execution allow boundary missing")
require("medical_device_control_allowed=False" in source_text, "device control boundary missing")

secret_assignment = re.compile(r"(?i)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|private[_-]?key|password|seed[_-]?phrase)\s*[:=]\s*['\"][^'\"]{8,}['\"]")
for path in ROOT.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in {".py", ".json", ".md", ".yml", ".yaml"}:
        continue
    text = path.read_text(encoding="utf-8")
    require(not secret_assignment.search(text), f"secret-like assignment in {path.relative_to(ROOT)}")

print(json.dumps({
    "verification_id":"HEALTH-RECONSTRUCTION-V14-VERIFY",
    "status":"DONE_VERIFIED_BOUNDED",
    "unique_conversations":156,
    "canonical_messages":27153,
    "bundled_sources":52,
    "requirements":32,
    "deterministic_tests":19,
    "device_control":"BLOCKED",
    "production":"NOT_AUTHORISED",
    "truth_boundary":"Bounded source reconstruction and local safety runtime only; no clinical validation or connected deployment."
}, indent=2))
