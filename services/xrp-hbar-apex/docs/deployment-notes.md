# XRP/HBAR Apex Deployment Notes

## Current service boundary

The first deployable boundary is intentionally small: health/readiness plus explicit unsupported MCP responses. This keeps Railway deployment testable without claiming unfinished intelligence or automation features are live.

## Railway checklist

1. Connect Railway to `rafsof22-lgtm/jarvis-build`.
2. Create a new service with root directory `services/xrp-hbar-apex`.
3. Confirm build uses Nixpacks.
4. Set `APP_ENV=production` and `LOG_LEVEL=info`.
5. Deploy.
6. Verify `/health` returns HTTP 200.
7. Verify `/ready` returns HTTP 200 and lists missing required variables as an empty array.
8. Treat `/mcp` as not implemented until real MCP handlers are added.

## External/manual only

The current agent can prepare GitHub files, but it cannot click through Railway project creation, set Railway variables, or prove a live Railway URL without the URL and endpoint results.

## Archive blocker

The attached ChatGPT export archive remains unparsed until a 7z-compatible extractor is available or the archive is re-uploaded in an extractable format such as `.zip` or expanded JSON.
