# VTI -> Hub Staging Canary Runbook

Status: `RUNTIME_APPROVAL_REQUIRED`
Date: 20 July 2026
Scope: staging only; no production financial action

## Purpose

Prove the source-controlled VTI evidence-event producer and Hub event consumer work together end to end without exposing secrets, weakening repository independence, or enabling trading, money movement or personalised financial advice.

## Preconditions

- VTI compatibility PR merged with green contract CI.
- Hub durable event consumer merged with green CI.
- A non-production Hub ingress service is deployed from `hub/main`.
- A non-production VTI service is deployed from `videotranscribe/main`.
- Matching signing-secret values are stored independently in approved provider secret stores.
- No secret value is committed, pasted into chat, written to evidence files or printed in logs.
- One non-sensitive, owner-authorised evidence fixture is selected.

## Required runtime variables

### VTI staging

| Variable | Secret | Purpose |
|---|---:|---|
| `HUB_VTI_EVENT_ENDPOINT` | No | HTTPS Hub staging route ending `/v1/federation/vti/events` |
| `VTI_EVENT_SIGNING_SECRET` | Yes | HMAC-SHA256 signing key, at least 32 characters |
| `VTI_INTERNAL_CRON_SECRET` | Yes | Authorises bounded outbox dispatch |
| `NEXT_PUBLIC_SUPABASE_URL` | No | VTI staging data service URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Service-role access for the approved staging dispatcher |

### Hub staging

| Variable | Secret | Purpose |
|---|---:|---|
| `VTI_EVENT_SIGNING_SECRET` | Yes | Must match the VTI staging secret |
| `VTI_EVENT_DATABASE` | No | Staging database path or approved persistence location |
| `HOST` | No | Bind host; provider-specific |
| `PORT` | No | Ingress port; provider-specific |

## Canary event constraints

- schema version `1.0.0`;
- producer `vti-evidence-service`;
- consumer `xrp-hbar-hub-runtime`;
- event type `evidence.created`;
- status `INTEGRATED_STAGING`;
- unique event, correlation and idempotency identifiers;
- nested payload keys deliberately inserted in non-alphabetic order to prove recursive canonicalisation;
- source/evidence references must identify a non-sensitive fixture, not private media;
- approval state must be explicit;
- no portfolio action, order, transfer, wallet operation or advice directive.

## Acceptance sequence

1. **Health proof** — Hub staging GET route responds and reports schema `1.0.0`.
2. **Valid event** — VTI sends a signed event; Hub returns HTTP 202 with `accepted=true`, `duplicate=false`.
3. **Duplicate proof** — resend identical idempotency key; Hub returns `accepted=true`, `duplicate=true` without a second logical record.
4. **Invalid signature proof** — isolated test uses a deliberately invalid test signature; Hub returns HTTP 401. Do not alter stored secrets.
5. **Correlation mismatch proof** — isolated request header and event body differ; Hub returns HTTP 400.
6. **Validation proof** — unsupported schema or event type returns HTTP 400 and is not routed.
7. **Processing proof** — accepted event is routed to the intended XRP/HBAR module and marked processed.
8. **Retry proof** — a controlled processing fixture fails below the maximum-attempt threshold and becomes `retry_pending`.
9. **Dead-letter proof** — controlled fixture reaches the configured limit and enters dead-letter storage.
10. **Replay proof** — an authorised replay resets only the selected dead letter and preserves the audit trail.
11. **Evidence proof** — raw event hash, acknowledgement, attempts and final state are exported without secret values.
12. **Jarvis proof** — Command Centre receives commit refs, environment, test IDs, evidence references, blocker state and rollback reference.

## Required evidence pack

- VTI commit SHA and deployment identifier;
- Hub commit SHA and deployment identifier;
- schema version;
- sanitised health response;
- sanitised valid acknowledgement;
- duplicate acknowledgement;
- invalid-signature and correlation-mismatch status codes;
- retry/dead-letter/replay record identifiers;
- event payload hash and evidence references;
- timestamps and correlation ID;
- runtime log references with secrets redacted;
- rollback result;
- unresolved blockers.

## Rollback

1. Pause VTI outbox dispatch.
2. Disable or remove `HUB_VTI_EVENT_ENDPOINT` from VTI staging.
3. Revoke/rotate the staging signing secret in both provider stores if exposure is suspected.
4. Stop Hub staging ingress without deleting event evidence.
5. Revert deployment to the last verified commit.
6. Preserve raw events, attempts, dead letters and audit evidence according to retention policy.
7. Record rollback reason, owner, timestamps and verification.
8. Do not promote to production until the failed gate is corrected and replayed in staging.

## Promotion gate

Staging success does not authorise production. Production requires explicit owner approval, security review, secret rotation plan, monitoring, rate limits, backup/restore, incident response and a separate production canary. Financial execution remains out of scope.

## Exact current blocker

`BLOCKED_AT_PROVIDER_CONFIGURATION`: the active tool environment cannot create the staging services or set provider secret values. The provider administrator must configure the named variables through the provider vault/UI, then return only deployment identifiers and sanitised proof—not secret values.
