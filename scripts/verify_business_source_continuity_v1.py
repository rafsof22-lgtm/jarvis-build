from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> None:
    policy = load("registry/governance/request-intake-and-progress-policy-v1.json")
    denominator = load("registry/source-accounting/jarvis-project-source-denominator-v1.json")
    module = load("registry/business/business-module-v1.json")
    jenok = load("registry/business/jenok-business-framework-v1.json")
    cost = load("registry/business/cost-plus-one-auto-parts-framework-v1.json")
    sof = load("registry/property-sof/sof-property-scout-email-capture-framework-v1.json")
    ledger = load("registry/requests/jarvis-user-request-ledger-20260721.json")

    assert denominator["coverage_conclusion"] == "NO_100_PERCENT_HISTORICAL_COMPLETENESS_CLAIM"
    assert {x["business_id"] for x in module["businesses"]} == {"BUSINESS-JENOK", "BUSINESS-COST-PLUS-ONE-AUTO-PARTS"}
    assert all(x["separation_required"] for x in module["businesses"])
    assert "+ 1_AUD" in cost["canonical_price_formula"]
    assert any("Fail closed" in x for x in cost["pricing_controls"])
    assert any("robots.txt" in x for x in jenok["governance"])
    assert any("Do not bypass" in x for x in jenok["governance"])
    assert sof["pattern_engine_policy"].startswith("DISABLED_QUARANTINED")
    assert any("Generate or infer personal email" in x for x in sof["prohibited_default_actions"])
    assert any("Purchase verification credits" in x for x in sof["prohibited_default_actions"])
    assert any("Send outreach" in x for x in sof["prohibited_default_actions"])
    assert sof["source"]["sha256"] == "47707733c77345237a19349132ba73ea0be3ab8c320ffc0473159e220839bb74"
    assert len(ledger["requirements"]) >= 8
    assert "TRACKER_AND_CONTINUITY_UPDATE" in policy["intake_sequence"]

    source_path = Path("/mnt/data/Pasted markdown(2).md")
    local_hash_status = "not_mounted_in_ci"
    if source_path.exists():
        digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
        assert digest == sof["source"]["sha256"]
        local_hash_status = "verified"

    evidence = {
        "verification_id": "BUSINESS-SOURCE-CONTINUITY-V1-VERIFY",
        "status": "DONE_VERIFIED_REPOSITORY_SCOPE",
        "local_uploaded_file_hash_status": local_hash_status,
        "historical_completeness_claimed": False,
        "businesses_distinct": True,
        "cost_plus_one_formula_present": True,
        "jenok_public_boundary_present": True,
        "unsafe_email_generation_quarantined": True,
        "owner_approval_gates_present": True,
    }
    out = ROOT / "evidence" / "business-source-continuity-v1-verification.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
