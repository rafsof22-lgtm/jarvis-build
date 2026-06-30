import http from "node:http";

const SERVICE_NAME = "bill-cfo-ocr-mcp";
const VERSION = "0.1.0";
const ROUTE_NAMESPACE = "/bill-cfo-ocr-mcp";
const REQUIRED_ENV = ["APP_ENV", "BASE_URL", "LOG_LEVEL"];

function hasValue(value) {
  return typeof value === "string" && value.trim().length > 0;
}

function getConfig(env = process.env) {
  const port = Number.parseInt(env.PORT ?? "3000", 10);
  const missing = REQUIRED_ENV.filter((name) => !hasValue(env[name]));

  return {
    serviceName: SERVICE_NAME,
    version: VERSION,
    routeNamespace: ROUTE_NAMESPACE,
    port: Number.isFinite(port) && port > 0 ? port : 3000,
    appEnv: env.APP_ENV || "development",
    logLevel: env.LOG_LEVEL || "info",
    requiredEnv: REQUIRED_ENV,
    missingRequiredEnv: missing,
    optionalIntegrations: {
      openai: hasValue(env.OPENAI_API_KEY),
      ocrProvider: hasValue(env.OCR_PROVIDER_API_KEY) && hasValue(env.OCR_PROVIDER_BASE_URL),
      googleSheets: hasValue(env.GOOGLE_SERVICE_ACCOUNT_JSON) && hasValue(env.GOOGLE_SHEET_ID),
      postgres: hasValue(env.POSTGRES_URL),
      redis: hasValue(env.REDIS_URL),
      webhookSigning: hasValue(env.WEBHOOK_SECRET)
    }
  };
}

function sendJson(res, statusCode, payload) {
  res.writeHead(statusCode, {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store"
  });
  res.end(JSON.stringify(payload, null, 2));
}

function normalizePath(pathname) {
  if (pathname.startsWith(`${ROUTE_NAMESPACE}/`)) {
    return pathname.slice(ROUTE_NAMESPACE.length) || "/";
  }
  if (pathname === ROUTE_NAMESPACE) {
    return "/";
  }
  return pathname;
}

export function createServer(runtimeConfig = getConfig()) {
  return http.createServer((req, res) => {
    const url = new URL(req.url ?? "/", "http://localhost");
    const path = normalizePath(url.pathname);
    const ready = runtimeConfig.missingRequiredEnv.length === 0;

    if (req.method === "GET" && path === "/health") {
      return sendJson(res, 200, {
        ok: true,
        service: runtimeConfig.serviceName,
        status: "healthy",
        routeNamespace: runtimeConfig.routeNamespace
      });
    }

    if (req.method === "GET" && path === "/ready") {
      return sendJson(res, ready ? 200 : 503, {
        ok: ready,
        service: runtimeConfig.serviceName,
        status: ready ? "ready" : "degraded_missing_env",
        routeNamespace: runtimeConfig.routeNamespace,
        checks: {
          configLoaded: true,
          requiredEnv: runtimeConfig.requiredEnv,
          missingRequiredEnv: runtimeConfig.missingRequiredEnv,
          ocrDependency: runtimeConfig.optionalIntegrations.ocrProvider ? "configured" : "not_configured",
          storageDependency: runtimeConfig.optionalIntegrations.postgres || runtimeConfig.optionalIntegrations.googleSheets ? "configured" : "not_configured",
          providerAuth: runtimeConfig.optionalIntegrations.openai || runtimeConfig.optionalIntegrations.ocrProvider ? "configured" : "not_configured"
        }
      });
    }

    if (req.method === "GET" && path === "/deployment/status") {
      return sendJson(res, 200, {
        ok: true,
        service: runtimeConfig.serviceName,
        version: runtimeConfig.version,
        appEnv: runtimeConfig.appEnv,
        railwayRootDirectory: "services/bill-cfo-ocr-mcp",
        deployBranch: "main",
        routeNamespace: runtimeConfig.routeNamespace,
        envNamespacePrefix: "BILL_CFO_OCR_MCP_",
        queueJobPrefix: "bill_cfo_ocr_mcp_",
        databasePrefix: "bill_cfo_ocr_mcp_",
        webhookPrefix: "bill-cfo-ocr-mcp-",
        implementedNow: ["GET /health", "GET /ready", "GET /deployment/status"],
        notImplementedYet: ["OCR route", "workbook writes", "queue workers", "provider integrations"],
        integrations: runtimeConfig.optionalIntegrations,
        truthBoundary: "This endpoint proves only that the service shell is reachable. OCR/provider/workbook functionality is not proven until a real route and provider smoke test pass."
      });
    }

    if (req.method === "GET" && path === "/") {
      return sendJson(res, 200, {
        service: runtimeConfig.serviceName,
        status: "starter_shell",
        endpoints: ["/health", "/ready", "/deployment/status"],
        routeNamespace: runtimeConfig.routeNamespace
      });
    }

    return sendJson(res, 404, {
      ok: false,
      error: "not_found"
    });
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const config = getConfig();
  createServer(config).listen(config.port, () => {
    console.log(`${config.serviceName} listening on port ${config.port}`);
  });
}
