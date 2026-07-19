# XRP/HBAR Framework Options — Jarvis Federation Integration

Status: `IMPLEMENTED_NOT_INTEGRATED`

## Purpose

Unify the reconstructed XRP/HBAR Framework Options module with Jarvis without destroying repository independence, source lineage, rollback capability, or module-specific security boundaries.

## Authority and lineage

The canonical requirement source is the verified XRP/HBAR Framework Options reconstruction pack and its registries. Runtime truth is determined only from current repository code, CI, deployment records, health checks, evidence, and rollback proof.

Historical completion, probability, accuracy, live-data, profit, and zero-gap claims remain unverified until the required proof chain exists:

`Requirement -> Placement -> Implementation -> Test/Waiver -> Evidence -> Verification -> Rollback`

## Repository federation

| Repository | Primary role | Integration rule |
|---|---|---|
| `rafsof22-lgtm/jarvis-build` | Sovereign control plane, canonical registries, Command Centre, policies and shared contracts | Owns module metadata, requirements, service contracts, health aggregation, approval policy and release evidence |
| `rafsof22-lgtm/hub` | Existing XRP/HBAR DigitalOcean runtime and deployment evidence | Remains independently deployable; implements versioned runtime and event contracts |
| `rafsof22-lgtm/videotranscribe` | Video/transcript capture, claim extraction and evidence generation | Remains independently deployable; exposes transcript/evidence contracts to Jarvis and XRP/HBAR services |

No repository is copied wholesale into another. Shared behavior is introduced through versioned APIs, events, schemas, MCP tools and evidence records.

## Canonical service identifiers

- `jarvis-control-plane`
- `xrp-hbar-apex-control`
- `xrp-hbar-hub-runtime`
- `vti-evidence-service`

## Required interfaces

### Control-plane to hub

- Read deployment and readiness state.
- Submit bounded research or paper-first jobs.
- Retrieve structured results, run state, source provenance, costs, failures and evidence.
- Pause, resume or cancel only within scoped policy.

### Hub to control plane

- Emit versioned status, evidence, discrepancy, alert, cost and incident events.
- Never assert live or complete state without a source timestamp and evidence pointer.

### Video intelligence to hub/control plane

- Submit URL, file or transcript intake.
- Return transcript metadata, extracted claims, timestamps, source pointers, verification state and failure reasons.
- Treat social/video repetition as leads, not proof.

## Event envelope

Every cross-repository event must contain:

- `event_id`
- `event_type`
- `schema_version`
- `producer`
- `consumer`
- `occurred_at`
- `correlation_id`
- `idempotency_key`
- `source_refs`
- `approval_state`
- `payload`
- `evidence_refs`
- `retry_count`
- `status`

## Security and approvals

- Secrets remain in repository or platform secret stores and are referenced only by name.
- Use least-privilege service credentials, scoped tokens and environment separation.
- Research and paper trading are default.
- Production promotion, public publishing, credential changes, money movement and live trading remain owner-gated.
- No direct writes to `main`; use branch, tests, PR, independent verification and controlled merge.

## Future module-chat integration rule

Future module chats in this Jarvis project must produce an additions-only module pack containing:

1. canonical requirements;
2. source lineage;
3. module/service ownership;
4. interfaces and schemas;
5. tools, Skills, APIs, connectors and credential names;
6. tests and evidence;
7. risks, gaps and approval gates;
8. rollback and resume instructions.

The Jarvis control plane federates the module through stable contracts. It must not flatten unrelated repositories, silently overwrite prior module instructions, or claim activation across inaccessible chats or systems.

## Completion gates

1. Contract schemas added and validated.
2. `jarvis-build` registry updated.
3. `hub` adapter implemented and tested.
4. `videotranscribe` adapter implemented and tested.
5. Cross-repository contract tests pass.
6. Staging federation health and freshness checks pass.
7. Rollback drill passes.
8. Independent verification approves the exact artifact.
9. Owner approves production promotion.

Until all gates pass, integration status remains `IMPLEMENTED_NOT_INTEGRATED` or `INTEGRATED_STAGING`, never `DONE_VERIFIED`.