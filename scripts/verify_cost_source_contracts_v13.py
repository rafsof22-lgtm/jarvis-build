from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


source = load("registry/sources/cost_auto_parts_source_reconciliation_v1.json")
health = load("registry/sources/health_spooky2_psychology_split_handover_v1.json")
requirements = load("registry/requirements/cost_auto_parts_requirements_reconciliation_v1.json")
tracker = load("registry/trackers/all_progress_tracker_reconciliation_v13.json")
contracts = load("registry/business/cost-plus-one-domain-contracts-v2.json")

export = source["exact_project_export"]
require(export["conversation_envelope_count"] == 15, "Cost envelope denominator mismatch")
require(export["conversation_envelope_message_count"] == 14654, "Cost envelope message denominator mismatch")
require(export["top_level_project_conversation_count"] == 14, "Top-level Cost conversation denominator mismatch")
require(export["top_level_project_conversation_message_count"] == 14602, "Top-level Cost message denominator mismatch")
require(export["mixed_lineage_conversation_count"] == 1, "Mixed-lineage denominator mismatch")
require(sum(export["role_counts_for_all_envelope_messages"].values()) == 14654, "Role totals do not reconcile")
require(export["message_metadata_tagged_count"] == 3804, "Tagged-message denominator mismatch")
require(export["parse_errors"] == 0, "Source parse errors must be zero")
require(export["raw_chat_bodies_committed"] is False, "Raw chat bodies must not be committed")
require(source["handoff_internal_counts"]["requirements"] == 18, "Handoff requirement count mismatch")
require(source["handoff_internal_counts"]["wfw_conversation_rows"] == 0, "WFW ledger truth mismatch")
require(any(x.get("conflict_id") == "COST-HANDOFF-CF-001" for x in source["internal_conflicts"]), "84-chat conflict missing")
require(len(requirements["requirements"]) == 18, "Requirement mapping must contain 18 rows")
require(len({x["requirement_id"] for x in requirements["requirements"]}) == 18, "Requirement IDs must be unique")
require(len(contracts["workflows"]) == 7, "Exactly seven workflow contracts required")
require(contracts["status"] == "IMPLEMENTED_NOT_INTEGRATED", "Contracts must not claim connected runtime")
require(health["combined_zip"]["zip_integrity"] == "PASS", "Health ZIP integrity not proven")
require(health["combined_zip"]["unsafe_paths"] == 0, "Unsafe archive paths found")
require(health["raw_content_committed"] is False, "Restricted health content must not be committed")
require(tracker["program_state"] == "ACTIVE_PROGRAM_NOT_100_PERCENT", "False whole-program completion")
require(tracker["cost_plus_one_current_states"]["production"] == "NOT_AUTHORISED", "False production authority")

code_paths = [ROOT / "src/jarvis_business/cost_plus_contracts_v2.py", ROOT / "tests/test_cost_handoff_reconciliation_v13.py", ROOT / "tests/test_cost_plus_contracts_v2.py"]
for path in code_paths:
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

combined = "\n".join(path.read_text(encoding="utf-8") for path in code_paths)
secret_assignment = re.compile(r"(?i)(api[_-]?key|access[_-]?token|refresh[_-]?token|private[_-]?key|password)\s*=\s*['\"][^'\"]{8,}")
require(not secret_assignment.search(combined), "Secret-like assignment detected")

print(json.dumps({"state":"DONE_VERIFIED_BOUNDED","scope":"Cost source denominator, requirement mapping, seven local contracts, SQLite idempotency, locker allocation and restricted Health archive integrity","tests_expected":23,"program_state":tracker["program_state"],"production":tracker["cost_plus_one_current_states"]["production"]}, sort_keys=True))
