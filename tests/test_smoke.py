from swe_team_agents import __version__
from swe_team_agents.cli import main


def test_package_version_is_defined() -> None:
    assert __version__ == "0.1.0"


def test_cli_main_returns_success() -> None:
    assert main() == 0
