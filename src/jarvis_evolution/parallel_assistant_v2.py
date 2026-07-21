from __future__ import annotations
from dataclasses import asdict
from typing import Any, Mapping, Sequence

from jarvis_model_router.provider_execution import ExecutionPolicy, ProviderExecutor
from jarvis_model_router.selector import ModelCatalogue, ModelResponseRecord, build_synthesis_packet, plan_parallel_panel, selector_surface_contract, verify_consolidated_response
from .panel_store_v1 import PanelRunStore

class ParallelJarvisAssistantV2:
    """Concrete model selector, governed execution and durable panel evidence."""
    def __init__(self,catalogue:ModelCatalogue,*,store:PanelRunStore|None=None,executor:ProviderExecutor|None=None)->None:
        self.catalogue=catalogue; self.store=store or PanelRunStore(); self.executor=executor
    def popup_payload(self,*,active_object:Mapping[str,Any]|None=None)->dict[str,Any]:
        return {"component":"JARVIS_POP_UNIFIED_ASSISTANT_V2","universal_model_selector":selector_surface_contract(self.catalogue),"active_object":dict(active_object or {}),"panel_metrics":self.store.metrics(),"controls":{"parallel_thinking":"ENABLED" if self.catalogue.parallel_enabled else "BLOCKED_NEEDS_TWO_CONNECTED_MODELS","parallel_model_limit":8,"view_each_raw_response":"ENABLED","view_consolidated_response":"ENABLED_AFTER_PANEL_CAPTURE","claim_matrix":"REQUIRED","contradiction_register":"REQUIRED","omission_register":"REQUIRED","cancel":"ENABLED","provider_execution":"POLICY_BUDGET_PRIVACY_GATED","production":"DISABLED_UNTIL_RELEASE_GATE"},"truth_boundary":"Voice and text use the same policy; no control bypasses owner, budget, privacy or release gates."}
    def create_panel(self,prompt:str,task_type:str,*,policy:ExecutionPolicy,selected_ids:Sequence[str]|None=None,panel_size:int=8,high_risk_domain:bool=False)->dict[str,Any]:
        plan=plan_parallel_panel(prompt,task_type,self.catalogue,selected_ids=selected_ids,panel_size=panel_size,high_risk_domain=high_risk_domain)
        run_id=self.store.create_run(plan,prompt,asdict(policy))
        return {"run_id":run_id,"plan":plan,"provider_calls_executed":False}
    def execute_panel(self,run_id:str,plan:Any,prompt:str,policy:ExecutionPolicy,*,system_prompt:str="")->dict[str,Any]:
        if self.executor is None:raise RuntimeError("provider executor not configured")
        outcome=self.executor.execute_panel(plan,prompt,policy,system_prompt=system_prompt)
        self.store.record_preflights(run_id,outcome.get("preflights",[]))
        if outcome.get("results"):
            self.store.set_state(run_id,"RUNNING")
            self.store.capture_results(run_id,outcome["results"])
        return outcome
    def persist_manual_responses(self,run_id:str,responses:Sequence[ModelResponseRecord])->None:
        for response in responses:self.store.record_response(run_id,response)
        self.store.set_state(run_id,"RESPONSES_CAPTURED")
    def synthesize(self,run_id:str,plan:Any,consolidated:Mapping[str,Any],*,required_sections:Sequence[str]=())->dict[str,Any]:
        return self.store.persist_synthesis(run_id,plan,consolidated,required_sections=required_sections)
    @staticmethod
    def synthesis_packet(plan:Any,responses:Sequence[ModelResponseRecord],*,required_sections:Sequence[str]=())->dict[str,Any]:return build_synthesis_packet(plan,responses,required_sections=required_sections)
    @staticmethod
    def verify_synthesis(packet:Mapping[str,Any],consolidated:Mapping[str,Any])->dict[str,Any]:return verify_consolidated_response(packet,consolidated)
