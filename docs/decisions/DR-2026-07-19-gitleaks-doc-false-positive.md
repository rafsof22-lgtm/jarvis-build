# DecisionRecord: Documentation false-positive fingerprint

Date: 2026-07-19 Australia/Melbourne  
Status: accepted, narrowly scoped

## Finding
Gitleaks rule `generic-api-key` flagged line 24 of commit `3007b3806f0a2344d947c30f6c876029e48b6329` in `skills/jarvis-sovereign-builder/references/skill-update-and-release-governance.md`.

## Verification
The flagged content was prose describing validation for prohibited sensitive material. It contained no credential, token, password, private key, protected value, service identifier, or usable authentication material. The workflow diagnostic exposed only rule/path/commit/line/fingerprint and explicitly omitted matched values.

## Action
1. Rewrite the current prose to avoid the detector-like phrase.
2. Add only the exact historical fingerprint to `.gitleaksignore` because full-history scanning continues to encounter the superseded commit.
3. Do not disable `generic-api-key`, exclude the file/path, reduce scan depth, or weaken any other detector.
4. Continue full-history scanning and fail closed for every non-ignored finding.

## Rollback
Remove the fingerprint if branch history is later rewritten to eliminate the superseded false-positive commit, then rerun full-history scanning.
