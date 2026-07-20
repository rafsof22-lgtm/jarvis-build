#!/usr/bin/env python3
"""Static, non-executing triage of a local repository snapshot."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

RISK_PATTERNS = {
    "dynamic_execution": re.compile(r"\b(eval|exec)\s*\(", re.I),
    "shell_execution": re.compile(r"\b(subprocess\.|os\.system\(|child_process|powershell|cmd\.exe)", re.I),
    "credential_access": re.compile(r"(\.ssh|browser.*profile|AWS_SECRET|PRIVATE_KEY|API_KEY|TOKEN|PASSWORD)", re.I),
    "network_download": re.compile(r"(curl\s+|wget\s+|requests\.|urllib\.|fetch\(|axios\.)", re.I),
    "unsafe_deserialisation": re.compile(r"(pickle\.loads|yaml\.load\s*\(|marshal\.loads)", re.I),
    "docker_privilege": re.compile(r"(--privileged|/var/run/docker\.sock|network_mode:\s*host|hostNetwork:\s*true)", re.I),
}
TEXT_EXTENSIONS={'.py','.js','.mjs','.cjs','.ts','.tsx','.jsx','.sh','.bash','.ps1','.yml','.yaml','.json','.toml','.ini','.cfg','.md','.txt','.dockerfile'}
SKIP_DIRS={'.git','node_modules','.venv','venv','dist','build','__pycache__'}

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('snapshot', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--max-bytes', type=int, default=2_000_000)
    args=ap.parse_args()
    root=args.snapshot.resolve()
    if not root.is_dir():
        raise SystemExit('snapshot must be a directory')
    findings=[]
    files=[]
    for path in sorted(root.rglob('*')):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        rel=path.relative_to(root).as_posix()
        size=path.stat().st_size
        files.append({'path':rel,'size_bytes':size,'sha256':sha256(path)})
        name=path.name.lower()
        ext=path.suffix.lower()
        if size > args.max_bytes:
            continue
        if ext in TEXT_EXTENSIONS or name in {'dockerfile','makefile','package.json','package-lock.json','pyproject.toml','requirements.txt'}:
            try:
                content=path.read_text(encoding='utf-8', errors='replace')
            except OSError:
                continue
            for category,pattern in RISK_PATTERNS.items():
                for m in pattern.finditer(content):
                    line=content.count('\n',0,m.start())+1
                    findings.append({'category':category,'path':rel,'line':line,'match':m.group(0)[:160]})
            if name=='package.json':
                try:
                    data=json.loads(content)
                    for script_name,script in (data.get('scripts') or {}).items():
                        if script_name in {'preinstall','install','postinstall','prepare','prepublish'}:
                            findings.append({'category':'lifecycle_script','path':rel,'line':None,'match':f'{script_name}: {script}'})
                except json.JSONDecodeError:
                    findings.append({'category':'invalid_json','path':rel,'line':None,'match':'package.json parse failed'})
        if ext in {'.exe','.dll','.so','.dylib','.bin'}:
            findings.append({'category':'binary_artifact','path':rel,'line':None,'match':ext})
    categories=sorted({f['category'] for f in findings})
    high={'dynamic_execution','unsafe_deserialisation','docker_privilege','binary_artifact','credential_access'}
    state='HIGH_RISK_BLOCKED' if high.intersection(categories) else ('REVIEW_REQUIRED' if findings else 'NO_STATIC_FLAGS')
    report={'tool':'github-repo-capability-scout/analyze_repo_snapshot.py','snapshot':str(root),'execution_policy':'NO_CANDIDATE_CODE_EXECUTED','static_analysis_limit':'STATIC_SCAN_NOT_MALWARE_PROOF','state':state,'file_count':len(files),'finding_count':len(findings),'categories':categories,'findings':findings,'files':files}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'state':state,'file_count':len(files),'finding_count':len(findings)},indent=2))
    return 2 if state=='HIGH_RISK_BLOCKED' else 0
if __name__=='__main__':
    raise SystemExit(main())
