from __future__ import annotations

import hashlib
import ipaddress
import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol
from urllib.parse import urlparse

from src.jarvis_completion.runtime_v1 import SignedEnvelope, canonical_json, sign_envelope


@dataclass(frozen=True)
class N8nExecutionPolicy:
    execution_enabled: bool = False
    allowed_workflows: frozenset[str] = frozenset()
    timeout_seconds: int = 10
    maximum_attempts: int = 1
    maximum_age_seconds: int = 300
    allow_private_http: bool = False
    allowed_data_classifications: frozenset[str] = frozenset({"public", "internal"})


@dataclass(frozen=True)
class N8nRequest:
    workflow_id: str
    payload: Mapping[str, Any]
    idempotency_key: str
    data_classification: str = "internal"


class N8nTransport(Protocol):
    def send(self, url: str, headers: Mapping[str, str], payload: Mapping[str, Any], timeout: int) -> Mapping[str, Any]: ...


class ReplayStore:
    """Persistent message and idempotency replay protection without payload storage."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.db = sqlite3.connect(str(path))
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS n8n_replay_guard("
            "message_id TEXT PRIMARY KEY,idempotency_key TEXT UNIQUE NOT NULL,seen_at INTEGER NOT NULL)"
        )

    def close(self) -> None:
        self.db.close()

    def claim(self, envelope: SignedEnvelope) -> bool:
        try:
            with self.db:
                self.db.execute(
                    "INSERT INTO n8n_replay_guard VALUES(?,?,?)",
                    (envelope.message_id, envelope.idempotency_key, int(time.time())),
                )
        except sqlite3.IntegrityError:
            return False
        return True


class N8nAdapter:
    """Fail-closed n8n webhook adapter. Live execution requires explicit policy and injected transport."""

    def __init__(
        self,
        endpoint: str,
        key_material: bytes,
        *,
        replay_store: ReplayStore | None = None,
        transport: N8nTransport | None = None,
    ) -> None:
        self.endpoint = endpoint
        self.key_material = key_material
        self.replay_store = replay_store or ReplayStore()
        self.transport = transport

    @staticmethod
    def _private_host(hostname: str | None) -> bool:
        if not hostname:
            return False
        if hostname in {"localhost", "localhost.localdomain"}:
            return True
        try:
            address = ipaddress.ip_address(hostname)
        except ValueError:
            return hostname.endswith(".internal") or hostname.endswith(".local")
        return address.is_private or address.is_loopback

    def preflight(self, request: N8nRequest, policy: N8nExecutionPolicy) -> dict[str, Any]:
        reasons: list[str] = []
        parsed = urlparse(self.endpoint)
        private_host = self._private_host(parsed.hostname)
        if not policy.execution_enabled:
            reasons.append("EXECUTION_NOT_EXPLICITLY_ENABLED")
        if not request.workflow_id or request.workflow_id not in policy.allowed_workflows:
            reasons.append("WORKFLOW_NOT_ALLOWLISTED")
        if not request.idempotency_key:
            reasons.append("IDEMPOTENCY_KEY_REQUIRED")
        if request.data_classification not in policy.allowed_data_classifications:
            reasons.append("DATA_CLASSIFICATION_NOT_ALLOWED")
        if parsed.scheme != "https" and not (policy.allow_private_http and parsed.scheme == "http" and private_host):
            reasons.append("HTTPS_OR_APPROVED_PRIVATE_HTTP_REQUIRED")
        if not parsed.hostname:
            reasons.append("ENDPOINT_HOST_REQUIRED")
        if not self.key_material:
            reasons.append("SIGNING_KEY_REFERENCE_NOT_RESOLVED")
        if not 1 <= policy.timeout_seconds <= 30:
            reasons.append("TIMEOUT_OUT_OF_RANGE")
        if not 1 <= policy.maximum_attempts <= 3:
            reasons.append("ATTEMPT_LIMIT_OUT_OF_RANGE")
        if self.transport is None:
            reasons.append("TRANSPORT_NOT_CONFIGURED")
        return {
            "allowed": not reasons,
            "reasons": reasons,
            "workflow_id": request.workflow_id,
            "endpoint_origin": f"{parsed.scheme}://{parsed.netloc}" if parsed.netloc else "UNRESOLVED",
            "private_host": private_host,
            "payload_sha256": hashlib.sha256(canonical_json(request.payload).encode()).hexdigest(),
            "secret_values_exposed": False,
        }

    @staticmethod
    def _wire_payload(envelope: SignedEnvelope, request: N8nRequest) -> dict[str, Any]:
        return {
            "message_id": envelope.message_id,
            "timestamp": envelope.timestamp,
            "idempotency_key": envelope.idempotency_key,
            "workflow_id": request.workflow_id,
            "payload": dict(request.payload),
        }

    def execute(self, request: N8nRequest, policy: N8nExecutionPolicy, *, timestamp: int | None = None) -> dict[str, Any]:
        preflight = self.preflight(request, policy)
        if not preflight["allowed"]:
            return {"state": "BLOCKED", "preflight": preflight, "provider_call_executed": False}
        envelope = sign_envelope(
            {"workflow_id": request.workflow_id, "payload": dict(request.payload)},
            self.key_material,
            idempotency_key=request.idempotency_key,
            timestamp=timestamp,
        )
        if not self.replay_store.claim(envelope):
            return {
                "state": "REPLAY_REJECTED",
                "preflight": preflight,
                "message_id": envelope.message_id,
                "idempotency_key": envelope.idempotency_key,
                "provider_call_executed": False,
            }
        headers = {
            "Content-Type": "application/json",
            "X-Jarvis-Message-Id": envelope.message_id,
            "X-Jarvis-Timestamp": str(envelope.timestamp),
            "X-Jarvis-Idempotency-Key": envelope.idempotency_key,
            "X-Jarvis-Signature": envelope.signature,
        }
        response = self.transport.send(self.endpoint, headers, self._wire_payload(envelope, request), policy.timeout_seconds)
        response_digest = hashlib.sha256(canonical_json(response).encode()).hexdigest()
        return {
            "state": "SUCCEEDED",
            "preflight": preflight,
            "message_id": envelope.message_id,
            "idempotency_key": envelope.idempotency_key,
            "response_sha256": response_digest,
            "provider_call_executed": True,
            "secret_values_exposed": False,
        }
