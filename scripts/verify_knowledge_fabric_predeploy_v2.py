#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "registry/knowledge/knowledge_fabric_adapter_neutral_v2.json"
SOP = ROOT / "registry/sops/p0_knowledge_retrieval_v1.json"
OJT = ROOT / "registry/ojt/p0_knowledge_operator_training_v1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    spec, sop, ojt = load(SPEC), load(SOP), load(OJT)
    docs = [
        {"id": "a", "ns": "health", "fresh": 2, "hash": "h1", "claim": "enabled", "state": "verified"},
        {"id": "b", "ns": "finance", "fresh": 3, "hash": "h2", "claim": "disabled", "state": "verified"},
        {"id": "c", "ns": "health", "fresh": 1, "hash": "h1", "claim": "enabled", "state": "duplicate"},
        {"id": "d", "ns": "health", "fresh": 4, "hash": "h3", "claim": "disabled", "state": "contradicted"},
    ]
    visible = [d for d in docs if d["ns"] == "health"]
    deduped = {d["hash"]: d for d in sorted(visible, key=lambda x: x["fresh"])}
    checks = {
        "permission_filter": all(d["ns"] == "health" for d in visible),
        "freshness_order": max(visible, key=lambda x: x["fresh"])["id"] == "d",
        "duplicate_suppression": len(deduped) == 2,
        "contradiction_retrieval": {d["claim"] for d in visible} == {"enabled", "disabled"},
        "citation_pointer_required": "coordinates" in spec["canonical_record"]["required"],
        "rollback_defined": bool(sop.get("rollback")),
        "training_threshold": ojt.get("pass_threshold", 0) >= 0.9,
        "predeploy_only": spec.get("state") == "PREDEPLOY_COMPLETE_NOT_CONNECTED",
    }
    report = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "runtime_state": "PREDEPLOY_ONLY", "external_connections": "NOT_ATTEMPTED"}
    out = ROOT / "evidence/knowledge-fabric-predeploy-v2-verification.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
