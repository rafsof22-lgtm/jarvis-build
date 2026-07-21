from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> None:
    model = load("registry/model-routing/universal_model_selector_parallel_panel_v1.json")
    sources = load("registry/source-accounting/chathub-source-universe-20260721-v3.json")
    applicability = load("registry/requirements/chathub-applicability-20260721-v3.json")
    health = load("registry/health/chathub-health-safety-quarantine-v1.json")
    apollo = load("registry/integrations/chathub-apollo-source-delta-v1.json")
    skill = (ROOT / "skills/jarvis-sovereign-builder/SKILL.md").read_text(encoding="utf-8")
    reference = (ROOT / "skills/jarvis-sovereign-builder/references/universal-model-selector-and-chathub-intake.md").read_text(encoding="utf-8")

    assert model["parallel_panel"]["maximum_models"] == 8
    assert model["parallel_panel"]["response_proof_key"] == "selector_id + sha256"
    assert model["parallel_panel"]["universal_zero_error_or_zero_gap_claim"] is False
    assert len(model["shared_surfaces"]) >= 13
    assert sources["source_count"] == 3
    assert sources["totals"] == {"bytes": 2055754, "lines": 43776, "messages": 143, "responses": 71, "user_prompts": 72, "words": 268012}
    assert sources["all_files_hashed"] and sources["all_messages_accounted"]
    assert sum(item["messages"] for item in sources["files"]) == 143
    assert applicability["quarantine"]["unique_messages"] == 29
    assert {route["module"] for route in applicability["routes"]} >= {"model_router", "jarvis_control_plane", "health", "apollo_property"}
    assert health["execution_policy"]["activate_as_protocol"] is False
    assert apollo["status"] == "IMPLEMENTED_NOT_INTEGRATED"
    assert "redacted exact saved-search request body or authorised API payload" in apollo["remaining_exact_blockers"]
    assert "Universal model selectors, Parallel Thinking, and ChatHub intake" in skill
    assert "selector_id + response_sha256" in reference
    print(json.dumps({
        "status": "DONE_VERIFIED_LOCAL_CONTRACTS_AND_THREE_FILE_SOURCE_DENOMINATOR",
        "tests_expected": 16,
        "source_files": 3,
        "messages_accounted": 143,
        "quarantined_claims": 29,
        "parallel_model_maximum": 8,
        "universal_completion_claim": False,
    }, indent=2))


if __name__ == "__main__":
    main()
