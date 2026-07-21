# Jarvis V17 Completion Tranche

**Date:** 22 July 2026 (Melbourne)  
**Baseline main:** `f9d02bbaf03d676f42342b7970607ec803f86b25`  
**Programme:** `ACTIVE_PROGRAM_NOT_100_PERCENT`

## Outcome

V17 executes the six safe work packages requested after V16:

1. expose the canonical 18-layer tree, traffic lights and gaps in Command Centre;
2. compare the available ChatGPT archive against the 25 June export and generate a truthful delta result;
3. build a hash-only Health claim-review manifest and synthetic care journeys;
4. add Cost + $1 customer, workshop, vehicle, supplier and order schemas plus a synthetic order-to-billing route;
5. continue bounded reconstruction of XRP, Longevity, Tax, Active Trust, Finance Planning and Financial New;
6. exercise all 18 layers through a zero-spend local staging digital twin with privacy, security, persistence, retry, backup, restore, cost and rollback tests.

## Command Centre

`jarvis_command_centre/full_stack_v17.py` adds:

- `/api/v1/full-stack`;
- 18 expandable layer cards;
- green, amber, blue, grey and red evidence states;
- per-layer evidence pointers and open gaps;
- local-staging evidence summary;
- explicit external-staging and production truth boundaries.

Rendering performs no provider call and writes no external state.

## Chat delta

The supplied archive SHA-256 is:

`fa61e528ae1ffbe1b8f5c2addc76dab0129264fc5c918fdfc4dd78a23964ac82`

It exactly matches the registered 25 June 2026 archive. Therefore novel export bytes are `0` and a real post-cutoff delta remains `PENDING_INGEST` until a newer export or explicit later-chat pack exists.

## Health claim review

The older 194-conversation Health handover was processed into a detailed local file containing hashes, hashed pointers, risk classes and priorities only. The repository stores the bounded summary, category counts and Merkle roots.

This is pattern triage, not clinical validation. No raw claim text, names, medical values or direct identifiers are committed.

Synthetic care journeys verify pseudonymous subjects, scoped consent, diagnostic hashes, regimen references, blocked devices, official-source provider references, unreviewed interventions remaining not started, hash-only claim queueing, consent withdrawal and clinician packets without raw medical values.

## Cost + $1 profiles and workflow

The local profile store adds customer, workshop, vehicle, supplier and order records. Direct names and contact values are rejected; fields must use pointer/reference schemes. Vehicle identifiers use hashes. The synthetic route exercises supplier splitting, side-locker allocation and approved-policy billing without supplier, Xero, payment, scanner, driver or production calls.

## Remaining projects

| Project | Direct export denominator | Current bounded state |
|---|---:|---|
| XRP Tracking New | 83 chats / 32,239 messages | Historical XRP/finance bucket linked; direct message mapping continues |
| Longevity Plan | 6 / 2,614 | Shared restricted-health bucket counted; direct separation pending |
| Tax | 8 / 8,672 | Shared tax/trust bucket counted; direct separation and current-law verification pending |
| Active Trust | 17 / 11,478 | Shared tax/trust bucket counted; direct separation and adviser review pending |
| Finance Planning | 132 / 17,356 | Shared finance bucket counted; direct mapping pending |
| Financial New | 12 / 8,835 | Shared finance bucket counted; direct mapping pending |

The shared buckets prove bounded progress only and do not merge tax, trust, finance or health decision authority.

## 18-layer local staging digital twin

Verified dimensions:

- privacy: direct-identifier keys fail closed;
- security: secret-like keys fail closed;
- persistence: SQLite layer-event ledger;
- retry: one transient Layer 8 failure succeeds on the second attempt;
- backup: SQLite backup created;
- restore: one run and 18 events restored;
- cost: projected spend above the A$0 ceiling is blocked;
- rollback: all layer events removed with zero external side effects.

This is `DONE_VERIFIED_LOCAL_STAGING_SIMULATION`, not connected external staging.

## Rollback

Revert the V17 merge commit. All new runtime and registry files are additive. Package-export changes can be restored from Git history. No external state was created.
