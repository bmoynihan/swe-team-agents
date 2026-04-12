from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "package_copilot_agent_converter_portable.py"


def load_module():
    spec = importlib.util.spec_from_file_location("portable_bundle_builder", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_build_bundle_creates_manifest_install_guide_and_zip() -> None:
    module = load_module()
    sandbox_root = Path(tempfile.mkdtemp(prefix="portable-bundle-", dir=ROOT / ".tmp"))
    try:
        result = module.build_bundle(output_root=sandbox_root, include_optional=True)

        bundle_root = Path(result["bundleRoot"])
        manifest_path = Path(result["manifest"])
        install_guide_path = Path(result["installGuide"])
        zip_path = Path(result["zipPath"])

        assert bundle_root.exists()
        assert manifest_path.exists()
        assert install_guide_path.exists()
        assert zip_path.exists()

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert ".github/agents/copilot-agent-converter.agent.md" in manifest["requiredFiles"]
        assert (
            ".github/prompts/convert-agent-to-databricks-app.prompt.md" in manifest["requiredFiles"]
        )
        assert "scripts/run_copilot_agent_conversion.py" in manifest["requiredFiles"]
        assert ".vscode/settings.json" in manifest["requiredFiles"]
        assert ".github/agents/hello-repo-guide.agent.md" in manifest["optionalFiles"]

        install_guide = install_guide_path.read_text(encoding="utf-8")
        assert "Do not copy personal auth files" in install_guide
        assert "run_copilot_agent_conversion.py" in install_guide
        assert "chat.promptFiles" in install_guide

        with ZipFile(zip_path) as archive:
            names = set(archive.namelist())
            assert ".github/agents/copilot-agent-converter.agent.md" in names
            assert ".github/skills/copilot-agent-converter/SKILL.md" in names
            assert ".github/prompts/convert-agent-to-databricks-app.prompt.md" in names
            assert "scripts/run_copilot_agent_conversion.py" in names
            assert ".vscode/settings.json" in names
            assert "INSTALL.md" in names
            assert "bundle-manifest.json" in names
    finally:
        shutil.rmtree(sandbox_root, ignore_errors=True)
