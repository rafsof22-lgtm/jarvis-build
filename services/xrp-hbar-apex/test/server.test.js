import assert from "node:assert/strict";
import { after, before, describe, it } from "node:test";
import { createServer } from "../src/server.js";
import { getConfig } from "../src/config.js";

function startTestServer(env = {}) {
  const config = getConfig({
    APP_ENV: "test",
    BASE_URL: "http://127.0.0.1",
    MCP_AUTH_MODE: "none",
    PORT: "0",
    ...env
  });
  const server = createServer(config);

  return new Promise((resolve) => {
    server.listen(0, "127.0.0.1", () => {
      const { port } = server.address();
      resolve({ server, baseUrl: `http://127.0.0.1:${port}` });
    });
  });
}

describe("xrp-hbar-apex service compatibility contract", () => {
  let running;

  before(async () => {
    running = await startTestServer();
  });

  after(async () => {
    await new Promise((resolve, reject) => {
      running.server.close((error) => (error ? reject(error) : resolve()));
    });
  });

  it("reports health", async () => {
    const response = await fetch(`${running.baseUrl}/health`);
    const body = await response.json();

    assert.equal(response.status, 200);
    assert.equal(body.ok, true);
    assert.equal(body.service, "xrp-hbar-apex");
  });

  it("reports ready when required non-secret runtime settings are supplied", async () => {
    const response = await fetch(`${running.baseUrl}/ready`);
    const body = await response.json();

    assert.equal(response.status, 200);
    assert.equal(body.ok, true);
    assert.deepEqual(body.checks.missingRequiredEnv, []);
    assert.equal(body.checks.mcpPostImplemented, true);
    assert.equal(body.checks.federationPollingImplemented, true);
  });

  it("reports implemented metadata-first MCP tools without overstating providers", async () => {
    const statusResponse = await fetch(`${running.baseUrl}/deployment/status`);
    const statusBody = await statusResponse.json();
    const toolsResponse = await fetch(`${running.baseUrl}/mcp/tools`);
    const toolsBody = await toolsResponse.json();

    assert.equal(statusResponse.status, 200);
    assert.equal(statusBody.capabilities.mcp, "implemented_metadata_first");
    assert.equal(statusBody.capabilities.mcpTools, "implemented");
    assert.equal(toolsResponse.status, 200);
    assert.equal(toolsBody.status, "implemented");
    assert.ok(toolsBody.tools.some((tool) => tool.name === "extract_metadata"));
    assert.ok(statusBody.notImplementedYet.includes("provider-backed URL transcription"));
  });

  it("supports namespaced health aliases", async () => {
    const response = await fetch(`${running.baseUrl}/xrp-hbar-apex/health`);
    const body = await response.json();

    assert.equal(response.status, 200);
    assert.equal(body.ok, true);
  });

  it("dispatches implemented MCP tools and rejects malformed requests honestly", async () => {
    const successResponse = await fetch(`${running.baseUrl}/mcp`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ tool: "extract_metadata", input: { url: "https://example.com/source" } })
    });
    const successBody = await successResponse.json();

    assert.equal(successResponse.status, 200);
    assert.equal(successBody.ok, true);
    assert.equal(successBody.tool, "extract_metadata");
    assert.equal(successBody.output.proof_label, "METADATA_ONLY");

    const invalidResponse = await fetch(`${running.baseUrl}/mcp`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: "{}"
    });
    const invalidBody = await invalidResponse.json();

    assert.equal(invalidResponse.status, 400);
    assert.equal(invalidBody.error.code, "INVALID_REQUEST");
  });
});
