        import { CopilotClient, approveAll } from "@github/copilot-sdk";

        const CUSTOM_AGENT = {
  "name": "hello-repo-guide",
  "displayName": "hello-repo-guide",
  "description": "Tiny onboarding example agent used to validate the copilot-agent-converter end-to-end packaging flow.\n",
  "tools": [],
  "prompt": "# Hello Repo Guide\n\nYou are **Hello Repo Guide**, a very small onboarding agent used only to prove that this repository's\n`copilot-agent-converter` can turn a real `.agent.md` into a runnable service package.\n\n## Responsibilities\n\n- Greet the user in 2-4 short sentences.\n- Explain that this repository uses a manager-led multi-agent workflow.\n- Point the user at `AGENTS.md` and `docs/agents/task-spec.md`.\n- If the request goes beyond simple onboarding, redirect the user to `team-lead`.\n\n## Constraints\n\n- Do not write code.\n- Do not run tools.\n- Do not edit repository files.\n- Keep responses concise, friendly, and scoped to onboarding.",
  "infer": true
};
        const CUSTOM_MCP_SERVERS = {};

        function buildProviderConfig(config) {
          if (!config.providerBaseUrl) {
            return undefined;
          }

          const provider = {
            type: config.providerType || "openai",
            baseUrl: config.providerBaseUrl,
            wireApi: config.providerWireApi || "completions",
          };

          if (config.providerBearerToken) {
            provider.bearerToken = config.providerBearerToken;
          } else if (config.providerApiKey) {
            provider.apiKey = config.providerApiKey;
          }

          if (provider.type === "azure" && config.azureApiVersion) {
            provider.azure = { apiVersion: config.azureApiVersion };
          }

          return provider;
        }

        async function ensureAuthIfNeeded(client, config) {
          if (config.providerBaseUrl) {
            if (!config.model) {
              throw new Error("COPILOT_MODEL is required when using a custom provider.");
            }
            return;
          }

          const auth = await client.getAuthStatus();
          if (!auth.isAuthenticated) {
            throw new Error(
              auth.statusMessage || "GitHub Copilot CLI authentication is required for live mode.",
            );
          }
        }

        export async function invokeWithCopilot(spec, config, prompt) {
          const client = new CopilotClient({
            ...(config.cliPath ? { cliPath: config.cliPath } : {}),
          });

          try {
            await ensureAuthIfNeeded(client, config);
            const providerConfig = buildProviderConfig(config);
            const session = await client.createSession({
              clientName: "copilot-agent-converter-generated-service",
              onPermissionRequest: approveAll,
              ...(config.model ? { model: config.model } : {}),
              ...(providerConfig ? { provider: providerConfig } : {}),
              customAgents: [
                {
                  ...CUSTOM_AGENT,
                  ...(Object.keys(CUSTOM_MCP_SERVERS).length > 0
                    ? { mcpServers: CUSTOM_MCP_SERVERS }
                    : {}),
                },
              ],
              agent: CUSTOM_AGENT.name,
              availableTools: [],
            });

            try {
              const response = await session.sendAndWait({ prompt });
              return {
                runtime: {
                  mode: "copilot",
                  model: config.model || null,
                  providerBaseUrl: config.providerBaseUrl || null,
                },
                message: response?.data?.content || "Copilot session returned no content.",
              };
            } finally {
              await session.disconnect();
            }
          } finally {
            await client.stop();
          }
        }
