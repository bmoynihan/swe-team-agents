function extractFileHints(systemPrompt) {
  const matches = [...systemPrompt.matchAll(/`([^`]+)`/g)];
  return [...new Set(matches.map((match) => match[1]).filter(Boolean))].slice(0, 4);
}

export async function invokeMock(spec, prompt) {
  const hints = extractFileHints(spec.behavior.systemPrompt);
  const guidance = hints.length > 0 ? hints.join(", ") : "AGENTS.md";
  const message = [
    `Hello from ${spec.identity.displayName}.`,
    spec.identity.description || "This is a generated mock runtime for validation.",
    "This response came from the deterministic mock mode of the generated service.",
    `Suggested next docs: ${guidance}.`,
    `Prompt received: ${String(prompt || "").trim() || "(empty prompt)"}`,
  ].join(" ");

  return {
    runtime: {
      mode: "mock",
      usedTools: spec.capabilities.rawTools,
    },
    message,
  };
}
