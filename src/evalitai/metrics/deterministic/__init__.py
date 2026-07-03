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

DETERMINISTIC_METRICS: list[DeterministicEvaluator] = [
    evaluate_output_format,
    evaluate_must_include,
    evaluate_must_not_include,
    evaluate_prohibited_terms,
    evaluate_latency,
]
