# VTI saved-video capture and manual review control plane

## Ownership

VTI owns all platform connectors, copied-link intake, export parsers, candidate review, transcription queueing and evidence production. Jarvis routes commands, displays status and distributes verified intelligence. Jarvis must not connect directly to Facebook, Instagram, X, YouTube, TikTok or Cobalt for saved-video acquisition.

## Canonical command flow

`Jarvis command -> Sovereign Control Plane -> VTI saved-video capability check -> authorised OAuth/export/copied-link route -> saved-video candidate -> manual review -> selected queue action -> captions/media acquisition -> transcription/OCR -> claims/verification -> evidence pack -> Jarvis event`

## Commands

- `SYNC SAVED VIDEOS <platform>`
- `IMPORT SAVED VIDEO EXPORT <platform>`
- `CAPTURE SAVED VIDEO LINKS <links>`
- `SHOW SAVED VIDEO REVIEW`
- `SELECT SAVED VIDEO <id>`
- `SELECT ALL VISIBLE SAVED VIDEOS`
- `REJECT SELECTED SAVED VIDEOS`
- `TRANSCRIBE SELECTED SAVED VIDEOS`
- `VERIFY SELECTED SAVED VIDEOS`
- `EXPORT SELECTED VIDEO EVIDENCE`

## Platform truth states

- YouTube: OAuth/API and export routes are possible only within granted scopes and live tests.
- X/Twitter: bookmark sync depends on OAuth scope, API tier, pagination and rate limits.
- Facebook: personal saved folders use authorised export, copied links, visible capture or upload unless official access is proven.
- Instagram: private saved collections use authorised export, copied links, visible capture or upload unless official access is proven.
- TikTok: `video.list` is not treated as favourites access; exports/copied links are the default until explicit official proof exists.

## Manual-control invariant

Automatic capture means importing candidates into VTI's review queue. It never means automatic transcription by default. The user can select none, individual candidates, all visible candidates, reject candidates, queue transcription, queue verification or retain metadata only.

## Registry state

- Repository code: `IMPLEMENTED_NOT_INTEGRATED` until VTI PR #10 passes and merges.
- Supabase saved-video migration: `PENDING_DEPLOYMENT_PROOF`.
- OAuth saved-item connectors: `PENDING_CREDENTIALS` / `ACCESS_RESTRICTED` by platform.
- Platform export parsers: `BACKLOGGED` until fixtures and reconciliation tests exist.
- Browser/mobile share capture: `SCAFFOLDED` until signed live intake proof exists.
- End-to-end saved-video transcript/evidence/purge: `DEPLOYED_UNVERIFIED` only after live canary; otherwise `BLOCKED`.

## Required telemetry

Record platform, route, connector/scopes, sync cursor, pages, rate limits, discovered/selected/queued/blocked counts, candidate proof status, queue job, cost, source hash, transcript/evidence references, retention and rollback target. Never expose tokens.

## Rollback

Disable each platform sync independently, preserve candidates and source records, revoke connector tokens, stop scheduled discovery, and continue copied-link/export/manual intake. Disabling a connector must not delete evidence or user review decisions.
