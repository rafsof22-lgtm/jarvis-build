#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${XRP_HBAR_APEX_URL:-${BASE_URL:-}}"
if [[ -z "${BASE_URL}" ]]; then
  echo '{"ok":false,"blocker":"MISSING_ENV_VAR","missing":["XRP_HBAR_APEX_URL or BASE_URL"]}'
  exit 1
fi

BASE_URL="${BASE_URL%/}"
case "${BASE_URL}" in
  http://*|https://*) ;;
  *) BASE_URL="https://${BASE_URL}" ;;
esac

check_json() {
  local path="$1"
  local url="${BASE_URL}${path}"
  local tmp
  tmp="$(mktemp)"
  local status
  status="$(curl --silent --show-error --output "${tmp}" --write-out '%{http_code}' "${url}")"
  if [[ "${status}" != "200" ]]; then
    cat "${tmp}" >&2 || true
    rm -f "${tmp}"
    echo "{\"ok\":false,\"blocker\":\"ROUTE_HEALTH_FAILURE\",\"path\":\"${path}\",\"status\":${status}}"
    exit 1
  fi
  node -e 'JSON.parse(require("node:fs").readFileSync(process.argv[1], "utf8"));' "${tmp}"
  rm -f "${tmp}"
}

for path in /health /ready /deployment/status /xrp-hbar-apex/health /xrp-hbar-apex/ready /xrp-hbar-apex/deployment/status; do
  echo "Checking ${BASE_URL}${path}"
  check_json "${path}"
done

# Smallest current live route: the shell exposes /mcp/tools as an implemented empty tool surface.
check_json /mcp/tools

echo '{"ok":true,"status":"ROUTE_SMOKE_VERIFIED","service":"xrp-hbar-apex"}'
