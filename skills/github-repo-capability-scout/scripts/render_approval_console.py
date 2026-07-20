#!/usr/bin/env python3
"""Render a standalone no-network approval console from candidate JSON."""
from __future__ import annotations
import argparse, html, json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('candidates',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    rows=json.loads(args.candidates.read_text(encoding='utf-8'))
    body=['<!doctype html><meta charset="utf-8"><title>Jarvis Capability Approval Console</title><h1>Jarvis Capability Approval Console</h1><p>Local-only review. No network calls.</p><table border="1"><tr><th>Candidate</th><th>Repository</th><th>Licence</th><th>Security</th><th>Placement</th><th>Decision</th></tr>']
    for row in rows:
        cells=[row.get('name') or row.get('candidate_id'),row.get('canonical_url') or 'UNRESOLVED',row.get('licence') or 'UNVERIFIED',row.get('security_state') or 'NOT_SCANNED',row.get('jarvis_placement') or 'UNASSIGNED',row.get('decision') or 'HOLD']
        body.append('<tr>'+''.join(f'<td>{html.escape(str(value))}</td>' for value in cells)+'</tr>')
    body.append('</table>')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text('\n'.join(body),encoding='utf-8')
    print(args.output)
if __name__=='__main__':
    main()
