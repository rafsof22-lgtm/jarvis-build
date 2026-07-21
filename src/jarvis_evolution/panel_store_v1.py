"""SQLite persistence for governed Jarvis multi-model panel runs."""
from __future__ import annotations
import hashlib, json, re, sqlite3, time, uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from jarvis_model_router.selector import ModelResponseRecord, ParallelPanelPlan, build_synthesis_packet, verify_consolidated_response

RUN_STATES={"PLANNED","PREFLIGHT_BLOCKED","APPROVED","RUNNING","RESPONSES_CAPTURED","SYNTHESIZED","VERIFIED","FAILED","CANCELLED"}
SCHEMA="""
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS panel_runs(run_id TEXT PRIMARY KEY,panel_id TEXT NOT NULL,task_type TEXT NOT NULL,prompt_sha256 TEXT NOT NULL,prompt_redacted TEXT NOT NULL,state TEXT NOT NULL,high_risk INTEGER NOT NULL,policy_json TEXT NOT NULL,created_at INTEGER NOT NULL,updated_at INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS panel_models(run_id TEXT NOT NULL REFERENCES panel_runs(run_id),selector_id TEXT NOT NULL,role TEXT NOT NULL,model_json TEXT NOT NULL,PRIMARY KEY(run_id,selector_id));
CREATE TABLE IF NOT EXISTS panel_preflights(run_id TEXT NOT NULL REFERENCES panel_runs(run_id),selector_id TEXT NOT NULL,decision_json TEXT NOT NULL,created_at INTEGER NOT NULL,PRIMARY KEY(run_id,selector_id));
CREATE TABLE IF NOT EXISTS panel_responses(run_id TEXT NOT NULL REFERENCES panel_runs(run_id),selector_id TEXT NOT NULL,role TEXT NOT NULL,raw_text TEXT NOT NULL,response_sha256 TEXT NOT NULL,citations_json TEXT NOT NULL,claim_ids_json TEXT NOT NULL,created_at INTEGER NOT NULL,PRIMARY KEY(run_id,selector_id));
CREATE TABLE IF NOT EXISTS panel_syntheses(run_id TEXT PRIMARY KEY REFERENCES panel_runs(run_id),packet_json TEXT NOT NULL,consolidated_json TEXT NOT NULL,verification_json TEXT NOT NULL,created_at INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS panel_events(event_id TEXT PRIMARY KEY,run_id TEXT NOT NULL REFERENCES panel_runs(run_id),event_type TEXT NOT NULL,outcome TEXT NOT NULL,payload_json TEXT NOT NULL,created_at INTEGER NOT NULL);
"""
SECRET_PATTERNS=(re.compile(r"(?i)(password|secret|token|api[_ -]?key)\s*[:=]\s*\S+"),re.compile(r"\b(?:sk|key)-[A-Za-z0-9_-]{12,}\b"),re.compile(r"\b\d{6}\b"))

def digest(text:str)->str:return hashlib.sha256(text.encode()).hexdigest()
def canonical(value:Any)->str:return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def redact(text:str)->tuple[str,bool]:
    out=text
    for pattern in SECRET_PATTERNS:out=pattern.sub("[REDACTED]",out)
    return out,out!=text

