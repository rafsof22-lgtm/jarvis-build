#!/usr/bin/env python3
"""Verify Jarvis voice-command policy without microphone or provider access."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jarvis_voice_gateway import VoiceGatewayPolicy, classify_voice_command, redact_sensitive_text

EVIDENCE = ROOT / "evidence/voice-command-gateway-v1-verification.json"


def main() -> None:
    policy = VoiceGatewayPolicy()
    policy.validate()

    stop = classify_voice_command("Stop Jarvis", policy)
    read_only = classify_voice_command("Show the current project status", policy)
    ambiguous = classify_voice_command("Do the thing", policy)
    financial = classify_voice_command("Buy 100 XRP now", policy)
    credential = classify_voice_command("My API key is sk-1234567890abcdef", policy)
    device = classify_voice_command("Start the Spooky2 plasma device", policy)
    production = classify_voice_command("Deploy this to production", policy)
    destructive = classify_voice_command("Delete the customer database", policy)
    communication = classify_voice_command("Send this email to the supplier", policy)
    locked = classify_voice_command("Show my calendar", policy, device_locked=True)
    code_action = classify_voice_command("Run this shell command", policy)
    redacted = redact_sensitive_text("password is hunter2 and code 123456")

    invalid_policy_rejected = False
    try:
        VoiceGatewayPolicy(visible_recording_indicator=False).validate()
    except ValueError:
        invalid_policy_rejected = True

    decisions = [stop, read_only, ambiguous, financial, credential, device, production, destructive, communication, locked, code_action]
    checks = {
        "stop_is_immediate_non_executing_policy_decision": stop.action == "STOP_CURRENT_VOICE_WORKFLOW" and not stop.requires_confirmation and not stop.execute,
        "read_only_routes_without_owner_gate": read_only.risk_class == "R0_READ_ONLY" and not read_only.requires_owner_gate,
        "ambiguous_asks_for_clarification": ambiguous.action == "ASK_FOR_CLARIFICATION",
        "financial_blocked": financial.risk_class == "R5_FINANCIAL" and financial.requires_owner_gate and not financial.execute,
        "credential_blocked_and_redacted": credential.risk_class == "R5_CREDENTIAL" and "[REDACTED]" in credential.redacted_transcript,
        "health_device_blocked": device.risk_class == "R5_CLINICAL_OR_WELLNESS_DEVICE" and device.action == "BLOCK",
        "production_prepare_only": production.action == "PREPARE_ONLY_REQUIRE_OWNER_APPROVAL",
        "destructive_exact_gate": destructive.requires_confirmation and destructive.requires_owner_gate,
        "communication_preview_gate": communication.action == "DRAFT_OR_PREVIEW_ONLY" and communication.requires_confirmation,
        "locked_device_denied": locked.risk_class == "R4_LOCKED_DEVICE",
        "code_action_prepare_only": code_action.action == "PREPARE_ONLY_REQUIRE_REVIEW",
        "generic_secret_and_code_redaction": redacted.count("[REDACTED]") >= 2,
        "invalid_policy_fails_closed": invalid_policy_rejected,
        "no_decision_executes": all(not decision.execute for decision in decisions),
        "no_raw_transcript_retention": all(not decision.raw_transcript_retained for decision in decisions),
        "default_sensitive_permissions_off": not policy.microphone_permission_default and not policy.camera_permission_default and not policy.clipboard_permission_default,
        "speaker_verification_not_sole_auth": not policy.speaker_verification_is_sole_auth,
        "voice_financial_production_device_authority_off": not policy.financial_actions_from_voice and not policy.production_actions_from_voice and not policy.clinical_device_actions_from_voice
    }

    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "id": "EVIDENCE-VOICE-COMMAND-GATEWAY-V1",
        "status": status,
        "checks": checks,
        "proof_scope": "Text-transcript risk classification and policy validation only.",
        "microphone_camera_or_clipboard_access": "NOT_ATTEMPTED",
        "speech_provider_calls": "NOT_ATTEMPTED",
        "external_actions": "NOT_EXECUTED",
        "production_state": "NOT_DEPLOYED",
        "rollback": "Revert the voice-gateway tranche and keep Jarvis text-only."
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
