import { findTool } from "./tools.js";

export async function dispatchMcpRequest(body) {
  if (!body || typeof body !== "object" || Array.isArray(body)) {
    return {
      statusCode: 400,
      payload: { ok: false, error: { code: "INVALID_REQUEST", message: "Request body must be a JSON object." } }
    };
  }

  const toolName = typeof body.tool === "string" ? body.tool.trim() : "";
  const input = body.input && typeof body.input === "object" && !Array.isArray(body.input) ? body.input : {};

  if (!toolName) {
    return {
      statusCode: 400,
      payload: { ok: false, error: { code: "INVALID_REQUEST", message: "tool is required." } }
    };
  }

  const tool = findTool(toolName);
  if (!tool) {
    return {
      statusCode: 404,
      payload: { ok: false, error: { code: "UNSUPPORTED_TOOL", message: `Unsupported tool: ${toolName}` } }
    };
  }

  const result = await tool.handler(input);
  if (!result.ok) {
    return { statusCode: 400, payload: { ok: false, tool: tool.name, error: result.error } };
  }

  return { statusCode: 200, payload: { ok: true, tool: tool.name, output: result.output } };
}
