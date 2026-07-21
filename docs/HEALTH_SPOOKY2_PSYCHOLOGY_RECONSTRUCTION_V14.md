# Health, Spooky2 and Psychology Reconstruction V14

## Outcome

This tranche reconciles the latest accessible ChatGPT export with the older Health/Spooky2/Psychology handover, performs format-specific analysis of every bundled source file, normalises the recurring requirements, and adds a privacy-safe fail-closed health evidence gate.

## Source truth

- Latest export: 2,610 conversations and zero JSONL parse errors.
- Unique target-project set: 156 conversations and 27,153 canonical messages.
- Health Optimisation: 105 conversations / 21,877 messages.
- Spooky2: 36 conversations / 2,908 messages.
- Psychology: 15 conversations / 2,368 messages.
- Prior v12 count of 157 is preserved as a mixed-lineage envelope count. One Psychology conversation was also counted in the prior Health envelope, so the unique denominator is 156.
- The older keyword-selected handover contains 194 conversations, but only 77 are exact target-project conversations; 117 are non-target or unscoped keyword hits.
- The latest export adds 79 target-project conversations absent from the older handover.

## Bundled source processing

All 52 copied source files were processed using the appropriate format path:

- 36 text/DOCX/Markdown/Python sources: 574,219 words extracted.
- 7 XLSX workbooks: 42 sheets and 2,476 non-empty cells inspected through `artifact_tool`.
- 4 PDFs: 774 pages, text layers extracted, and first pages rendered.
- 4 JPEGs: visually classified without identifying people.
- 1 nested ZIP: retained as source lineage.

Personal laboratory values, genetic variants and medical records were not interpreted as diagnoses. Raw sensitive material remains outside the repository.

## Safety finding

Historical assistant outputs produced 1,629 deterministic safety-pattern flags. These are review candidates rather than clinical judgments. The largest categories include medication-change language, device settings, detox/biologic claims, invasive experimental interventions and psychedelic dosing.

## Implemented control

`src/jarvis_health/evidence_gate_v1.py` provides:

- explicit source classes;
- evidence grades;
- high-risk claim detection;
- emergency escalation state;
- guaranteed-cure quarantine;
- clinician review gates;
- blocked medical-device control;
- privacy-safe hash-only assessment persistence;
- idempotent replay protection;
- an output contract requiring risks, contraindications, interactions, monitoring, escalation, citations and freshness.

It does **not** diagnose, treat, change medication, prescribe, interpret personal records as final authority, operate a medical device, or validate historical claims.

## Next work

1. Build privacy-safe health profile and care-coordination schemas with synthetic fixtures.
2. Construct a hash/pointer-only high-risk claim review queue.
3. Build clinician/pharmacist review packet generation.
4. Verify specific high-priority claims against current official and peer-reviewed sources when required.
5. Keep all connected health data, clinician portal, staging and production work behind privacy, credential, professional and owner gates.
