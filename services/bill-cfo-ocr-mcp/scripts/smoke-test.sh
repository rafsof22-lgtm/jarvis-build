#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BILL_CFO_OCR_MCP_URL:-${BASE_URL:-}}"
if [[ -z "${BASE_URL}" ]]; then
  echo '{"ok":false,"blocker":"MISSING_ENV_VAR","missing":["BILL_CFO_OCR_MCP_URL or BASE_URL"]}'
  exit 1
fi

BASE_URL="${BASE_URL%/}"
case "${BASE_URL}" in
  http://*|https://*) ;;
  *) BASE_URL="https://${BASE_URL}" ;;
esac

for path in /health /ready /deployment/status /bill-cfo-ocr-mcp/health /bill-cfo-ocr-mcp/ready /bill-cfo-ocr-mcp/deployment/status; do
  echo "Checking ${BASE_URL}${path}"
  curl --fail --silent --show-error "${BASE_URL}${path}" >/dev/null
done

echo '{"ok":true,"status":"ROUTE_SMOKE_VERIFIED","service":"bill-cfo-ocr-mcp"}'
