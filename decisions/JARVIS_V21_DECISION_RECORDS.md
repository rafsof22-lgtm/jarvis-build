# JARVIS V21 Decision Records

## DR-V21-001 — Target-builder-overlay separation

**Decision:** Original Jarvis Framework is the target; Jarvis Build is the builder; control overlays do not replace the target.  
**Authority:** current explicit human-owner correction.  
**Status:** accepted for candidate pack; repository merge pending.

## DR-V21-002 — Preserve V18/V19/V20 lineage

**Decision:** do not replace the V18 Mammoth framework, V19 merged tracker, or V20 open PR. Add V21 compatibility and delta files.  
**Reason:** additions-only evolution and non-duplication.

## DR-V21-003 — Source denominator coexistence

**Decision:** keep native and flattened export denominators as separate source classes.  
**Reason:** different schemas, missing native metadata, and non-comparable message counts.

## DR-V21-004 — GitHub write authorised for V21 branch/PR

**Decision:** create the V21 branch and draft PR under the current explicit user request; do not merge or deploy.  
**Reason:** Phase 7 was explicitly requested, while merge remains separately owner-gated.

## DR-V21-005 — V21 depends on V20 lineage

**Decision:** branch V21 from PR #105 head so V20 evidence is preserved and not duplicated. Keep #105 open during review; if V21 is later approved and merged, close #105 as superseded.  
**Reason:** additions-only lineage and avoidance of duplicate independent merges.
