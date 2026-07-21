# GitHub Actions Secrets Setup

## Purpose - plain meaning - Example

GitHub Actions secrets hold private values outside the repository. Example: add `VTI_EVENT_SIGNING_SECRET` in GitHub Settings, never in a file or issue.

## Where to add each value

1. Open the target GitHub repository.
2. Select **Settings**.
3. Select **Secrets and variables**.
4. Select **Actions**.
5. Select **New repository secret**.
6. Enter the exact name shown by the `Jarvis Secret Readiness` workflow.
7. Paste the value once and save it.

## Required names

### Jarvis Health
- `JARVIS_HEALTH_BASE_URL`
- `JARVIS_HEALTH_MCP_BEARER_TOKEN`

### VTI to Hub staging
- `HUB_STAGING_BASE_URL`
- `VTI_STAGING_BASE_URL`
- `HUB_VTI_EVENT_ENDPOINT`
- `VTI_EVENT_SIGNING_SECRET`

### Property Sheets fallback
- `PROPERTY_GOOGLE_SHEET_ID`
- `PROPERTY_GOOGLE_SHEETS_WEBHOOK_URL`
- `PROPERTY_GOOGLE_SHEETS_WEBHOOK_SECRET`

### VTI Cobalt
- `VTI_COBALT_BASE_URL`
- `VTI_COBALT_ACCESS_TOKEN`

### Optional model gateway
- `OPENROUTER_API_KEY`

## Safety rules

- Never paste values into chat, GitHub issues, commits, pull requests or logs.
- Use separate staging and production values.
- Give each value the smallest possible scope.
- Rotate a value after suspected exposure.
- Revoke unused values.
- Do not enable billing or production promotion automatically.

## Verification

Run **Actions -> Jarvis Secret Readiness -> Run workflow**. The report shows names as present or missing. It never prints or stores the values.
