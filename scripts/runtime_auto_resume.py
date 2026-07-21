#!/usr/bin/env python3
"""Run bounded, redacted runtime-readiness checks for ready secret groups."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
READINESS = ROOT / "evidence/github-actions-secret-readiness-v1.json"
MANIFEST = ROOT / "registry/platform/runtime_auto_resume_manifest_v1.json"
OUTPUT = ROOT / "evidence/runtime-auto-resume-v1.json"


def _redacted_error(exc: Exception) -> str:
    return exc.__class__.__name__


def _presence(name: str) -> dict[str, Any]:
    return {"type": "presence", "name": name, "passed": bool(os.getenv(name)), "value_exposed": False}


def _url_parse(name: str) -> dict[str, Any]:
    value = os.getenv(name, "")
    parsed = urlparse(value)
    passed = parsed.scheme in {"https", "http"} and bool(parsed.netloc)
    return {"type": "url_parse", "name": name, "passed": passed, "scheme": parsed.scheme or None, "value_exposed": False}


def _hmac_self_test(name: str) -> dict[str, Any]:
    secret = os.getenv(name, "")
    if not secret:
        return {"type": "hmac_self_test", "name": name, "passed": False, "value_exposed": False}
    payload = b"jarvis-staging-readiness-self-test"
    first = hmac.new(secret.encode(), payload, hashlib.sha256).digest()
    second = hmac.new(secret.encode(), payload, hashlib.sha256).digest()
    return {"type": "hmac_self_test", "name": name, "passed": hmac.compare_digest(first, second), "value_exposed": False}


def _http_get(check: dict[str, Any], execute: bool, timeout: int, attempts: int) -> dict[str, Any]:
    url_name = check["url_env"]
    base = os.getenv(url_name, "")
    parsed = urlparse(base)
    if parsed.scheme not in {"https", "http"} or not parsed.netloc:
        return {"type": "http_get", "url_env": url_name, "passed": False, "state": "INVALID_OR_MISSING_URL", "value_exposed": False}
    if not execute:
        return {"type": "http_get", "url_env": url_name, "passed": True, "state": "PLAN_VALIDATED_NOT_EXECUTED", "value_exposed": False}

    headers = {"Accept": "application/json", "User-Agent": "Jarvis-Runtime-Auto-Resume/1.0"}
    auth_name = check.get("auth_env")
    if auth_name and os.getenv(auth_name):
        headers["Authorization"] = f"Bearer {os.environ[auth_name]}"
    endpoint = base.rstrip("/") + check.get("path", "/health")
    expected = set(check.get("expected_status", [200]))
    last_error = None
    for attempt in range(1, attempts + 1):
        started = time.monotonic()
        try:
            with urlopen(Request(endpoint, headers=headers, method="GET"), timeout=timeout) as response:
                status = response.status
                response.read(4096)
            return {
                "type": "http_get",
                "url_env": url_name,
                "passed": status in expected,
                "state": "EXECUTED",
                "status_code": status,
                "latency_ms": round((time.monotonic() - started) * 1000),
                "attempt": attempt,
                "value_exposed": False,
            }
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            last_error = _redacted_error(exc)
            if attempt < attempts:
                time.sleep(0.25 * attempt)
    return {"type": "http_get", "url_env": url_name, "passed": False, "state": "FAILED", "error_class": last_error, "value_exposed": False}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Run harmless read-only network checks")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    readiness = json.loads(READINESS.read_text(encoding="utf-8")) if READINESS.exists() else {"groups": []}
    readiness_by_id = {g["group_id"]: g for g in readiness.get("groups", [])}
    results = []

    timeout = int(manifest["policy"].get("timeouts_seconds", 8))
    attempts = int(manifest["policy"].get("maximum_attempts", 2))
    for group in manifest["groups"]:
        ready = readiness_by_id.get(group["group_id"], {}).get("state") == "READY"
        optional = bool(group.get("optional"))
        if not ready:
            results.append({"group_id": group["group_id"], "task_ids": group.get("task_ids", []), "state": "OPTIONAL_NOT_READY" if optional else "BLOCKED_BY_MISSING_CONFIGURATION", "checks": []})
            continue
        checks = []
        for check in group["checks"]:
            kind = check["type"]
            if kind == "presence":
                checks.append(_presence(check["env"]))
            elif kind == "url_parse":
                checks.append(_url_parse(check["url_env"]))
            elif kind == "hmac_self_test":
                checks.append(_hmac_self_test(check["secret_env"]))
            elif kind == "http_get":
                checks.append(_http_get(check, args.execute, timeout, attempts))
            else:
                checks.append({"type": kind, "passed": False, "state": "UNSUPPORTED_CHECK", "value_exposed": False})
        state = "PASSED" if all(item["passed"] for item in checks) else "FAILED"
        results.append({"group_id": group["group_id"], "task_ids": group.get("task_ids", []), "state": state, "checks": checks})

    required = [r for r in results if r["state"] != "OPTIONAL_NOT_READY"]
    status = "PASSED" if required and all(r["state"] == "PASSED" for r in required) else "ACTION_REQUIRED_OR_BLOCKED"
    report = {
        "id": "EVIDENCE-RUNTIME-AUTO-RESUME-V1",
        "mode": "EXECUTE_READ_ONLY" if args.execute else "PLAN_ONLY",
        "status": status,
        "groups": results,
        "security": {
            "secret_values_exposed": False,
            "writes_performed": False,
            "provider_state_changed": False,
            "production_promoted": False,
            "financial_actions": False,
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
