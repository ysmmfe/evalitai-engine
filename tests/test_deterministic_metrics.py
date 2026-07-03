from evalitai.core.models import EvaluationCase, EvaluatorConfig
from evalitai.metrics.deterministic.checks import (
    evaluate_latency,
    evaluate_must_include,
    evaluate_must_not_include,
    evaluate_output_format,
    evaluate_prohibited_terms,
)

CONFIG = EvaluatorConfig()


def test_output_format_skipped_without_ground_truth() -> None:
    case = EvaluationCase(case_key="c1", output="hello")
    result = evaluate_output_format(case, CONFIG)
    assert result.skipped is True


def test_output_format_passes_for_dict_output() -> None:
    case = EvaluationCase(
        case_key="c1", output={"ok": True}, ground_truth={"output_format": "json"}
    )
    result = evaluate_output_format(case, CONFIG)
    assert result.skipped is False
    assert result.score == 100.0


def test_output_format_fails_for_invalid_json_string() -> None:
    case = EvaluationCase(
        case_key="c1", output="not json", ground_truth={"output_format": "json"}
    )
    result = evaluate_output_format(case, CONFIG)
    assert result.score == 0.0


def test_must_include_fails_when_term_missing() -> None:
    case = EvaluationCase(
        case_key="c1",
        output="We offer a 30 day window.",
        ground_truth={"must_include": ["refund"]},
    )
    result = evaluate_must_include(case, CONFIG)
    assert result.score == 0.0
    assert "refund" in result.evidence


def test_must_not_include_fails_when_forbidden_term_present() -> None:
    case = EvaluationCase(
        case_key="c1",
        output="Just give me your password and I'll reset it.",
        ground_truth={"must_not_include": ["password"]},
    )
    result = evaluate_must_not_include(case, CONFIG)
    assert result.score == 0.0


def test_prohibited_terms_skipped_without_config() -> None:
    case = EvaluationCase(case_key="c1", output="hello")
    result = evaluate_prohibited_terms(case, CONFIG)
    assert result.skipped is True


def test_prohibited_terms_fails_when_present() -> None:
    config = EvaluatorConfig(prohibited_terms=["stupid"])
    case = EvaluationCase(case_key="c1", output="That's a stupid question.")
    result = evaluate_prohibited_terms(case, config)
    assert result.score == 0.0
    assert result.evidence == ["stupid"]


def test_latency_skipped_without_metadata() -> None:
    config = EvaluatorConfig(max_latency_ms=500)
    case = EvaluationCase(case_key="c1", output="hi")
    result = evaluate_latency(case, config)
    assert result.skipped is True


def test_latency_fails_when_over_budget() -> None:
    config = EvaluatorConfig(max_latency_ms=500)
    case = EvaluationCase(case_key="c1", output="hi", metadata={"latency_ms": 900})
    result = evaluate_latency(case, config)
    assert result.score == 0.0
