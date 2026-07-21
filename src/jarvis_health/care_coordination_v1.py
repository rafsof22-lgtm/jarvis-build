from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from uuid import NAMESPACE_URL, uuid5

ALLOWED_CONSENT = {"GRANTED", "WITHDRAWN", "EXPIRED", "PENDING"}
ALLOWED_GRADES = {"A", "B", "C", "D", "F", "UNASSESSED"}
ALLOWED_REVIEW = {"NOT_REVIEWED", "CLINICIAN_REVIEWED", "PHARMACIST_REVIEWED", "SPECIALIST_REVIEWED", "REJECTED"}
ALLOWED_DEVICE = {"BLOCKED", "INVENTORIED", "REVIEW_PENDING", "SUPERVISED_INFORMATION_ONLY"}
ALLOWED_PRIORITY = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def stable_id(namespace: str, *parts: object) -> str:
    material = "|".join(str(part).strip().lower() for part in parts)
    return str(uuid5(NAMESPACE_URL, f"jarvis:{namespace}:{material}"))


def required(value: Any, label: str) -> str:
    result = str(value or "").strip()
    if not result:
        raise ValueError(f"{label} is required")
    return result


@dataclass(frozen=True)
class ConsentRecord:
    subject_ref: str
    scope: str
    state: str
    evidence_ref: str
    expires_at: str | None = None


@dataclass(frozen=True)
class DiagnosticSourceRecord:
    subject_ref: str
    source_ref: str
    source_sha256: str
    source_type: str
    review_state: str = "NOT_REVIEWED"


@dataclass(frozen=True)
class RegimenItem:
    subject_ref: str
    item_ref: str
    category: str
    status: str
    source_ref: str
    review_state: str = "NOT_REVIEWED"
    interaction_review_ref: str | None = None


@dataclass(frozen=True)
class DeviceRecord:
    subject_ref: str
    device_ref: str
    device_class: str
    regulatory_state: str
    control_state: str = "BLOCKED"
    manual_ref: str | None = None
    competency_ref: str | None = None


@dataclass(frozen=True)
class ProviderRecord:
    provider_ref: str
    service_class: str
    jurisdiction: str
    official_source_ref: str
    verified_at: str | None = None
    freshness_days: int = 30


@dataclass(frozen=True)
class InterventionRecord:
    subject_ref: str
    intervention_ref: str
    evidence_grade: str
    review_state: str
    source_ref: str
    outcome_state: str = "NOT_STARTED"


