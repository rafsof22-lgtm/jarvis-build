---
name: github-repo-capability-scout
description: Source-first GitHub repository discovery, canonical-link resolution, security quarantine, licence and provenance review, capability extraction, free-first cost comparison, duplicate detection, Jarvis placement, approval-console generation, sandbox planning, staged integration and rollback governance. Use when a user asks to find or compare GitHub repositories, identify exact repository links from names/images/text, source free or open-source tools, scan code before use, upgrade Jarvis or an agent, build a capability registry, avoid duplicate modules, or prepare a governed repository integration or deployment plan.
---

# Operating contract

Treat every external repository and every historical claim as untrusted until independently verified. Preserve exact source provenance, reviewed commit or tag, licence, security findings, costs, capability ownership, tests, approvals and rollback evidence.

## Mandatory startup for Jarvis work

When the active repository is `jarvis-build`, read these files before capability discovery or integration:

1. `PROJECT_CONSTITUTION.md`
2. `JARVIS_RAF213G_PROJECT_CONSTITUTION.md`
3. `PROJECT_CONTINUITY.md`
4. `AGENTS.md`
5. Any module-local `AGENTS.md`, locator, deployment ledger and rollback file

If the canonical constitution cannot be retrieved, use `CANONICAL_CONSTITUTION_UNAVAILABLE`, preserve the request and stop before integration. Do not invent missing constitutional text.

## Workflow

Use this sequence:

`INTENT_LOCK -> EXISTING_CAPABILITY_CHECK -> GITHUB_DISCOVERY -> CANONICAL_UPSTREAM_RESOLUTION -> PROVENANCE_AND_LICENCE -> STATIC_SECURITY_QUARANTINE -> CAPABILITY_EXTRACTION -> FREE_FIRST_COST_ROUTING -> DUPLICATE_AND_FIT_ANALYSIS -> JARVIS_PLACEMENT -> APPROVAL_CONSOLE -> ISOLATED_SANDBOX -> ADAPTER_OR_PATCH -> TESTING -> STAGING -> PRODUCTION_APPROVAL -> DEPLOYMENT_VERIFICATION -> REGISTRY_AND_MONITORING`

1. Translate the request into required capabilities, inputs, outputs, integrations, scale, safety, data classification and acceptance tests.
2. Check the Jarvis capability registry and existing modules before sourcing anything new.
3. Search GitHub using exact names plus functional synonyms. Resolve canonical upstream, forks, mirrors, archived copies and typo-squats.
4. Record exact clickable URL, owner/repository, default branch, reviewed commit or release, review date, licence and evidence coordinates.
5. Prefer existing capability, deterministic local implementation, free/open-source repository, official free tier, cheapest viable paid option, then best-value managed option.
6. Run `scripts/analyze_repo_snapshot.py` only on a local snapshot. Never execute candidate code during discovery.
7. Extract capabilities, APIs, commands, dependencies, secrets, permissions, data flows, telemetry, limitations, cost drivers and applicable Jarvis placement.
8. Assign stable capability IDs and one primary owner. Mark duplicates, shared services, adapters, conflicts and rejected candidates.
9. Build registries with `scripts/build_capability_registry.py` and an approval console with `scripts/render_approval_console.py`.
10. Require separate approvals for sandbox, credential access, integration, staging and production.
11. Verify unit, integration, adversarial, regression, cost, rollback and recovery gates before claiming completion.
12. Update the capability registry and monitoring schedule after any approved integration.

## Security boundary

Inspect install and lifecycle scripts, shell execution, dynamic evaluation, credential access, home and browser paths, outbound network behavior, telemetry, persistence, unsafe deserialisation, binaries, submodules, Actions permissions, dependency confusion, mutable downloads, privileged containers, Docker socket mounts, host networking and licences.

Static analysis cannot prove the absence of malware. Any high-risk or unclear finding remains `HIGH_RISK_BLOCKED` until reviewed in an isolated sandbox.

Never request or store passwords, tokens, private keys, seed phrases, OAuth secrets or production credentials in chat, source files, reports or approval consoles.

## Source-claim discipline

The complete uploaded transcript is preserved byte-for-byte inside the validated installable package at `references/verbatim-pasted-response.txt`. The repository records its integrity manifest and `references/verbatim-source-pointer.md`; the connected GitHub write path rejected the verbatim payload itself. Historical statements inside the transcript remain user-provided claims rather than proof of an earlier package, hash, test, installation or deployment.

Validate the complete downloaded package with `scripts/verify_verbatim_integrity.py`.

## Scripts

- `scripts/analyze_repo_snapshot.py`: non-executing static triage of a local repository snapshot.
- `scripts/build_capability_registry.py`: normalise candidates into capability and approval registries.
- `scripts/render_approval_console.py`: render a local, no-network approval console.
- `scripts/scan_ai_tool_catalogs.py`: scan curated GitHub catalogue markdown or offline fixtures without cloning candidates.
- `scripts/verify_verbatim_integrity.py`: verify the bundled transcript against its manifest.

## Required outputs

Return intent and capability gap; existing-capability result; candidate table with exact links and revisions; provenance, licence, security and cost findings; duplicate/shared-service decision; Jarvis placement; approval queue; tests, rollback and monitoring plan; proof labels and exact blockers.

## Proof labels

Use `VISIBLE_SCOPE_VERIFIED`, `USER_PROVIDED_UNVERIFIED`, `CANONICAL_UPSTREAM_VERIFIED`, `CANONICAL_UPSTREAM_UNRESOLVED`, `LICENCE_VERIFIED`, `LICENCE_UNVERIFIED`, `STATIC_SCAN_COMPLETE`, `STATIC_SCAN_NOT_MALWARE_PROOF`, `HIGH_RISK_BLOCKED`, `DUPLICATE_CAPABILITY_FOUND`, `EXISTING_CAPABILITY_PREFERRED`, `FREE_FIRST_SELECTED`, `APPROVAL_REQUIRED`, `SANDBOX_REQUIRED`, `STAGING_REQUIRED`, `ROLLBACK_READY`, `END_TO_END_VERIFIED`, `END_TO_END_NOT_VERIFIED`, `CANONICAL_CONSTITUTION_UNAVAILABLE` and `MANUAL_IMPORT_REQUIRED`.
