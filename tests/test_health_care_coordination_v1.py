from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from src.jarvis_health.care_coordination_v1 import (
    CareCoordinationStore, ConsentRecord, DeviceRecord, DiagnosticSourceRecord,
    InterventionRecord, ProviderRecord, RegimenItem, synthetic_subject_ref,
)


class CareCoordinationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = CareCoordinationStore(Path(self.temp.name) / "care.sqlite")
        self.subject = synthetic_subject_ref("synthetic-fixture")
        self.store.create_subject(self.subject)

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def consent(self, scope, state="GRANTED"):
        return self.store.set_consent(ConsentRecord(self.subject, scope, state, "evidence:test"))

    def test_01_pseudonymous_subject(self):
        self.assertTrue(self.subject.startswith("subject-"))

    def test_02_reject_wrong_classification(self):
        with self.assertRaises(ValueError):
            self.store.create_subject("x", data_classification="PUBLIC")

    def test_03_unknown_subject_consent(self):
        with self.assertRaises(ValueError):
            self.store.set_consent(ConsentRecord("missing", "x", "GRANTED", "e"))

    def test_04_invalid_consent_state(self):
        with self.assertRaises(ValueError):
            self.store.set_consent(ConsentRecord(self.subject, "x", "YES", "e"))

    def test_05_diagnostic_consent_required(self):
        with self.assertRaises(PermissionError):
            self.store.add_diagnostic_source(DiagnosticSourceRecord(self.subject, "p", "0" * 64, "lab"))

    def test_06_add_diagnostic_hash_only(self):
        self.consent("diagnostic_sources")
        self.assertTrue(self.store.add_diagnostic_source(DiagnosticSourceRecord(self.subject, "p", "a" * 64, "lab")))

    def test_07_invalid_diagnostic_hash(self):
        self.consent("diagnostic_sources")
        with self.assertRaises(ValueError):
            self.store.add_diagnostic_source(DiagnosticSourceRecord(self.subject, "p", "bad", "lab"))

    def test_08_regimen_consent_required(self):
        with self.assertRaises(PermissionError):
            self.store.add_regimen_item(RegimenItem(self.subject, "item", "supplement", "current", "src"))

    def test_09_add_regimen_item(self):
        self.consent("regimen")
        self.assertTrue(self.store.add_regimen_item(RegimenItem(self.subject, "item", "supplement", "current", "src")))

    def test_10_device_defaults_blocked(self):
        self.consent("devices")
        rid = self.store.add_device(DeviceRecord(self.subject, "device", "frequency", "UNVERIFIED"))
        row = self.store.connection.execute("SELECT control_state FROM devices WHERE record_id=?", (rid,)).fetchone()
        self.assertEqual(row[0], "BLOCKED")

    def test_11_supervised_device_requires_evidence(self):
        self.consent("devices")
        with self.assertRaises(ValueError):
            self.store.add_device(DeviceRecord(self.subject, "device", "PBM", "REGISTERED", "SUPERVISED_INFORMATION_ONLY"))

    def test_12_supervised_device_with_evidence(self):
        self.consent("devices")
        self.assertTrue(self.store.add_device(DeviceRecord(self.subject, "device", "PBM", "REGISTERED", "SUPERVISED_INFORMATION_ONLY", "manual", "competency")))

    def test_13_provider_freshness_positive(self):
        with self.assertRaises(ValueError):
            self.store.add_provider(ProviderRecord("provider", "clinic", "AU", "official", freshness_days=0))

    def test_14_provider_record(self):
        self.assertEqual(self.store.add_provider(ProviderRecord("provider", "clinic", "AU", "official")), "provider")

    def test_15_intervention_consent_required(self):
        with self.assertRaises(PermissionError):
            self.store.add_intervention(InterventionRecord(self.subject, "i", "A", "CLINICIAN_REVIEWED", "src"))

    def test_16_unreviewed_intervention_cannot_advance(self):
        self.consent("interventions")
        with self.assertRaises(ValueError):
            self.store.add_intervention(InterventionRecord(self.subject, "i", "A", "NOT_REVIEWED", "src", "STARTED"))

    def test_17_intervention_record(self):
        self.consent("interventions")
        self.assertTrue(self.store.add_intervention(InterventionRecord(self.subject, "i", "B", "CLINICIAN_REVIEWED", "src")))

    def test_18_queue_hash_only(self):
        digest = hashlib.sha256(b"claim").hexdigest()
        item = self.store.enqueue_claim(claim_sha256=digest, source_pointer="source:1", risk_classes=["MEDICAL_DEVICE_SETTINGS"], priority="HIGH")
        self.assertEqual(item.claim_sha256, digest)

    def test_19_queue_rejects_raw_text(self):
        with self.assertRaises(ValueError):
            self.store.enqueue_claim(claim_sha256="claim text", source_pointer="x", risk_classes=["R"], priority="HIGH")

    def test_20_queue_dedupes(self):
        digest = "b" * 64
        first = self.store.enqueue_claim(claim_sha256=digest, source_pointer="p", risk_classes=["R"], priority="HIGH")
        second = self.store.enqueue_claim(claim_sha256=digest, source_pointer="p", risk_classes=["R"], priority="HIGH")
        self.assertEqual(first.queue_id, second.queue_id)
        self.assertEqual(self.store.connection.execute("SELECT COUNT(*) FROM claim_review_queue").fetchone()[0], 1)

    def test_21_review_packet_has_no_values(self):
        packet = self.store.build_review_packet(self.subject)
        self.assertFalse(packet["contains_raw_medical_values"])
        self.assertTrue(packet["professional_decision_required"])

    def test_22_schema_has_no_direct_pii_or_raw_claim_columns(self):
        prohibited = {"name", "email", "phone", "address", "dob", "medicare", "claim_text", "raw_text"}
        for table in ["subjects", "diagnostic_sources", "regimen_items", "devices", "interventions", "claim_review_queue"]:
            columns = {row[1] for row in self.store.connection.execute(f"PRAGMA table_info({table})")}
            self.assertFalse(columns & prohibited)

    def test_23_withdrawn_consent_denies(self):
        self.consent("regimen", "WITHDRAWN")
        self.assertFalse(self.store.has_consent(self.subject, "regimen"))


if __name__ == "__main__":
    unittest.main()
