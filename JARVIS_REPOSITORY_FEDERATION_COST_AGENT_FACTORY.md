# Jarvis Repository Federation, Cost Governor and Agent/Skill Factory

## Purpose

Preserve all existing Jarvis repositories as independently usable systems while connecting them to one sovereign control plane. Minimise ChatGPT credits, model tokens, build credits and infrastructure spend without reducing required capability, safety, quality, verification, rollback or live-preview freedom.

## Repository federation

Jarvis uses a federated multi-repository architecture rather than a destructive monorepo migration.

Each repository retains:

- its own source history and rollback points;
- independent local editing and preview;
- independent CI/CD and deployment target;
- module-local secrets, scopes and data boundaries;
- independent health, readiness and deployment status;
- the ability to run while other modules are changed or unavailable.

Shared capabilities are exposed through versioned contracts:

- API schemas and MCP tool contracts;
- event envelope and workflow state schema;
- identity and authorization claims;
- evidence and run identifiers;
- health, readiness, cost and dependency schema;
- shared source, requirement, module, agent, skill and integration registries.

No repository is renamed, moved, archived, deleted, absorbed or made dependent on another repository without migration tests, rollback and explicit evidence.

## Credit and cost governor

### Route order

1. Reuse an existing verified result, cache, artifact or source extract.
2. Use deterministic local software or a repository script.
3. Use a connected native tool already covered by the user's ChatGPT plan.
4. Use local browser/editor preview, local Docker and local databases.
5. Use local open models through Ollama or llama.cpp.
6. Use free public-repository GitHub Actions where data sensitivity permits.
7. Use a free preview/static/serverless tier that satisfies the task.
8. Use an existing paid service before creating another paid service.
9. Use the lowest-cost qualified paid model or host.
10. Use premium models, panels or GPU compute only when a measured quality gap justifies them.

### Required controls

- per-task estimated and actual credits/tokens/cost;
- provider and model allowance tracking;
- hard and soft budget caps;
- cache hit rate and avoided-call accounting;
- deterministic substitution detector;
- batch and dedupe before model calls;
- cheap-model-first escalation with quality gates;
- automatic pause before unexpected billable usage;
- provider fallback and circuit breaker;
- monthly free-tier and pricing revalidation;
- vendor-exit and export path.

### Current preferred free stack

- GitHub and GitHub Actions for source control and public non-sensitive CI.
- Local VS Code/Cursor-compatible editing, Git, Docker, Node, Python and browser preview.
- Ollama or llama.cpp for private zero-token local workers.
- Cloudflare Pages/Workers free tier for compatible previews, lightweight gateways and event functions.
- Oracle Cloud Always Free for the future always-on controller after account and host setup.
- Existing Vercel, Railway and DigitalOcean services stay in service until a tested alternative is demonstrably cheaper and equal or better.

## Continuous source and capability scout

Scheduled and event-triggered scouts monitor official sources first for:

- model, framework, runtime and tool releases;
- API, SDK, MCP and connector changes;
- free-tier, credit, quota and price changes;
- security advisories, CVEs and unsafe dependency changes;
- better open-source components and reference implementations;
- deprecations, provider shutdowns and lock-in risks;
- new evaluation, observability, memory, orchestration and deployment techniques;
- lawful competitor feature and workflow patterns.

Each candidate receives:

- source and version;
- license and commercial-use status;
- security and supply-chain review;
- capability and compatibility score;
- cost and credit score;
- latency and reliability score;
- maintenance and lock-in score;
- baseline comparison;
- recommended action: reject, watch, quarantine, test, canary or promote.

No candidate enters production merely because it is new, popular, hidden or described as a hack.

## Elastic agent mesh

Jarvis may expand into many parallel agents through bounded worker pools.

Every agent requires:

- unique ID, purpose, owner and template version;
- one primary skill set and only necessary supporting skills;
- allowed tools, denied tools and data scope;
- isolated workspace and memory partition;
- task, token, credit, time, retry and concurrency limits;
- dependencies and parent/child relationships;
- health, heartbeat and stuck-job detection;
- tests, evidence and independent verifier;
- safe stop, cancellation, cleanup and rollback;
- automatic retirement, suspension or return to pool.

Prohibited:

- unlimited recursive spawning;
- inherited owner credentials;
- self-escalation of permissions or budgets;
- production self-modification without release gates;
- unbounded retries or untracked paid calls;
- silent skill installation or execution from unreviewed sources.

## Governed skill factory

When Jarvis detects a recurring capability gap, it may generate or acquire a skill using:

`detect gap -> search existing approved skills -> search official/public candidates -> quarantine -> inspect -> generate/adapt -> unit test -> security test -> quality/cost/latency evaluation -> canary -> independent verification -> approve/store -> route on demand -> monitor -> update/rollback/retire`

Every stored skill requires:

- immutable version and hash;
- source, author, license and provenance;
- triggers and negative boundaries;
- module and agent ownership;
- required tools, permissions and secret names;
- dependency lock and network/file-system behavior;
- test fixtures and expected outputs;
- quality, latency, token and cost baseline;
- security review and expiry date;
- rollout, rollback and deprecation path.

Skills are stored in approved, custom, quarantine, rejected and superseded-preserved states. They are loaded only when a task requires them.

## Lawful high-execution discovery

Requests for hidden techniques, loopholes, hacks or guru methods are interpreted as requests for underused but lawful and security-reviewed optimisations, advanced official features, open-source patterns, cost-saving configurations and operational best practices.

Jarvis must not:

- bypass payment, authentication, access controls, rate limits or provider policies;
- use stolen or leaked credentials;
- evade billing, licensing, KYC or legal requirements;
- copy proprietary code or private implementations;
- weaken security or owner authority for convenience.

## Claw-style control modules

Jarvis may implement bounded claw-style modules that actively detect and act on:

- stuck jobs and failed workflows;
- cost spikes and credit depletion;
- broken integrations and expired credentials;
- source freshness gaps and deprecations;
- security findings and dependency risks;
- idle resources and duplicated services;
- missing tests, evidence and rollback;
- new capability gaps and high-value automation opportunities.

Each claw module must use policy limits, evidence, reversible actions, rate limits, audit logs and escalation rules.

## Release gate

A new agent, skill, tool, model route, integration or autonomous claw is promoted only after:

- defined acceptance criteria;
- security and permission review;
- cost and credit budget approval;
- isolated tests and baseline comparison;
- canary operation;
- independent evidence review;
- rollback verification;
- registry and change-log updates.