class PanelRunStore:
    def __init__(self,path:str|Path=":memory:") -> None:
        self.path=str(path); self.db=sqlite3.connect(self.path); self.db.row_factory=sqlite3.Row; self.db.executescript(SCHEMA)
    def close(self)->None:self.db.close()
    def _event(self,run_id:str,event_type:str,outcome:str,payload:Mapping[str,Any]|None=None)->None:
        with self.db:self.db.execute("INSERT INTO panel_events VALUES(?,?,?,?,?,?)",(f"evt-{uuid.uuid4().hex}",run_id,event_type,outcome,canonical(payload or {}),int(time.time())))
    def create_run(self,plan:ParallelPanelPlan,prompt:str,policy:Mapping[str,Any])->str:
        safe,_=redact(prompt); now=int(time.time()); run_id=f"run-{uuid.uuid4().hex}"
        with self.db:
            self.db.execute("INSERT INTO panel_runs VALUES(?,?,?,?,?,?,?,?,?,?)",(run_id,plan.panel_id,plan.task_type,plan.prompt_sha256,safe,"PLANNED",int(bool(plan.synthesis_contract.get('human_or_qualified_review_required'))),canonical(policy),now,now))
            for model,role in zip(plan.selected_models,plan.roles):self.db.execute("INSERT INTO panel_models VALUES(?,?,?,?)",(run_id,model.selector_id,role,canonical(asdict(model))))
        self._event(run_id,"run_created","PLANNED",{"models":len(plan.selected_models),"prompt_redacted":safe!=prompt}); return run_id
    def set_state(self,run_id:str,state:str,*,reason:str="")->None:
        if state not in RUN_STATES:raise ValueError("invalid panel state")
        if self.db.execute("SELECT 1 FROM panel_runs WHERE run_id=?",(run_id,)).fetchone() is None:raise KeyError(run_id)
        with self.db:self.db.execute("UPDATE panel_runs SET state=?,updated_at=? WHERE run_id=?",(state,int(time.time()),run_id))
        self._event(run_id,"state_change",state,{"reason":reason})
    def record_preflights(self,run_id:str,decisions:Sequence[Mapping[str,Any]])->None:
        with self.db:
            for decision in decisions:self.db.execute("INSERT OR REPLACE INTO panel_preflights VALUES(?,?,?,?)",(run_id,str(decision['selector_id']),canonical(decision),int(time.time())))
        blocked=any(not bool(decision.get('allowed')) for decision in decisions); self.set_state(run_id,"PREFLIGHT_BLOCKED" if blocked else "APPROVED")
    def record_response(self,run_id:str,response:ModelResponseRecord)->str:
        expected=self.db.execute("SELECT role FROM panel_models WHERE run_id=? AND selector_id=?",(run_id,response.selector_id)).fetchone()
        if expected is None:raise ValueError("unexpected model response")
        safe,_=redact(response.raw_text); sha=digest(safe)
        try:
            with self.db:self.db.execute("INSERT INTO panel_responses VALUES(?,?,?,?,?,?,?,?)",(run_id,response.selector_id,response.role,safe,sha,canonical(response.citations),canonical(response.claim_ids),int(time.time())))
        except sqlite3.IntegrityError as exc:raise ValueError("duplicate model response") from exc
        self._event(run_id,"response_captured","SUCCEEDED",{"selector_id":response.selector_id,"proof_ref":f"{response.selector_id}:{sha}"}); return sha
    def capture_results(self,run_id:str,results:Sequence[Mapping[str,Any]])->None:
        failed=[]
        for result in results:
            if result.get('state')!='SUCCEEDED':failed.append(result.get('selector_id'));continue
            self.record_response(run_id,ModelResponseRecord(str(result['selector_id']),str(result['role']),str(result['raw_text']),tuple(result.get('citations',())),tuple(result.get('claim_ids',()))))
        self.set_state(run_id,"FAILED" if failed else "RESPONSES_CAPTURED",reason=",".join(str(item) for item in failed))
    def responses(self,run_id:str)->list[ModelResponseRecord]:
        rows=self.db.execute("SELECT * FROM panel_responses WHERE run_id=? ORDER BY created_at,selector_id",(run_id,)).fetchall()
        return [ModelResponseRecord(row['selector_id'],row['role'],row['raw_text'],tuple(json.loads(row['citations_json'])),tuple(json.loads(row['claim_ids_json']))) for row in rows]
    def persist_synthesis(self,run_id:str,plan:ParallelPanelPlan,consolidated:Mapping[str,Any],*,required_sections:Sequence[str]=())->dict[str,Any]:
        packet=build_synthesis_packet(plan,self.responses(run_id),required_sections=required_sections); verification=verify_consolidated_response(packet,consolidated)
        with self.db:self.db.execute("INSERT OR REPLACE INTO panel_syntheses VALUES(?,?,?,?,?)",(run_id,canonical(packet),canonical(consolidated),canonical(verification),int(time.time())))
        self.set_state(run_id,"VERIFIED" if verification['passed'] else "SYNTHESIZED"); return verification
    def get_run(self,run_id:str)->dict[str,Any]:
        row=self.db.execute("SELECT * FROM panel_runs WHERE run_id=?",(run_id,)).fetchone()
        if row is None:raise KeyError(run_id)
        result=dict(row); result['policy']=json.loads(result.pop('policy_json'))
        result['models']=[{**dict(item),"model":json.loads(item['model_json'])} for item in self.db.execute("SELECT * FROM panel_models WHERE run_id=? ORDER BY selector_id",(run_id,))]
        result['preflights']=[json.loads(item['decision_json']) for item in self.db.execute("SELECT decision_json FROM panel_preflights WHERE run_id=? ORDER BY selector_id",(run_id,))]
        result['response_refs']=[f"{item['selector_id']}:{item['response_sha256']}" for item in self.db.execute("SELECT selector_id,response_sha256 FROM panel_responses WHERE run_id=? ORDER BY selector_id",(run_id,))]
        synthesis=self.db.execute("SELECT * FROM panel_syntheses WHERE run_id=?",(run_id,)).fetchone(); result['synthesis']=None if synthesis is None else {"packet":json.loads(synthesis['packet_json']),"consolidated":json.loads(synthesis['consolidated_json']),"verification":json.loads(synthesis['verification_json'])}
        result['events']=[{**dict(item),"payload":json.loads(item['payload_json'])} for item in self.db.execute("SELECT * FROM panel_events WHERE run_id=? ORDER BY created_at,event_id",(run_id,))]
        return result
    def metrics(self)->dict[str,Any]:
        total=self.db.execute("SELECT count(*) FROM panel_runs").fetchone()[0]
        states={row[0]:row[1] for row in self.db.execute("SELECT state,count(*) FROM panel_runs GROUP BY state")}
        responses=self.db.execute("SELECT count(*) FROM panel_responses").fetchone()[0]
        return {"panel_runs":total,"verified_runs":states.get('VERIFIED',0),"responses_captured":responses,"states":states,"persistence":"sqlite","secret_values_exposed":False}
