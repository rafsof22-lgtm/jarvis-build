from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "xrp-hbar-federation-contract-v1.json"
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "xrp-hbar-federation-events.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture_doc = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    required = set(schema["required"])
    properties = schema["properties"]
    allowed_event_types = set(properties["event_type"]["enum"])
    allowed_services = set(properties["producer"]["enum"])
    allowed_approval_states = set(properties["approval_state"]["enum"])
    allowed_statuses = set(properties["status"]["enum"])

    fixtures = fixture_doc.get("fixtures", [])
    require(fixtures, "At least one federation fixture is required")

    seen_event_ids: set[str] = set()
    seen_idempotency_keys: set[str] = set()

    for index, event in enumerate(fixtures):
        missing = required - set(event)
        require(not missing, f"Fixture {index} missing required fields: {sorted(missing)}")
        require(event["schema_version"] == "1.0.0", f"Fixture {index} has wrong schema version")
        require(event["event_type"] in allowed_event_types, f"Fixture {index} has invalid event type")
        require(event["producer"] in allowed_services, f"Fixture {index} has invalid producer")
        require(event["consumer"] in allowed_services, f"Fixture {index} has invalid consumer")
        require(event["approval_state"] in allowed_approval_states, f"Fixture {index} has invalid approval state")
        require(event["status"] in allowed_statuses, f"Fixture {index} has invalid status")
        require(isinstance(event["payload"], dict), f"Fixture {index} payload must be an object")
        require(isinstance(event.get("source_refs", []), list), f"Fixture {index} source_refs must be an array")
        require(isinstance(event.get("evidence_refs", []), list), f"Fixture {index} evidence_refs must be an array")
        require(event.get("retry_count", 0) >= 0, f"Fixture {index} retry_count must be non-negative")
        require(event["event_id"] not in seen_event_ids, f"Duplicate event_id: {event['event_id']}")
        require(event["idempotency_key"] not in seen_idempotency_keys, f"Duplicate idempotency_key: {event['idempotency_key']}")
        seen_event_ids.add(event["event_id"])
        seen_idempotency_keys.add(event["idempotency_key"])

        serialized = json.dumps(event).lower()
        forbidden = ("api_key", "secret", "private_key", "refresh_token", "password")
        require(not any(token in serialized for token in forbidden), f"Fixture {index} contains a secret-like field")

    producers = {event["producer"] for event in fixtures}
    require("xrp-hbar-hub-runtime" in producers, "Hub producer fixture is required")
    require("vti-evidence-service" in producers, "VTI producer fixture is required")
    require("jarvis-control-plane" in producers, "Jarvis producer fixture is required")

    print(f"Validated {len(fixtures)} XRP/HBAR federation fixtures")


if __name__ == "__main__":
    main()
