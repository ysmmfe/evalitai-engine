from pathlib import Path

import typer
from dotenv import load_dotenv

from evalitai import __version__
from evalitai.core import contract
from evalitai.core.models import (
    ComparisonResult,
    Criteria,
    EvaluationResult,
    EvaluatorConfig,
)
from evalitai.io.jsonl import read_cases, read_criteria, write_json
from evalitai.judge.provider import JudgeCallError

app = typer.Typer(
    name="evalitai",
    help="Evalitai engine: compare candidate vs baseline LLM outputs, offline.",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)

# Convention over configuration: `init` scaffolds exactly these filenames
# in the current directory, and compare/evaluate default to them — so the
# common case needs zero flags. Pass --baseline/--candidate/--criteria
# explicitly only to use a different name or location.
DEFAULT_BASELINE = Path("baseline.jsonl")
DEFAULT_CANDIDATE = Path("candidate.jsonl")
DEFAULT_CRITERIA = Path("criteria.yaml")
DEFAULT_ENV = Path(".env")

_SCAFFOLD_CASE_KEY = "refund-policy"
_SCAFFOLD_BASELINE = (
    f'{{"case_key": "{_SCAFFOLD_CASE_KEY}", '
    '"input": {"question": "What is your refund policy?"}, '
    '"output": "We offer full refunds within 30 days of purchase.", '
    '"ground_truth": {"must_include": ["refund"]}}\n'
)
_SCAFFOLD_CANDIDATE = (
    f'{{"case_key": "{_SCAFFOLD_CASE_KEY}", '
    '"input": {"question": "What is your refund policy?"}, '
    '"output": "Sorry, no refunds are offered on any purchase.", '
    '"ground_truth": {"must_include": ["refund"]}}\n'
)
_SCAFFOLD_CRITERIA = (
    "# The model that judges your outputs. Any LiteLLM-supported model\n"
    "# string works: \"gpt-5-mini\", \"claude-haiku-4-5\", \"ollama/llama3\"\n"
    "# (local, no API key), etc. See docs/installation.md.\n"
    "judge: gpt-5-mini\n"
)
_SCAFFOLD_ENV = (
    "# Only set the key for the provider you picked as `judge` above.\n"
    "OPENAI_API_KEY=\n"
    "ANTHROPIC_API_KEY=\n"
    "GEMINI_API_KEY=\n"
)


@app.callback()
def main() -> None:
    """Evalitai engine CLI."""
    load_dotenv()


def _resolve_judge(judge: str | None, criteria: Criteria | None) -> str:
    """Precedence: --judge flag > criteria.yaml's judge field > 'stub'."""
    return judge or (criteria.judge if criteria else None) or "stub"


def _resolve_criteria(criteria: Path | None) -> Path | None:
    if criteria is not None:
        return criteria
    return DEFAULT_CRITERIA if DEFAULT_CRITERIA.exists() else None


@app.command()
def version() -> None:
    """Print the installed evalitai-engine version."""
    typer.echo(__version__)


@app.command()
def init() -> None:
    """Scaffold baseline.jsonl, candidate.jsonl, criteria.yaml, and .env
    in the current directory, pre-filled with a runnable example - edit
    them in place, then run `evalitai compare` with no flags."""
    scaffold = {
        DEFAULT_BASELINE: _SCAFFOLD_BASELINE,
        DEFAULT_CANDIDATE: _SCAFFOLD_CANDIDATE,
        DEFAULT_CRITERIA: _SCAFFOLD_CRITERIA,
        DEFAULT_ENV: _SCAFFOLD_ENV,
    }
    for path, content in scaffold.items():
        if path.exists():
            typer.echo(f"Skipped {path} (already exists)")
            continue
        path.write_text(content, encoding="utf-8")
        typer.echo(f"Created {path}")
    typer.echo(
        "\nNext: edit criteria.yaml's judge: field and set its API key in "
        ".env, then replace baseline.jsonl/candidate.jsonl with your own "
        "data. Run `evalitai compare` when ready."
    )


