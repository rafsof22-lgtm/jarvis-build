from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def require(ok:bool,msg:str)->None:
    if not ok:raise SystemExit(msg)
def main()->None:
    provider=(ROOT/'jarvis_model_router/provider_execution.py').read_text()
    store=(ROOT/'src/jarvis_evolution/panel_store_v1.py').read_text()
    command=(ROOT/'jarvis_command_centre/integrated_v13.py').read_text()
    runtime=json.loads((ROOT/'registry/model-routing/provider_execution_and_panel_persistence_v1.json').read_text())
    ux=json.loads((ROOT/'registry/ux/universal_model_selector_surface_integration_v1.json').read_text())
    tracker=json.loads((ROOT/'registry/trackers/all_progress_tracker_reconciliation_v3.json').read_text())
    passes=json.loads((ROOT/'registry/jarvis_completion_pass_registry_v2.json').read_text())
    plan=json.loads((ROOT/'registry/full_completion_priority_plan_v1.json').read_text())
    require('execution_enabled: bool = False' in provider,'execution must default off')
    require('restricted' in provider and 'RESTRICTED_DATA_LOCAL_ONLY' in provider,'privacy gate missing')
    require('maximum_parallel_calls' in provider and 'ThreadPoolExecutor' in provider,'bounded panel execution missing')
    require('panel_responses' in store and 'panel_syntheses' in store and 'panel_events' in store,'panel evidence tables missing')
    require('response_sha256' in store and 'duplicate model response' in store,'provenance/immutability missing')
    require('command_centre_version"] = "1.3.0"' in command,'Command Centre v1.3 missing')
    for route in ('/api/v1/model-control','/api/v1/editor-surfaces','/api/v1/progress-tracker'):require(route in command,f'{route} missing')
    require(runtime['live_provider_state']=='BLOCKED','live provider truth gate missing')
    require(runtime['execution_defaults']['enabled'] is False,'registry execution default unsafe')
    require(len(ux['surfaces'])==13,'all selector surfaces not registered')
    require(tracker['program_state']=='ACTIVE_PROGRAM_NOT_100_PERCENT','tracker false completion')
    require(plan['state']=='ACTIVE_PROGRAM_NOT_100_PERCENT','priority plan false completion')
    require(passes['state']=='ACTIVE_PROGRAM_NOT_100_PERCENT','pass registry false completion')
    require(any(item['task_id']=='P1-5' and item['state']=='INTEGRATED_STAGING' for item in plan['tasks']),'P1-5 not reconciled')
    print(json.dumps({'status':'DONE_VERIFIED','scope':'LOCAL_PROVIDER_ADAPTER_PANEL_PERSISTENCE_COMMAND_CENTRE_V1_3','universal_100_percent':False},indent=2))
if __name__=='__main__':main()
