from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping
from uuid import NAMESPACE_URL, uuid5

SCHEMA_VERSION = "1.0.0"

ALLOWED_SOURCE_CLASSES = {
    "USER_REPORTED_FACT",
    "USER_PROVIDED_DIAGNOSTIC_DOCUMENT",
    "USER_PROVIDED_PRODUCT_LABEL",
    "ASSISTANT_HISTORICAL_PROPOSAL",
    "OFFICIAL_CLINICAL_GUIDANCE",
    "PEER_REVIEWED_RESEARCH",
    "PROVIDER_MARKETING_OR_DIRECTORY",
    "ALTERNATIVE_OR_EXPLORATORY_SOURCE",
    "SYSTEM_DERIVED_REQUIREMENT",
}
ALLOWED_EVIDENCE_GRADES = {"A", "B", "C", "D", "F", "UNASSESSED"}
ALLOWED_DATA_CLASSES = {"PUBLIC", "INTERNAL", "CONFIDENTIAL_HEALTH", "RESTRICTED_HEALTH"}

RISK_PATTERNS: dict[str, re.Pattern[str]] = {
    "CRISIS_OR_EMERGENCY": re.compile(r"\b(?:suicid|self[- ]?harm|overdose|cannot breathe|chest pain|stroke|medical emergency)\w*\b", re.I),
    "GUARANTEED_CURE_OR_INEVITABILITY": re.compile(r"\b(?:guaranteed cure|cure all|inevitable remission|permanent cure|100% cure|complete eradication)\b", re.I),
    "PRESCRIPTION_OR_MEDICATION_CHANGE": re.compile(r"\b(?:start|stop|increase|decrease|taper|combine|switch)\b.{0,35}\b(?:medication|prescription|antidepressant|stimulant|antipsychotic|benzodiazepine|naltrexone|varenicline|modafinil)\b", re.I),
    "PSYCHEDELIC_OR_CONTROLLED_DOSING": re.compile(r"\b(?:psilocybin|mdma|ibogaine|ketamine|lsd|dmt|5-meo-dmt)\b.{0,45}\b(?:mg|dose|protocol|infusion|session|microdose)\b", re.I),
    "INVASIVE_OR_EXPERIMENTAL_INTERVENTION": re.compile(r"\b(?:crispr|gene edit|deep brain stimulation|\bdbs\b|optogenetic|stem cell|exosome|young plasma|plasmapheresis|apheresis)\b", re.I),
    "MEDICAL_DEVICE_SETTINGS": re.compile(r"\b(?:spooky2|rife|pemf|tdcs|tacs|tms|vns|hbot|laser|photobiomodulation)\b.{0,55}\b(?:hz|mhz|khz|ma|volts?|ata|pulse width|duty cycle|offset|waveform|wobble|gate|minutes?|hours?)\b", re.I),
    "FREQUENCY_AS_CURE_OR_DRUG_SIMULATION": re.compile(r"\b(?:frequency|bioresonance|rife|spooky2)\b.{0,70}\b(?:cure|eradicate|simulate|emulate)\b.{0,30}\b(?:drug|mdma|psilocybin|ibogaine|ketamine|cancer|addiction|pathogen)\b", re.I),
    "UNVERIFIED_DETOX_OR_BIOLOGIC": re.compile(r"\b(?:heavy metal detox|parasite cleanse|colon hydrotherapy|chelation|young plasma|unregulated stem cell|exosome therapy|miracle detox)\b", re.I),
    "UNVERIFIED_PROVIDER_OR_REGULATORY": re.compile(r"\b(?:fda approved|legal in|licensed clinic|best clinic|compassionate use|clinical trial enrollment)\b", re.I),
    "SPIRITUAL_CLAIM_AS_MEDICAL_FACT": re.compile(r"\b(?:chakra|morphogenetic field|quantum entanglement|orgonite|torsion field|biofield reset)\b.{0,50}\b(?:treat|cure|heal|diagnose)\b", re.I),
}

