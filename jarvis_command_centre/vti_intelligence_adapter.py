from __future__ import annotations

import json
import os
import uuid
from typing import Any
from urllib.request import Request, urlopen


def discover_vti() -> dict[str, Any]:
    base = os.getenv("VTI_BASE_URL")
    if not base:
        return {"status": "blocked", "reason": "VTI_BASE_URL not configured", "proof_label": "RUNTIME_NOT_PROVEN"}
    with urlopen(Request(base.rstrip("/") + "/api/vti/capabilities", headers={"Accept": "application/json"}), timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def build_vti_task(command: str, requester_agent: str, requester_module: str, destination_modules: list[str], source_refs: list[str] | None = None, parameters: dict[str, Any] | None = None, budget_aud: float = 0.0, approval_state: str = "not_required") -> dict[str, Any]:
    task_id = str(uuid.uuid4())
    correlation_id = str(uuid.uuid4())
    return {
        "contract_version": "1.0.0", "task_id": task_id, "correlation_id": correlation_id,
        "idempotency_key": f"{requester_module}:{command}:{task_id}",
        "requester_agent": requester_agent, "requester_module": requester_module,
        "command": command, "priority": "normal", "source_refs": source_refs or [],
        "destination_modules": destination_modules, "approval_state": approval_state,
        "budget": {"currency": "AUD", "maximum": budget_aud, "free_first": True},
        "expected_outputs": [], "parameters": parameters or {},
    }


def submit_vti_task(task: dict[str, Any]) -> dict[str, Any]:
    base = os.getenv("VTI_BASE_URL")
    token = os.getenv("VTI_AGENT_BEARER_TOKEN")
    if not base or not token:
        return {"accepted": False, "status": "blocked", "reason": "VTI runtime URL or bearer token not configured"}
    request = Request(base.rstrip("/") + "/api/vti/agent-task", data=json.dumps(task).encode("utf-8"), method="POST", headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))
