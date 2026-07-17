# GitHub Secret Preflight Checklist

Last updated: 2026-07-17

## Purpose

This checklist supports the repo-side secret preflight workflow without exposing values. It maps user-provided `Google` and `Google2` GitHub Actions secrets into the Google/Gmail/Drive/Calendar candidate family and keeps deployment blocked until values are placed and validated safely.

## Important GitHub behavior

GitHub repository secret names are case-insensitive when referenced and are stored as uppercase. If a secret is typed into GitHub as `Google`, workflows should treat it as `GOOGLE`. If a secret is typed as `Google2`, workflows should treat it as `GOOGLE2`.

This repo therefore reads:

```text
GOOGLE
GOOGLE2
```

## Safety boundary

- Do not paste secret values into chat, commits, docs, workflow logs, issue comments, PR comments, or `.env.example`.
- Use GitHub Actions repository secrets for repo-side workflows.
- Use Railway variables, n8n credentials, or provider stores for runtime/provider secrets when deployment is approved.
- Run `.github/workflows/secret-preflight.yml` manually only.
- The preflight checks presence and safe shape only. It does not prove Google, Gmail, Drive, Calendar, or Sheets permission.
- No deployment, paid infrastructure, send action, Calendar write, Gmail send, Drive write, or destructive action is part of this checklist.

## Manual GitHub Secrets already expected

Go to: Repo -> Settings -> Secrets and variables -> Actions -> New repository secret

| Status | Secret | Used for | Where to get it | Where to place it | Safe test |
|---|---|---|---|---|---|
| 📍 place-in-github-secrets | `GOOGLE` | Google/Gmail/Drive/Calendar candidate bundle or alias. GitHub may show this even if entered as `Google`. | https://console.cloud.google.com/apis/credentials | GitHub repository secret | `secret-preflight` workflow |
| 📍 place-in-github-secrets | `GOOGLE2` | Second Google-family candidate secret or alias. GitHub may show this even if entered as `Google2`. | https://console.cloud.google.com/apis/credentials | GitHub repository secret | `secret-preflight` workflow |

## What the classifier distinguishes

The workflow runs `scripts/google_secret_preflight.py`. It can inspect `GOOGLE` and `GOOGLE2` inside GitHub Actions without printing values and label them as:

- `service-account JSON candidate`
- `OAuth client/refresh-token bundle candidate`
- `API-key JSON candidate`
- `JSON key/value bundle candidate`
- `.env/key-value pasted bundle candidate`
- `possible service-account/private-key pasted bundle`
- `single API-key/token candidate`
- `unknown Google secret format`
- `missing`

If you pasted several lines into `GOOGLE` or `GOOGLE2`, such as:

```text
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REFRESH_TOKEN=...
```

then the workflow should report only the detected key names, not the values.

## Supported conventional key names

The classifier recognizes these Google-family key names when they appear inside a pasted bundle or as separate repository secrets:

```text
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
GOOGLE_REFRESH_TOKEN
GOOGLE_SERVICE_ACCOUNT_JSON
GOOGLE_APPLICATION_CREDENTIALS
GOOGLE_API_KEY
GOOGLE_AI_API_KEY
GOOGLE_GEMINI_API_KEY
GMAIL_CLIENT_ID
GMAIL_CLIENT_SECRET
GMAIL_REFRESH_TOKEN
GMAIL_API_KEY
GOOGLE_DRIVE_CLIENT_ID
GOOGLE_DRIVE_CLIENT_SECRET
GOOGLE_CALENDAR_CLIENT_ID
GOOGLE_CALENDAR_CLIENT_SECRET
GOOGLE_CUSTOM_SEARCH_API_KEY
GOOGLE_CUSTOM_SEARCH_CX
YOUTUBE_API_KEY
GOOGLE_VISION_API_KEY
GOOGLE_SHEET_ID
GOOGLE_DRIVE_FOLDER_ID
```

## What cannot be done automatically

GitHub Secrets are write-only after saving. The repo and workflow can use them at runtime, but this agent cannot read their raw values back out and cannot safely split one pasted secret into multiple new GitHub Secrets without the values.

The safe automation path is therefore:

1. Keep the raw pasted values in `GOOGLE` and `GOOGLE2`.
2. Run `Secret preflight`.
3. Use the summary to see what each secret appears to contain.
4. Add a later runtime adapter that consumes `GOOGLE` / `GOOGLE2` directly, or manually create separate conventional secrets from your original local source if a specific service needs them.

## Current repo proof boundary

- Top-level `.env.example` contains safe blank placeholders only.
- `.github/workflows/secret-preflight.yml` is manual-only and does not deploy.
- Existing service-level `.env.example` files still define module-specific runtime variables.
- Secret presence in GitHub Actions does not prove credential validity, provider scopes, quota, billing, Railway configuration, n8n configuration, or live runtime readiness.

## Remaining manual steps

1. Confirm `GOOGLE` and/or `GOOGLE2` exist in GitHub repository secrets. Do not paste values into chat.
2. Run the `Secret preflight` workflow manually from GitHub Actions.
3. Review the workflow summary for names and shape labels only.
4. Only after preflight passes, decide which runtime or service should consume the credential and whether a read-only Google/Gmail/Drive/Calendar smoke test should be added.
