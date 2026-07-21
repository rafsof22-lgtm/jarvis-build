"""Authentication policy helpers for the Jarvis Command Centre.

The helper verifies an environment-provided bearer token without logging, storing or
returning its value. It is framework-neutral and does not create user accounts.
"""
from __future__ import annotations

import hashlib
import hmac
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AuthDecision:
    authorised: bool
    state: str
    reason: str
    token_value_exposed: bool = False


def _digest(value: str) -> bytes:
    return hashlib.sha256(value.encode("utf-8")).digest()


def authenticate_bearer(authorization_header: str | None, *, env_name: str = "JARVIS_COMMAND_CENTRE_BEARER_TOKEN") -> AuthDecision:
    configured = os.getenv(env_name, "")
    if not configured:
        return AuthDecision(False, "BLOCKED", "Command Centre bearer token is not configured in the approved runtime secret store.")
    if not authorization_header or not authorization_header.startswith("Bearer "):
        return AuthDecision(False, "DENIED", "A bearer credential is required.")
    supplied = authorization_header.removeprefix("Bearer ").strip()
    if not supplied:
        return AuthDecision(False, "DENIED", "The bearer credential is empty.")
    authorised = hmac.compare_digest(_digest(configured), _digest(supplied))
    return AuthDecision(authorised, "AUTHORISED" if authorised else "DENIED", "Credential verified." if authorised else "Credential rejected.")


def authentication_contract() -> dict[str, object]:
    return {
        "contract_id": "JARVIS-COMMAND-CENTRE-AUTH-V1",
        "state": "IMPLEMENTED_NOT_INTEGRATED",
        "method": "bearer_token_from_approved_secret_store",
        "token_env_name": "JARVIS_COMMAND_CENTRE_BEARER_TOKEN",
        "token_values_logged": False,
        "token_values_returned": False,
        "mfa_replacement": False,
        "production_identity_provider": "BLOCKED_PENDING_OIDC_OR_APPROVED_SSO",
        "required_next_tests": ["unauthorised denial", "valid access", "invalid access", "redacted logs", "session expiry", "CSRF and origin controls", "role and permission enforcement", "rollback"],
    }
