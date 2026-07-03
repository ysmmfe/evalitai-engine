"""Resolves which metrics actually run for a given (optional) Criteria.

Effective-criteria resolution: ``criteria.metrics`` is an allowlist by
name over every built-in deterministic and judge metric. When absent
(the common case), every built-in metric runs, same as before criteria
existed.
"""

from collections.abc import Callable

from evalitai.core.models import Criteria, EvaluationCase, EvaluatorConfig, MetricResult
from evalitai.judge.metrics import JUDGE_METRICS
from evalitai.judge.prompts import JUDGE_METRIC_NAMES
from evalitai.metrics.deterministic import DETERMINISTIC_METRICS_BY_NAME

Evaluator = Callable[[EvaluationCase, EvaluatorConfig], MetricResult]

ALL_METRICS_BY_NAME: dict[str, Evaluator] = {
    **DETERMINISTIC_METRICS_BY_NAME,
    **dict(zip(JUDGE_METRIC_NAMES, JUDGE_METRICS, strict=True)),
}


def resolve_effective_metrics(criteria: Criteria | None) -> list[Evaluator]:
    if criteria is None or criteria.metrics is None:
        return list(ALL_METRICS_BY_NAME.values())
    return [
        ALL_METRICS_BY_NAME[name]
        for name in criteria.metrics
        if name in ALL_METRICS_BY_NAME
    ]
