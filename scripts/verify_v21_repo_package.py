#!/usr/bin/env python3
from pathlib import Path
import csv,json,re
ROOT=Path(__file__).resolve().parents[1]
required=['CONSTITUTION.md','JARVIS_BUILD_MAMMOTH_CONSOLIDATED_SPEC.md','JARVIS_AUTONOMOUS_META_EXECUTION_PROGRESS_TRACKER.md','JARVIS_SOVEREIGN_REQUEST_CAPTURE_BUILD_COMPILER.md','JARVIS_SOVEREIGN_OMNI_META_ROLE_COUNCIL_EXECUTION_PROTOCOL.md','JARVIS_100_PERCENT_COMPLETION_EXECUTION_PLAN.md','JARVIS_V21_PR_BODY.md','specs/JARVIS_MASTER_SPEC.md','specs/JARVIS_FORENSIC_TASK_MAP.md','registers/REQUIREMENTS_REGISTER.csv','registers/FEATURE_REGISTRY.csv','registers/FUNCTION_REGISTRY.csv','registers/SKILL_REGISTRY.csv','registers/TOOL_REGISTRY.csv','registers/API_REGISTRY.csv','registers/MODEL_REGISTRY.csv','registers/WORKFLOW_REGISTRY.csv','registers/SOP_REGISTRY.csv','registers/OJT_REGISTRY.csv','registers/APPROVAL_LEDGER.csv','registers/GAP_REGISTER.csv','registers/EVIDENCE_REGISTER.csv','registers/DEPLOYMENT_LEDGER.csv','rollback/ROLLBACK_RUNBOOK.md','continuity/RESUME_PROMPT.md','manifests/JARVIS_V21_COMPLETION_STATE.json','scripts/search_index.py','tests/test_search_index.py']
missing=[p for p in required if not (ROOT/p).exists()]
if missing: raise SystemExit('missing:'+','.join(missing))
state=json.loads((ROOT/'manifests/JARVIS_V21_COMPLETION_STATE.json').read_text()); assert state['extraction']['requests_mapped']==state['source_counts']['candidate_user_messages']
for name in ['REQUIREMENTS_REGISTER.csv','FEATURE_REGISTRY.csv','FUNCTION_REGISTRY.csv','SKILL_REGISTRY.csv']:
    with (ROOT/'registers'/name).open(newline='',encoding='utf-8') as f: assert list(csv.DictReader(f)),name
text='\n'.join(p.read_text(errors='ignore') for p in ROOT.rglob('*.md'))
for phrase in ['Original Jarvis Framework','Jarvis Build','CONTROL_OVERLAY','Owner Acceptance']: assert phrase in text,phrase
bad=[]
for p in ROOT.rglob('*'):
    if p.is_file() and p.suffix.lower() in {'.md','.csv','.json','.py','.txt'} and re.search(r'(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*[A-Za-z0-9_\-]{16,}',p.read_text(errors='ignore')): bad.append(str(p))
assert not bad,bad
print('V21_REPO_PACKAGE_VALIDATION_PASS')
