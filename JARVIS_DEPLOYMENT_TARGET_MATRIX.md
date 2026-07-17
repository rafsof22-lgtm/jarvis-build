# Jarvis Deployment Target Matrix

## Purpose

Use this matrix to choose the best deployment route for Jarvis modules and runtime services.

Default priority: free-first, cheapest cost-effective paid second, easiest reliable fallback third.

## Recommended Deployment Order

| Rank | Target | Best For | Cost Position | Automation Level | Use When | Main Blockers |
|---|---|---|---|---|---|---|
| 1 | ChatGPT Agent Builder + Memory + API channel | Control plane and command interface | Native/already available | High within Builder limits | Always keep as Jarvis command layer | Cannot replace core model with third-party models |
| 2 | GitHub | Source control, CI, PRs, deployment workflows | Free tier first | High | Always use as implementation spine | Control-registry route verified: `rafsof22-lgtm/jarvis-build`, base `main`, branch `jarvis/control-registry-model-router-plan` |
| 3 | Oracle Cloud Free Tier | Free always-on VPS/runtime | Free if available | Medium/High after setup | Best free always-on controller | External account/KYC/host setup and secrets |
| 4 | Local workstation/Ollama/llama.cpp | Zero-token local workers | Hardware sunk cost | Medium | Private/local bulk jobs and fallback workers | Requires local hardware uptime |
| 5 | Hetzner-class VPS | Cheapest strong paid VPS | Very cheap paid | High | Best long-run paid control | Account/payment/external setup |
| 6 | DigitalOcean | Easier paid VPS/deploy path | Moderate paid | High | When speed beats lowest cost | Cost and confirmation required |
| 7 | Hostinger | Fast website/app fallback | Low/moderate paid | Medium | Simple public site/app surface | Less control than VPS |
| 8 | Hercules | Fast app/site generation | Varies | Medium | Rapid app prototype | Confirm external publish/cost |
| 9 | Railway/Render/Fly-style PaaS | App deploy convenience | Paid/limited free | High | If repo-native PaaS is preferred | Cost and provider limits |
| 10 | AWS/Azure/GCP | Enterprise scale | High | High | Enterprise/institutional | Cost, complexity, lock-in |

## Free-First Default

1. Keep ChatGPT Agent Builder as the command/control plane.
2. Use GitHub free tier for repo, CI, branches, and PRs.
3. Use Oracle Cloud Free Tier for always-on runtime if account setup is possible.
4. Use local Ollama/llama.cpp workers for repetitive zero-token work where hardware exists.
5. Use OpenRouter/free model endpoints only when external model routing is needed.

## Cheapest Paid Default

1. Hetzner-class VPS for long-running runtime.
2. DeepSeek/Kimi/Qwen/OpenRouter cheapest capable models for worker tasks.
3. DigitalOcean only when ease/current integration matter more than lowest cost.
4. Burst GPU providers only for temporary GPU jobs.

## Required Secrets

- OPENROUTER_API_KEY
- DEEPSEEK_API_KEY
- KIMI_API_KEY or provider-compatible key
- QWEN_API_KEY or DASHSCOPE_API_KEY
- DATABASE_URL
- REDIS_URL
- DEPLOY_HOST
- DEPLOY_USER
- DEPLOY_SSH_KEY or provider deploy key
- DIGITALOCEAN_ACCESS_TOKEN if using DigitalOcean
- HOSTINGER credentials/tokens if using Hostinger
- HERCULES credentials/tokens if using Hercules

Store these in GitHub Secrets or provider secret stores. Never commit values.

## Deployment Readiness Gates

- Target repo confirmed: `rafsof22-lgtm/jarvis-build`
- Target branch confirmed: `jarvis/control-registry-model-router-plan` against `main`
- Runtime module selected
- `.env.example` contains names only
- Secrets placed outside chat
- CI passes
- Health endpoint exists
- Rollback path exists
- Cost-impacting actions approved
- Smoke test plan exists

## Immediate Recommendation

Prepare and verify the GitHub-first PR now, but do not claim live deployment until external host configuration and secrets are confirmed in GitHub Secrets or provider secret stores.
