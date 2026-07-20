#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--skill-root',type=Path,default=Path(__file__).resolve().parents[1])
    args=ap.parse_args()
    manifest=json.loads((args.skill_root/'references/verbatim-content-manifest.json').read_text(encoding='utf-8'))
    path=args.skill_root/manifest['bundled_path']
    data=path.read_bytes()
    actual=hashlib.sha256(data).hexdigest()
    result={'path':str(path),'expected_sha256':manifest['sha256'],'actual_sha256':actual,'expected_size':manifest['size_bytes'],'actual_size':len(data),'pass':actual==manifest['sha256'] and len(data)==manifest['size_bytes']}
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['pass'] else 1)
if __name__=='__main__':
    main()
