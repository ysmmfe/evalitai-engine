import json
from pathlib import Path

from typer.testing import CliRunner

from evalitai import __version__
from evalitai.cli import app

runner = CliRunner()
FIXTURES = Path(__file__).parent / "fixtures"


def test_help_lists_version_command() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "version" in result.stdout


def test_version_command_prints_package_version() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == __version__


def test_compare_prints_comparison_json_to_stdout() -> None:
    result = runner.invoke(
        app,
        [
            "compare",
            "--baseline",
            str(FIXTURES / "baseline.jsonl"),
            "--candidate",
            str(FIXTURES / "candidate.jsonl"),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["compared_case_count"] == 2


def test_compare_writes_output_file_when_requested(tmp_path: Path) -> None:
    output_path = tmp_path / "comparison.json"

    result = runner.invoke(
        app,
        [
            "compare",
            "--baseline",
            str(FIXTURES / "baseline.jsonl"),
            "--candidate",
            str(FIXTURES / "candidate.jsonl"),
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    payload = json.loads(output_path.read_text())
    assert payload["compared_case_count"] == 2


def test_evaluate_prints_result_json_to_stdout() -> None:
    result = runner.invoke(
        app, ["evaluate", "--candidate", str(FIXTURES / "candidate.jsonl")]
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert len(payload["cases"]) == 2


def test_compare_rejects_missing_baseline_file() -> None:
    result = runner.invoke(
        app,
        [
            "compare",
            "--baseline",
            str(FIXTURES / "does-not-exist.jsonl"),
            "--candidate",
            str(FIXTURES / "candidate.jsonl"),
        ],
    )

    assert result.exit_code != 0
