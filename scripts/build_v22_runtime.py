from pathlib import Path
import csv, json

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


requirements = read_csv("registers/REQUIREMENTS_REGISTER.csv")
features = {row["requirement_id"]: row for row in read_csv("registers/FEATURE_REGISTRY.csv")}
functions = {row["requirement_id"]: row for row in read_csv("registers/FUNCTION_REGISTRY.csv")}

skill_routes = {
    "deployment": "github-railway-deploy-controller",
    "github_ci": "github-railway-deploy-controller",
    "source_ingestion": "master-chatgpt-kb",
    "requirements": "jarvis-reconstruction",
    "modules": "agent-skill-integration-builder",
    "skills": "agent-skill-integration-builder",
    "tools_apis": "project-stack-access-mapper",
    "models": "universal-sourcing-stack-scout",
    "intelligence": "universal-intelligence-gatherer",
    "xrp_hbar": "xrp-hbar-apex-tracker",
    "trading": "trading-bot-apex-orchestrator",
    "finance": "cfo-audit-controller",
    "property": "property-buyer-capture",
    "automotive": "jenok-catalog-extractor",
    "video": "vti-video-intelligence-builder",
    "passive_income": "passive-income-apex-autonomy",
    "dream_home": "dream-home-estate-planner",
}

instructions = []
for row in requirements:
    requirement_id = row["requirement_id"]
    instructions.append(
        {
            "instruction_id": "INST-" + requirement_id.rsplit("-", 1)[-1],
            "requirement_id": requirement_id,
            "canonical_instruction": row["requirement"],
            "category": row["category"],
            "primary_module": row["primary_module"],
            "feature_id": row["feature_id"],
            "feature_name": features.get(requirement_id, {}).get("feature_name", ""),
            "function_id": row["function_id"],
            "function_name": functions.get(requirement_id, {}).get("function_name", ""),
            "primary_skill": skill_routes.get(row["category"], "jarvis-sovereign-builder"),
            "user_request_message_count": row["user_request_message_count"],
            "assistant_response_message_count": row["assistant_response_message_count"],
            "source_proof": row["source_proof"],
            "approval_rule": "Constitution and module risk policy",
            "status": "APPLIED_MERGED_V21_RUNTIME_RECONCILED_V22",
            "evidence_id": row["evidence_id"],
        }
    )
write_csv("registers/INSTRUCTION_REGISTER.csv", instructions)

integrated_staging = {
    "MOD-CORE-PLATFORM",
    "MOD-MODULE-RUNTIME",
    "MOD-AGENT-ORCHESTRATOR",
    "MOD-PROCUREMENT",
    "MOD-INTELLIGENCE-JOBS",
    "MOD-DASHBOARD",
    "MOD-BUSINESS-DIGITAL",
    "MOD-BUSINESS-FINANCIAL",
    "MOD-CONSOLE-JARVIS-POP",
}
spec_only = {
    "MOD-TRADING-RESEARCH",
    "MOD-AUTOMOTIVE-JENOK",
    "MOD-PASSIVE-INCOME",
    "MOD-SURVIVAL",
    "MOD-SPOOKY2",
    "MOD-DREAM-HOME",
    "MOD-GROW",
    "MOD-LEGAL-ADMIN",
}
federated_states = {
    "MOD-XRP-HBAR-APEX": "DEPLOYED_UNVERIFIED",
    "MOD-AI-CFO": "SCAFFOLDED",
    "MOD-MASTER-KB": "IMPLEMENTED_NOT_INTEGRATED",
    "MOD-HEALTH": "IMPLEMENTED_NOT_INTEGRATED",
    "MOD-PROPERTY": "IMPLEMENTED_NOT_INTEGRATED",
    "MOD-VIDEO-INTEL": "IMPLEMENTED_NOT_INTEGRATED",
}

modules = []
for line in (ROOT / "JARVIS_MODULE_REGISTRY_V21.md").read_text().splitlines():
    if not line.startswith("| MOD-"):
        continue
    parts = [part.strip() for part in line.strip("|").split("|")]
    module_id = parts[0]
    if module_id in integrated_staging:
        state = "INTEGRATED_STAGING"
    elif module_id in spec_only:
        state = "SPEC_ONLY"
    else:
        state = federated_states.get(module_id, "IMPLEMENTED_NOT_INTEGRATED")
    blocker = {
        "SPEC_ONLY": "No physical implementation verified",
        "SCAFFOLDED": "Scaffold lacks full integration proof",
        "DEPLOYED_UNVERIFIED": "External deployment path exists but current live health is unverified",
    }.get(state, "External live route and full contract depth not proven")
    modules.append(
        {
            "module_id": module_id,
            "module_name": parts[1],
            "layer": parts[2],
            "baseline_status": parts[3],
            "user_request_message_count": parts[4],
            "assistant_response_message_count": parts[5],
            "runtime_state": state,
            "local_control_plane_staging": "INTEGRATED_STAGING",
            "external_staging_state": "DEPLOYED_UNVERIFIED" if state == "DEPLOYED_UNVERIFIED" else "BLOCKED",
            "canary_state": "BLOCKED",
            "production_state": "BLOCKED",
            "exact_blocker": blocker,
            "next_action": "Verify smallest live route, deployed commit, health, smoke, rollback and owner acceptance.",
        }
    )
write_csv("registry/runtime/MODULE_RUNTIME_RECONCILIATION_V22.csv", modules)

assert len(instructions) == 38
assert len(modules) == 51
print(json.dumps({"instructions": len(instructions), "modules": len(modules)}))
