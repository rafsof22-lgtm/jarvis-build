export function authenticateRequest(req, config) {
  if (!config.auth.enabled) return { ok: true, mode: "none" };

  if (config.auth.mode === "bearer") {
    const authHeader = req.headers.authorization || "";
    if (config.auth.bearerToken && authHeader === `Bearer ${config.auth.bearerToken}`) {
      return { ok: true, mode: "bearer" };
    }
  }

  if (config.auth.mode === "api_key") {
    const apiKey = req.headers["x-api-key"];
    if (config.auth.apiKey && apiKey === config.auth.apiKey) {
      return { ok: true, mode: "api_key" };
    }
  }

  return {
    ok: false,
    statusCode: 401,
    error: {
      code: "UNAUTHORIZED",
      message: "Valid MCP authentication is required."
    }
  };
}
