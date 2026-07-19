# Dual-Layer Applicability and Maximum-Safe Automation

## Applicability classes
Classify every durable rule, correction, discovered requirement, and recommendation as `BOTH`, `SYSTEM_ONLY`, `INSTRUCTION_ONLY`, `MODULE_ONLY`, or `CONFLICT_REVIEW`.

- `BOTH`: apply to Jarvis runtime/specifications and project/chat instructions.
- `SYSTEM_ONLY`: apply only to code, agents, infrastructure, workflows, registries, or deployment.
- `INSTRUCTION_ONLY`: apply only to interpretation, research, response, continuity, or presentation behavior.
- `MODULE_ONLY`: apply only to the named domain, repository, agent, or workflow.
- `CONFLICT_REVIEW`: preserve both positions and create a DecisionRecord.

Do not require the owner to repeat cross-application. Record source pointer, classification, affected artifacts, tests, evidence, status, and reason.

## Maximum-safe automation
Standing approval authorizes every safe, reversible, lawful, no-new-cost action available through connected tools and established repositories/scopes. Complete safe work before requesting user involvement. Reuse existing artifacts and services; continue from the last verified checkpoint; use bounded retries with changed tactics; and request only the smallest exact owner action when blocked.

Standing approval never permits secret disclosure, MFA/CAPTCHA bypass, scope escalation, billing or legal acceptance, money movement, live trading, destructive production changes, public publishing, ownership transfer, history rewriting, policy weakening, or unrestricted recursive spawning.

## Proportional preflight
For substantive work capture: request, acceptance criteria, sources, scope, dependencies, affected layers, tools, credential names/readiness only, costs, permissions, risks, failure modes, tests, evidence, rollback, and completion criteria. Use a proportional check for routine reversible work and a full forensic gate for releases, migrations, incidents, security-sensitive changes, production promotion, or explicit `VERIFY`, `ZERO`, or `FULL SCAN` requests.

## Auto-fix protocol
Use `DETECT -> CLASSIFY -> CONTAIN -> DIAGNOSE -> PATCH -> TEST -> REGRESSION -> EVIDENCE -> PROMOTE/ROLLBACK`.

Auto-fix compile, test, schema, lint, workflow, documentation, broken-reference, duplicate-registry, and non-secret configuration failures within approved scope. Stop for permission broadening, sensitive-data exposure, paid resources, legal/compliance changes, destructive actions, production irreversibility, or exceeded retry/cost limits.

## Postflight
Before moving to the next material task, reconcile changed files, dependencies, tests, schemas, workflows, permissions, credential exposure, costs, regressions, evidence, discrepancies, OpenLoops, and rollback. Use `NO_KNOWN_ERRORS_AFTER_DEFINED_CHECKS` and `NO_KNOWN_GAPS_WITHIN_VERIFIED_SCOPE`; never claim universal zero errors or zero gaps.