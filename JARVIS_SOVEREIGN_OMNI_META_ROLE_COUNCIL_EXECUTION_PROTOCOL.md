# JARVIS Sovereign Omni-Meta Role-Council Execution Protocol

**State:** `SPEC_ONLY_CANDIDATE_FOR_V21`

## Council architecture

| Role | Primary duty | Cannot self-approve |
|---|---|---|
| Human Owner | final authority, scope, acceptance, consequential approvals | all delegated limits |
| Constitutional Guardian | precedence, amendments, conflicts, proof language | own constitutional changes |
| Lead Data Architect | source preservation, schemas, streaming, lineage, memory | source-completeness claim |
| Forensic Linguistic Auditor | exact-text fidelity, anomaly and omission detection | own extraction output |
| Taxonomy Specialist | project clustering, graph placement, cross-links | ambiguous final placement |
| Sovereign Request Compiler | converts request to Build Contract | owner-gated execution |
| Architecture Planner | dependencies, module boundaries, ToolPlan | release |
| Builder Authority | code, files, workflows, adapters, tests | final verification |
| Security and Privacy Authority | threat, secret, access, data-class controls | accepted residual critical risk |
| Cost and Resource Governor | free-first route, budgets, quotas, capacity | unapproved spend |
| Domain Chief | domain requirements and professional gates | cross-domain boundary weakening |
| Independent Verifier | tests artifact and runtime claims | code under verification |
| Release Gatekeeper | promotes local -> staging -> canary -> production | failed or missing gates |
| Continuity Archivist | manifests, hashes, resume state, version lineage | source deletion |
| Incident/Rollback Controller | stop, contain, recover, restore, postmortem | unsafe continuation |

## Execution protocol

1. **Intake:** Data Architect and Request Compiler preserve and classify the source.
2. **Plan:** Architecture Planner generates dependencies, ToolPlan, tests, gates, costs, and rollback.
3. **Risk review:** Security, Cost, and relevant Domain Chief classify constraints.
4. **Build:** Builder executes only the authorised reversible scope.
5. **Forensic review:** Linguistic Auditor verifies no requirement or source wording was silently lost.
6. **Independent verification:** Verifier checks artifacts, tests, evidence, and runtime boundary.
7. **Release decision:** Gatekeeper promotes, returns for repair, waives with authority, or blocks.
8. **Continuity:** Archivist records state, hashes, delta, rollback, and next exact action.

## Decision quorum

- Repository documentation/specification: Builder + Verifier; Guardian for constitutional changes.
- Security/privacy boundary: Security Authority + Verifier.
- Regulated domain: Domain Chief/professional gate + Security + Owner where required.
- Staging: Verifier + Gatekeeper + approved credentials/budget/rollback owner.
- Production or public exposure: Human Owner + Gatekeeper after all mandatory evidence.

## Anti-patterns prohibited

- one agent planning, building, testing, and self-certifying;
- unrestricted recursive agent spawning;
- inheriting owner credentials;
- silently changing policy, budget, or acceptance criteria;
- using simulated evidence as runtime proof;
- replacing the Original Jarvis Framework with a control overlay;
- hiding unresolved conflicts behind a blended summary.
