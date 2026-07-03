import json

from evalitai.core.models import EvaluationCase, EvaluatorConfig, MetricResult


def _skipped(name: str, reason: str) -> MetricResult:
    return MetricResult(
        name=name, score=None, confidence=None, rationale=reason, skipped=True
    )


def _stringify(output: object) -> str:
    return output if isinstance(output, str) else json.dumps(output)


def evaluate_output_format(
    case: EvaluationCase, config: EvaluatorConfig
) -> MetricResult:
    name = "output_format"
    expected = (case.ground_truth or {}).get("output_format")
    if expected != "json":
        return _skipped(name, "no ground_truth.output_format == 'json' specified")

    if isinstance(case.output, dict | list):
        return MetricResult(
            name=name, score=100.0, confidence=1.0, rationale="Output is valid JSON."
        )
    try:
        json.loads(case.output)
    except (TypeError, json.JSONDecodeError):
        return MetricResult(
            name=name,
            score=0.0,
            confidence=1.0,
            rationale="Output is not valid JSON.",
            evidence=[_stringify(case.output)[:200]],
        )
    return MetricResult(
        name=name, score=100.0, confidence=1.0, rationale="Output is valid JSON."
    )


def evaluate_must_include(
    case: EvaluationCase, config: EvaluatorConfig
) -> MetricResult:
    name = "must_include"
    terms = (case.ground_truth or {}).get("must_include")
    if not terms:
        return _skipped(name, "no ground_truth.must_include specified")

    text = _stringify(case.output).lower()
    missing = [term for term in terms if term.lower() not in text]
    if missing:
        return MetricResult(
            name=name,
            score=0.0,
            confidence=1.0,
            rationale=f"Missing required terms: {missing}",
            evidence=missing,
        )
    return MetricResult(
        name=name,
        score=100.0,
        confidence=1.0,
        rationale="All required terms are present.",
        evidence=terms,
    )


def evaluate_must_not_include(
    case: EvaluationCase, config: EvaluatorConfig
) -> MetricResult:
    name = "must_not_include"
    terms = (case.ground_truth or {}).get("must_not_include")
    if not terms:
        return _skipped(name, "no ground_truth.must_not_include specified")

    text = _stringify(case.output).lower()
    found = [term for term in terms if term.lower() in text]
    if found:
        return MetricResult(
            name=name,
            score=0.0,
            confidence=1.0,
            rationale=f"Forbidden terms present: {found}",
            evidence=found,
        )
    return MetricResult(
        name=name,
        score=100.0,
        confidence=1.0,
        rationale="No forbidden terms found.",
    )


def evaluate_prohibited_terms(
    case: EvaluationCase, config: EvaluatorConfig
) -> MetricResult:
    name = "prohibited_terms"
    if not config.prohibited_terms:
        return _skipped(name, "no EvaluatorConfig.prohibited_terms configured")

    text = _stringify(case.output).lower()
    found = [term for term in config.prohibited_terms if term.lower() in text]
    if found:
        return MetricResult(
            name=name,
            score=0.0,
            confidence=1.0,
            rationale=f"Prohibited terms present: {found}",
            evidence=found,
        )
    return MetricResult(
        name=name,
        score=100.0,
        confidence=1.0,
        rationale="No prohibited terms found.",
    )


def evaluate_latency(case: EvaluationCase, config: EvaluatorConfig) -> MetricResult:
    name = "latency"
    if config.max_latency_ms is None:
        return _skipped(name, "no EvaluatorConfig.max_latency_ms configured")
    latency_ms = (case.metadata or {}).get("latency_ms")
    if latency_ms is None:
        return _skipped(name, "no metadata.latency_ms on this case")

    ok = latency_ms <= config.max_latency_ms
    return MetricResult(
        name=name,
        score=100.0 if ok else 0.0,
        confidence=1.0,
        rationale=f"latency_ms={latency_ms} vs max_latency_ms={config.max_latency_ms}",
        evidence=[f"latency_ms={latency_ms}"],
    )
