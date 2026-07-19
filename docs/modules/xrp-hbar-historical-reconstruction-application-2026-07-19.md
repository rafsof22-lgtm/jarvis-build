# XRP/HBAR Historical Reconstruction Application and Runtime Reconciliation

**Date:** 19 July 2026 (Australia/Melbourne)  
**Applies to:** XRP/HBAR Apex Intelligence OS, Jarvis control plane, Hub runtime and VTI evidence service  
**Evolution:** Additions-only. This document supersedes stale source-denominator statements without deleting historical specifications.

## 1. Corrected source truth

The statement in `docs/modules/xrp-hbar-apex-stage-specification-2026-07-19.md` that the complete historical ChatGPT export denominator was inaccessible is now superseded.

The verified accessible historical denominator is:

| Measure | Count | State |
|---|---:|---|
| Conversations | 2,610 | DONE_VERIFIED |
| Mapping nodes | 360,445 | DONE_VERIFIED |
| Message nodes | 357,835 | DONE_VERIFIED |
| User messages | 53,473 | DONE_VERIFIED |
| Assistant messages | 169,369 | DONE_VERIFIED |
| Tool messages | 112,284 | DONE_VERIFIED |
| System messages | 22,709 | DONE_VERIFIED |
| Parse errors | 0 | DONE_VERIFIED |
| Explicit reference-bearing messages | 17,634 | DONE_VERIFIED |
| Recursive reference-bearing messages | 196,373 | DONE_VERIFIED |
| Reference-pointer rows | 609,760 | DONE_VERIFIED |

The canonical tracker is `docs/reconstruction/JARVIS_HISTORICAL_SOURCE_RECONSTRUCTION_TRACKER_2026-07-19.md`.

## 2. Historical requirement application

Historical requirements applicable to XRP, Ripple, HBAR, Hedera, Jarvis, Hub, VTI, trading research, market intelligence, source ingestion, forecasting, alerts, custody, passive income, regulation, institutional adoption, tokenization, ETFs, on-chain analysis, social/video evidence, security, costs, deployment and rollback are governed through this placement chain:

`Source -> Conversation -> Message occurrence -> Requirement group -> Canonical domain -> Module/agent/skill -> Artifact -> Test/Waiver -> Evidence -> Deployment -> Rollback`

The historical corpus is not flattened into prose. Verbatim messages and occurrence lineage remain authoritative source records; normalized framework rows are derivatives.

## 3. Applicable unified module stack

The XRP/HBAR module must route applicable historical requirements through these canonical capability groups:

1. XRP/Ripple market, liquidity, payments, stablecoin and institutional intelligence.
2. HBAR/Hedera network, enterprise, tokenization and ecosystem intelligence.
3. Regulation, tax, macro, reserve, custody and retail-holder risk.
4. ETF/ETP, institutional flow, RWA, CBDC and interoperability monitoring.
5. Whale, exchange, on-chain and public-wallet intelligence.
6. Social, influencer, video, transcript and claim-evidence processing.
7. Catalyst, milestone, probability, timeline and discrepancy engines.
8. Source health, provenance, contradictions, invalidations and audit evidence.
9. Research-only/paper-first strategy discovery and simulation.
10. Passive-income, custody, insurance and entity-separation research.
11. Jarvis Command Centre status, alerts, reports, approvals and continuity.
12. Security, credential readiness, cost routing, deployment and rollback.

## 4. Repository placement

| Repository | Responsibility |
|---|---|
| `jarvis-build` | Governing requirements, contracts, read-only federation polling, state classification, evidence and Command Centre integration |
| `hub` | XRP/HBAR runtime, persistence, market/news/on-chain workers, health and deployment evidence |
| `videotranscribe` | Video/transcript intake, claim extraction and evidence events |

Repositories remain independently deployable. Integration uses versioned contracts and does not copy whole repositories into Jarvis.

## 5. Read-only federation poller

The control-plane service now has a staged implementation for:

- polling Hub and VTI well-known health/capability routes;
- bounded retries and timeouts;
- durable JSON state using atomic replacement;
- idempotency-key duplicate suppression;
- dead-letter classification after retry exhaustion;
- rejection of embedded URL credentials;
- secret-free persisted response summaries;
- `BLOCKED` state when service URLs are not configured;
- authenticated poll and state routes.

Configuration names:

- `HUB_FEDERATION_BASE_URL`
- `VTI_FEDERATION_BASE_URL`
- `FEDERATION_STATE_PATH`
- `FEDERATION_POLL_TIMEOUT_MS`
- `FEDERATION_POLL_MAX_RETRIES`
- `FEDERATION_POLL_RETRY_DELAY_MS`

No provider credential is required for public read-only health routes. No production mutation or trading execution is introduced.

## 6. Runtime truth and stale-test correction

The existing service runtime already implements authenticated MCP discovery and dispatch with five metadata/transcript intake tools. The previous server tests expected an empty tool list and HTTP 501, which no longer matched `main` runtime behavior.

The test suite is corrected to require:

- implemented MCP tool discovery;
- successful metadata normalization through authenticated dispatch;
- unsupported-tool rejection;
- malformed-request rejection;
- read-only federation state retrieval;
- safe `BLOCKED` response when Hub/VTI URLs are absent.

## 7. Closed discrepancies

| Discrepancy | Resolution | State |
|---|---|---|
| Stage spec said historical export was inaccessible | Superseded by verified reconstruction tracker and this addendum | DONE_VERIFIED |
| Earlier PR #23 contained stale completion percentages | Closed unmerged and marked superseded by PR #24 | DONE_VERIFIED |
| Server tests expected obsolete unimplemented MCP behavior | Replaced with runtime-accurate tests | INTEGRATED_STAGING |
| Jarvis had no read-only live-contract polling core | Poller, state store, retries, idempotency and dead-letter logic added | INTEGRATED_STAGING |
| Federation URL configuration was undefined | Named configuration contract added | INTEGRATED_STAGING |

## 8. Remaining evidence gates

These cannot be converted to `DONE_VERIFIED` without external evidence:

1. DigitalOcean firewall/host recovery and live Hub route proof.
2. Public VTI route and provider-runtime proof.
3. Production-grade shared persistence replacing single-instance JSON state where horizontal scaling is used.
4. Authoritative live event exchange from VTI and Hub into Jarvis.
5. Isolated database backup/restore proof.
6. Production rollback drill with known-good commit and verified data preservation.
7. Gmail OAuth token refresh and bounded metadata-fetch proof.
8. Live market/on-chain/news/social provider configuration and cost evidence.
9. Separate approval and risk controls before any live trading or money movement.

## 9. Completion boundary

Historical reconstruction and canonical application are complete for the verified accessible textual/source denominator. Missing binary bytes, non-exported ChatGPT-native project names and inaccessible external runtime/provider state remain individually classified rather than fabricated.

The module is `INTEGRATED_STAGING` after repository tests pass. It remains `DEPLOYED_UNVERIFIED` for external runtime claims until the live evidence and rollback chain are complete.
