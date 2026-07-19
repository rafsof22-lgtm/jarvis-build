#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    spec = (ROOT / 'docs/practitioner-intelligence-and-capability-universe.md').read_text(encoding='utf-8')
    addendum = (ROOT / 'docs/project-instruction-addendum-practitioner-intelligence.md').read_text(encoding='utf-8')
    registry = json.loads((ROOT / 'registry/practitioner-intelligence.json').read_text(encoding='utf-8'))
    applicability = json.loads((ROOT / 'registry/instruction-applicability.json').read_text(encoding='utf-8'))
    for phrase in ['Practitioner/Jarvis-builder intelligence','Capability-universe taxonomy','Gap-exhaustion standard']:
        assert phrase in spec
    for phrase in ['credible implementation evidence','Capability Universe','NO_KNOWN_GAPS_WITHIN_VERIFIED_SCOPE']:
        assert phrase in addendum
    assert len(registry['source_classes']) >= 10
    assert len(registry['capability_classes']) >= 15
    assert {'ADOPT','PILOT','WATCHLIST','REJECT'}.issubset(set(registry['dispositions']))
    rule = next(r for r in applicability['rules'] if r['instruction_id'] == 'practitioner-intelligence-capability-universe')
    assert rule['applicability_class'] == 'BOTH'
    assert rule['runtime_controls'] and rule['chat_controls'] and rule['tests']
    print('practitioner intelligence smoke checks passed')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
