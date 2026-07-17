# Jarvis Deployment Readiness Blockers

## Current Status

Live deployment is intentionally blocked in this scaffold. The repository now has CI and a manual deployment-readiness workflow, but it does not prove an Oracle Free Tier host, VPS host, SSH identity, target path, firewall, Docker runtime, or provider secrets.

No workflow in this branch performs SSH, provider API calls, infrastructure creation, or paid deployment actions.

## Missing For Oracle Free Tier Readiness

The following must be created or confirmed outside the repository before live deployment steps can be added:

- `ORACLE_HOST`
- `ORACLE_SSH_USER`
- `ORACLE_SSH_PRIVATE_KEY`
- `ORACLE_DEPLOY_PATH`
- Oracle instance shape and region
- inbound firewall/network rule for the intended health-check port
- Docker or target runtime installed on the host
- rollback path and backup location

## Missing For Cheap VPS Readiness

The following must be created or confirmed outside the repository before VPS deployment steps can be added:

- `VPS_HOST`
- `VPS_SSH_USER`
- `VPS_SSH_PRIVATE_KEY`
- `VPS_DEPLOY_PATH`
- selected provider and monthly cost approval
- firewall/network rule for the intended health-check port
- Docker or target runtime installed on the host
- rollback path and backup location

## Optional Model Provider Secrets

Cloud model routes remain disabled until explicitly configured. Optional secrets include:

- `OPENROUTER_API_KEY`
- `DEEPSEEK_API_KEY`
- `KIMI_API_KEY`
- `QWEN_API_KEY`
- `OPENAI_API_KEY`

## Safe Next Gate

Run the deployment readiness workflow manually with `require_host=false` to list blockers without failing. Use `require_host=true` only after the target secrets are believed to exist.
