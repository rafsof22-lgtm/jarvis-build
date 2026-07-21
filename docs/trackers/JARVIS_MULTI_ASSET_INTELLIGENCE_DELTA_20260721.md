# Jarvis Multi-Asset Intelligence Delta — 21 July 2026

## Requirements captured

This tranche records and implements the latest visible requirements without replacing prior XRP/HBAR histories:

1. consolidate related XRP tracking and intelligence instructions behind one XRP profile;
2. retain a separate HBAR profile with equivalent governance but HBAR-specific analysis;
3. run UPDATE, DEEP_SCAN and ALL_INTELLIGENCE workstreams together when the broad trigger is used;
4. support up to 100 meaningful sources per asset per apex run and continue expanding source registries over time;
5. track XRP through $10,000 and dynamic scenarios above it;
6. track HBAR through $100 and dynamic scenarios above it;
7. calculate multiple constrained maximum/ceiling scenarios for every asset;
8. onboard future crypto and stocks using unique class and asset requirements;
9. export intelligence into the main Knowledge Fabric for Jarvis and agent retrieval;
10. provide one original sci-fi, voice-ready, novice-friendly Command Centre across Jarvis.

## Artifacts

| Artifact | State |
|---|---|
| Shared multi-asset intelligence orchestrator contract | `IMPLEMENTED_NOT_INTEGRATED` |
| Separate XRP asset profile | `IMPLEMENTED_NOT_INTEGRATED` |
| Separate HBAR asset profile | `IMPLEMENTED_NOT_INTEGRATED` |
| Future crypto/stock/ETF asset template | `IMPLEMENTED_NOT_INTEGRATED` |
| Deterministic trigger and fan-out planner | `IMPLEMENTED_NOT_INTEGRATED` |
| Omnichannel Command Centre contract | `IMPLEMENTED_NOT_INTEGRATED` |
| Command Centre v1.2 asset HUD and API | `IMPLEMENTED_NOT_INTEGRATED` |
| Deterministic verifier and CI integration | `IMPLEMENTED_PENDING_CI` |
| Live source adapters and current market intelligence | `BLOCKED_RUNTIME_NOT_EXECUTED` |
| Audio STT/TTS/wake-word runtime | `BLOCKED_RUNTIME_NOT_CONNECTED` |
| Connected Knowledge Fabric export | `BLOCKED_CONNECTED_BACKEND_REQUIRED` |

## Progress effect

| Workstream | Prior evidence-backed state | Current branch state |
|---|---|---|
| P2-5 universal intelligence fabric | `BACKLOGGED` | `IMPLEMENTED_NOT_INTEGRATED` for the multi-asset orchestration and profile layer |
| P1-5 Command Centre | `IMPLEMENTED_NOT_INTEGRATED` | v1.2 HUD and asset API implemented; authenticated live UI and adapters remain open |
| XRP profile consolidation | fragmented trackers and bounded reconciliation batches | one governed active profile added; full historical backfill remains open |
| HBAR profile consolidation | bounded cross-asset controls | one separate governed active profile added; full historical backfill remains open |
| Future asset support | generic cross-asset intent | crypto/stock/ETF and other class extensions implemented as a validated template |
| Knowledge Fabric asset export | specified | collection and record contract implemented; connected write path remains open |

## Known open loops

1. Merge or supersede PR #69 only after its independent CI passes; do not silently combine its historical source tranche with this architecture tranche.
2. Execute current-source XRP and HBAR intelligence runs through authorised web/data tools and persist exact source denominators.
3. Build official-source adapters and source registry storage.
4. Connect the asset records to the production Knowledge Fabric after staging benchmark and permission tests.
5. Add authenticated Command Centre front-end interaction, streaming tasks and approval cards.
6. Connect reviewed local/private wake word, STT, transport and TTS components.
7. Add future assets only through validated unique profiles.
8. Continue historical XRP, HBAR, prediction, table, trigger, discrepancy and assistant-response reconstruction.
9. Continue the global P0–P6 tracker; provider, credential, production and owner gates remain unchanged.

## Truth boundary

The branch implements repository contracts, deterministic planning, validation and a static/offline Command Centre integration. It has not performed a live 100-source scan, produced current asset recommendations, connected speech providers, written to a live Knowledge Fabric or deployed production services.
