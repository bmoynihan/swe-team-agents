#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = ROOT / "generated" / "transfer-bundles"
BUNDLE_SLUG = "copilot-agent-converter-portable"

REQUIRED_FILES = [
    ".github/agents/copilot-agent-converter.agent.md",
    ".github/prompts/convert-agent-to-databricks-app.prompt.md",
    ".github/skills/copilot-agent-converter/SKILL.md",
    ".github/skills/copilot-agent-converter/scripts/normalize_agent_profile.py",
    ".github/skills/copilot-agent-converter/scripts/emit_target_scaffolds.py",
    "scripts/run_copilot_agent_conversion.py",
    ".vscode/settings.json",
]

OPTIONAL_FILES = [
    ".github/agents/hello-repo-guide.agent.md",
    "tests/test_copilot_agent_converter.py",
    "tests/test_copilot_agent_scaffold_emitter.py",
    "tests/test_copilot_agent_conversion_runner.py",
    "tests/fixtures/copilot-agent-converter/planner.agent.md",
    "tests/fixtures/copilot-agent-converter/db-helper.agent.md",
]


def _json(data: Any) -> str:
    return json.dumps(data, indent=2) + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _copy(root: Path, relative_path: str, bundle_root: Path) -> str:
    source = root / relative_path
    if not source.exists():
        raise FileNotFoundError(relative_path)
    destination = bundle_root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return relative_path


def _render_install_guide(bundle_root: Path, included_optional: list[str]) -> str:
    optional_lines = (
        "\n".join(f"- `{path}`" for path in included_optional) if included_optional else "- None"
    )
    return (
        "# Copilot Agent Converter Portable Bundle\n\n"
        "This bundle is the minimal repo-safe package for moving "
        "`copilot-agent-converter` into another "
        "VS Code / GitHub Copilot custom-agent repository.\n\n"
        "## What to copy into the target repo\n\n"
        "- `.github/agents/copilot-agent-converter.agent.md`\n"
        "- `.github/prompts/convert-agent-to-databricks-app.prompt.md`\n"
        "- `.github/skills/copilot-agent-converter/`\n"
        "- `scripts/run_copilot_agent_conversion.py`\n\n"
        "## Optional extras included in this bundle\n\n"
        f"{optional_lines}\n\n"
        "## Install steps in the work repo\n\n"
        "1. Copy the `.github/agents/`, `.github/prompts/`, `.github/skills/`, "
        "and `scripts/` paths from this bundle into the target repo.\n"
        '2. Ensure the workspace has `"chat.promptFiles": true` in `.vscode/settings.json`.\n'
        "3. If the target repo does not already have `docs/agents/`, allow "
        "the converter to create it on first run.\n"
        "4. Do not copy personal auth files such as `.databrickscfg`, `.env`, "
        "`.databricks.env`, or any tokens.\n"
        "5. Recreate Databricks auth on the work machine using the work profile and workspace.\n"
        "6. Open the prompt file from `.github/prompts/` in VS Code or paste "
        "its contents into Copilot Chat.\n"
        "7. Validate from the target repo with:\n\n"
        "```bash\n"
        "py -3 scripts/run_copilot_agent_conversion.py --input "
        ".github/agents/hello-repo-guide.agent.md --skip-smoke-test\n"
        "```\n\n"
        "8. For full validation after Node and Databricks auth are ready:\n\n"
        "```bash\n"
        "py -3 scripts/run_copilot_agent_conversion.py --input "
        ".github/agents/hello-repo-guide.agent.md --deploy-databricks "
        "--profile <work-profile>\n"
        "```\n\n"
        "## Notes\n\n"
        "- This bundle is repo-level, not account-level. It is meant to be "
        "copied into another repository.\n"
        "- The converter can write "
        "`docs/agents/copilot-agent-conversion-report.generated.md` if the "
        "canonical report file is locked.\n"
        "- The generated service validates in deterministic `mock` mode first; "
        "live Copilot mode still needs GitHub Copilot CLI auth or provider env vars.\n"
    )


def _render_manifest(
    bundle_root: Path, required: list[str], optional: list[str], zip_path: Path
) -> str:
    manifest = {
        "bundleName": BUNDLE_SLUG,
        "bundleRoot": bundle_root.as_posix(),
        "zipPath": zip_path.as_posix(),
        "requiredFiles": required,
        "optionalFiles": optional,
        "excludedSensitiveFiles": [
            ".databrickscfg",
            ".env",
            ".databricks.env",
            "databricks-deploy-result.json",
            "smoke-test-result.json",
            "conversion-run-result.json",
        ],
        "installGuide": "INSTALL.md",
    }
    return _json(manifest)


def _zip_bundle(bundle_root: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as archive:
        for path in sorted(bundle_root.rglob("*")):
            if path.is_dir():
                continue
            archive.write(path, arcname=path.relative_to(bundle_root).as_posix())


def build_bundle(output_root: Path, include_optional: bool = True) -> dict[str, Any]:
    bundle_root = output_root / BUNDLE_SLUG
    if bundle_root.exists():
        shutil.rmtree(bundle_root)
    bundle_root.mkdir(parents=True, exist_ok=True)

    copied_required = [_copy(ROOT, relative_path, bundle_root) for relative_path in REQUIRED_FILES]
    copied_optional: list[str] = []
    if include_optional:
        for relative_path in OPTIONAL_FILES:
            if (ROOT / relative_path).exists():
                copied_optional.append(_copy(ROOT, relative_path, bundle_root))

    install_guide_path = bundle_root / "INSTALL.md"
    _write(install_guide_path, _render_install_guide(bundle_root, copied_optional))

    zip_path = output_root / f"{BUNDLE_SLUG}.zip"
    _write(
        bundle_root / "bundle-manifest.json",
        _render_manifest(bundle_root, copied_required, copied_optional, zip_path),
    )
    _zip_bundle(bundle_root, zip_path)

    return {
        "bundleRoot": bundle_root.as_posix(),
        "zipPath": zip_path.as_posix(),
        "requiredFiles": copied_required,
        "optionalFiles": copied_optional,
        "installGuide": install_guide_path.as_posix(),
        "manifest": (bundle_root / "bundle-manifest.json").as_posix(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a portable transfer bundle for the copilot-agent-converter assets."
    )
    parser.add_argument(
        "--output-root",
        default=DEFAULT_OUTPUT_ROOT.as_posix(),
        help="Folder where the portable bundle should be created.",
    )
    parser.add_argument(
        "--required-only",
        action="store_true",
        help="Exclude the optional sample agent and tests from the bundle.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build_bundle(
        output_root=Path(args.output_root).resolve(),
        include_optional=not args.required_only,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
