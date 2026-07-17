# Jarvis Schedule Runbook

## Purpose

This runbook defines recommended recurring Jarvis schedules. Schedules should be added only when the user wants recurring runs and the current draft/live state supports schedule creation.

## Recommended ChatGPT Schedules

### Daily Jarvis Build Health Check

Cadence: daily morning, Australia/Sydney unless changed.

Prompt:

Review Jarvis build status, Memory, module registry, active blockers, recently changed files, deployment state, and next best action. Update durable Memory where useful. Return Done / Proven / Gaps / Next Step.

### Weekly Cost And Deployment Audit

Cadence: weekly.

Prompt:

Audit Jarvis hosting, API, model-routing, connected apps, deployment targets, secrets gaps, and cost risks. Compare free-first and cheapest paid options. Update the deployment target matrix and app risk matrix if needed.

### Weekly Skill/File Drift Audit

Cadence: weekly.

Prompt:

Check Jarvis instructions, skills, files, module registry, skill dedupe map, and Memory for drift, duplicates, stale promises, missing hooks, and unsupported capabilities. Record recommended fixes.

### Monthly App Permission Audit

Cadence: monthly.

Prompt:

Review connected apps, write-capable actions, approval policy, risky automations, deployment-capable apps, and secrets requirements. Recommend any approval tightening or app cleanup.

## Slack Schedules

Only add Slack schedules after a Slack channel deployment exists. Slack app connection alone is not a Slack channel deployment.

## Schedule Safety

- Schedules start runs; they are not daemons or persistent workers.
- Schedule prompts should define the run-specific task.
- Do not use schedules to bypass approvals.
- Keep external writes confirmation-gated unless explicitly approved.

## Current Status

No ChatGPT schedules are currently configured. No Slack schedules are currently configured.
