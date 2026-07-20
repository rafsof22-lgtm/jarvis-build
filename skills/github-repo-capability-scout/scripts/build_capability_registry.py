#!/usr/bin/env python3
"""Build normalized capability, candidate and approval registries."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path

def load(path: Path):
    data=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data,list):
        raise ValueError('input must be a JSON list')
    return data

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('input',type=Path)
    ap.add_argument('--out-dir',type=Path,required=True)
    args=ap.parse_args()
    rows=load(args.input)
    args.out_dir.mkdir(parents=True,exist_ok=True)
    candidates=[]
    capabilities={}
    approvals=[]
    for idx,row in enumerate(rows,1):
        cid=row.get('candidate_id') or f'CAND-{idx:04d}'
        decision=row.get('decision','HOLD')
        candidate={'candidate_id':cid,'name':row.get('name'),'canonical_url':row.get('canonical_url'),'reviewed_revision':row.get('reviewed_revision'),'licence':row.get('licence','UNVERIFIED'),'security_state':row.get('security_state','NOT_SCANNED'),'maintenance_state':row.get('maintenance_state','UNVERIFIED'),'cost_state':row.get('cost_state','UNVERIFIED'),'duplicate_of':row.get('duplicate_of'),'jarvis_placement':row.get('jarvis_placement'),'decision':decision,'evidence_refs':row.get('evidence_refs',[])}
        candidates.append(candidate)
        for cap in row.get('capabilities',[]):
            cap_id=cap.get('capability_id') or cap.get('id')
            if not cap_id:
                continue
            if cap_id not in capabilities:
                capabilities[cap_id]={'capability_id':cap_id,'name':cap.get('name',cap_id),'description':cap.get('description',''),'primary_owner':cap.get('primary_owner',row.get('jarvis_placement')),'shared_service':bool(cap.get('shared_service',False)),'candidate_ids':[cid],'inputs':cap.get('inputs',[]),'outputs':cap.get('outputs',[]),'permissions':cap.get('permissions',[]),'data_classes':cap.get('data_classes',[]),'state':'CANDIDATE_UNVERIFIED'}
            else:
                capabilities[cap_id]['candidate_ids'].append(cid)
        if decision in {'APPROVE_SANDBOX','APPROVE_INTEGRATION','APPROVE_STAGING','APPROVE_PRODUCTION'}:
            approvals.append({'approval_id':f'APR-{idx:04d}','candidate_id':cid,'gate':decision.removeprefix('APPROVE_'),'status':'REQUESTED'})
    (args.out_dir/'candidates.json').write_text(json.dumps(candidates,indent=2)+'\n',encoding='utf-8')
    (args.out_dir/'capabilities.json').write_text(json.dumps(list(capabilities.values()),indent=2)+'\n',encoding='utf-8')
    (args.out_dir/'approval-queue.json').write_text(json.dumps(approvals,indent=2)+'\n',encoding='utf-8')
    for filename,data in [('candidates.csv',candidates),('capabilities.csv',list(capabilities.values()))]:
        if not data:
            continue
        fields=sorted({k for r in data for k in r})
        with (args.out_dir/filename).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=fields)
            w.writeheader()
            for r in data:
                w.writerow({k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in r.items()})
    print(json.dumps({'candidates':len(candidates),'capabilities':len(capabilities),'approvals':len(approvals)},indent=2))
if __name__=='__main__':
    main()
