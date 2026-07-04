from pathlib import Path

import typer

from evalitai import __version__
from evalitai.core import contract
from evalitai.core.models import ComparisonResult, EvaluationResult, EvaluatorConfig
from evalitai.io.jsonl import read_cases, read_criteria, write_json

app = typer.Typer(
    name="evalitai",
    help="Evalitai engine: compare candidate vs baseline LLM outputs, offline.",
    no_args_is_help=True,
)


@app.callback()
def main() -> None:
    """Evalitai engine CLI."""


@app.command()
def version() -> None:
    """Print the installed evalitai-engine version."""
    typer.echo(__version__)


def _emit(result: ComparisonResult | EvaluationResult, output: Path | None) -> None:
    if output is not None:
        write_json(result, output)
        typer.echo(f"Wrote {output}")
    else:
        typer.echo(result.model_dump_json(indent=2))


@app.command()
def compare(
    baseline: Path = typer.Option(
        ..., exists=True, dir_okay=False, help="Baseline JSONL file."
    ),
    candidate: Path = typer.Option(
        ..., exists=True, dir_okay=False, help="Candidate JSONL file."
    ),
    criteria: Path | None = typer.Option(
        None, exists=True, dir_okay=False, help="Optional criteria.yaml file."
    ),
    judge: str = typer.Option("stub", help="Judge provider identifier."),
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
    criteria_obj = read_criteria(criteria)
    config = EvaluatorConfig(
        judge=judge, regression_threshold=threshold, confidence_floor=confidence_floor
    )
    baseline_config = (
        config.model_copy(update={"judge": baseline_judge})
        if baseline_judge is not None
        else None
    )
    result = contract.compare(
        baseline_cases,
        candidate_cases,
        criteria=criteria_obj,
        config=config,
        baseline_config=baseline_config,
    )
    _emit(result, output)


@app.command()
def evaluate(
    candidate: Path = typer.Option(
        ..., exists=True, dir_okay=False, help="Candidate JSONL file."
    ),
    criteria: Path | None = typer.Option(
        None, exists=True, dir_okay=False, help="Optional criteria.yaml file."
    ),
    judge: str = typer.Option("stub", help="Judge provider identifier."),
    output: Path | None = typer.Option(
        None, help="Write result.json here instead of printing to stdout."
    ),
) -> None:
    """Evaluate candidate cases without comparing against a baseline."""
    candidate_cases = read_cases(candidate)
    criteria_obj = read_criteria(criteria)
    config = EvaluatorConfig(judge=judge)
    result = contract.evaluate(candidate_cases, criteria=criteria_obj, config=config)
    _emit(result, output)


if __name__ == "__main__":
    app()
