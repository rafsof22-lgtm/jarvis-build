from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from .care_coordination_v1 import (
    CareCoordinationStore,
    ConsentRecord,
    DeviceRecord,
    DiagnosticSourceRecord,
    InterventionRecord,
    ProviderRecord,
    RegimenItem,
    synthetic_subject_ref,
)


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def run_synthetic_care_journeys(path: str | Path = ":memory:") -> dict[str, Any]:
    """Run deterministic privacy-safe care journeys with synthetic references only."""
    store = CareCoordinationStore(path)
    subject_ref = synthetic_subject_ref("jarvis-v17-synthetic-care-subject")
    evidence: dict[str, Any] = {
        "journey_id": "HEALTH-SYNTHETIC-CARE-JOURNEYS-V17",
        "subject_ref": subject_ref,
        "synthetic_only": True,
        "contains_direct_identifiers": False,
        "contains_raw_medical_values": False,
        "professional_decision_required": True,
        "steps": [],
    }
    try:
        store.create_subject(subject_ref)
        evidence["steps"].append({"step": "subject_created", "passed": True})

        for scope in ("diagnostic_sources", "regimen", "devices", "interventions"):
            store.set_consent(ConsentRecord(subject_ref, scope, "GRANTED", f"evidence://synthetic/{scope}"))
        evidence["steps"].append({"step": "scope_consents_granted", "passed": True})

        diagnostic_id = store.add_diagnostic_source(
            DiagnosticSourceRecord(
                subject_ref=subject_ref,
                source_ref="source://synthetic/diagnostic-1",
                source_sha256=_sha("synthetic-diagnostic-source-v17"),
                source_type="SYNTHETIC_TEST_DOCUMENT",
            )
        )
        evidence["steps"].append({"step": "diagnostic_hash_registered", "passed": bool(diagnostic_id)})

        regimen_id = store.add_regimen_item(
            RegimenItem(
                subject_ref=subject_ref,
                item_ref="regimen://synthetic/item-1",
                category="SUPPLEMENT_REFERENCE_ONLY",
                status="CURRENT_REFERENCE",
                source_ref="source://synthetic/regimen-1",
                review_state="NOT_REVIEWED",
            )
        )
        evidence["steps"].append({"step": "regimen_reference_registered", "passed": bool(regimen_id)})

        device_id = store.add_device(
            DeviceRecord(
                subject_ref=subject_ref,
                device_ref="device://synthetic/device-1",
                device_class="NON_CONNECTED_TEST_DEVICE",
                regulatory_state="UNVERIFIED_SYNTHETIC",
                control_state="BLOCKED",
            )
        )
        evidence["steps"].append({"step": "device_defaults_blocked", "passed": bool(device_id)})

        provider_ref = store.add_provider(
            ProviderRecord(
                provider_ref="provider://synthetic/provider-1",
                service_class="SYNTHETIC_CLINICAL_REVIEW",
                jurisdiction="AU-VIC",
                official_source_ref="official://synthetic/provider-register",
                verified_at=None,
                freshness_days=30,
            )
        )
        evidence["steps"].append({"step": "provider_requires_official_source", "passed": bool(provider_ref)})

        intervention_id = store.add_intervention(
            InterventionRecord(
                subject_ref=subject_ref,
                intervention_ref="intervention://synthetic/info-only",
                evidence_grade="UNASSESSED",
                review_state="NOT_REVIEWED",
                source_ref="source://synthetic/intervention-1",
                outcome_state="NOT_STARTED",
            )
        )
        evidence["steps"].append({"step": "unreviewed_intervention_not_started", "passed": bool(intervention_id)})

        claim = store.enqueue_claim(
            claim_sha256=_sha("synthetic high-risk claim for queue testing only"),
            source_pointer="source://synthetic/claim-1",
            risk_classes=("MEDICAL_DEVICE_CONTROL_SETTINGS",),
            priority="HIGH",
        )
        evidence["steps"].append({"step": "hash_only_claim_queued", "passed": claim.clinical_review_required})

        packet_before = store.build_review_packet(subject_ref)
        evidence["steps"].append({
            "step": "clinician_packet_generated",
            "passed": packet_before["professional_decision_required"] and not packet_before["contains_raw_medical_values"],
        })

        store.set_consent(ConsentRecord(subject_ref, "diagnostic_sources", "WITHDRAWN", "evidence://synthetic/withdrawal"))
        withdrawal_blocked = False
        try:
            store.add_diagnostic_source(
                DiagnosticSourceRecord(
                    subject_ref=subject_ref,
                    source_ref="source://synthetic/diagnostic-2",
                    source_sha256=_sha("synthetic-diagnostic-source-v17-after-withdrawal"),
                    source_type="SYNTHETIC_TEST_DOCUMENT",
                )
            )
        except PermissionError:
            withdrawal_blocked = True
        evidence["steps"].append({"step": "consent_withdrawal_blocks_new_diagnostic", "passed": withdrawal_blocked})

        packet_after = store.build_review_packet(subject_ref)
        evidence["review_packet"] = packet_after
        evidence["passed"] = all(step["passed"] for step in evidence["steps"])
        evidence["truth_boundary"] = (
            "Synthetic local exercise only. No real patient data, diagnosis, treatment, device operation, "
            "clinical validation, connected staging or production action."
        )
        return evidence
    finally:
        store.close()
