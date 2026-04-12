import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DEFAULT_SPEC_PATH = path.resolve(__dirname, "..", "normalized-agent-spec.json");

export async function loadSpec() {
  const specPath = process.env.AGENT_SPEC_PATH || DEFAULT_SPEC_PATH;
  const raw = await readFile(specPath, "utf8");
  return JSON.parse(raw);
}

export function loadRuntimeConfig() {
  const runtimeMode = (process.env.COPILOT_RUNTIME_MODE || "mock").toLowerCase();
  return {
    runtimeMode,
    port: Number.parseInt(
      process.env.DATABRICKS_APP_PORT || process.env.PORT || "8000",
      10,
    ),
    copilot: {
      cliPath: process.env.COPILOT_CLI_PATH || undefined,
      model: process.env.COPILOT_MODEL || undefined,
      providerType: process.env.COPILOT_PROVIDER_TYPE || "openai",
      providerBaseUrl: process.env.COPILOT_PROVIDER_BASE_URL || undefined,
      providerApiKey: process.env.COPILOT_PROVIDER_API_KEY || undefined,
      providerBearerToken: process.env.COPILOT_PROVIDER_BEARER_TOKEN || undefined,
      providerWireApi: process.env.COPILOT_PROVIDER_WIRE_API || "completions",
      azureApiVersion: process.env.COPILOT_PROVIDER_AZURE_API_VERSION || undefined,
    },
  };
}
