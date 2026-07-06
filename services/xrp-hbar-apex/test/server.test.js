import assert from "node:assert/strict";
import { after, before, describe, it } from "node:test";
import { createServer } from "../src/server.js";
import { getConfig } from "../src/config.js";

function startTestServer(env = {}) {
  const config = getConfig({ PORT: "0", ...env });
  const server = createServer(config);

  return new Promise((resolve) => {
    server.listen(0, () => {
      const { port } = server.address();
      resolve({ server, baseUrl: `http://127.0.0.1:${port}` });
    });
  });
}

describe("xrp-hbar-apex service shell", () => {
  let running;

  before(async () => {
    running = await startTestServer();
  });

  after(() => {
    running.server.close();
  });

  it("reports health", async () => {
    const response = await fetch(`${running.baseUrl}/health`);
    const body = await response.json();

    assert.equal(response.status, 200);
    assert.equal(body.ok, true);
    assert.equal(body.service, "xrp-hbar-apex");
  });

  it("reports ready without requiring future integration secrets", async () => {
    const response = await fetch(`${running.baseUrl}/ready`);
    const body = await response.json();

    assert.equal(response.status, 200);
    assert.equal(body.ok, true);
    assert.deepEqual(body.checks.requiredEnv, []);
    assert.deepEqual(body.checks.missingRequiredEnv, []);
  });

  it("reports deployment status and explicit MCP tool limits", async () => {
    const statusResponse = await fetch(`${running.baseUrl}/deployment/status`);
    const statusBody = await statusResponse.json();
    const toolsResponse = await fetch(`${running.baseUrl}/mcp/tools`);
    const toolsBody = await toolsResponse.json();

    assert.equal(statusResponse.status, 200);
    assert.equal(statusBody.capabilities.mcp, "not_implemented");
    assert.equal(statusBody.capabilities.mcpTools, "implemented_empty");
    assert.equal(toolsResponse.status, 200);
    assert.deepEqual(toolsBody.tools, []);
  });

  it("supports namespaced health aliases", async () => {
    const response = await fetch(`${running.baseUrl}/xrp-hbar-apex/health`);
    const body = await response.json();

    assert.equal(response.status, 200);
    assert.equal(body.ok, true);
  });

  it("keeps POST /mcp explicitly disabled", async () => {
    const response = await fetch(`${running.baseUrl}/mcp`, {
      method: "POST",
      body: "{}"
    });
    const body = await response.json();

    assert.equal(response.status, 501);
    assert.equal(body.error, "not_implemented");
  });
});
