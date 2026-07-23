# Jarvis V21: sync Builder evidence, search audit, and deployment gates

## Outcome

Synchronises the V21 Builder evidence layer without replacing the Original Jarvis Framework. The branch incorporates V20 PR #105 history, adds target/builder/overlay separation, performs deterministic privacy-safe request extraction, generates the required canonical registries, adds a local search tool and tests, and records deployment/approval gates.

## Source and mapping proof

- 2669 flattened conversations / 97589 messages;
- 1508 Jarvis-relevant candidate conversations;
- 42994 / 42994 candidate user messages mapped;
- 33322 assistant commitments extracted;
- 14194 blocker/open-loop records extracted;
- mapping root `7d0cd7a21558fc39dadca23e4acf88b9181c8853090386559270e2dcccf4b698`;
- no raw private chat text committed.

## Files

Includes constitution compatibility entry, request compiler, role council, Mammoth spec, master spec compatibility file, module/project/Skill registers, required registries, search tool/tests, tracker, completion plan/state, deployment/approval/evidence/gap ledgers, rollback and resume prompt.

## PR #105 disposition

This branch starts from PR #105 head and therefore includes its V20 changes. Keep #105 open during review; after V21 is explicitly approved and merged, close #105 as superseded. Do not merge both independently.

## Verification

- deterministic mapping denominator and registry checks;
- search tool unit tests and actual-DB smoke;
- JSON/CSV/Markdown validation;
- unsupported completion-claim and secret-assignment scans;
- existing repository CI/security/historical verifier compatibility required.

## Truth boundary

This PR does not prove native ChatGPT tree metadata, resolve 383 low-confidence classifications or 1,069 applicability decisions, deploy authenticated staging, authorise production, or close owner-acceptance gates.

## Merge gate

Do not merge without explicit owner approval after required checks are green, secret/security review passes, rollback is accepted, and deployment impact is understood.
