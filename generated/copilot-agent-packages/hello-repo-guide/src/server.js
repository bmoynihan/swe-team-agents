import express from "express";
import { loadRuntimeConfig, loadSpec } from "./config.js";
import { invokeWithCopilot } from "./copilot-runtime.js";
import { invokeMock } from "./mock-runtime.js";

const app = express();
app.use(express.json({ limit: "1mb" }));

const spec = await loadSpec();
const config = loadRuntimeConfig();

async function runAgent(prompt) {
  if (config.runtimeMode === "copilot") {
    return invokeWithCopilot(spec, config.copilot, prompt);
  }
  return invokeMock(spec, prompt);
}

app.get("/", async (_req, res) => {
  res.json({
    name: spec.identity.displayName,
    id: spec.identity.id,
    runtimeMode: config.runtimeMode,
    endpoints: ["/health", "/agent", "/invoke"],
  });
});

app.get("/health", async (_req, res) => {
  res.json({
    status: "ok",
    runtimeMode: config.runtimeMode,
    agent: {
      id: spec.identity.id,
      displayName: spec.identity.displayName,
    },
    determinism: spec.conversionReport.determinism,
    manualReviewReasons: spec.conversionReport.manualReviewReasons,
  });
});

app.get("/agent", async (_req, res) => {
  res.json({
    source: spec.source,
    identity: spec.identity,
    behavior: {
      visibility: spec.behavior.visibility,
    },
    packagingHints: spec.packagingHints,
  });
});

app.post("/invoke", async (req, res) => {
  try {
    const prompt = typeof req.body?.prompt === "string" ? req.body.prompt : "";
    const result = await runAgent(prompt);
    res.json({
      agent: {
        id: spec.identity.id,
        displayName: spec.identity.displayName,
      },
      ...result,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    res.status(500).json({
      error: message,
      runtimeMode: config.runtimeMode,
      agentId: spec.identity.id,
    });
  }
});

app.listen(config.port, "0.0.0.0", () => {
  console.log(`Generated agent service listening on port ${config.port}`);
});