BLOCKING_RISKS = {
    "GUARANTEED_CURE_OR_INEVITABILITY",
    "PRESCRIPTION_OR_MEDICATION_CHANGE",
    "PSYCHEDELIC_OR_CONTROLLED_DOSING",
    "INVASIVE_OR_EXPERIMENTAL_INTERVENTION",
    "MEDICAL_DEVICE_SETTINGS",
    "FREQUENCY_AS_CURE_OR_DRUG_SIMULATION",
    "UNVERIFIED_DETOX_OR_BIOLOGIC",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def stable_id(namespace: str, *parts: object) -> str:
    material = "|".join(str(part).strip().lower() for part in parts)
    return str(uuid5(NAMESPACE_URL, f"jarvis:{namespace}:{material}"))


def _ensure_safe_metadata(value: Any, path: str = "metadata") -> None:
    prohibited = re.compile(r"(?:^|_)(?:name|email|phone|address|dob|medicare|patient_id|password|token|api_key|private_key|seed_phrase)(?:$|_)", re.I)
    if isinstance(value, Mapping):
        for key, child in value.items():
            if prohibited.search(str(key)):
                raise ValueError(f"PII/secret-like metadata field prohibited: {path}.{key}")
            _ensure_safe_metadata(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _ensure_safe_metadata(child, f"{path}[{index}]")


@dataclass(frozen=True)
class HealthClaimInput:
    claim_text: str
    domain: str
    source_class: str
    evidence_grade: str = "UNASSESSED"
    evidence_refs: tuple[str, ...] = ()
    data_classification: str = "RESTRICTED_HEALTH"
    user_specific: bool = False
    current_as_of: str | None = None
    metadata: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class HealthClaimAssessment:
    assessment_id: str
    claim_sha256: str
    domain: str
    source_class: str
    evidence_grade: str
    risk_classes: tuple[str, ...]
    disposition: str
    professional_review: str
    execution_allowed: bool
    medical_device_control_allowed: bool
    raw_text_persisted: bool
    evidence_refs: tuple[str, ...]
    data_classification: str
    current_as_of: str | None
    assessed_at: str
    policy_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class HealthEvidenceGate:
    """Privacy-safe triage gate. It classifies claims but never diagnoses or treats."""

    def assess(self, claim: HealthClaimInput) -> HealthClaimAssessment:
        text = str(claim.claim_text or "").strip()
        if not text:
            raise ValueError("claim_text is required")
        if claim.source_class not in ALLOWED_SOURCE_CLASSES:
            raise ValueError("unsupported source_class")
        if claim.evidence_grade not in ALLOWED_EVIDENCE_GRADES:
            raise ValueError("unsupported evidence_grade")
        if claim.data_classification not in ALLOWED_DATA_CLASSES:
            raise ValueError("unsupported data_classification")
        if claim.metadata:
            _ensure_safe_metadata(claim.metadata)
        refs = tuple(sorted({str(ref).strip() for ref in claim.evidence_refs if str(ref).strip()}))
        risks = tuple(sorted(name for name, pattern in RISK_PATTERNS.items() if pattern.search(text)))
        if "CRISIS_OR_EMERGENCY" in risks:
            disposition = "EMERGENCY_ESCALATION_REQUIRED"
            review = "URGENT_QUALIFIED_HUMAN_OR_EMERGENCY_SERVICE"
        elif "GUARANTEED_CURE_OR_INEVITABILITY" in risks or "FREQUENCY_AS_CURE_OR_DRUG_SIMULATION" in risks:
            disposition = "QUARANTINED_UNSUPPORTED_CLAIM"
            review = "LICENSED_CLINICIAN_AND_PRIMARY_SOURCE_REVIEW"
        elif set(risks) & BLOCKING_RISKS:
            disposition = "BLOCKED_PENDING_CLINICAL_REVIEW"
            review = "LICENSED_CLINICIAN_REVIEW"
        elif claim.source_class in {"USER_PROVIDED_DIAGNOSTIC_DOCUMENT", "USER_PROVIDED_PRODUCT_LABEL"} or claim.user_specific:
            disposition = "INFORMATION_ONLY_CLINICIAN_INTERPRETATION_REQUIRED"
            review = "LICENSED_CLINICIAN_OR_PHARMACIST_REVIEW"
        elif claim.source_class in {"ALTERNATIVE_OR_EXPLORATORY_SOURCE", "ASSISTANT_HISTORICAL_PROPOSAL", "PROVIDER_MARKETING_OR_DIRECTORY"} or claim.evidence_grade in {"D", "F", "UNASSESSED"}:
            disposition = "REFERENCE_ONLY_EVIDENCE_REVIEW_REQUIRED"
            review = "CURRENT_PRIMARY_SOURCE_REVIEW"
        else:
            disposition = "ELIGIBLE_FOR_INFORMATIONAL_SYNTHESIS"
            review = "STANDARD_EVIDENCE_REVIEW"
        claim_hash = sha256_text(text)
        assessment_id = stable_id("health-assessment", claim_hash, claim.domain, claim.source_class, claim.evidence_grade, risks, disposition)
        return HealthClaimAssessment(
            assessment_id=assessment_id,
            claim_sha256=claim_hash,
            domain=str(claim.domain).strip(),
            source_class=claim.source_class,
            evidence_grade=claim.evidence_grade,
            risk_classes=risks,
            disposition=disposition,
            professional_review=review,
            execution_allowed=False,
            medical_device_control_allowed=False,
            raw_text_persisted=False,
            evidence_refs=refs,
            data_classification=claim.data_classification,
            current_as_of=claim.current_as_of,
            assessed_at=utc_now(),
        )


class PrivacySafeHealthLedger:
    """Append-only SQLite ledger that stores hashes and classifications, never claim text."""

    def __init__(self, path: str | Path) -> None:
        self.connection = sqlite3.connect(str(path))
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode = WAL")
        self.connection.execute(
            """CREATE TABLE IF NOT EXISTS health_claim_assessments (
            assessment_id TEXT PRIMARY KEY,
            idempotency_key TEXT NOT NULL UNIQUE,
            claim_sha256 TEXT NOT NULL,
            domain TEXT NOT NULL,
            source_class TEXT NOT NULL,
            evidence_grade TEXT NOT NULL,
            risk_classes_json TEXT NOT NULL,
            disposition TEXT NOT NULL,
            professional_review TEXT NOT NULL,
            execution_allowed INTEGER NOT NULL,
            medical_device_control_allowed INTEGER NOT NULL,
            raw_text_persisted INTEGER NOT NULL,
            evidence_refs_json TEXT NOT NULL,
            data_classification TEXT NOT NULL,
            current_as_of TEXT,
            policy_version TEXT NOT NULL,
            assessment_json TEXT NOT NULL,
            recorded_at TEXT NOT NULL
            )"""
        )
        self.connection.commit()

    def append(self, assessment: HealthClaimAssessment, *, idempotency_key: str) -> dict[str, Any]:
        key = str(idempotency_key or "").strip()
        if not key:
            raise ValueError("idempotency_key is required")
        existing = self.connection.execute(
            "SELECT assessment_id, claim_sha256 FROM health_claim_assessments WHERE idempotency_key=?", (key,)
        ).fetchone()
        if existing:
            if existing["claim_sha256"] != assessment.claim_sha256:
                raise ValueError("idempotency collision with different claim hash")
            return {"state": "DUPLICATE_REPLAY", "assessment_id": existing["assessment_id"]}
        payload = assessment.to_dict()
        if "claim_text" in canonical_json(payload).lower():
            raise ValueError("raw claim text cannot be persisted")
        self.connection.execute(
            """INSERT INTO health_claim_assessments (
            assessment_id,idempotency_key,claim_sha256,domain,source_class,evidence_grade,risk_classes_json,
            disposition,professional_review,execution_allowed,medical_device_control_allowed,raw_text_persisted,
            evidence_refs_json,data_classification,current_as_of,policy_version,assessment_json,recorded_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                assessment.assessment_id,
                key,
                assessment.claim_sha256,
                assessment.domain,
                assessment.source_class,
                assessment.evidence_grade,
                canonical_json(assessment.risk_classes),
                assessment.disposition,
                assessment.professional_review,
                int(assessment.execution_allowed),
                int(assessment.medical_device_control_allowed),
                int(assessment.raw_text_persisted),
                canonical_json(assessment.evidence_refs),
                assessment.data_classification,
                assessment.current_as_of,
                assessment.policy_version,
                canonical_json(payload),
                utc_now(),
            ),
        )
        self.connection.commit()
        return {"state": "APPENDED", "assessment_id": assessment.assessment_id}

    def count(self) -> int:
        return int(self.connection.execute("SELECT COUNT(*) FROM health_claim_assessments").fetchone()[0])

    def read(self, assessment_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT assessment_json FROM health_claim_assessments WHERE assessment_id=?", (assessment_id,)
        ).fetchone()
        return json.loads(row["assessment_json"]) if row else None

    def close(self) -> None:
        self.connection.close()


def health_output_contract() -> dict[str, Any]:
    return {
        "contract_id": "JARVIS-HEALTH-OUTPUT-CONTRACT-V1",
        "required_sections": [
            "user_goal_and_context",
            "evidence_grade_and_source_class",
            "known_benefits_and_uncertainties",
            "risks_contraindications_and_interactions",
            "monitoring_and_stop_conditions",
            "professional_escalation",
            "citations_and_freshness",
        ],
        "denied_outputs": [
            "guaranteed cure or inevitable remission",
            "diagnosis as final authority",
            "prescription change without clinician",
            "psychedelic or controlled-substance dosing",
            "invasive experimental treatment instructions",
            "medical-device control settings without qualified supervision",
            "frequency or bioresonance presented as a drug replacement or disease cure",
        ],
        "execution_allowed": False,
        "medical_device_control": "BLOCKED",
        "emergency_override": "Direct urgent red flags to local emergency or crisis support; do not continue optimisation workflow.",
    }
