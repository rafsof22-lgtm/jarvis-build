from __future__ import annotations

import argparse
import html
import json
import os
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from jarvis_asset_intelligence import AssetIntelligenceOrchestrator

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"
EVIDENCE = ROOT / "evidence"
CONTRACT_VERSION = "1.0.0"


def _load(name: str) -> dict[str, Any]:
    with (REGISTRY / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def _load_optional(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _severity(status: str) -> str:
    return {
        "operational": "green", "proven": "green", "connected": "green",
        "partial": "amber", "scaffold": "amber", "present_unverified": "amber",
        "blocked": "red", "failed": "red", "rotation_required": "red",
        "unknown": "grey", "retired": "grey", "not_required": "grey",
    }.get(status, "grey")


def _poll(integration: dict[str, Any]) -> dict[str, Any] | None:
    env_name = integration.get("base_url_env")
    path = integration.get("capability_path") or integration.get("health_path")
    base = os.getenv(env_name or "") if env_name else None
    if not base or not path:
        return None
    token_name = (integration.get("secret_names") or [None])[0]
    token = os.getenv(token_name or "") if token_name else None
    headers = {"Accept": "application/json", "User-Agent": "Jarvis-Command-Centre/1.2"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    started = time.monotonic()
    try:
        with urlopen(Request(base.rstrip("/") + path, headers=headers), timeout=integration.get("timeout_seconds", 5)) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if payload.get("contract_version") != CONTRACT_VERSION:
            raise ValueError("unsupported contract_version")
        payload["poll_latency_ms"] = round((time.monotonic() - started) * 1000)
        return payload
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        return {
            "contract_version": CONTRACT_VERSION,
            "health": {"status": "unknown", "readiness": "unknown", "latency_ms": None},
            "blockers": [{"id": "poll-failed", "severity": "medium", "summary": exc.__class__.__name__}],
        }


def _asset_snapshot() -> dict[str, Any]:
    try:
        planner = AssetIntelligenceOrchestrator()
        plan = planner.build_plan("update all asset intelligence")
        profiles = []
        for task in plan.tasks:
            profiles.append({
                "asset": task.asset,
                "profile_id": task.profile_id,
                "asset_class": task.asset_class,
                "milestone_count": task.milestone_count,
                "dynamic_ceiling_enabled": task.dynamic_ceiling_enabled,
                "source_family_count": len(task.source_families),
                "intelligence_layer_count": len(task.intelligence_layers),
                "knowledge_namespace": task.knowledge_namespace,
                "state": "IMPLEMENTED_NOT_INTEGRATED",
            })
        return {
            "status": "IMPLEMENTED_NOT_INTEGRATED",
            "active_assets": list(plan.requested_assets),
            "profiles": profiles,
            "trigger_modes": ["UPDATE", "DEEP_SCAN", "ALL_INTELLIGENCE"],
            "apex_sources_per_asset_maximum": 100,
            "simultaneous_all_asset_fanout": True,
            "dynamic_ceiling_engine": True,
            "knowledge_fabric_export": True,
            "voice_route": "JARVIS-VOICE-COMMAND-GATEWAY-V1",
            "truth_boundary": plan.truth_boundary,
        }
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        return {
            "status": "BLOCKED",
            "active_assets": [],
            "profiles": [],
            "blocker": exc.__class__.__name__,
            "truth_boundary": "Asset intelligence registry could not be loaded; no scan was executed.",
        }


def build_snapshot(live: bool = False) -> dict[str, Any]:
    repositories = _load("repositories.json")["repositories"]
    integrations = _load("integrations.json")["integrations"]
    costs = _load("cost-credit-ledger.json")["accounts"]
    setup_actions = _load_optional(REGISTRY / "setup-actions.json", {"platforms": [], "status_vocabulary": []})
    readiness = _load_optional(EVIDENCE / "federated-config-readiness.json", {
        "summary": {"repositories_scanned": 0, "configuration_names": 0, "duplicate_candidates": 0, "stale_candidates": 0},
        "configuration": [], "duplicate_candidates": [], "stale_candidates": [],
        "tracked_environment_files_for_review": [], "status": "not_generated",
    })

    live_contracts: dict[str, Any] = {}
    if live:
        for integration in integrations:
            result = _poll(integration)
            if result:
                live_contracts[integration["source_repository_id"]] = result

    cards = []
    repo_readiness = {item.get("repository_id"): item for item in readiness.get("repositories", [])}
    for repo in repositories:
        contract = live_contracts.get(repo["repository_id"])
        status = repo["module_status"]
        health = (contract or {}).get("health", {}).get("status", "not-deployed" if not repo.get("contract_endpoint") else "unknown")
        blockers = list(repo.get("blockers", []))
        blockers.extend(item.get("summary", "") for item in (contract or {}).get("blockers", []) if item.get("summary"))
        config_summary = repo_readiness.get(repo["repository_id"], {})
        cards.append({
            "repository_id": repo["repository_id"], "full_name": repo["full_name"],
            "role": repo["role"], "visibility": repo["visibility"], "status": status,
            "traffic_light": _severity(status), "health": health,
            "deployments": repo.get("deployment_ids", []), "blockers": blockers,
            "configuration_readiness": config_summary,
            "capabilities": [cap for integration in integrations if integration["source_repository_id"] == repo["repository_id"] for cap in integration.get("capabilities", [])],
        })

    known_balances = [x for x in costs if x["balance_status"] == "verified"]
    assets = _asset_snapshot()
    return {
        "command_centre_version": "1.2.0", "contract_version": CONTRACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "repositories": len(repositories), "green": sum(c["traffic_light"] == "green" for c in cards),
            "amber": sum(c["traffic_light"] == "amber" for c in cards), "red": sum(c["traffic_light"] == "red" for c in cards),
            "known_credit_balances": len(known_balances), "unknown_credit_balances": sum(x["balance_status"] == "unavailable" for x in costs),
            "open_blockers": sum(len(c["blockers"]) for c in cards),
            "repositories_config_scanned": readiness.get("summary", {}).get("repositories_scanned", 0),
            "configuration_names": readiness.get("summary", {}).get("configuration_names", 0),
            "duplicate_candidates": readiness.get("summary", {}).get("duplicate_candidates", 0),
            "stale_candidates": readiness.get("summary", {}).get("stale_candidates", 0),
            "active_asset_profiles": len(assets.get("active_assets", [])),
        },
        "repositories": cards,
        "asset_intelligence": assets,
        "integrations": integrations,
        "cost_credit_ledger": costs,
        "configuration_readiness": readiness,
        "setup_actions": setup_actions,
        "global_jarvis": {
            "state": "TEXT_POLICY_AND_CONTEXT_ROUTING_AVAILABLE_AUDIO_RUNTIME_NOT_CONNECTED",
            "available_on_every_page": True,
            "commands": ["update", "deep scan", "all intelligence", "navigate", "explain", "continue"],
            "voice_gateway": "JARVIS-VOICE-COMMAND-GATEWAY-V1",
            "stop_mute_cancel_always_available": True,
        },
        "safety": {
            "secret_values_returned": False,
            "automatic_secret_deletion": False,
            "automatic_secret_rotation": False,
            "cleanup_requires_owner_approval": True,
            "financial_execution": False,
            "voice_bypasses_approval": False,
        },
    }


def _pill(text: str, tone: str = "blue") -> str:
    return f"<span class='pill {tone}'>{html.escape(text)}</span>"


def _html(snapshot: dict[str, Any]) -> bytes:
    repo_rows = "".join(
        f"<tr><td>{_pill(r['traffic_light'], r['traffic_light'])}</td><td>{html.escape(r['full_name'])}</td><td>{html.escape(r['status'])}</td>"
        f"<td>{html.escape(r['health'])}</td><td>{html.escape(', '.join(r['deployments']) or 'none')}</td>"
        f"<td>{html.escape(str(r.get('configuration_readiness', {}).get('configuration_names', 'not scanned')))}</td>"
        f"<td>{'<br>'.join(html.escape(str(x)) for x in r['blockers']) or 'none'}</td></tr>" for r in snapshot["repositories"]
    )
    asset_cards = "".join(
        f"<article class='asset-card'><div class='asset-symbol'>{html.escape(p['asset'])}</div>"
        f"<h3>{html.escape(p['profile_id'])}</h3>"
        f"<div class='metric-grid'><span>Milestones<b>{p['milestone_count']}</b></span>"
        f"<span>Source families<b>{p['source_family_count']}</b></span>"
        f"<span>Intel layers<b>{p['intelligence_layer_count']}</b></span>"
        f"<span>Ceiling engine<b>{'ACTIVE' if p['dynamic_ceiling_enabled'] else 'OFF'}</b></span></div>"
        f"<small>{html.escape(p['knowledge_namespace'])}</small></article>"
        for p in snapshot["asset_intelligence"].get("profiles", [])
    ) or "<article class='asset-card'><h3>Asset intelligence blocked</h3><p>No profile snapshot available.</p></article>"
    summary = snapshot["summary"]
    body = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Jarvis Command Centre</title>
<style>
:root{{--bg:#040914;--panel:rgba(9,24,45,.84);--line:#1d5575;--text:#dff8ff;--muted:#8bb8ca;--cyan:#44e5ff;--blue:#409cff;--green:#57e389;--amber:#ffd166;--red:#ff6577;--grey:#78909c;--purple:#b18cff}}
*{{box-sizing:border-box}}body{{margin:0;font-family:Inter,ui-sans-serif,system-ui;background:radial-gradient(circle at 50% -20%,#10385a 0,#071525 34%,var(--bg) 68%);color:var(--text);min-height:100vh}}body:before{{content:'';position:fixed;inset:0;pointer-events:none;background-image:linear-gradient(rgba(68,229,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(68,229,255,.035) 1px,transparent 1px);background-size:40px 40px}}
.shell{{max-width:1500px;margin:auto;padding:18px;position:relative}}.top{{display:flex;gap:14px;align-items:center;justify-content:space-between;padding:14px 18px;border:1px solid var(--line);background:var(--panel);backdrop-filter:blur(18px);border-radius:18px;box-shadow:0 0 40px rgba(68,229,255,.08)}}.brand{{display:flex;align-items:center;gap:12px}}.core{{width:42px;height:42px;border-radius:50%;border:2px solid var(--cyan);box-shadow:0 0 22px var(--cyan),inset 0 0 18px var(--blue);animation:pulse 2.5s infinite}}@keyframes pulse{{50%{{transform:scale(.92);opacity:.75}}}}h1{{font-size:1.15rem;margin:0;letter-spacing:.16em}}.sub{{color:var(--muted);font-size:.78rem}}.command{{flex:1;max-width:680px;border:1px solid #34769a;border-radius:999px;padding:12px 18px;background:#06101d;color:var(--muted)}}
.stats{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:14px 0}}.stat,.panel,.asset-card{{border:1px solid var(--line);background:var(--panel);backdrop-filter:blur(14px);border-radius:16px;padding:16px;box-shadow:0 8px 28px rgba(0,0,0,.28)}}.stat b{{font-size:1.45rem;display:block;color:var(--cyan)}}.stat span{{font-size:.76rem;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}}.section-head{{display:flex;align-items:end;justify-content:space-between;margin:22px 4px 10px}}.section-head h2{{margin:0;font-size:1rem;letter-spacing:.12em;text-transform:uppercase}}.section-head small{{color:var(--muted)}}.assets{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}}.asset-card{{position:relative;overflow:hidden}}.asset-card:after{{content:'';position:absolute;right:-50px;top:-50px;width:140px;height:140px;border:1px solid rgba(68,229,255,.18);border-radius:50%}}.asset-symbol{{font-size:2rem;font-weight:800;color:var(--cyan);letter-spacing:.08em}}.asset-card h3{{font-size:.78rem;color:var(--muted);font-weight:500}}.metric-grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:14px 0}}.metric-grid span{{background:#071421;border:1px solid #193e58;border-radius:10px;padding:9px;font-size:.68rem;color:var(--muted)}}.metric-grid b{{display:block;color:var(--text);font-size:.92rem;margin-top:3px}}.asset-card small{{color:var(--purple)}}
.panel{{overflow:auto}}table{{border-collapse:collapse;width:100%;min-width:900px}}td,th{{border-bottom:1px solid #163a52;padding:.68rem;text-align:left;font-size:.78rem}}th{{color:var(--cyan);text-transform:uppercase;letter-spacing:.07em}}.pill{{display:inline-block;border:1px solid currentColor;border-radius:999px;padding:2px 8px;font-size:.65rem}}.green{{color:var(--green)}}.amber{{color:var(--amber)}}.red{{color:var(--red)}}.grey{{color:var(--grey)}}.blue{{color:var(--blue)}}.jarvis-pop{{position:fixed;right:22px;bottom:22px;width:min(390px,calc(100vw - 44px));padding:16px;border:1px solid var(--cyan);border-radius:18px;background:rgba(3,13,25,.94);box-shadow:0 0 36px rgba(68,229,255,.2);z-index:2}}.jarvis-pop strong{{color:var(--cyan)}}.jarvis-pop p{{margin:.5rem 0;color:var(--muted);font-size:.82rem}}.chips{{display:flex;gap:6px;flex-wrap:wrap}}.chips span{{font-size:.68rem;padding:5px 8px;border:1px solid #285773;border-radius:999px}}@media(max-width:800px){{.stats{{grid-template-columns:1fr 1fr}}.top{{align-items:flex-start;flex-wrap:wrap}}.command{{order:3;min-width:100%}}.jarvis-pop{{position:static;width:auto;margin-top:16px}}}}
@media(prefers-reduced-motion:reduce){{*{{animation:none!important;scroll-behavior:auto!important}}}}
</style></head><body><main class='shell'>
<header class='top'><div class='brand'><div class='core' aria-label='Jarvis active core'></div><div><h1>JARVIS COMMAND CENTRE</h1><div class='sub'>Unified governance · intelligence · evidence · action control</div></div></div><div class='command'>⌕ Ask Jarvis, navigate, update, deep scan, compare, explain or continue…</div>{_pill('TEXT ACTIVE · VOICE RUNTIME PENDING','blue')}</header>
<section class='stats'><div class='stat'><b>{summary['repositories']}</b><span>Repositories</span></div><div class='stat'><b>{summary['active_asset_profiles']}</b><span>Asset profiles</span></div><div class='stat'><b>{summary['open_blockers']}</b><span>Open blockers</span></div><div class='stat'><b>{snapshot['asset_intelligence'].get('apex_sources_per_asset_maximum',0)}</b><span>Sources / asset / apex</span></div><div class='stat'><b>{summary['configuration_names']}</b><span>Config names</span></div></section>
<div class='section-head'><h2>Asset Intelligence HUD</h2><small>Separate profiles · shared orchestration · dynamic ceilings</small></div><section class='assets'>{asset_cards}</section>
<div class='section-head'><h2>System Federation</h2><small>Repository truth is separate from live runtime truth</small></div><section class='panel'><table><thead><tr><th>Light</th><th>Repository</th><th>Module</th><th>Health</th><th>Deployments</th><th>Config</th><th>Blockers</th></tr></thead><tbody>{repo_rows}</tbody></table></section>
<section class='jarvis-pop'><strong>JARVIS · CONTEXT GUIDE</strong><p>I can explain this page, open any authorised module, plan an update or deep scan, show evidence, identify the next blocker and resume from the last verified step.</p><div class='chips'><span>Update all assets</span><span>Deep scan XRP + HBAR</span><span>Show evidence</span><span>Continue next task</span><span>Stop / mute</span></div></section>
</main></body></html>"""
    return body.encode("utf-8")


def serve(host: str, port: int, live: bool) -> None:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            snapshot = build_snapshot(live=live)
            if self.path == "/api/v1/command-centre":
                content, media = json.dumps(snapshot, indent=2).encode(), "application/json"
            elif self.path == "/api/v1/configuration-readiness":
                content, media = json.dumps(snapshot["configuration_readiness"], indent=2).encode(), "application/json"
            elif self.path == "/api/v1/setup-actions":
                content, media = json.dumps(snapshot["setup_actions"], indent=2).encode(), "application/json"
            elif self.path == "/api/v1/asset-intelligence":
                content, media = json.dumps(snapshot["asset_intelligence"], indent=2).encode(), "application/json"
            elif self.path == "/health":
                content, media = b'{"status":"ok","version":"1.2.0"}', "application/json"
            else:
                content, media = _html(snapshot), "text/html; charset=utf-8"
            self.send_response(200)
            self.send_header("Content-Type", media)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def log_message(self, *_: Any) -> None:
            return

    ThreadingHTTPServer((host, port), Handler).serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Jarvis unified command centre")
    parser.add_argument("--live", action="store_true", help="poll configured read-only federation endpoints")
    parser.add_argument("--serve", action="store_true", help="serve cinematic HTML and JSON APIs")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.serve:
        serve(args.host, args.port, args.live)
        return
    rendered = json.dumps(build_snapshot(live=args.live), indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
