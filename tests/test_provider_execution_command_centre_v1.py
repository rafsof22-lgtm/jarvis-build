from __future__ import annotations
import json, os, tempfile, unittest
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

from jarvis_model_router import ExecutionPolicy, ProviderCallRequest, ProviderExecutor, RouterConfig, build_model_catalogue, plan_parallel_panel
from jarvis_model_router.config import ModelRoute
from jarvis_model_router.selector import ModelResponseRecord
from src.jarvis_evolution import PanelRunStore, ParallelJarvisAssistantV2, build_all_surface_payloads

class FakeTransport:
    def __init__(self):self.calls=[]
    def send(self,url,headers,payload,timeout):
        self.calls.append((url,headers,payload,timeout))
        if "/api/chat" in url:return {"message":{"content":"ollama answer"}}
        return {"choices":[{"message":{"content":f"answer from {payload['model']}"}}]}

def config(*,cloud=False):
    routes=(ModelRoute("local","ollama","OLLAMA_BASE_URL",None,"OLLAMA_DEFAULT_MODEL",True,"owned_compute","local_private"),ModelRoute("openai","openai","OPENAI_BASE_URL","OPENAI_API_KEY","OPENAI_DEFAULT_MODEL",False,"premium"))
    return RouterConfig("test","local",cloud,routes)

def catalogue_local():return build_model_catalogue(config(),environ={"OLLAMA_DEFAULT_MODEL":"llama-a","JARVIS_LOCAL_MODELS":"llama-a,llama-b"})

class ProviderExecutionTests(unittest.TestCase):
    def test_catalogue_has_two_concrete_models(self):self.assertEqual(len(catalogue_local().models),2)
    def test_execution_disabled_by_default(self):
        cat=catalogue_local();ex=ProviderExecutor(config(),cat,environ={"OLLAMA_DEFAULT_MODEL":"llama-a","JARVIS_LOCAL_MODELS":"llama-a,llama-b"},transport=FakeTransport());decision=ex.preflight(ProviderCallRequest(cat.models[0].selector_id,"primary","hello"),ExecutionPolicy());self.assertFalse(decision.allowed);self.assertIn("EXECUTION_NOT_EXPLICITLY_ENABLED",decision.reasons)
    def test_local_execution_with_explicit_policy(self):
        env={"OLLAMA_DEFAULT_MODEL":"llama-a","JARVIS_LOCAL_MODELS":"llama-a,llama-b","OLLAMA_BASE_URL":"http://ollama"};cat=build_model_catalogue(config(),environ=env);transport=FakeTransport();executor=ProviderExecutor(config(),cat,environ=env,transport=transport);decision,result=executor.execute(ProviderCallRequest(cat.models[0].selector_id,"primary","hello"),ExecutionPolicy(execution_enabled=True));self.assertTrue(decision.allowed);self.assertEqual(result.state,"SUCCEEDED");self.assertEqual(result.raw_text,"ollama answer");self.assertEqual(len(transport.calls),1)
    def test_restricted_cloud_blocked(self):
        env={"OPENAI_API_KEY":"x","OPENAI_DEFAULT_MODEL":"gpt-test","OPENAI_BASE_URL":"http://openai"}
        with patch.dict(os.environ,env,clear=False):cat=build_model_catalogue(config(cloud=True),environ=env);executor=ProviderExecutor(config(cloud=True),cat,environ=env,transport=FakeTransport());selector=next(model.selector_id for model in cat.models if model.route_name=="openai")
        decision=executor.preflight(ProviderCallRequest(selector,"primary","secret"),ExecutionPolicy(execution_enabled=True,data_classification="restricted",allow_unknown_cost=True));self.assertFalse(decision.allowed);self.assertIn("RESTRICTED_DATA_LOCAL_ONLY",decision.reasons)
    def test_unknown_cloud_cost_blocked(self):
        env={"OPENAI_API_KEY":"x","OPENAI_DEFAULT_MODEL":"gpt-test","OPENAI_BASE_URL":"http://openai"}
        with patch.dict(os.environ,env,clear=False):cat=build_model_catalogue(config(cloud=True),environ=env);executor=ProviderExecutor(config(cloud=True),cat,environ=env);selector=next(model.selector_id for model in cat.models if model.route_name=="openai")
        decision=executor.preflight(ProviderCallRequest(selector,"primary","hello"),ExecutionPolicy(execution_enabled=True,maximum_total_cost_usd=1));self.assertIn("COST_UNKNOWN",decision.reasons)
    def test_panel_runs_two_models_and_preserves_results(self):
        env={"OLLAMA_DEFAULT_MODEL":"a","JARVIS_LOCAL_MODELS":"a,b","OLLAMA_BASE_URL":"http://ollama"};cat=build_model_catalogue(config(),environ=env);plan=plan_parallel_panel("hello","general",cat,panel_size=2);executor=ProviderExecutor(config(),cat,environ=env,transport=FakeTransport());outcome=executor.execute_panel(plan,"hello",ExecutionPolicy(execution_enabled=True));self.assertEqual(outcome["state"],"RESPONSES_CAPTURED");self.assertEqual(len(outcome["results"]),2);self.assertFalse(outcome["secret_values_exposed"])