def _emit(result: ComparisonResult | EvaluationResult, output: Path | None) -> None:
    if output is not None:
        write_json(result, output)
        typer.echo(f"Wrote {output}")
    else:
        typer.echo(result.model_dump_json(indent=2))


@app.command()
def compare(
    baseline: Path = typer.Option(
        DEFAULT_BASELINE,
        exists=True,
        dir_okay=False,
        help="Baseline JSONL file. Defaults to ./baseline.jsonl "
        "(run `evalitai init` to scaffold one).",
    ),
    candidate: Path = typer.Option(
        DEFAULT_CANDIDATE,
        exists=True,
        dir_okay=False,
        help="Candidate JSONL file. Defaults to ./candidate.jsonl.",
    ),
    criteria: Path | None = typer.Option(
        None,
        exists=True,
        dir_okay=False,
        help="criteria.yaml file. Defaults to ./criteria.yaml if present; "
        "omit entirely to run with every built-in metric and the 'stub' judge.",
    ),
    judge: str | None = typer.Option(
        None,
        help="Judge provider identifier (e.g. 'gpt-5-mini', 'ollama/llama3'). "
        "Overrides criteria.yaml's judge field, if any; defaults to 'stub' "
        "(offline, no LLM calls) when neither is set.",
    ),
    baseline_judge: str | None = typer.Option(
        None,
        help="Judge provider identifier for the baseline, if different from "
        "--judge (surfaces as a warning in the comparison).",
    ),
    threshold: float = typer.Option(
        5.0, help="Minimum |delta| (score points) to classify a regression/improvement."
    ),
    confidence_floor: float = typer.Option(
        0.5, help="Minimum confidence required to trust a verdict."
    ),
    output: Path | None = typer.Option(
        None, help="Write comparison.json here instead of printing to stdout."
    ),
) -> None:
    """Compare candidate against baseline and report regressions."""
    baseline_cases = read_cases(baseline)
    candidate_cases = read_cases(candidate)
    criteria_obj = read_criteria(_resolve_criteria(criteria))
    config = EvaluatorConfig(
        judge=_resolve_judge(judge, criteria_obj),
        regression_threshold=threshold,
        confidence_floor=confidence_floor,
    )
    baseline_config = (
        config.model_copy(update={"judge": baseline_judge})
        if baseline_judge is not None
        else None
    )
    try:
        result = contract.compare(
            baseline_cases,
            candidate_cases,
            criteria=criteria_obj,
            config=config,
            baseline_config=baseline_config,
        )
    except JudgeCallError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    _emit(result, output)


@app.command()
def evaluate(
    candidate: Path = typer.Option(
        DEFAULT_CANDIDATE,
        exists=True,
        dir_okay=False,
        help="Candidate JSONL file. Defaults to ./candidate.jsonl "
        "(run `evalitai init` to scaffold one).",
    ),
    criteria: Path | None = typer.Option(
        None,
        exists=True,
        dir_okay=False,
        help="criteria.yaml file. Defaults to ./criteria.yaml if present.",
    ),
    judge: str | None = typer.Option(
        None,
        help="Judge provider identifier. Overrides criteria.yaml's judge "
        "field, if any; defaults to 'stub' when neither is set.",
    ),
    output: Path | None = typer.Option(
        None, help="Write result.json here instead of printing to stdout."
    ),
) -> None:
    """Evaluate candidate cases without comparing against a baseline."""
    candidate_cases = read_cases(candidate)
    criteria_obj = read_criteria(_resolve_criteria(criteria))
    config = EvaluatorConfig(judge=_resolve_judge(judge, criteria_obj))
    try:
        result = contract.evaluate(
            candidate_cases, criteria=criteria_obj, config=config
        )
    except JudgeCallError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    _emit(result, output)


if __name__ == "__main__":
    app()
