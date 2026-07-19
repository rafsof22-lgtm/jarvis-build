# Skill Update and Release Governance

## Automatic update candidate rule
When a substantive Jarvis request exposes a durable reusable correction, rule, workflow, trigger, source class, capability category, safety boundary, tool route, evidence requirement, or repeated failure, classify it as a `SKILL_UPDATE_CANDIDATE`.

Do not silently mutate the installed skill or claim permanent cross-chat activation. Instead:
1. capture the verbatim source pointer;
2. compare it against the installed skill and current canonical source;
3. create an additions-only delta;
4. classify affected entrypoint/references/scripts/metadata/tests;
5. preserve conflicts and prior versions;
6. implement and test in an isolated skill source;
7. validate and package the complete skill as `skill.zip`;
8. provide exact install/upload action when direct installation is unavailable;
9. record version, hash, delta, tests, evidence, rollback, and install status.

## Update triggers
Run the update-candidate check on `UPDATE`, `VERIFY`, `ZERO`, `SYNC`, `CONTINUE`, `RESUME`, `SCAN`, major architecture or deployment work, repeated user corrections, and whenever a missing durable instruction is discovered. Skip one-off facts and unrelated requests.

## No-loss update protocol
Inventory every existing skill file and hash where possible. Preserve all prior files unless a direct improvement, verified supersession, security repair, or deduplication is documented. Never return a partial patch when the requested deliverable is an updated skill. The final package must include `SKILL.md`, `agents/openai.yaml`, all referenced resources/scripts/assets, a delta report, validation results, and a source-preservation manifest.

## Validation
Check frontmatter, trigger description, reference paths, script syntax/execution, package size, sensitive-value detection, duplicate or contradictory rules, evidence-chain validators, and representative use cases. Package only after validation passes. If local packaging is blocked, use an approved CI workflow or return the exact blocker; do not fabricate a ZIP.

## Release states
Use `DELTA_CAPTURED`, `SOURCE_RECONCILED`, `IMPLEMENTED_NOT_VALIDATED`, `VALIDATED_NOT_PACKAGED`, `PACKAGED_NOT_INSTALLED`, `INSTALLED_UNVERIFIED`, `ACTIVE_VERIFIED`, or `BLOCKED`.

## Rollback
Keep the previous package/hash and a reversible change map. Never overwrite the only known-good package.
