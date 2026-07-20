#!/usr/bin/env python3
"""Extract and deduplicate GitHub repository links from curated markdown catalogues or offline fixtures."""
from __future__ import annotations
import argparse, csv, json, os, re, time, urllib.request
from pathlib import Path
URL_RE=re.compile(r'https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:[/#?\s)\],]|$)',re.I)

def canonical(owner,repo):
    return f'https://github.com/{owner}/{repo.removesuffix(".git")}'

def fetch(url, token_env, timeout, retries):
    headers={'User-Agent':'github-repo-capability-scout/1.0'}
    token=os.getenv(token_env) if token_env else None
    if token:
        headers['Authorization']=f'Bearer {token}'
    err=None
    for n in range(retries+1):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=timeout) as response:
                return response.read().decode('utf-8','replace')
        except Exception as exc:
            err=exc
            if n<retries:
                time.sleep(min(2**n,8))
    raise RuntimeError(f'fetch failed: {err}')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',action='append',default=[])
    ap.add_argument('--fixture',action='append',type=Path,default=[])
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--token-env',default='GITHUB_TOKEN')
    ap.add_argument('--timeout',type=int,default=20)
    ap.add_argument('--retries',type=int,default=2)
    args=ap.parse_args()
    docs=[]
    failures=[]
    for path in args.fixture:
        try:
            docs.append((str(path),path.read_text(encoding='utf-8')))
        except Exception as exc:
            failures.append({'source':str(path),'error':str(exc)})
    for url in args.source:
        try:
            docs.append((url,fetch(url,args.token_env,args.timeout,args.retries)))
        except Exception as exc:
            failures.append({'source':url,'error':str(exc)})
    found={}
    for source,content in docs:
        for match in URL_RE.finditer(content):
            url=canonical(match.group(1),match.group(2))
            key=url.lower()
            found.setdefault(key,{'canonical_url':url,'sources':[],'status':'USER_PROVIDED_UNVERIFIED','licence':'UNVERIFIED','security_state':'NOT_SCANNED','reviewed_revision':None})['sources'].append(source)
    rows=sorted(found.values(),key=lambda item:item['canonical_url'].lower())
    args.out_dir.mkdir(parents=True,exist_ok=True)
    (args.out_dir/'catalogue.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
    (args.out_dir/'failures.json').write_text(json.dumps(failures,indent=2)+'\n',encoding='utf-8')
    with (args.out_dir/'catalogue.csv').open('w',newline='',encoding='utf-8') as f:
        fields=['canonical_url','sources','status','licence','security_state','reviewed_revision']
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({**row,'sources':json.dumps(row['sources'])})
    queue=[{'candidate_id':f'CAND-{i:04d}','canonical_url':row['canonical_url'],'decision':'HOLD','required_next':'CANONICAL_UPSTREAM_AND_LICENCE_REVIEW'} for i,row in enumerate(rows,1)]
    (args.out_dir/'approval-queue.json').write_text(json.dumps(queue,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'documents':len(docs),'repositories':len(rows),'failures':len(failures)},indent=2))
if __name__=='__main__':
    main()
