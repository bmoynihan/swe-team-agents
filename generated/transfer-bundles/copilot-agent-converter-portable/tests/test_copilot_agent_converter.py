from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    ROOT
    / ".github"
    / "skills"
    / "copilot-agent-converter"
    / "scripts"
    / "normalize_agent_profile.py"
)
FIXTURES = ROOT / "tests" / "fixtures" / "copilot-agent-converter"


def load_module():
    spec = importlib.util.spec_from_file_location("copilot_agent_converter", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_normalize_basic_agent_profile() -> None:
    module = load_module()
    sample = FIXTURES / "planner.agent.md"
    spec = module.build_normalized_spec(sample)

    assert spec["identity"]["id"] == "planner"
    assert spec["behavior"]["visibility"]["pickerVisible"] is True
    assert spec["behavior"]["visibility"]["allowSubagentInvocation"] is True
    assert spec["capabilities"]["sessionToolPolicy"] == "allowlist"
    assert spec["capabilities"]["canonicalTools"]["search"] == ["search"]
    assert spec["runtimeRequirements"]["execution"]["mutationLevel"] == "read-only"
    assert spec["conversionReport"]["determinism"] == "high"


def test_stdio_mcp_server_requires_http_bridge() -> None:
    module = load_module()
    sample = FIXTURES / "db-helper.agent.md"
    spec = module.build_normalized_spec(sample)

    mcp_server = spec["integrations"]["mcpServers"][0]
    assert mcp_server["transport"]["input"] == "stdio"
    assert mcp_server["transport"]["servingTargetRequired"] == "http-bridge"
    assert any(
        "HTTP bridge" in reason for reason in spec["conversionReport"]["manualReviewReasons"]
    )
