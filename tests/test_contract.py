from pathlib import Path

from evalitai.core.contract import compare, evaluate
from evalitai.core.models import EvaluationCase, Verdict
from evalitai.io.jsonl import read_cases, read_criteria

FIXTURES = Path(__file__).parent / "fixtures"


def test_read_cases_parses_jsonl() -> None:
    cases = read_cases(FIXTURES / "baseline.jsonl")

    assert [case.case_key for case in cases] == ["reset-password", "refund-policy"]
    assert cases[0].input == {"question": "How do I reset my password?"}


def test_read_criteria_returns_none_when_no_path() -> None:
    assert read_criteria(None) is None


def test_evaluate_produces_one_case_evaluation_per_input_case() -> None:
    cases = read_cases(FIXTURES / "candidate.jsonl")

    result = evaluate(cases)

    assert len(result.cases) == len(cases)
    assert all(case.metrics for case in result.cases)


def test_compare_only_includes_shared_case_keys() -> None:
    baseline = [EvaluationCase(case_key="only-in-baseline", output="a")]
    candidate = [EvaluationCase(case_key="only-in-candidate", output="b")]

    result = compare(baseline, candidate)

    assert result.baseline_case_count == 1
    assert result.candidate_case_count == 1
    assert result.compared_case_count == 0
    assert result.comparisons == []


def test_compare_skips_metrics_with_no_applicable_ground_truth() -> None:
    # The fixtures carry no ground_truth, so every deterministic metric is
    # skipped on both sides — nothing shared to compare, but the case keys
    # still line up.
    baseline = read_cases(FIXTURES / "baseline.jsonl")
    candidate = read_cases(FIXTURES / "candidate.jsonl")

    result = compare(baseline, candidate)

    assert result.compared_case_count == 2
    for case_comparison in result.comparisons:
        assert case_comparison.metrics == []


def test_compare_flags_regression_when_must_include_starts_failing() -> None:
    baseline = [
        EvaluationCase(
            case_key="c1",
            output="Please contact support@example.com for help.",
            ground_truth={"must_include": ["support@example.com"]},
        )
    ]
    candidate = [
        EvaluationCase(
            case_key="c1",
            output="Sorry, I can't help with that.",
            ground_truth={"must_include": ["support@example.com"]},
        )
    ]

    result = compare(baseline, candidate)

    metric = result.comparisons[0].metrics[0]
    assert metric.metric == "must_include"
    assert metric.verdict == Verdict.REGRESSION
    assert metric.delta == -100.0
