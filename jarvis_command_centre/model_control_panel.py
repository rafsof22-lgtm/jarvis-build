from __future__ import annotations
import argparse, html, json, os
from pathlib import Path
from typing import Any
from jarvis_model_router import ExecutionPolicy, RouterConfig, build_model_catalogue
from src.jarvis_evolution.panel_store_v1 import PanelRunStore
from src.jarvis_evolution.surface_controls_v1 import build_all_surface_payloads

def _metrics(path:str|Path|None)->dict[str,Any]:
    if not path or not Path(path).exists():return {"panel_runs":0,"verified_runs":0,"responses_captured":0,"states":{},"persistence":"sqlite","secret_values_exposed":False}
    store=PanelRunStore(path)
    try:return store.metrics()
    finally:store.close()

def build_model_control_snapshot(config:RouterConfig|None=None,*,panel_db_path:str|Path|None=None)->dict[str,Any]:
    active=config or RouterConfig.from_env(); catalogue=build_model_catalogue(active); metrics=_metrics(panel_db_path or os.getenv("JARVIS_PANEL_DB"))
    surfaces=build_all_surface_payloads(catalogue,metrics=metrics)
    default_policy=ExecutionPolicy()
    return {"component":"JARVIS_COMMAND_CENTRE_MODEL_CONTROL_V2","status":"INTEGRATED_STAGING","connected_model_count":len(catalogue.models),"routes_without_model_inventory":list(catalogue.routes_without_model_inventory),"selector_options":catalogue.selector_options(),"parallel_button_state":"ENABLED" if catalogue.parallel_enabled else "BLOCKED_NEEDS_TWO_CONNECTED_MODELS","panel_metrics":metrics,"shared_surfaces":surfaces,"execution_readiness":{"execution_enabled":default_policy.execution_enabled,"cloud_enabled":active.allow_cloud,"cost_preflight_required":True,"privacy_preflight_required":True,"credential_references_only":True,"live_provider_calls_executed_by_snapshot":False},"safety":{"secret_values_exposed":False,"high_risk_qualified_review_required":True,"universal_zero_error_claim_allowed":False,"money_movement":False,"live_trading":False},"truth_boundary":"Local selector, surfaces and persistence are integrated. Provider calls require explicit policy, credentials, endpoints and budget evidence."}

def render_model_control_html(snapshot:dict[str,Any])->str:
    opts="".join(f"<option value='{html.escape(item['selector_id'])}'>{html.escape(item['provider'])} · {html.escape(item['model_id'])}</option>" for item in snapshot['selector_options']) or "<option disabled>No concrete model inventory</option>"
    disabled="" if snapshot['parallel_button_state']=="ENABLED" else " disabled"
    return f"""<section class='model-control'><h2>Model Intelligence</h2><p>Select 2–8 connected models. Raw responses are stored before synthesis.</p><select id='models' multiple size='8'>{opts}</select><button id='parallel-thinking'{disabled}>Parallel Thinking · Up to 8 LLMs</button><div class='model-meta'>Models: {snapshot['connected_model_count']} · Runs: {snapshot['panel_metrics']['panel_runs']} · Verified: {snapshot['panel_metrics']['verified_runs']} · State: {html.escape(snapshot['parallel_button_state'])}</div></section>"""

def main()->None:
    parser=argparse.ArgumentParser();parser.add_argument("--html",action="store_true");parser.add_argument("--output",type=Path);parser.add_argument("--panel-db",type=Path);args=parser.parse_args();snapshot=build_model_control_snapshot(panel_db_path=args.panel_db);text=render_model_control_html(snapshot) if args.html else json.dumps(snapshot,indent=2)
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text+"\n")
    else:print(text)
if __name__=="__main__":main()
