# GitHub Secret Preflight Checklist

Last updated: 2026-07-17

## Purpose

This checklist supports the repo-side secret preflight workflow without exposing values. It maps user-provided `Google` and `Google2` GitHub Actions secrets into the Google/Gmail/Drive/Calendar candidate family and keeps deployment blocked until values are placed and validated safely.

## Safety boundary

- Do not paste secret values into chat, commits, docs, workflow logs, issue comments, PR comments, or `.env.example`.
- Use GitHub Actions repository secrets for repo-side workflows.
- Use Railway variables, n8n credentials, or provider stores for runtime/provider secrets when deployment is approved.
- Run `.github/workflows/secret-preflight.yml` manually only.
- The preflight checks presence and safe shape only. It does not prove Google, Gmail, Drive, Calendar, or Sheets permission.
- No deployment, paid infrastructure, send action, Calendar write, Gmail send, Drive write, or destructive action is part of this checklist.

## Manual GitHub Secrets needed

Go to: Repo -> Settings -> Secrets and variables -> Actions -> New repository secret

| Status | Secret | Used for | Where to get it | Where to place it | Safe test |
|---|---|---|---|---|---|
| 📍 place-in-github-secrets | `Google` | Google/Gmail/Drive/Calendar candidate bundle or alias | https://console.cloud.google.com/apis/credentials | GitHub repository secret | `secret-preflight` workflow |
| 📍 place-in-github-secrets | `Google2` | Second Google-family candidate secret or alias | https://console.cloud.google.com/apis/credentials | GitHub repository secret | `secret-preflight` workflow |

## Supported alias names

The workflow checks these Google-family alias names without printing values:

```text
GOOGLE
Google
GOOGLE2
Google2
GMAIL
Gmail
```

The workflow also supports conventional explicit names:

```text
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
GOOGLE_REFRESH_TOKEN
GOOGLE_SERVICE_ACCOUNT_JSON
GOOGLE_APPLICATION_CREDENTIALS
GMAIL_CLIENT_ID
GMAIL_CLIENT_SECRET
GMAIL_REFRESH_TOKEN
GMAIL_API_KEY
GOOGLE_DRIVE_CLIENT_ID
GOOGLE_DRIVE_CLIENT_SECRET
GOOGLE_CALENDAR_CLIENT_ID
GOOGLE_CALENDAR_CLIENT_SECRET
```

## Safe shape labels

The manual preflight can classify the selected raw Google candidate as one of these labels without printing the value:

- `service-account JSON candidate`
- `OAuth client/refresh-token bundle candidate`
- `API-key candidate`
- `unknown Google secret format`
- `missing`

## Current repo proof boundary

- Top-level `.env.example` contains safe blank placeholders only.
- `.github/workflows/secret-preflight.yml` is manual-only and does not deploy.
- Existing service-level `.env.example` files still define module-specific runtime variables.
- Secret presence in GitHub Actions does not prove credential validity, provider scopes, quota, billing, Railway configuration, n8n configuration, or live runtime readiness.

## Remaining manual steps

1. Place `Google` and/or `Google2` in GitHub repository secrets. Do not paste values into chat.
2. Optionally place explicit conventional Google/Gmail/Drive/Calendar secrets if the alias bundle is not enough.
3. Run the `Secret preflight` workflow manually from GitHub Actions.
4. Review the workflow summary for names and shape labels only.
5. Only after preflight passes, decide which runtime or service should consume the credential and whether a read-only Google/Gmail/Drive/Calendar smoke test should be added.
