# Missing Controls and Completeness Checklist

During SPEC_LOCK, implementation, verification and release, classify every item as implemented, applicable backlog, blocked, waived, excluded with reason, or not applicable with reason.

## Governance
Owner/delegations; environment autonomy ceilings; planner/executor/verifier/risk/release separation; conflict/exception/break-glass with review; legal/contract/regulatory/data-residency; tenant isolation/consent; dual-layer applicability; skill-update candidates.

## Requirements/product truth
Verbatim request log; acceptance/non-goals; hidden dependencies/side effects; measurable success/failure; ButtonTruth/OutcomeContract; accessibility/localization/offline/mobile/degraded mode; migration/deprecation/compatibility; source denominator; capability-universe classification.

## Architecture/runtime
Typed service/event contracts; idempotency/reconciliation/durable workflows; state machines; workspace boundaries; configuration/feature flags; schema migrations/rollback; capacity/performance/latency; local/hybrid/cloud profiles; RTO/RPO and restore tests; checkpoint/resume; circuit breakers/dead letters.

## Agents/models
Signed identity/template; prompt/version registry; model benchmarks/evaluation sets; tool schemas/policy; memory poisoning/prompt injection; context/data minimization; deterministic fallback; provider outage/degradation; hallucination/bias/privacy/unsafe-tool evaluation; role separation; bounded spawning.

## Integrations/credentials
Lifecycle proposed/sandbox/staged/active/suspended/revoked; scopes/owners; secret names/readiness only; expiry/rotation; quotas/retries/webhooks; API/schema drift; retention/DPA; revoke/export/vendor exit; billing alerts; cross-repo readiness; provider adapters; novice setup.

## Security/supply chain
Threat model/abuse; SBOM/provenance; vulnerability/license/malicious-package scanning; signed artifacts/attestations; least privilege/egress; immutable audit; incident forensics/notification; red team; secure deletion/data rights; current/history secret scans.

## Data/knowledge
Raw-source immutability; lineage/provenance/citations; retention/deletion/legal hold/backups; sensitive classifications; contradiction/freshness/expiry; OCR/transcription/table/code quality; access at source/chunk/claim/tenant; knowledge rollback/correction propagation; practitioner findings and negative lessons.

## UX/operations
Novice golden path; guided recovery/one-click safe fixes; visible costs/scopes/consequences; progressive expert controls; onboarding/runbooks; explainable timeline; notification/escalation; outcome confirmation; manual override/edit/approval/kill switch.

## Business/cost
Free-first/cheapest-safe routing; caps per task/agent/module/tenant/period; attribution/unit economics; subscription consolidation/lock-in; lawful demand proof; taxes/refunds/churn/disputes; no guaranteed revenue/profit.

## Testing/release
Unit, contract, integration, E2E, security, policy, accessibility, load, chaos, cost, backup, restore, rollback; representative fixtures; canary/shadow/staging; post-deploy smoke/reconciliation; independent verifier; evidence manifest/hashes; explicit status; credential/setup/readiness tests; skill validation/package tests.

## Continuity/update
State/resume; source/upload/thread/build/decision/instruction/skill ledgers; delta/discrepancy reports; provider/model/framework/practitioner watches; deprecation/security advisories; restore/failover/kill-switch drills; archival/handoff package; automatic update-candidate capture without unverified installed-skill claims.