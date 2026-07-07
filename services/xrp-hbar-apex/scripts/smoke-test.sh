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

for path in /health /ready /deployment/status /xrp-hbar-apex/health /xrp-hbar-apex/ready /xrp-hbar-apex/deployment/status /mcp /mcp/tools; do
  echo "Checking ${BASE_URL}${path}"
  check_json "${path}"
done

AUTH_HEADER=()
if [[ "${MCP_AUTH_MODE:-none}" == "bearer" ]]; then
  if [[ -z "${MCP_BEARER_TOKEN:-}" ]]; then
    echo '{"ok":false,"blocker":"MISSING_ENV_VAR","missing":["MCP_BEARER_TOKEN"]}'
    exit 1
  fi
  AUTH_HEADER=(-H "Authorization: Bearer ${MCP_BEARER_TOKEN}")
elif [[ "${MCP_AUTH_MODE:-none}" == "api_key" ]]; then
  if [[ -z "${MCP_API_KEY:-}" ]]; then
    echo '{"ok":false,"blocker":"MISSING_ENV_VAR","missing":["MCP_API_KEY"]}'
    exit 1
  fi
  AUTH_HEADER=(-H "x-api-key: ${MCP_API_KEY}")
fi

tmp="$(mktemp)"
status="$(curl --silent --show-error --output "${tmp}" --write-out '%{http_code}' \
  -X POST "${BASE_URL}/mcp" \
  -H "content-type: application/json" \
  "${AUTH_HEADER[@]}" \
  --data '{"tool":"extract_metadata","input":{"url":"https://ripple.com/insights/the-xrpl-lending-protocol-bringing-credit-infrastructure-onchain/","platform_hint":"web"}}')"

if [[ "${status}" != "200" ]]; then
  cat "${tmp}" >&2 || true
  rm -f "${tmp}"
  echo "{\"ok\":false,\"blocker\":\"MCP_POST_FAILURE\",\"status\":${status}}"
  exit 1
fi

node -e 'const data = JSON.parse(require("node:fs").readFileSync(process.argv[1], "utf8")); if (!data.ok || data.tool !== "extract_metadata") process.exit(1);' "${tmp}"
rm -f "${tmp}"

echo '{"ok":true,"status":"MCP_SMOKE_VERIFIED","service":"xrp-hbar-apex"}'
