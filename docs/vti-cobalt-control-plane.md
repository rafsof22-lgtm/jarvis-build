# VTI cobalt control-plane integration

## Unified ownership

Jarvis coordinates media acquisition through VTI. Jarvis does not call cobalt directly, store cobalt credentials, receive platform cookies, or become responsible for media transformation.

- VTI owns source intake, authentication, policy, acquisition routing, provenance, media processing, transcription, OCR, claims and evidence.
- A self-hosted cobalt service is an optional isolated resolver used only after VTI policy approval.
- Jarvis owns command normalization, capability routing, correlation, status visibility, approval state, evidence references and incident controls.

## Command route

1. Jarvis receives `resolve_media_source` with source URL, purpose, project, requested output and correlation/idempotency identifiers.
2. Jarvis sends the request to VTI's authenticated API.
3. VTI records or reconciles the source record and evaluates public-source and rights policy.
4. VTI attempts captions and official routes first.
5. If configured and allowed, VTI asks its self-hosted cobalt instance for an ephemeral descriptor.
6. A future bounded media worker streams and validates bytes before storage or transcription.
7. VTI emits transcript, OCR, claim and evidence references through its federation event contract.
8. Jarvis displays status and routes the evidence to applicable modules, including XRP/HBAR intelligence, research, health, finance or property, without changing the evidence.

## Cross-layer placement

| Layer | Placement |
|---|---|
| Gateway | Jarvis command normalization and VTI authentication |
| Sovereign control plane | Registry, approval, cost, status and incident records |
| Agent core | Source-intake and evidence-routing tasks |
| Tool layer | VTI acquisition endpoint; cobalt remains behind VTI |
| Model/cost router | Captions/local tools before paid STT |
| Memory/knowledge | Immutable source URL, hashes, transcript and evidence references |
| Evidence/verification | Chain of custody, claim verification, contradictions and confidence |
| Command Centre | Readiness, queue, failure, quota, cost and rollback visibility |

## Safety and legal boundary

Only process media the user is authorised to process. Block private or credentialed URLs and do not automate authentication, CAPTCHA, paywall or DRM circumvention. Do not persist ephemeral resolver URLs. Do not redistribute source media by default. Use copied-link metadata and manual-upload fallbacks whenever acquisition is unavailable or inappropriate.

## Status rule

The repository adapter may be `IMPLEMENTED_NOT_INTEGRATED`; it becomes `DONE_VERIFIED` only after VTI CI, self-hosted runtime proof, bounded streaming, owned/public-domain media tests, provenance reconciliation, end-to-end transcription/evidence export and rollback evidence all pass.
