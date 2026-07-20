from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "xrp-hbar-vti-semantic-payload-v1.json"
FIXTURES = ROOT / "tests" / "fixtures" / "xrp-hbar-vti-semantic-payload-v1.json"

BASE_REQUIRED = {"payload_schema", "payload_version", "record_type", "verification_state"}
ASSET_REQUIRED = {"asset", "network", "finding", "direct_token_demand", "token_use_mandatory", "bypass_paths", "contrary_evidence"}
CFO_REQUIRED = {"approved_finding_ids", "execution_allowed"}


def validate(payload: dict) -> None:
    missing = BASE_REQUIRED - payload.keys()
    if missing:
        raise AssertionError(f"missing base fields: {sorted(missing)}")
    if payload["payload_schema"] != "jarvis.xrp-hbar-vti.semantic":
        raise AssertionError("invalid payload_schema")
    if payload["payload_version"] != "1.0.0":
        raise AssertionError("invalid payload_version")
    if payload.get("execution_allowed") is not False:
        raise AssertionError("financial execution must remain disabled")
    record_type = payload["record_type"]
    if record_type == "asset_finding":
        missing = ASSET_REQUIRED - payload.keys()
        if missing:
            raise AssertionError(f"asset finding missing demand-path fields: {sorted(missing)}")
        if payload["direct_token_demand"] in {"proven", "supported"} and not payload["evidence_refs"]:
            raise AssertionError("positive direct demand requires evidence_refs")
        if not isinstance(payload["bypass_paths"], list) or not isinstance(payload["contrary_evidence"], list):
            raise AssertionError("demand pathway arrays required")
    elif record_type == "cfo_handoff":
        missing = CFO_REQUIRED - payload.keys()
        if missing:
            raise AssertionError(f"CFO handoff missing fields: {sorted(missing)}")
        if not payload["approved_finding_ids"]:
            raise AssertionError("CFO handoff requires approved findings")
    elif record_type == "vti_evidence":
        if payload["verification_state"] == "verified" and not payload.get("evidence_refs"):
            raise AssertionError("verified VTI evidence requires evidence_refs")
    else:
        raise AssertionError(f"unsupported record_type: {record_type}")


def main() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["$id"].endswith("xrp-hbar-vti-semantic-payload-v1.json")
    doc = json.loads(FIXTURES.read_text(encoding="utf-8"))
    for payload in doc["fixtures"]:
        validate(payload)
    for payload in doc["invalid_fixtures"]:
        try:
            validate(payload)
        except AssertionError:
            continue
        raise AssertionError(f"invalid fixture unexpectedly passed: {payload.get('name')}")
    print(f"validated {len(doc['fixtures'])} positive and {len(doc['invalid_fixtures'])} negative semantic fixtures")


if __name__ == "__main__":
    main()
