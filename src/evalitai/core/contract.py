from evalitai import __version__
from evalitai.core.models import (
    CaseComparison,
    CaseEvaluation,
    ComparisonResult,
    Criteria,
    CriterionSpec,
    EvaluationCase,
    EvaluationResult,
    EvaluatorConfig,
    MetricComparison,
    MetricResult,
    Severity,
    Verdict,
)
from evalitai.judge.criteria import compile_criteria, evaluate_custom_criterion
from evalitai.metrics.registry import Evaluator, resolve_effective_metrics

# Severity buckets, keyed by the minimum |delta| (score points, 0-100 scale)
# that earns each level. Only assigned to non-stable verdicts.
SEVERITY_THRESHOLDS: list[tuple[float, Severity]] = [
    (50.0, Severity.CRITICAL),
    (25.0, Severity.HIGH),
    (10.0, Severity.MEDIUM),
]


def _evaluate_case(
    case: EvaluationCase,
    config: EvaluatorConfig,
    effective_metrics: list[Evaluator],
    custom_criteria: list[CriterionSpec],
) -> CaseEvaluation:
    """Run every effective built-in metric plus every compiled custom
    criterion against one case.

    Judge-backed metrics (built-in or custom) are skipped when
    ``config.judge == "stub"`` (the default), so evaluation stays fully
    offline unless a real judge model is configured.
    """
    metrics: list[MetricResult] = [
        evaluator(case, config) for evaluator in effective_metrics
    ]
    metrics += [
        evaluate_custom_criterion(criterion, case, config)
        for criterion in custom_criteria
    ]
    return CaseEvaluation(case_key=case.case_key, metrics=metrics)


def evaluate(
    candidate: list[EvaluationCase],
    criteria: Criteria | None = None,
    config: EvaluatorConfig | None = None,
) -> EvaluationResult:
    resolved_config = config or EvaluatorConfig()
    effective_metrics = resolve_effective_metrics(criteria)
    custom_criteria = compile_criteria(criteria)
    return EvaluationResult(
        engine_version=__version__,
        judge=resolved_config.judge,
        cases=[
            _evaluate_case(case, resolved_config, effective_metrics, custom_criteria)
            for case in candidate
        ],
    )


def _classify(
    delta: float,
    confidence: float,
    unstable: bool,
    threshold: float,
    confidence_floor: float,
) -> Verdict:
    if unstable or confidence < confidence_floor:
        return Verdict.STABLE
    if delta <= -threshold:
        return Verdict.REGRESSION
    if delta >= threshold:
        return Verdict.IMPROVEMENT
    return Verdict.STABLE


def _severity(verdict: Verdict, delta: float) -> Severity | None:
    if verdict == Verdict.STABLE:
        return None
    magnitude = abs(delta)
    for min_magnitude, severity in SEVERITY_THRESHOLDS:
        if magnitude >= min_magnitude:
            return severity
    return Severity.LOW


def _version_warnings(
    baseline_result: EvaluationResult, candidate_result: EvaluationResult
) -> list[str]:
    warnings: list[str] = []
    if baseline_result.judge != candidate_result.judge:
        warnings.append(
            "baseline and candidate were evaluated with different judge "
            f"providers ({baseline_result.judge!r} vs {candidate_result.judge!r})"
        )
    if baseline_result.engine_version != candidate_result.engine_version:
        warnings.append(
            "baseline and candidate were evaluated with different engine "
            f"versions ({baseline_result.engine_version!r} vs "
            f"{candidate_result.engine_version!r})"
        )
    return warnings


def compare(
    baseline: list[EvaluationCase],
    candidate: list[EvaluationCase],
    criteria: Criteria | None = None,
    config: EvaluatorConfig | None = None,
    baseline_config: EvaluatorConfig | None = None,
) -> ComparisonResult:
    """Compare candidate against baseline.

    ``baseline_config`` lets callers evaluate the baseline with a different
    judge than the candidate (e.g. re-scoring an older run) — ``config`` is
    used for both sides when it is omitted. Any mismatch in judge or engine
    version between the two runs surfaces as a warning rather than silently
    affecting the verdicts.
    """
    resolved_config = config or EvaluatorConfig()
    baseline_result = evaluate(
        baseline, criteria=criteria, config=baseline_config or resolved_config
    )
    candidate_result = evaluate(candidate, criteria=criteria, config=resolved_config)

    baseline_by_key = {case.case_key: case for case in baseline_result.cases}
    candidate_by_key = {case.case_key: case for case in candidate_result.cases}
    shared_keys = baseline_by_key.keys() & candidate_by_key.keys()

    comparisons: list[CaseComparison] = []
    for case_key in sorted(shared_keys):
        baseline_metrics = {
            m.name: m for m in baseline_by_key[case_key].metrics if not m.skipped
        }
        candidate_metrics = {
            m.name: m for m in candidate_by_key[case_key].metrics if not m.skipped
        }
        shared_metric_names = baseline_metrics.keys() & candidate_metrics.keys()

        metric_comparisons: list[MetricComparison] = []
        for metric_name in sorted(shared_metric_names):
            base_metric = baseline_metrics[metric_name]
            cand_metric = candidate_metrics[metric_name]
            assert base_metric.score is not None and cand_metric.score is not None
            assert (
                base_metric.confidence is not None
                and cand_metric.confidence is not None
            )
            delta = cand_metric.score - base_metric.score
            confidence = min(base_metric.confidence, cand_metric.confidence)
            unstable = base_metric.unstable or cand_metric.unstable
            verdict = _classify(
                delta,
                confidence,
                unstable,
                resolved_config.regression_threshold,
                resolved_config.confidence_floor,
            )
            metric_comparisons.append(
                MetricComparison(
                    metric=metric_name,
                    baseline_score=base_metric.score,
                    candidate_score=cand_metric.score,
                    delta=delta,
                    confidence=confidence,
                    verdict=verdict,
                    severity=_severity(verdict, delta),
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
        warnings=_version_warnings(baseline_result, candidate_result),
    )
