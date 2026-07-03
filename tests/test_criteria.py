import json

from evalitai.core.contract import evaluate
from evalitai.core.models import (
    Criteria,
    CriterionExample,
    CriterionSpec,
    EvaluationCase,
    EvaluatorConfig,
)
from evalitai.judge.criteria import compile_criteria, evaluate_custom_criterion
from evalitai.judge.provider import JudgeResponse
from evalitai.metrics.registry import resolve_effective_metrics

CASE = EvaluationCase(case_key="c1", input={"question": "hi"}, output="hello there")


def test_compile_criteria_returns_empty_for_no_criteria() -> None:
    assert compile_criteria(None) == []
    assert compile_criteria(Criteria()) == []


def test_compile_criteria_slugifies_plain_strings() -> None:
    criteria = Criteria(criteria=["Must be polite and professional"])

    compiled = compile_criteria(criteria)

    assert len(compiled) == 1
    assert compiled[0].name == "must_be_polite_and_professional"
    assert compiled[0].description == "Must be polite and professional"


def test_compile_criteria_disambiguates_duplicate_names() -> None:
    criteria = Criteria(
        criteria=[
            CriterionSpec(name="tone", description="Be nice"),
            CriterionSpec(name="tone", description="Be extra nice"),
        ]
    )

    compiled = compile_criteria(criteria)

    assert [c.name for c in compiled] == ["tone", "tone_2"]


def test_resolve_effective_metrics_defaults_to_everything() -> None:
    assert len(resolve_effective_metrics(None)) > 0
    assert resolve_effective_metrics(None) == resolve_effective_metrics(Criteria())


def test_resolve_effective_metrics_filters_by_allowlist() -> None:
    criteria = Criteria(metrics=["must_include", "unknown_metric"])

    metrics = resolve_effective_metrics(criteria)

    assert len(metrics) == 1


def test_custom_criterion_skipped_under_stub_judge() -> None:
    criterion = CriterionSpec(name="tone", description="Be polite")
    result = evaluate_custom_criterion(criterion, CASE, EvaluatorConfig())
    assert result.skipped is True


def test_custom_criterion_evaluated_with_real_judge(monkeypatch) -> None:
    def fake_call_judge(prompt: str, config: EvaluatorConfig) -> JudgeResponse:
        assert "<<<GOOD_EXAMPLE>>>" in prompt
        return JudgeResponse(
            raw_content=json.dumps(
                {
                    "score": 100,
                    "confidence": 0.9,
                    "rationale": "Matches the good example.",
                    "evidence": ["hello there"],
                }
            ),
            latency_ms=5.0,
            cost_usd=None,
        )

    monkeypatch.setattr("evalitai.judge.criteria.call_judge", fake_call_judge)
    criterion = CriterionSpec(
        name="tone",
        description="Be polite",
        examples=[CriterionExample(text="Thanks for reaching out", label="positive")],
    )
    config = EvaluatorConfig(judge="fake-model")

    result = evaluate_custom_criterion(criterion, CASE, config)

    assert result.name == "criteria.tone"
    assert result.skipped is False
    assert result.score == 100.0
    assert any(e.startswith("prompt_version=") for e in result.evidence)


def test_evaluate_produces_one_metric_per_compiled_criterion(monkeypatch) -> None:
    def fake_call_judge(prompt: str, config: EvaluatorConfig) -> JudgeResponse:
        return JudgeResponse(
            raw_content=json.dumps(
                {"score": 80, "confidence": 0.7, "rationale": "ok", "evidence": []}
            ),
            latency_ms=1.0,
            cost_usd=None,
        )

    monkeypatch.setattr("evalitai.judge.criteria.call_judge", fake_call_judge)
    criteria = Criteria(
        metrics=[],  # no built-in metrics, isolate custom criteria
        criteria=["Must mention a greeting", "Must be concise"],
    )
    config = EvaluatorConfig(judge="fake-model")

    result = evaluate([CASE], criteria=criteria, config=config)

    assert len(result.cases) == 1
    metric_names = {m.name for m in result.cases[0].metrics}
    assert metric_names == {
        "criteria.must_mention_a_greeting",
        "criteria.must_be_concise",
    }
    assert all(m.rationale for m in result.cases[0].metrics)
