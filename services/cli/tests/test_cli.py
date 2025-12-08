"""Tests for the Typer CLI interface.

Tests verify that CLI commands execute correctly and produce expected output.
Uses Typer's CliRunner for isolated command invocation and result validation.
"""

from typer.testing import CliRunner, Result
from services.cli.src.cli import app

runner: CliRunner = CliRunner()


def test_cli_help() -> None:
    """Test that help command displays usage information.

    Verifies that the --help flag returns success and shows the CLI name.
    """
    result: Result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Workout Tracker CLI" in result.stdout


def test_cli_list_command() -> None:
    """Test that list command executes successfully.

    The command should succeed even when no exercises exist in the database.
    """
    result: Result = runner.invoke(app, ["list"])
    assert result.exit_code == 0


def test_cli_list_json_format() -> None:
    """Test that list command supports JSON output format.

    Verifies the --format json option works correctly.
    """
    result: Result = runner.invoke(app, ["list", "--format", "json"])
    assert result.exit_code == 0


def test_cli_list_csv_format() -> None:
    """Test that list command supports CSV output format.

    Verifies the --format csv option works correctly.
    """
    result: Result = runner.invoke(app, ["list", "--format", "csv"])
    assert result.exit_code == 0


def test_cli_stats_command() -> None:
    """Test that stats command displays workout statistics.

    Verifies the stats command runs without errors.
    """
    result: Result = runner.invoke(app, ["stats"])
    assert result.exit_code == 0

