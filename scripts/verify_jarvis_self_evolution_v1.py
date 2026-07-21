from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    registry = json.loads((ROOT / "registry/jarvis_self_evolution_control_plane_v1.json").read_text(encoding="utf-8"))
    sources = json.loads((ROOT / "registry/source-coverage/jarvis_source_universe_status_v3_20260721.json").read_text(encoding="utf-8"))
    skill = (ROOT / "skills/jarvis-sovereign-builder/SKILL.md").read_text(encoding="utf-8")
    reference = (ROOT / "skills/jarvis-sovereign-builder/references/self-evolution-and-unified-assistant.md").read_text(encoding="utf-8")
    runtime = (ROOT / "src/jarvis_evolution/control_plane_v1.py").read_text(encoding="utf-8")

    required_types = {
        "framework", "spec", "workflow", "stack", "architecture", "orchestrator", "skill", "agent",
        "prompt", "instruction", "policy", "schema", "model_route", "tool", "integration", "connector",
        "ui", "test", "deployment_profile", "memory_policy", "source", "module", "service", "sop", "ojt",
    }
    require(required_types <= set(registry["editable_object_types"]), "editable object classes incomplete")
    required_panels = {"chat", "voice_transcript", "llm_selector", "object_browser", "diff_preview", "approval_queue", "activity_timeline", "rollback_history"}
    require(required_panels <= set(registry["unified_assistant"]["required_panels"]), "assistant panels incomplete")
    require(registry["unified_assistant"]["voice_and_text_same_policy"] is True, "voice/text policy parity missing")
    require(registry["unified_assistant"]["voice_is_authorization"] is False, "voice cannot be authorization")
    require(registry["acceptance"]["direct_production_self_modification"] is False, "production self-modification must remain false")
    require(sources["universal_100_percent_allowed"] is False, "source register must reject false universal completion")
    states = {item["state"] for item in sources["known_sources"]}
    require("PENDING_INGEST" in states and "BLOCKED_BY_ACCESS" in states, "missing sources not represented")
    require("references/self-evolution-and-unified-assistant.md" in skill, "Skill entrypoint missing reference")
    require("Observe -> Detect" in reference, "governed self-evolution loop missing")
    require("direct high-risk or production self-modification is prohibited" in runtime, "runtime production prohibition missing")
    require("manual_override" in runtime and "rollback" in runtime, "manual override or rollback missing")

    print(json.dumps({
        "status": "passed",
        "editable_object_types": len(registry["editable_object_types"]),
        "assistant_panels": len(registry["unified_assistant"]["required_panels"]),
        "known_sources": len(sources["known_sources"]),
        "universal_100_percent_allowed": sources["universal_100_percent_allowed"],
        "truth_boundary": registry["truth_boundary"],
    }, indent=2))


if __name__ == "__main__":
    main()
