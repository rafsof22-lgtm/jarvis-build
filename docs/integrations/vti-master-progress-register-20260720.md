# VTI Master Progress Register

Date: 20 July 2026 (Australia/Melbourne)
System of implementation truth: `rafsof22-lgtm/videotranscribe`.
Canonical operational tracker: videotranscribe issue #15.
Detailed gates: videotranscribe issues #3 and #9.

## Ownership

- Jarvis Sovereign Control Plane owns command routing, approval gates, status aggregation, task dependency display and escalation.
- VTI owns platform capability truth, saved-video candidates, OAuth/export intake, Cobalt acquisition, transcription, verification and evidence.
- Platform providers own OAuth consent, scopes, rate limits and saved-resource availability.
- The owner controls credentials, provider consent, production migrations, paid infrastructure, authorised canaries and credential revocation.

## Current proven implementation

- Copied-link and authorised-export candidate model.
- Manual select, select none, select all visible, reject and approved queue controls.
- Truthful YouTube, Facebook, Instagram, X and TikTok capability policies.
- Governed Cobalt adapter plus deployable worker package with FFmpeg, ClamAV, STT, evidence and purge controls.
- Jarvis/VTI federation contracts and deterministic repository CI.
- Vercel workflow no longer contains an embedded credential fallback.

## Active repository tranche

VTI PR #16 implements:

- primary Saved Video Review navigation;
- truthful integration status cards;
- authenticated OAuth initiation;
- signed expiring OAuth state and nonce;
- X S256 PKCE;
- exact callback allowlist;
- encrypted OAuth token storage aligned with the schema;
- bounded authorised-export parsing;
- deterministic security and tracker regression checks.

Status: `INTEGRATED_STAGING` until PR checks and merge pass.

## Jarvis task classes

| Class | Examples | Jarvis action |
|---|---|---|
| Safe repository task | code, tests, docs, schemas, CI | execute through branch, PR, checks and rollback |
| Credential task | OAuth IDs/secrets, Cobalt API key | show exact secret name and least-privilege scope; pause for owner entry |
| Consent task | Google/X/provider OAuth | request interactive owner consent; never bypass MFA/CAPTCHA |
| Production data task | Supabase migration/RLS | require backup, migration plan, owner approval and rollback proof |
| Infrastructure task | Cobalt/worker host | reuse approved host or request cost approval; never create billable resources silently |
| Rights task | media canary | require explicit owned/licensed/authorised source confirmation |
| Restricted platform task | Facebook/Instagram private saved folders, TikTok favourites | use export/copied-link/manual route unless official permission and live proof exist |

## Command routing

- `SHOW VTI PROGRESS` → read issue #15 and VTI federation capability state.
- `CONTINUE VTI` → execute the first dependency-ready safe repository task.
- `SYNC SAVED VIDEOS <platform>` → run capability check, then OAuth/export/copied-link/manual route.
- `IMPORT SAVED VIDEO EXPORT <platform>` → VTI bounded parser → candidate review.
- `TRANSCRIBE SELECTED SAVED VIDEOS` → approval gate → VTI queue → worker.
- `VERIFY SELECTED SAVED VIDEOS` → VTI claims/evidence workflow.
- `COBALT STATUS` → VTI provider status; never infer live readiness from source code.
- `DEPLOY VTI WORKER` → stop at host/secret/cost/production approval gates.

## Remaining blockers

1. Merge VTI PR #16 after all checks pass.
2. Supply user-owned export fixtures for deterministic provider parsers.
3. Apply saved-video, acquisition and worker migrations in staging and regenerate database types.
4. Configure protected OAuth and encryption secrets.
5. Connect YouTube and X one at a time with bounded live tests.
6. Use export/copied-link/manual routes for Facebook and Instagram private saved collections.
7. Require explicit platform scope proof before TikTok favourites sync.
8. Approve a Cobalt/worker host and protected secret mapping.
9. Run an owned/licensed canary and prove hashes, transcript, evidence, cost and purge.
10. Confirm historical Vercel credential revocation through sanitized provider evidence.
11. Complete evidence ZIP, metadata enrichment, categories, browser/mobile capture and runtime progress synchronization.

## Proof boundary

Repository implementation is not live provider proof. OAuth connection is not proof of saved-folder coverage. A deployment signal is not proof of end-to-end transcription. Completion requires requirement → artifact → test → deployment → runtime evidence → rollback.
