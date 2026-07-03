from evalitai import __version__
from evalitai.core.models import (
    CaseComparison,
    CaseEvaluation,
    ComparisonResult,
    Criteria,
    EvaluationCase,
    EvaluationResult,
    EvaluatorConfig,
    MetricComparison,
    MetricResult,
    Verdict,
)

# Placeholder threshold (score points, 0-100 scale). OE-06 replaces this with
# the full rule: delta <= -threshold AND confidence >= floor AND !unstable.
DEFAULT_REGRESSION_THRESHOLD = 5.0


def _stub_evaluate_case(case: EvaluationCase) -> CaseEvaluation:
    """Placeholder evaluator: no real metrics yet (those land in OE-03/04)."""
    metric = MetricResult(
        name="stub_quality",
        score=100.0,
        confidence=1.0,
        rationale="Stub evaluator: OE-02 only fixes the contract shape, "
        "real metrics land in OE-03 (deterministic) and OE-04 (judge).",
        evidence=[],
    )
    return CaseEvaluation(case_key=case.case_key, metrics=[metric])


def evaluate(
    candidate: list[EvaluationCase],
    criteria: Criteria | None = None,
    config: EvaluatorConfig | None = None,
) -> EvaluationResult:
    del criteria, config  # unused until OE-04/OE-05 wire in real evaluators
    return EvaluationResult(
        engine_version=__version__,
        cases=[_stub_evaluate_case(case) for case in candidate],
    )


def _classify(delta: float, threshold: float) -> Verdict:
    if delta <= -threshold:
        return Verdict.REGRESSION
    if delta >= threshold:
        return Verdict.IMPROVEMENT
    return Verdict.STABLE


def compare(
    baseline: list[EvaluationCase],
    candidate: list[EvaluationCase],
    criteria: Criteria | None = None,
    config: EvaluatorConfig | None = None,
) -> ComparisonResult:
    baseline_result = evaluate(baseline, criteria=criteria, config=config)
    candidate_result = evaluate(candidate, criteria=criteria, config=config)

    baseline_by_key = {case.case_key: case for case in baseline_result.cases}
    candidate_by_key = {case.case_key: case for case in candidate_result.cases}
    shared_keys = baseline_by_key.keys() & candidate_by_key.keys()

    comparisons: list[CaseComparison] = []
    for case_key in sorted(shared_keys):
        baseline_metrics = {m.name: m for m in baseline_by_key[case_key].metrics}
        candidate_metrics = {m.name: m for m in candidate_by_key[case_key].metrics}
        shared_metric_names = baseline_metrics.keys() & candidate_metrics.keys()

        metric_comparisons: list[MetricComparison] = []
        for metric_name in sorted(shared_metric_names):
            base_metric = baseline_metrics[metric_name]
            cand_metric = candidate_metrics[metric_name]
            delta = cand_metric.score - base_metric.score
            metric_comparisons.append(
                MetricComparison(
                    metric=metric_name,
                    baseline_score=base_metric.score,
                    candidate_score=cand_metric.score,
                    delta=delta,
                    confidence=min(base_metric.confidence, cand_metric.confidence),
                    verdict=_classify(delta, DEFAULT_REGRESSION_THRESHOLD),
                )
            )
        comparisons.append(
            CaseComparison(case_key=case_key, metrics=metric_comparisons)
        )

    return ComparisonResult(
        engine_version=__version__,
        baseline_case_count=len(baseline_by_key),
        candidate_case_count=len(candidate_by_key),
        compared_case_count=len(shared_keys),
        comparisons=comparisons,
    )
