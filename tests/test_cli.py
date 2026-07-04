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


def test_evaluate_defaults_to_stub_judge_with_no_criteria() -> None:
    result = runner.invoke(
        app, ["evaluate", "--candidate", str(FIXTURES / "candidate.jsonl")]
    )

    assert result.exit_code == 0
    assert json.loads(result.stdout)["judge"] == "stub"


def test_evaluate_uses_judge_from_criteria_yaml_when_no_cli_flag() -> None:
    result = runner.invoke(
        app,
        [
            "evaluate",
            "--candidate",
            str(FIXTURES / "candidate.jsonl"),
            "--criteria",
            str(FIXTURES / "criteria_with_judge.yaml"),
        ],
    )

    assert result.exit_code == 0
    assert json.loads(result.stdout)["judge"] == "fake-model-from-criteria"


def test_evaluate_judge_flag_overrides_criteria_yaml() -> None:
    result = runner.invoke(
        app,
        [
            "evaluate",
            "--candidate",
            str(FIXTURES / "candidate.jsonl"),
            "--criteria",
            str(FIXTURES / "criteria_with_judge.yaml"),
            "--judge",
            "cli-override-model",
        ],
    )

    assert result.exit_code == 0
    assert json.loads(result.stdout)["judge"] == "cli-override-model"


def test_init_scaffolds_all_files_in_cwd(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0
    assert (tmp_path / "baseline.jsonl").exists()
    assert (tmp_path / "candidate.jsonl").exists()
    assert (tmp_path / "criteria.yaml").exists()
    assert (tmp_path / ".env").exists()
    assert "judge: gpt-4o-mini" in (tmp_path / "criteria.yaml").read_text()


def test_init_does_not_overwrite_existing_files(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "baseline.jsonl").write_text("keep me", encoding="utf-8")

    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0
    assert "Skipped" in result.stdout
    assert (tmp_path / "baseline.jsonl").read_text() == "keep me"


def test_compare_uses_conventional_filenames_with_no_flags(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    (tmp_path / "criteria.yaml").unlink()  # isolate baseline/candidate lookup

    result = runner.invoke(app, ["compare"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["compared_case_count"] == 1


def test_compare_auto_discovers_criteria_yaml_with_no_flag(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "candidate.jsonl").write_text(
        (FIXTURES / "candidate.jsonl").read_text(encoding="utf-8"), encoding="utf-8"
    )
    (tmp_path / "criteria.yaml").write_text(
        "judge: auto-discovered-model\nmetrics: []\n", encoding="utf-8"
    )

    result = runner.invoke(app, ["evaluate"])

    assert result.exit_code == 0
    assert json.loads(result.stdout)["judge"] == "auto-discovered-model"


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
