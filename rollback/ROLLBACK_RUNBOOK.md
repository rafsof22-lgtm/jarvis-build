# V21 Rollback Runbook

1. Do not merge while checks/review are incomplete.
2. Before merge: close the V21 PR and delete the unmerged V21 branch only with owner approval; V19 main and V20 PR history remain unchanged.
3. After merge: revert the V21 merge commit through a dedicated rollback PR; do not rewrite history.
4. Restore prior tracker pointers to V19/V20 lineage.
5. Preserve all local source/evidence packs and hashes.
6. No runtime/provider rollback is required because this V21 phase creates governance/search/registry repository artifacts only.
