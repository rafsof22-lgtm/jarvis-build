from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class ProviderAssessment:
    account_id: str
    provider: str
    evidence_state: str
    freshness_state: str
    usage_percent: float | None
    exhaustion_forecast: str
    alert_state: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class RemediationProposal:
    proposal_id: str
    target_id: str
    issue_kind: str
    risk_class: str
    action_mode: str
    primary_action: str
    approval_required: bool
    evidence_required: tuple[str, ...]
    rollback: str


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _numeric_usage(account: Mapping[str, Any]) -> tuple[float | None, float | None]:
    for item in account.get("usage", []):
        value, limit = item.get("value"), item.get("limit")
        if isinstance(value, (int, float)) and isinstance(limit, (int, float)) and limit > 0:
            return float(value), float(limit)
    for item in account.get("allowances", []):
        value, limit = item.get("value"), item.get("limit")
        if isinstance(value, (int, float)) and isinstance(limit, (int, float)) and limit > 0:
            return float(value), float(limit)
    return None, None


def assess_provider_account(account: Mapping[str, Any], *, now: datetime | None = None, stale_after_hours: int = 24) -> ProviderAssessment:
    current = now or datetime.now(timezone.utc)
    reasons: list[str] = []
    verified_at = _parse_time(account.get("last_verified_at"))
    evidence_state = "VERIFIED" if account.get("balance_status") == "verified" and verified_at else "UNVERIFIED"
    if verified_at is None:
        freshness = "UNKNOWN"
        reasons.append("No authoritative verification timestamp")
    else:
        age_hours = (current - verified_at).total_seconds() / 3600
        freshness = "FRESH" if age_hours <= stale_after_hours else "STALE"
        if freshness == "STALE":
            reasons.append(f"Evidence is {round(age_hours, 1)} hours old")

    used, limit = _numeric_usage(account)
    usage_percent = round(used / limit * 100, 2) if used is not None and limit else None
    threshold = float(account.get("alert_threshold_percent", 80))
    renewal = _parse_time(account.get("renewal_at"))
    forecast = "UNAVAILABLE"
    if usage_percent is not None:
        if usage_percent >= 100:
            forecast = "EXHAUSTED"
        elif usage_percent >= threshold:
            forecast = "AT_RISK_BEFORE_RENEWAL" if renewal and renewal > current else "AT_RISK"
        else:
            forecast = "WITHIN_ALLOWANCE"
    else:
        reasons.append("Numeric usage and limit are unavailable")

    if evidence_state != "VERIFIED" or freshness in {"UNKNOWN", "STALE"}:
        alert = "EVIDENCE_REQUIRED"
    elif forecast in {"EXHAUSTED", "AT_RISK", "AT_RISK_BEFORE_RENEWAL"}:
        alert = "ACTION_REQUIRED"
    else:
        alert = "OK"
    reasons.extend(str(item) for item in account.get("blockers", []) if item)
    return ProviderAssessment(
        account_id=str(account.get("account_id", "unknown")),
        provider=str(account.get("provider", "unknown")),
        evidence_state=evidence_state,
        freshness_state=freshness,
        usage_percent=usage_percent,
        exhaustion_forecast=forecast,
        alert_state=alert,
        reasons=tuple(dict.fromkeys(reasons)),
    )


def assess_provider_ledger(accounts: Iterable[Mapping[str, Any]], *, now: datetime | None = None) -> dict[str, Any]:
    assessments = [assess_provider_account(item, now=now) for item in accounts]
    return {
        "accounts": [asdict(item) for item in assessments],
        "summary": {
            "accounts": len(assessments),
            "verified": sum(item.evidence_state == "VERIFIED" for item in assessments),
            "fresh": sum(item.freshness_state == "FRESH" for item in assessments),
            "action_required": sum(item.alert_state == "ACTION_REQUIRED" for item in assessments),
            "evidence_required": sum(item.alert_state == "EVIDENCE_REQUIRED" for item in assessments),
        },
        "authoritative_balances_inferred": False,
    }


def build_remediation_proposal(*, target_id: str, issue_kind: str, evidence_pointer: str) -> RemediationProposal:
    risk_map = {
        "stale_evidence": ("LOW", "Refresh read-only evidence"),
        "failed_health": ("MEDIUM", "Prepare diagnostic and rollback plan"),
        "credential_rotation": ("HIGH", "Prepare provider-console rotation checklist"),
        "production_drift": ("HIGH", "Prepare staging reconciliation and rollback"),
    }
    risk, action = risk_map.get(issue_kind, ("MEDIUM", "Prepare bounded diagnostic plan"))
    proposal_id = hashlib.sha256(f"{target_id}|{issue_kind}|{evidence_pointer}".encode()).hexdigest()[:20]
    return RemediationProposal(
        proposal_id=proposal_id,
        target_id=target_id,
        issue_kind=issue_kind,
        risk_class=risk,
        action_mode="PROPOSAL_ONLY",
        primary_action=action,
        approval_required=risk in {"MEDIUM", "HIGH"},
        evidence_required=(evidence_pointer, "test_result", "rollback_proof"),
        rollback="No mutation occurs; discard proposal or revert any separately approved implementation.",
    )


def proposal_json(proposal: RemediationProposal) -> str:
    return json.dumps(asdict(proposal), sort_keys=True, separators=(",", ":"))
