import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import process from "node:process";
import { setTimeout as sleep } from "node:timers/promises";

const port = 8123;
const baseUrl = `http://127.0.0.1:${port}`;
const child = spawn(process.execPath, ["src/server.js"], {
  env: {
    ...process.env,
    PORT: String(port),
    COPILOT_RUNTIME_MODE: "mock",
  },
  stdio: ["ignore", "pipe", "pipe"],
});

let output = "";
child.stdout.on("data", (chunk) => {
  output += chunk.toString();
});
child.stderr.on("data", (chunk) => {
  output += chunk.toString();
});

async function waitForHealth() {
  for (let attempt = 0; attempt < 40; attempt += 1) {
    try {
      const response = await fetch(`${baseUrl}/health`);
      if (response.ok) {
        return response.json();
      }
    } catch (_error) {
      // service not ready yet
    }
    await sleep(250);
  }
  throw new Error(`Service did not become healthy. Output: ${output}`);
}

try {
  const health = await waitForHealth();
  assert.equal(health.status, "ok");
  assert.equal(health.runtimeMode, "mock");

  const response = await fetch(`${baseUrl}/invoke`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify({
      prompt: "Say hello and point me to the repo workflow docs.",
    }),
  });
  assert.equal(response.status, 200);

  const payload = await response.json();
  assert.equal(payload.runtime.mode, "mock");
  assert.match(payload.message, /Hello from/i);

  console.log(JSON.stringify({ health, invoke: payload }, null, 2));
} finally {
  child.kill("SIGTERM");
}
