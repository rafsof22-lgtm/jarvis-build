# Jarvis API Channel Runbook

## Purpose

The API channel lets external systems start Jarvis runs programmatically. Use this runbook to keep API-triggered work safe, structured, and aligned with Jarvis governance.

## Allowed API Use Cases

- source intake notifications
- repo/build task requests
- deployment-prep requests
- smoke-test requests
- status/report generation
- module registry update requests
- cost audit requests
- skill dedupe audit requests
- other-agent import requests

## Preferred Payload Shape

External callers should include:

- task type
- source or repo reference
- requested output
- urgency
- whether writes are requested
- whether deployment is requested
- callback/destination if any
- evidence links or file references

## Forbidden Payloads

Do not allow API-triggered runs to directly perform without approval:

- send emails
- post Slack messages
- delete files
- delete repo files
- merge pull requests
- deploy paid infrastructure
- create paid cloud resources
- rotate or expose secrets
- execute financial trades
- bypass approval policy

## Safe API Response Pattern

For major API-triggered work, Jarvis should return:

- accepted / blocked / completed status
- evidence used
- action taken
- artifacts created
- writes requiring approval
- deployment blockers
- next step

## Secrets Policy

API callers must not send raw secrets in payloads. Secrets belong in provider secret stores, GitHub Secrets, or secure runtime environment variables.

## Required Future Work

- Define exact JSON schemas for common payloads.
- Add an allowlist or authentication strategy for external callers.
- Add rate limits and replay protection in the deployed runtime.
- Add audit logs for all API-triggered requests.
