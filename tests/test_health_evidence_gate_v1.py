from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.jarvis_health.evidence_gate_v1 import (
    HealthClaimInput,
    HealthEvidenceGate,
    PrivacySafeHealthLedger,
    health_output_contract,
)


class HealthEvidenceGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gate = HealthEvidenceGate()

    def assess(self, text: str, **kwargs):
        defaults = dict(domain="test", source_class="ASSISTANT_HISTORICAL_PROPOSAL")
        defaults.update(kwargs)
        return self.gate.assess(HealthClaimInput(claim_text=text, **defaults))

    def test_rejects_empty_claim(self):
        with self.assertRaises(ValueError):
            self.assess(" ")

    def test_rejects_unknown_source_class(self):
        with self.assertRaises(ValueError):
            self.assess("neutral claim", source_class="UNKNOWN")

    def test_rejects_unknown_evidence_grade(self):
        with self.assertRaises(ValueError):
            self.assess("neutral claim", evidence_grade="Z")

    def test_guaranteed_cure_is_quarantined(self):
        out = self.assess("This is a guaranteed cure for all disease.")
        self.assertEqual(out.disposition, "QUARANTINED_UNSUPPORTED_CLAIM")
        self.assertIn("GUARANTEED_CURE_OR_INEVITABILITY", out.risk_classes)
        self.assertFalse(out.execution_allowed)

    def test_frequency_drug_simulation_is_quarantined(self):
        out = self.assess("Use a Spooky2 frequency to simulate ketamine and cure addiction.")
        self.assertEqual(out.disposition, "QUARANTINED_UNSUPPORTED_CLAIM")
        self.assertIn("FREQUENCY_AS_CURE_OR_DRUG_SIMULATION", out.risk_classes)

    def test_medication_change_is_blocked(self):
        out = self.assess("Stop the prescription medication tomorrow.")
        self.assertEqual(out.disposition, "BLOCKED_PENDING_CLINICAL_REVIEW")
        self.assertIn("PRESCRIPTION_OR_MEDICATION_CHANGE", out.risk_classes)

    def test_psychedelic_dosing_is_blocked(self):
        out = self.assess("Ibogaine 12 mg/kg dosing protocol")
        self.assertEqual(out.disposition, "BLOCKED_PENDING_CLINICAL_REVIEW")
        self.assertIn("PSYCHEDELIC_OR_CONTROLLED_DOSING", out.risk_classes)

    def test_invasive_experimental_is_blocked(self):
        out = self.assess("Use CRISPR gene editing and deep brain stimulation.")
        self.assertEqual(out.disposition, "BLOCKED_PENDING_CLINICAL_REVIEW")
        self.assertIn("INVASIVE_OR_EXPERIMENTAL_INTERVENTION", out.risk_classes)

    def test_device_settings_are_blocked(self):
        out = self.assess("Run Spooky2 at 146 Hz for 2 hours.")
        self.assertEqual(out.disposition, "BLOCKED_PENDING_CLINICAL_REVIEW")
        self.assertIn("MEDICAL_DEVICE_SETTINGS", out.risk_classes)
        self.assertFalse(out.medical_device_control_allowed)

    def test_crisis_signal_escalates(self):
        out = self.assess("This may be a medical emergency with chest pain.")
        self.assertEqual(out.disposition, "EMERGENCY_ESCALATION_REQUIRED")

    def test_user_diagnostic_document_requires_clinician(self):
        out = self.assess(
            "A laboratory report contains a result.",
            source_class="USER_PROVIDED_DIAGNOSTIC_DOCUMENT",
            user_specific=True,
            evidence_grade="UNASSESSED",
        )
        self.assertEqual(out.disposition, "INFORMATION_ONLY_CLINICIAN_INTERPRETATION_REQUIRED")

    def test_product_label_requires_pharmacist_or_clinician(self):
        out = self.assess(
            "Supplement label lists lion's mane and PQQ.",
            source_class="USER_PROVIDED_PRODUCT_LABEL",
            evidence_grade="UNASSESSED",
        )
        self.assertEqual(out.disposition, "INFORMATION_ONLY_CLINICIAN_INTERPRETATION_REQUIRED")

    def test_high_grade_guidance_can_enter_informational_synthesis(self):
        out = self.assess(
            "A current official guideline recommends routine monitoring.",
            source_class="OFFICIAL_CLINICAL_GUIDANCE",
            evidence_grade="A",
            evidence_refs=("official:guideline",),
        )
        self.assertEqual(out.disposition, "ELIGIBLE_FOR_INFORMATIONAL_SYNTHESIS")
        self.assertFalse(out.execution_allowed)

    def test_raw_text_is_not_returned(self):
        secret_phrase = "a unique private sentence"
        out = self.assess(secret_phrase)
        payload = json.dumps(out.to_dict())
        self.assertNotIn(secret_phrase, payload)
        self.assertFalse(out.raw_text_persisted)

    def test_pii_metadata_key_is_rejected(self):
        with self.assertRaises(ValueError):
            self.gate.assess(HealthClaimInput(
                claim_text="neutral",
                domain="test",
                source_class="USER_REPORTED_FACT",
                metadata={"patient_id": "x"},
            ))

    def test_ledger_append_and_duplicate_replay(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "health.sqlite"
            ledger = PrivacySafeHealthLedger(db)
            assessment = self.assess("A neutral historical proposal.")
            first = ledger.append(assessment, idempotency_key="same")
            second = ledger.append(assessment, idempotency_key="same")
            self.assertEqual(first["state"], "APPENDED")
            self.assertEqual(second["state"], "DUPLICATE_REPLAY")
            self.assertEqual(ledger.count(), 1)
            ledger.close()

    def test_ledger_rejects_idempotency_collision(self):
        with tempfile.TemporaryDirectory() as td:
            ledger = PrivacySafeHealthLedger(Path(td) / "health.sqlite")
            ledger.append(self.assess("claim one"), idempotency_key="collision")
            with self.assertRaises(ValueError):
                ledger.append(self.assess("claim two"), idempotency_key="collision")
            ledger.close()

    def test_ledger_schema_has_no_raw_text_column(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "health.sqlite"
            ledger = PrivacySafeHealthLedger(db)
            ledger.close()
            con = sqlite3.connect(db)
            cols = [row[1] for row in con.execute("PRAGMA table_info(health_claim_assessments)")]
            con.close()
            self.assertNotIn("claim_text", cols)
            self.assertNotIn("raw_text", cols)

    def test_output_contract_denies_high_risk_outputs(self):
        contract = health_output_contract()
        self.assertFalse(contract["execution_allowed"])
        self.assertEqual(contract["medical_device_control"], "BLOCKED")
        self.assertGreaterEqual(len(contract["denied_outputs"]), 7)


if __name__ == "__main__":
    unittest.main()
