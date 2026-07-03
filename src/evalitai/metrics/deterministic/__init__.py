from collections.abc import Callable

from evalitai.core.models import EvaluationCase, EvaluatorConfig, MetricResult
from evalitai.metrics.deterministic.checks import (
    evaluate_latency,
    evaluate_must_include,
    evaluate_must_not_include,
    evaluate_output_format,
    evaluate_prohibited_terms,
)

DeterministicEvaluator = Callable[[EvaluationCase, EvaluatorConfig], MetricResult]

# Single source of truth for metric name -> evaluator, so criteria.yaml's
# `metrics:` allowlist can select by name without running each evaluator.
DETERMINISTIC_METRICS_BY_NAME: dict[str, DeterministicEvaluator] = {
    "output_format": evaluate_output_format,
    "must_include": evaluate_must_include,
    "must_not_include": evaluate_must_not_include,
    "prohibited_terms": evaluate_prohibited_terms,
    "latency": evaluate_latency,
}

DETERMINISTIC_METRICS: list[DeterministicEvaluator] = list(
    DETERMINISTIC_METRICS_BY_NAME.values()
)
