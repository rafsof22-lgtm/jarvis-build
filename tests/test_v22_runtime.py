import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["JARVIS_ENV"] = "test"

from fastapi.testclient import TestClient
from runtime.v22.app.main import app

client = TestClient(app)


def test_health_ready():
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/ready").json()["status"] == "ready"


def test_registry_counts():
    result = client.get("/registry/summary").json()
    assert (
        result["requirements"],
        result["instructions"],
        result["features"],
        result["functions"],
        result["skills"],
        result["modules"],
    ) == (38, 38, 38, 38, 38, 51)


def test_runtime_reconciliation_denominator():
    result = client.get("/runtime/reconciliation").json()
    assert result["module_count"] == 51
    assert sum(result["runtime_state_counts"].values()) == 51


def test_acceptance_truth_boundary():
    result = client.get("/acceptance/status").json()
    assert result["accepted_100_percent"] is False
    assert result["status"] == "BLOCKED"


def test_deployment_truth_boundary():
    result = client.get("/deployment/status").json()
    assert result["local_staging"] == "INTEGRATED_STAGING"
    assert result["production"] == "BLOCKED"
