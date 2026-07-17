# Jarvis GitHub Commit And Deploy Handoff

## Purpose

This file defines the exact handoff needed to commit and deploy the Jarvis hybrid model-router and control-registry updates through GitHub in the most efficient free-first or cheapest cost-effective paid way.

## Current Draft-Safe Work Completed

The following files are ready to commit into the Jarvis repo through the verified safe branch:

- `JARVIS_MODULE_REGISTRY.md`
- `JARVIS_SKILL_DEDUPE_MAP.md`
- `JARVIS_APP_RISK_APPROVAL_MATRIX.md`
- `JARVIS_DEPLOYMENT_TARGET_MATRIX.md`
- `JARVIS_OTHER_AGENT_UNIFICATION_WORKFLOW.md`
- `JARVIS_API_CHANNEL_RUNBOOK.md`
- `JARVIS_SCHEDULE_RUNBOOK.md`
- `JARVIS_OBSERVABILITY_AND_SMOKE_TEST_MATRIX.md`
- `JARVIS_HYBRID_MODEL_ROUTER_PLAN.md`
- `frameworks/UNIVERSAL_APEX_INFRASTRUCTURE_COST_PLANNING_FRAMEWORK.md`

## Verified GitHub Route

- Repository: `rafsof22-lgtm/jarvis-build`
- Base branch: `main`
- Work branch: `jarvis/control-registry-model-router-plan`
- Commit strategy: branch + pull request, not direct `main` update
- Live deployment: blocked until workflow/host configuration and required secrets are proven available

## Remaining Commit Scope Decision

Default for this pass:

- Include control-registry, governance, deployment, API, schedule, observability, hybrid model-router, handoff, and universal infrastructure framework files.
- Do not include raw archives or unrelated source exports.
- Do not deploy live unless required secrets and host configuration are already proven.

## Recommended Commit Message

```text
Add Jarvis control registries and hybrid model-router plan
```

## Recommended PR Title

```text
Add Jarvis control registries, risk matrix, deployment matrix, and hybrid model-router plan
```

## Recommended PR Body

```markdown
## Summary

Adds durable Jarvis control files for module tracking, skill dedupe, app approval risk, deployment target selection, API channel safety, schedules, observability, other-agent unification, and hybrid model routing.

## Why

These files turn the setup gap audit into version-controlled operating structure and prepare Jarvis for free-first / cheapest-paid deployment and model-router implementation.

## Safety

- No secrets included.
- No live deployment performed.
- No app approval settings changed.
- No skills detached.
- No external infrastructure created.

## Next Steps

- Confirm provider secrets in GitHub Secrets or host secret store.
- Implement runtime model-router package.
- Add CI smoke tests.
- Deploy to Oracle Free Tier or chosen paid fallback after external host setup is ready.
```

## Required GitHub Secrets For Deployment

Use GitHub Secrets or provider secret stores. Never commit values.

Minimum model-router secrets:

- `OPENROUTER_API_KEY`
- `DEEPSEEK_API_KEY`
- `KIMI_API_KEY`
- `QWEN_API_KEY` or `DASHSCOPE_API_KEY`

Runtime/deployment secrets:

- `DATABASE_URL`
- `REDIS_URL`
- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_SSH_KEY`
- `MODEL_ROUTER_MAX_DAILY_COST_USD`
- `MODEL_ROUTER_REQUIRE_APPROVAL_ABOVE_USD`

Provider-specific optional secrets:

- `DIGITALOCEAN_ACCESS_TOKEN`
- `HOSTINGER_API_TOKEN` or equivalent
- `HERCULES_API_TOKEN` or equivalent
- Oracle Cloud deployment secrets if Oracle is used

## Best Free-First Deployment Path

1. Commit docs/control files to GitHub branch.
2. Add/confirm `.env.example` names only.
3. Implement model-router package with mock providers first.
4. Add GitHub Actions tests.
5. Place secrets in GitHub Secrets.
6. Deploy to Oracle Cloud Free Tier if the host is externally prepared.
7. Use local Ollama workers for zero-token background work when available.

## Cheapest Paid Fallback

1. Hetzner-class VPS for persistent runtime if Oracle is blocked.
2. DigitalOcean if ease/current integration matters more than lowest price.
3. Hostinger or Hercules if the deliverable is mainly a website/app surface.
4. OpenRouter/LiteLLM for cheap provider switching.

## Deployment Readiness Checklist

- [x] Repo confirmed: `rafsof22-lgtm/jarvis-build`
- [x] Branch confirmed: `jarvis/control-registry-model-router-plan` against `main`
- [x] GitHub write requested by user for this branch/PR workflow
- [ ] Secrets stored outside chat
- [ ] CI workflow passes
- [ ] Runtime health endpoint exists
- [ ] Smoke tests pass
- [ ] Deployment host confirmed
- [ ] Rollback path confirmed
- [ ] Cost guard configured

## Current Blocker

Live deployment cannot safely proceed until the repo's deployment workflow, host target, and required secrets are proven in GitHub Secrets or provider secret stores. Do not expose or request secret values in chat.
