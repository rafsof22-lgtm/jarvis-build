# JARVIS Forensic Task Map — V21 Candidate

| Task ID | Priority | Task | Dependency | Current state | Evidence | Exit criterion |
|---|---:|---|---|---|---|---|
| V21-001 | P0 | verify canonical governance and repo state | none | DONE_VERIFIED_READ_ONLY | constitution/master/module/continuity files; main `3d5e7344706cae2909ebad2aa540078464285db2` | source refs recorded |
| V21-002 | P0 | verify V20 open PR lineage | V21-001 | DONE_VERIFIED_READ_ONLY | PR #105, head `334f4d39a51fbcb536d8db83d7bf5b7c739d85ed`, mergeable | no duplicate V20 work |
| V21-003 | P0 | recover and verify 23 July source database | none | DONE_VERIFIED_LOCAL | DB SHA `dcf640212e38e5d0fc3c5b229734a735ee9c174bca836633b1b1a098da4f164d`, SQLite integrity ok | manifest/counts reconcile |
| V21-004 | P0 | register target-builder-overlay correction | V21-001 | SPEC_ONLY_CANDIDATE | current human-owner instruction | approved constitution/master-spec append |
| V21-005 | P0 | create root compatibility constitution | V21-004 | CREATED_BRANCH_NOT_MERGED | `CONSTITUTION.md` | deterministic verifier pass and PR review |
| V21-006 | P0 | compile Mammoth V21 spec | V21-003, V21-004 | CREATED_BRANCH_NOT_MERGED | consolidated spec | coverage matrix and no-gaps status |
| V21-007 | P0 | create request compiler and role council | V21-004 | CREATED_BRANCH_NOT_MERGED | two control-overlay specs | scenario and separation tests |
| V21-008 | P0 | create project/module/Skill registers | V21-003 | CREATED_BRANCH_NOT_MERGED | registers | low-confidence review plan |
| V21-009 | P0 | reconcile native and flattened source denominators | V21-003 | BLOCKED_PARTIAL | flattened source lacks native IDs/tree | native export or mapping-bearing source |
| V21-010 | P0 | review 383 low-confidence placements | V21-008 | BACKLOGGED | review queue CSV | accepted/corrected/excluded decisions |
| V21-011 | P1 | map 1,069 applicability links to requirements | V21-010 | BACKLOGGED | applicability matrix | accepted or excluded with reason |
| V21-012 | P1 | preserve/supersede V20 candidate | V21-002 | DECISION_RECORDED | V21 branches from #105 head | close #105 only after V21 approval/merge |
| V21-013 | P1 | create V21 branch/draft PR | V21-012 | IN_PROGRESS_BRANCH_CREATED | branch and tree objects | commit, PR, checks |
| V21-014 | P1 | run repository regression/security suite | V21-013 | PENDING_PR | verifier plan | required checks pass |
| V21-015 | P2 | authenticated staging reconciliation | V21-014 | BLOCKED_AT_EXACT_STEP | V19/V20 blockers | IAM/secrets/endpoints/DB/budgets/rollback approved |
| V21-016 | P5 | canary and production | V21-015 | NOT_AUTHORISED | constitution gate | separate owner approval and acceptance |
