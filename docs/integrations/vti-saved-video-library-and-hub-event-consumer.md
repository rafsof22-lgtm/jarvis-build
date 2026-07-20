# VTI Saved Video Library and Hub Event Consumer

## Scope

This record extends the canonical VTI progress tracker with the saved-video intelligence library and the first durable Hub consumer implementation. Repository boundaries remain intact:

- VTI owns candidate capture, metadata, thumbnails, review, transcript/OCR/summary/claim/evidence production and LLM context exports.
- Hub owns authenticated event acceptance, durable processing history, idempotency, retries, dead-letter handling and XRP/HBAR module routing.
- Jarvis owns requirements, status, approvals, costs, evidence references, release records and owner-facing Command Centre presentation.

## VTI library capability

Repository: `rafsof22-lgtm/videotranscribe`

Stacked PR: `#17 Add saved-video library and LLM exports`

Implemented repository scope:

- public metadata enrichment with network-safety controls;
- deterministic YouTube thumbnails where an item ID is available;
- thumbnail-rich searchable cards;
- title, creator, description, publication date and duration presentation;
- platform and governed-status filters;
- individual checkbox selection and select-all-visible;
- owner notes, collections and labels;
- explicit metadata/intelligence, transcription and verification queue actions;
- bounded Markdown and JSON LLM exports containing available transcript, OCR, summaries, claims and evidence references;
- Cobalt, FFmpeg, ClamAV, local Whisper and approved fallback routing retained;
- automatic transcription remains disabled.

Status: `INTEGRATED_STAGING` pending CI, parent PR integration, database migration and browser smoke proof.

## Hub consumer capability

Repository: `rafsof22-lgtm/hub`

PR: `#11 Add durable VTI federation event consumer`

Implemented repository scope:

- schema version `1.0.0` preserved;
- producer `vti-evidence-service` and consumer `xrp-hbar-hub-runtime` enforced;
- HMAC-SHA256 signature verification with timing-safe comparison;
- required-field and event-type validation;
- raw immutable event storage;
- payload hash;
- correlation ID and unique idempotency key;
- duplicate acknowledgement without duplicate storage;
- processing-attempt history;
- bounded retries;
- dead-letter storage;
- controlled dead-letter replay;
- deterministic unit tests and focused CI.

Status: `INTEGRATED_STAGING` pending CI, PR merge and runtime route/database integration.

## Remaining gaps from current chat and master instruction

| Gap | Owner | Status | Next proof |
|---|---|---|---|
| Browser extension copied-link capture | VTI | `SCAFFOLDED` | signed identity, replay protection and browser E2E |
| Mobile share-sheet/PWA capture | VTI | `SCAFFOLDED` | device E2E and authenticated intake |
| Live metadata enrichment against representative platform URLs | VTI | `DEPLOYED_UNVERIFIED` after release | authorised browser smoke evidence |
| Production saved-video library migration | VTI/Supabase | `BLOCKED` | backup, staging migration, regenerated types and RLS tests |
| Evidence ZIP containing transcript, claims, verification and manifests | VTI | `BACKLOGGED` | deterministic exporter and archive tests |
| Creator reliability history | VTI/Hub | `BACKLOGGED` | versioned creator records and accuracy scoring tests |
| Scheduled re-verification and stale-evidence handling | Hub | `BACKLOGGED` | scheduler, freshness policy and invalidation tests |
| VTI event dispatch adapter with signed delivery | VTI | `BACKLOGGED` | secret-name mapping, retry client and Hub test fixture |
| Hub HTTP/queue ingress around consumer | Hub | `IMPLEMENTED_NOT_INTEGRATED` | authenticated endpoint/queue and persistence binding |
| Hub XRP/HBAR specialist routing | Hub | `BACKLOGGED` | route matrix and module tests using both XRP/Ripple and HBAR/Hedera terms |
| Verification-source attachments | Hub/VTI | `BACKLOGGED` | primary-source records linked to claim/evidence IDs |
| Central cost-event ingestion | Hub/Jarvis | `BACKLOGGED` | `cost.recorded` consumer and Command Centre view |
| Command Centre library/job/evidence status | Jarvis | `BACKLOGGED` | read-only VTI/Hub status adapters and UI proof |
| End-to-end authorised canary | All | `BLOCKED` | owner-approved source, credentials, migrations and deployed routes |
| Duplicate/malformed/failure/rollback live proof | All | `BLOCKED` | controlled staging canary and rollback evidence |

## Commands

- `CAPTURE SAVED VIDEO LINKS <links>`
- `IMPORT SAVED VIDEO EXPORT <platform>`
- `SHOW SAVED VIDEO LIBRARY`
- `ENRICH SELECTED VIDEO METADATA`
- `ORGANISE SELECTED VIDEOS <collection/labels/notes>`
- `TRANSCRIBE SELECTED SAVED VIDEOS`
- `VERIFY SELECTED SAVED VIDEOS`
- `EXPORT SELECTED VIDEO CONTEXT <markdown|json|evidence_zip>`
- `SHOW VTI EVENT CONSUMER STATUS`
- `REPLAY APPROVED DEAD LETTER <event_id>`

## Proof boundary

Do not claim direct access to private Facebook or Instagram saved folders, TikTok favourites, or every YouTube private collection without live official scope proof. Do not claim the Hub consumer is deployed merely because repository code and tests exist. Production migrations, signing secrets, provider consent, authorised canaries and rollback evidence remain approval-gated.
