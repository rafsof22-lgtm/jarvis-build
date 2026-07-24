from pathlib import Path
import csv, json, os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

ROOT = Path(__file__).resolve().parents[3]
ENV = os.getenv("JARVIS_ENV", "local-staging")


def read_csv(path):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path):
    return json.loads((ROOT / path).read_text())


app = FastAPI(title="Jarvis V22 Runtime Reconciliation Control Plane", version="22.0.0")


@app.get("/health")
def health():
    return {"status": "ok", "version": "V22", "environment": ENV}


@app.get("/ready")
def ready():
    required = [
        "registers/REQUIREMENTS_REGISTER.csv",
        "registers/INSTRUCTION_REGISTER.csv",
        "registers/FEATURE_REGISTRY.csv",
        "registers/FUNCTION_REGISTRY.csv",
        "registers/SKILL_REGISTRY.csv",
        "registry/runtime/MODULE_RUNTIME_RECONCILIATION_V22.csv",
        "manifests/JARVIS_V22_COMPLETION_STATE.json",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    if missing:
        raise HTTPException(503, {"missing": missing})
    return {"status": "ready", "environment": ENV, "missing": []}


@app.get("/registry/summary")
def summary():
    return {
        "requirements": len(read_csv("registers/REQUIREMENTS_REGISTER.csv")),
        "instructions": len(read_csv("registers/INSTRUCTION_REGISTER.csv")),
        "features": len(read_csv("registers/FEATURE_REGISTRY.csv")),
        "functions": len(read_csv("registers/FUNCTION_REGISTRY.csv")),
        "skills": len(read_csv("registers/SKILL_REGISTRY.csv")),
        "tools": len(read_csv("registers/TOOL_REGISTRY.csv")),
        "apis": len(read_csv("registers/API_REGISTRY.csv")),
        "models": len(read_csv("registers/MODEL_REGISTRY.csv")),
        "workflows": len(read_csv("registers/WORKFLOW_REGISTRY.csv")),
        "modules": len(read_csv("registry/runtime/MODULE_RUNTIME_RECONCILIATION_V22.csv")),
    }


@app.get("/runtime/reconciliation")
def reconcile():
    modules = read_csv("registry/runtime/MODULE_RUNTIME_RECONCILIATION_V22.csv")
    counts = {}
    for module in modules:
        state = module["runtime_state"]
        counts[state] = counts.get(state, 0) + 1
    return {"module_count": len(modules), "runtime_state_counts": counts, "modules": modules}


@app.get("/deployment/status")
def deployment():
    return {"environment": ENV, **read_json("manifests/JARVIS_V22_COMPLETION_STATE.json")}


@app.get("/acceptance/status")
def acceptance():
    state = read_json("manifests/JARVIS_V22_COMPLETION_STATE.json")
    return {
        "accepted_100_percent": False,
        "status": state["final_100_percent_acceptance"],
        "blockers": state["blockers"],
    }


@app.get("/", response_class=HTMLResponse)
def index():
    return "<h1>Jarvis V22</h1><p>Local staging operational. External deployment remains evidence-gated.</p>"
