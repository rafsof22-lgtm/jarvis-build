#!/usr/bin/env bash
set -Eeuo pipefail

# Guarded federation/consolidation tool for Jarvis + XRP/HBAR Apex.
# It never deletes a Droplet, never prints secret values, and defaults to audit-only.

MODE="${1:-audit}"
PRIMARY_HOST="${PRIMARY_HOST:-134.199.144.115}"
REPAIR_HOST="${REPAIR_HOST:-170.64.230.87}"
SSH_USER="${SSH_USER:-root}"
SSH_PORT="${SSH_PORT:-22}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_ed25519}"
WORK_ROOT="${WORK_ROOT:-$PWD/jarvis-consolidation-evidence}"
PRIMARY_ROOT="${PRIMARY_ROOT:-/opt/jarvis}"
GITHUB_OWNER="${GITHUB_OWNER:-rafsof22-lgtm}"
JARVIS_REPO="${JARVIS_REPO:-jarvis-build}"
XRP_REPO="${XRP_REPO:-hub}