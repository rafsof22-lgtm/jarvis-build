# XRP/HBAR Apex Rollback

Last updated: 2026-06-30

## Files changed by scaffold completion

- `services/xrp-hbar-apex/scripts/smoke-test.sh`
- `services/xrp-hbar-apex/docs/deployment-ledger.md`
- `services/xrp-hbar-apex/docs/rollback.md`
- `services/xrp-hbar-apex/src/server.js` if route namespace aliases are patched

## Repo rollback

Revert only the commit or commits that changed files under `services/xrp-hbar-apex/` unless a separate shared-runtime change is proven. Do not roll back Bill CFO OCR MCP or any other service root while repairing XRP/HBAR.

## Disabling route aliases

If `/xrp-hbar-apex/health`, `/xrp-hbar-apex/ready`, or `/xrp-hbar-apex/deployment/status` causes runtime issues, revert the `src/server.js` alias patch only. Preserve the existing root-level routes:

- `/health`
- `/ready`
- `/deployment/status`

Root-level routes are the backward-compatible Railway health/readiness contract.

## Railway rollback placeholder

When a dedicated Railway service exists:

1. Open only the XRP/HBAR Apex Railway service.
2. Roll back to the last successful deployment or redeploy the prior known-good commit.
3. Verify `/health`, `/ready`, and `/deployment/status` after rollback.
4. Do not alter Bill CFO OCR MCP service variables, deploy branch, root directory, or domain.

## Secret handling

Never paste real secrets into chat or commit them to the repository. Rotate any secret that was accidentally exposed outside Railway, GitHub Secrets, or the approved vault.

## Proof warning

These rollback instructions are prepared repo-side guidance only. They are not proven live until a Railway service exists and rollback verification has passed with route-level proof.
