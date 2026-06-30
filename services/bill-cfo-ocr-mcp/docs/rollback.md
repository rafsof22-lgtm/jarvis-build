# Bill CFO OCR MCP Rollback

## Repo rollback

Revert the commit that introduced or changed files under `services/bill-cfo-ocr-mcp/`. This service is isolated from other roots, so rollback should not touch unrelated services.

## Railway rollback

1. In Railway, open the Bill CFO OCR MCP service only.
2. Roll back to the prior successful deployment or disconnect the service root if it was created only for testing.
3. Do not alter XRP/HBAR Apex or other service variables.

## Secret handling

Never paste real secrets into chat or commit them to the repository. Rotate any secret that was accidentally exposed outside Railway, GitHub Secrets, or the approved vault.