class StoreAndSurfaceTests(unittest.TestCase):
    def setUp(self):self.cat=catalogue_local();self.plan=plan_parallel_panel("prompt api_key=abc123","general",self.cat,panel_size=2);self.store=PanelRunStore()
    def tearDown(self):self.store.close()
    def test_store_redacts_prompt(self):
        run=self.store.create_run(self.plan,"prompt api_key=abc123",asdict(ExecutionPolicy()));self.assertIn("[REDACTED]",self.store.get_run(run)["prompt_redacted"])
    def test_response_is_immutable_per_model(self):
        run=self.store.create_run(self.plan,"prompt",{});response=ModelResponseRecord(self.cat.models[0].selector_id,"primary_reasoner","answer");self.store.record_response(run,response)
        with self.assertRaises(ValueError):self.store.record_response(run,response)
    def test_store_verifies_complete_synthesis(self):
        run=self.store.create_run(self.plan,"prompt",{})
        for model,role in zip(self.plan.selected_models,self.plan.roles):self.store.record_response(run,ModelResponseRecord(model.selector_id,role,f"answer {model.model_id}"))
        self.store.set_state(run,"RESPONSES_CAPTURED");refs=self.store.get_run(run)["response_refs"];result=self.store.persist_synthesis(run,self.plan,{"included_response_refs":refs,"present_sections":["outcome"],"unresolved_conflicts":[]},required_sections=["outcome"]);self.assertTrue(result["passed"]);self.assertEqual(self.store.get_run(run)["state"],"VERIFIED")
    def test_missing_response_fails_synthesis(self):
        run=self.store.create_run(self.plan,"prompt",{});model=self.plan.selected_models[0];self.store.record_response(run,ModelResponseRecord(model.selector_id,self.plan.roles[0],"one"));self.store.set_state(run,"RESPONSES_CAPTURED");result=self.store.persist_synthesis(run,self.plan,{"included_response_refs":self.store.get_run(run)["response_refs"],"present_sections":[]});self.assertFalse(result["passed"])
    def test_all_selector_surfaces_propagated(self):
        payloads=build_all_surface_payloads(self.cat,metrics={"panel_runs":1});self.assertEqual(len(payloads),13);self.assertIn("workflow_builder",payloads);self.assertEqual(payloads["agent_editor"]["state"],"INTEGRATED_STAGING")
    def test_popup_reports_persistence_and_gates(self):
        payload=ParallelJarvisAssistantV2(self.cat,store=self.store).popup_payload();self.assertEqual(payload["component"],"JARVIS_POP_UNIFIED_ASSISTANT_V2");self.assertEqual(payload["controls"]["provider_execution"],"POLICY_BUDGET_PRIVACY_GATED")

class CommandCentreTests(unittest.TestCase):
    def _registry(self,root:Path):
        registry=root/"registry";evidence=root/"evidence";(registry/"trackers").mkdir(parents=True);evidence.mkdir();(registry/"repositories.json").write_text(json.dumps({"repositories":[]}));(registry/"integrations.json").write_text(json.dumps({"integrations":[]}));(registry/"cost-credit-ledger.json").write_text(json.dumps({"accounts":[]}));(registry/"trackers"/"all_progress_tracker_reconciliation_v3.json").write_text(json.dumps({"tracker_id":"v3","program_state":"ACTIVE_PROGRAM_NOT_100_PERCENT"}));return registry,evidence
    def test_command_centre_integrates_model_control(self):
        import jarvis_command_centre.integrated_v13 as command
        import jarvis_command_centre.command_centre as legacy
        with tempfile.TemporaryDirectory() as directory:
            registry,evidence=self._registry(Path(directory))
            with patch.object(legacy,"REGISTRY",registry),patch.object(legacy,"EVIDENCE",evidence),patch.dict(os.environ,{"OLLAMA_DEFAULT_MODEL":"a","JARVIS_LOCAL_MODELS":"a,b"},clear=False):snapshot=command.build_snapshot();self.assertEqual(snapshot["command_centre_version"],"1.3.0");self.assertEqual(snapshot["summary"]["connected_models"],2);self.assertIn("model_control",snapshot);self.assertIn("selector_surface_state",snapshot)
    def test_snapshot_never_executes_provider(self):
        from jarvis_command_centre.model_control_panel import build_model_control_snapshot
        with patch.dict(os.environ,{"OLLAMA_DEFAULT_MODEL":"a","JARVIS_LOCAL_MODELS":"a,b"},clear=False):self.assertFalse(build_model_control_snapshot()["execution_readiness"]["live_provider_calls_executed_by_snapshot"])
    def test_html_contains_parallel_button(self):
        from jarvis_command_centre.model_control_panel import build_model_control_snapshot,render_model_control_html
        with patch.dict(os.environ,{"OLLAMA_DEFAULT_MODEL":"a","JARVIS_LOCAL_MODELS":"a,b"},clear=False):self.assertIn("Parallel Thinking",render_model_control_html(build_model_control_snapshot()))
    def test_no_false_universal_completion_claim(self):
        from jarvis_command_centre.model_control_panel import build_model_control_snapshot
        with patch.dict(os.environ,{"OLLAMA_DEFAULT_MODEL":"a","JARVIS_LOCAL_MODELS":"a,b"},clear=False):self.assertFalse(build_model_control_snapshot()["safety"]["universal_zero_error_claim_allowed"])

if __name__=="__main__":unittest.main()