@dataclass(frozen=True)
class ClaimQueueItem:
    queue_id: str
    claim_sha256: str
    source_pointer: str
    risk_classes: tuple[str, ...]
    priority: str
    status: str
    clinical_review_required: bool
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CareCoordinationStore:
    """Pseudonymous local health coordination store; no names or raw source bodies."""

    def __init__(self, path: str | Path) -> None:
        self.connection = sqlite3.connect(str(path))
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS subjects (
              subject_ref TEXT PRIMARY KEY, data_classification TEXT NOT NULL,
              created_at TEXT NOT NULL, active INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS consents (
              consent_id TEXT PRIMARY KEY, subject_ref TEXT NOT NULL, scope TEXT NOT NULL,
              state TEXT NOT NULL, evidence_ref TEXT NOT NULL, expires_at TEXT,
              recorded_at TEXT NOT NULL, UNIQUE(subject_ref, scope),
              FOREIGN KEY(subject_ref) REFERENCES subjects(subject_ref)
            );
            CREATE TABLE IF NOT EXISTS diagnostic_sources (
              record_id TEXT PRIMARY KEY, subject_ref TEXT NOT NULL, source_ref TEXT NOT NULL,
              source_sha256 TEXT NOT NULL, source_type TEXT NOT NULL, review_state TEXT NOT NULL,
              recorded_at TEXT NOT NULL, UNIQUE(subject_ref, source_sha256),
              FOREIGN KEY(subject_ref) REFERENCES subjects(subject_ref)
            );
            CREATE TABLE IF NOT EXISTS regimen_items (
              record_id TEXT PRIMARY KEY, subject_ref TEXT NOT NULL, item_ref TEXT NOT NULL,
              category TEXT NOT NULL, status TEXT NOT NULL, source_ref TEXT NOT NULL,
              review_state TEXT NOT NULL, interaction_review_ref TEXT, recorded_at TEXT NOT NULL,
              UNIQUE(subject_ref, item_ref, category), FOREIGN KEY(subject_ref) REFERENCES subjects(subject_ref)
            );
            CREATE TABLE IF NOT EXISTS devices (
              record_id TEXT PRIMARY KEY, subject_ref TEXT NOT NULL, device_ref TEXT NOT NULL,
              device_class TEXT NOT NULL, regulatory_state TEXT NOT NULL, control_state TEXT NOT NULL,
              manual_ref TEXT, competency_ref TEXT, recorded_at TEXT NOT NULL,
              UNIQUE(subject_ref, device_ref), FOREIGN KEY(subject_ref) REFERENCES subjects(subject_ref)
            );
            CREATE TABLE IF NOT EXISTS providers (
              provider_ref TEXT PRIMARY KEY, service_class TEXT NOT NULL, jurisdiction TEXT NOT NULL,
              official_source_ref TEXT NOT NULL, verified_at TEXT, freshness_days INTEGER NOT NULL,
              recorded_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS interventions (
              record_id TEXT PRIMARY KEY, subject_ref TEXT NOT NULL, intervention_ref TEXT NOT NULL,
              evidence_grade TEXT NOT NULL, review_state TEXT NOT NULL, source_ref TEXT NOT NULL,
              outcome_state TEXT NOT NULL, recorded_at TEXT NOT NULL,
              UNIQUE(subject_ref, intervention_ref), FOREIGN KEY(subject_ref) REFERENCES subjects(subject_ref)
            );
            CREATE TABLE IF NOT EXISTS claim_review_queue (
              queue_id TEXT PRIMARY KEY, claim_sha256 TEXT NOT NULL, source_pointer TEXT NOT NULL,
              risk_classes_json TEXT NOT NULL, priority TEXT NOT NULL, status TEXT NOT NULL,
              clinical_review_required INTEGER NOT NULL, created_at TEXT NOT NULL,
              UNIQUE(claim_sha256, source_pointer)
            );
            """
        )
        self.connection.commit()

    def create_subject(self, subject_ref: str, *, data_classification: str = "RESTRICTED_HEALTH") -> dict[str, Any]:
        ref = required(subject_ref, "subject_ref")
        if data_classification != "RESTRICTED_HEALTH":
            raise ValueError("health subjects must use RESTRICTED_HEALTH")
        self.connection.execute(
            "INSERT OR IGNORE INTO subjects(subject_ref,data_classification,created_at,active) VALUES(?,?,?,1)",
            (ref, data_classification, utc_now()),
        )
        self.connection.commit()
        return {"subject_ref": ref, "data_classification": data_classification, "active": True}

    def set_consent(self, record: ConsentRecord) -> dict[str, Any]:
        if record.state not in ALLOWED_CONSENT:
            raise ValueError("invalid consent state")
        self._subject_exists(record.subject_ref)
        consent_id = stable_id("health-consent", record.subject_ref, record.scope)
        self.connection.execute(
            """INSERT INTO consents(consent_id,subject_ref,scope,state,evidence_ref,expires_at,recorded_at)
            VALUES(?,?,?,?,?,?,?) ON CONFLICT(subject_ref,scope) DO UPDATE SET
            state=excluded.state,evidence_ref=excluded.evidence_ref,
            expires_at=excluded.expires_at,recorded_at=excluded.recorded_at""",
            (consent_id, record.subject_ref, required(record.scope, "scope"), record.state,
             required(record.evidence_ref, "evidence_ref"), record.expires_at, utc_now()),
        )
        self.connection.commit()
        return {"consent_id": consent_id, "state": record.state}

    def has_consent(self, subject_ref: str, scope: str) -> bool:
        row = self.connection.execute(
            "SELECT state,expires_at FROM consents WHERE subject_ref=? AND scope=?",
            (subject_ref, scope),
        ).fetchone()
        if not row or row["state"] != "GRANTED":
            return False
        return not row["expires_at"] or row["expires_at"] > utc_now()

    def add_diagnostic_source(self, record: DiagnosticSourceRecord) -> str:
        self._require_consent(record.subject_ref, "diagnostic_sources")
        if record.review_state not in ALLOWED_REVIEW:
            raise ValueError("invalid review state")
        if not re.fullmatch(r"[0-9a-f]{64}", record.source_sha256):
            raise ValueError("source_sha256 must be a lowercase SHA-256")
        record_id = stable_id("diagnostic-source", record.subject_ref, record.source_sha256)
        self.connection.execute(
            "INSERT OR IGNORE INTO diagnostic_sources VALUES(?,?,?,?,?,?,?)",
            (record_id, record.subject_ref, required(record.source_ref, "source_ref"),
             record.source_sha256, required(record.source_type, "source_type"),
             record.review_state, utc_now()),
        )
        self.connection.commit()
        return record_id

    def add_regimen_item(self, record: RegimenItem) -> str:
        self._require_consent(record.subject_ref, "regimen")
        if record.review_state not in ALLOWED_REVIEW:
            raise ValueError("invalid review state")
        record_id = stable_id("regimen", record.subject_ref, record.item_ref, record.category)
        self.connection.execute(
            "INSERT OR REPLACE INTO regimen_items VALUES(?,?,?,?,?,?,?,?,?)",
            (record_id, record.subject_ref, required(record.item_ref, "item_ref"),
             required(record.category, "category"), required(record.status, "status"),
             required(record.source_ref, "source_ref"), record.review_state,
             record.interaction_review_ref, utc_now()),
        )
        self.connection.commit()
        return record_id

    def add_device(self, record: DeviceRecord) -> str:
        self._require_consent(record.subject_ref, "devices")
        if record.control_state not in ALLOWED_DEVICE:
            raise ValueError("invalid control state")
        if record.control_state == "SUPERVISED_INFORMATION_ONLY" and not (record.manual_ref and record.competency_ref):
            raise ValueError("manual and competency evidence required")
        record_id = stable_id("device", record.subject_ref, record.device_ref)
        self.connection.execute(
            "INSERT OR REPLACE INTO devices VALUES(?,?,?,?,?,?,?,?,?)",
            (record_id, record.subject_ref, required(record.device_ref, "device_ref"),
             required(record.device_class, "device_class"), required(record.regulatory_state, "regulatory_state"),
             record.control_state, record.manual_ref, record.competency_ref, utc_now()),
        )
        self.connection.commit()
        return record_id

    def add_provider(self, record: ProviderRecord) -> str:
        if record.freshness_days <= 0:
            raise ValueError("freshness_days must be positive")
        self.connection.execute(
            "INSERT OR REPLACE INTO providers VALUES(?,?,?,?,?,?,?)",
            (required(record.provider_ref, "provider_ref"), required(record.service_class, "service_class"),
             required(record.jurisdiction, "jurisdiction"), required(record.official_source_ref, "official_source_ref"),
             record.verified_at, record.freshness_days, utc_now()),
        )
        self.connection.commit()
        return record.provider_ref

    def add_intervention(self, record: InterventionRecord) -> str:
        self._require_consent(record.subject_ref, "interventions")
        if record.evidence_grade not in ALLOWED_GRADES or record.review_state not in ALLOWED_REVIEW:
            raise ValueError("invalid evidence grade or review state")
        if record.outcome_state != "NOT_STARTED" and record.review_state == "NOT_REVIEWED":
            raise ValueError("unreviewed intervention cannot advance outcome state")
        record_id = stable_id("intervention", record.subject_ref, record.intervention_ref)
        self.connection.execute(
            "INSERT OR REPLACE INTO interventions VALUES(?,?,?,?,?,?,?,?)",
            (record_id, record.subject_ref, required(record.intervention_ref, "intervention_ref"),
             record.evidence_grade, record.review_state, required(record.source_ref, "source_ref"),
             record.outcome_state, utc_now()),
        )
        self.connection.commit()
        return record_id

    def enqueue_claim(self, *, claim_sha256: str, source_pointer: str,
                      risk_classes: Iterable[str], priority: str) -> ClaimQueueItem:
        if not re.fullmatch(r"[0-9a-f]{64}", claim_sha256):
            raise ValueError("claim_sha256 must be a lowercase SHA-256")
        if priority not in ALLOWED_PRIORITY:
            raise ValueError("invalid priority")
        risks = tuple(sorted({required(risk, "risk_class") for risk in risk_classes}))
        if not risks:
            raise ValueError("risk_classes required")
        pointer = required(source_pointer, "source_pointer")
        queue_id = stable_id("health-claim-queue", claim_sha256, pointer)
        item = ClaimQueueItem(queue_id, claim_sha256, pointer, risks, priority, "QUEUED", True, utc_now())
        self.connection.execute(
            "INSERT OR IGNORE INTO claim_review_queue VALUES(?,?,?,?,?,?,?,?)",
            (queue_id, claim_sha256, pointer, canonical_json(risks), priority,
             item.status, 1, item.created_at),
        )
        self.connection.commit()
        return item

    def build_review_packet(self, subject_ref: str) -> dict[str, Any]:
        self._subject_exists(subject_ref)
        counts = {}
        for table in ("diagnostic_sources", "regimen_items", "devices", "interventions"):
            counts[table] = int(self.connection.execute(
                f"SELECT COUNT(*) FROM {table} WHERE subject_ref=?", (subject_ref,)
            ).fetchone()[0])
        consent_rows = self.connection.execute(
            "SELECT scope,state,expires_at FROM consents WHERE subject_ref=? ORDER BY scope",
            (subject_ref,),
        ).fetchall()
        return {
            "subject_ref": subject_ref,
            "record_counts": counts,
            "consents": [dict(row) for row in consent_rows],
            "contains_raw_medical_values": False,
            "professional_decision_required": True,
            "generated_at": utc_now(),
        }

    def _subject_exists(self, subject_ref: str) -> None:
        if not self.connection.execute(
            "SELECT 1 FROM subjects WHERE subject_ref=?", (subject_ref,)
        ).fetchone():
            raise ValueError("unknown subject_ref")

    def _require_consent(self, subject_ref: str, scope: str) -> None:
        self._subject_exists(subject_ref)
        if not self.has_consent(subject_ref, scope):
            raise PermissionError(f"active consent required for {scope}")

    def close(self) -> None:
        self.connection.close()


def synthetic_subject_ref(seed: str) -> str:
    return f"subject-{sha256_text(required(seed, 'seed'))[:16]}"
