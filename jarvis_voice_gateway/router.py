"""Deterministic transcript classification for Jarvis voice commands.

This module returns policy decisions only. It never executes a command, opens a
microphone, authenticates a user, calls a provider or changes an external system.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from .policy import VoiceGatewayPolicy


SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\b(?:api[_ -]?key|token|password|passcode|secret)\s*(?:is|=|:)\s*\S+", re.IGNORECASE),
    re.compile(r"\b\d{6}\b"),
)

STOP_PHRASES = {"stop", "stop jarvis", "cancel", "cancel jarvis", "pause", "mute"}
FINANCIAL_TERMS = {"buy", "sell", "trade", "transfer", "pay", "purchase", "bet", "deposit", "withdraw", "bridge", "swap"}
DESTRUCTIVE_TERMS = {"delete", "remove", "wipe", "erase", "format", "reset", "purge", "destroy", "drop"}
COMMUNICATION_TERMS = {"send", "email", "message", "post", "publish", "call", "forward", "reply"}
PRODUCTION_TERMS = {"deploy", "release", "promote", "merge", "ship", "rollback production", "restart production"}
CREDENTIAL_TERMS = {"password", "passcode", "mfa", "otp", "token", "api key", "secret", "seed phrase", "private key", "recovery phrase", "login"}
HEALTH_DEVICE_TERMS = {"spooky2", "pemf", "laser", "plasma", "scalar", "rife", "medical device", "wellness device"}
DEVICE_ACTION_TERMS = {"start", "run", "activate", "enable", "control", "set frequency", "change setting"}
READ_ONLY_PREFIXES = ("show", "read", "search", "find", "summarise", "summarize", "explain", "what", "when", "where", "who", "list", "check status")
LOCAL_LOW_RISK_PREFIXES = ("open", "navigate", "go to", "play", "pause media", "set timer", "remind me")


@dataclass(frozen=True)
class VoiceCommandDecision:
    risk_class: str
    action: str
    requires_confirmation: bool
    requires_owner_gate: bool
    reason: str
    redacted_transcript: str
    raw_transcript_retained: bool = False
    execute: bool = False


def redact_sensitive_text(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def classify_voice_command(
    transcript: str,
    policy: VoiceGatewayPolicy | None = None,
    *,
    device_locked: bool = False,
) -> VoiceCommandDecision:
    """Classify a transcript and return a fail-closed policy decision."""

    active_policy = policy or VoiceGatewayPolicy()
    active_policy.validate()
    normalized = " ".join(transcript.strip().lower().split())
    redacted = redact_sensitive_text(transcript.strip())
    tokens = set(re.findall(r"[a-z0-9]+", normalized))

    if not normalized:
        return _decision("R0_EMPTY", "NO_ACTION", False, False, "No command was detected.", redacted)

    if normalized in STOP_PHRASES or normalized.startswith("stop jarvis"):
        return _decision("R0_EMERGENCY_STOP", "STOP_CURRENT_VOICE_WORKFLOW", False, False, "Stop and mute commands are always available and do not require confirmation.", redacted)

    if device_locked and not active_policy.lock_screen_commands_enabled:
        return _decision("R4_LOCKED_DEVICE", "BLOCK", False, True, "Voice commands are disabled while the device is locked.", redacted)

    if _contains_phrase(normalized, CREDENTIAL_TERMS):
        return _decision("R5_CREDENTIAL", "BLOCK_AND_REDACT", False, True, "Credentials, MFA and recovery material cannot be supplied or authorised by voice.", redacted)

    if _contains_phrase(normalized, FINANCIAL_TERMS):
        return _decision("R5_FINANCIAL", "BLOCK_PENDING_SEPARATE_FINANCIAL_APPROVAL", True, True, "Voice cannot authorise trading, betting, purchases, custody or money movement.", redacted)

    if _contains_phrase(normalized, HEALTH_DEVICE_TERMS) and _contains_phrase(normalized, DEVICE_ACTION_TERMS):
        return _decision("R5_CLINICAL_OR_WELLNESS_DEVICE", "BLOCK", False, True, "Live clinical or wellness-device control is disabled.", redacted)

    if _contains_phrase(normalized, PRODUCTION_TERMS):
        return _decision("R4_PRODUCTION", "PREPARE_ONLY_REQUIRE_OWNER_APPROVAL", True, True, "Voice may prepare a production plan but cannot approve or perform the production action.", redacted)

    if _contains_phrase(normalized, DESTRUCTIVE_TERMS):
        return _decision("R4_DESTRUCTIVE", "BLOCK_PENDING_EXACT_READBACK_AND_OWNER_APPROVAL", True, True, "Destructive or irreversible actions require exact target read-back and explicit owner approval outside voice-only authentication.", redacted)

    if _contains_phrase(normalized, COMMUNICATION_TERMS):
        return _decision("R3_EXTERNAL_COMMUNICATION", "DRAFT_OR_PREVIEW_ONLY", True, True, "External messages, calls and publication require recipient/content preview and explicit approval.", redacted)

    if normalized.startswith(READ_ONLY_PREFIXES):
        return _decision("R0_READ_ONLY", "ROUTE_TO_READ_ONLY_CAPABILITY", False, False, "Read-only requests may proceed through the normal capability and data-policy checks.", redacted)

    if normalized.startswith(LOCAL_LOW_RISK_PREFIXES):
        return _decision("R1_LOCAL_REVERSIBLE", "PREVIEW_THEN_ROUTE", True, False, "A reversible local action may proceed after a concise confirmation and normal permission checks.", redacted)

    if tokens.intersection({"shell", "powershell", "terminal", "command", "script", "execute", "run"}):
        return _decision("R3_CODE_OR_SYSTEM_ACTION", "PREPARE_ONLY_REQUIRE_REVIEW", True, True, "System or code execution requires a reviewed plan, permission boundary and rollback.", redacted)

    return _decision("R2_AMBIGUOUS", "ASK_FOR_CLARIFICATION", False, False, "The command is ambiguous and must be clarified before any tool or action is selected.", redacted)


def _contains_phrase(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)


def _decision(
    risk_class: str,
    action: str,
    requires_confirmation: bool,
    requires_owner_gate: bool,
    reason: str,
    redacted: str,
) -> VoiceCommandDecision:
    return VoiceCommandDecision(
        risk_class=risk_class,
        action=action,
        requires_confirmation=requires_confirmation,
        requires_owner_gate=requires_owner_gate,
        reason=reason,
        redacted_transcript=redacted,
        raw_transcript_retained=False,
        execute=False,
    )
