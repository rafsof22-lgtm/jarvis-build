import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = {
    "standard": ROOT / "registry/universal_module_execution_standard_v1.json",
    "knowledge": ROOT / "registry/jarvis_knowledge_fabric_decision_v1.json",
    "ojt": ROOT / "registry/ojt_sop_coverage_v1.json",
    "health": ROOT / "registry/health_spooky2_framework_v2.json",
}


def load(name):
    path = FILES[name]
    assert path.exists(), f"missing {path}"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main():
    standard = load("standard")
    knowledge = load("knowledge")
    ojt = load("ojt")
    health = load("health")

    required_spine = {
        "REQUEST_LOCK",
        "SOURCE_DENOMINATOR",
        "CURRENT_SOURCE_CHECK",
        "INDEPENDENT_REVIEW",
        "TEST_OR_WAIVER",
        "EVIDENCE_CAPTURE",
        "ROLLBACK",
    }
    assert required_spine.issubset(set(standard["mandatory_execution_spine"]))
    assert "SOPs" in standard["required_module_contract"]
    assert "OJT" in standard["required_module_contract"]
    assert standard["universal_quality_gates"]["no_false_completion"] is True
    assert standard["domain_overlays"]["financial"][0] == "research_only_default"
    assert "live_control_disabled_by_default" in standard["domain_overlays"]["device_control"]

    assert knowledge["decision_status"] == "SELECTED_SPEC"
    assert knowledge["selected_stack"]["canonical_production_store"].startswith("PostgreSQL")
    assert knowledge["llamaindex_assessment"]["role"] == "optional adapter and accelerator"
    assert "migration_rule" in knowledge
    assert "citation_precision" in knowledge["evaluation_gates"]

    assert ojt["execution_gate"].startswith("A task requiring an SOP")
    assert "P0_CRITICAL" in {row["priority"] for row in ojt["module_coverage"]}
    assert "rollback" in ojt["sop_contract"]
    assert "pass_threshold" in ojt["ojt_contract"]

    assert health["default_boundary"]["live_device_control"] == "DISABLED"
    assert health["default_boundary"]["diagnosis"] == "PROHIBITED"
    assert health["mode_rules"]["cross_mode_copy"] == "PROHIBITED_WITHOUT_COMPATIBILITY_VERIFICATION"
    assert health["current_runtime"]["clinical_tools"] == "NOT_IMPLEMENTED"
    assert "health_request_triage" in health["mandatory_SOPs"]
    assert "evidence_grading" in health["mandatory_OJT"]

    print("Universal module execution, knowledge fabric, OJT/SOP and Health/Spooky2 specifications verified")


if __name__ == "__main__":
    main()
