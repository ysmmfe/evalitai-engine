"""LLM-judge metrics: overall_quality, instruction_adherence, completeness,
relevance, tone, hallucination, faithfulness, tool_use.

Each metric follows the same ``(case, config) -> MetricResult`` shape as the
deterministic metrics, so they slot into the same evaluator list in
``core.contract``.
"""

import json
from collections.abc import Callable

from evalitai.core.models import EvaluationCase, EvaluatorConfig, MetricResult
from evalitai.judge.prompts import (
    JUDGE_METRIC_NAMES,
    build_prompt,
    prompt_hash,
    template_signature,
)
from evalitai.judge.provider import JudgeResponse, call_judge

REQUIRED_FIELDS = ("score", "confidence", "rationale")

STUB_SKIP_REASON = (
    "stub judge configured — set EvaluatorConfig.judge to a model id "
    "(e.g. 'ollama/llama3') to enable LLM-judge metrics"
)


def _stringify(value: object) -> str:
    if value is None:
        return ""
    return value if isinstance(value, str) else json.dumps(value)


def _skipped(name: str, reason: str) -> MetricResult:
    return MetricResult(
        name=name, score=None, confidence=None, rationale=reason, skipped=True
    )


def parse_judge_response(name: str, response: JudgeResponse) -> MetricResult:
    """Parse a raw judge response into a MetricResult, skipping on any
    missing required field rather than raising.

    Shared by both the fixed judge metrics and the compiled custom
    criteria evaluator (``judge.criteria``) — same response shape either
    way.
    """
    try:
        payload = json.loads(response.raw_content)
    except json.JSONDecodeError:
        return _skipped(name, "judge response was not valid JSON")

    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        return _skipped(name, f"judge response missing required fields: {missing}")

    evidence = [str(item) for item in (payload.get("evidence") or [])]
    evidence.append(f"latency_ms={response.latency_ms:.1f}")
    if response.cost_usd is not None:
        evidence.append(f"cost_usd={response.cost_usd}")

    return MetricResult(
        name=name,
        score=float(payload["score"]),
        confidence=float(payload["confidence"]),
        rationale=str(payload["rationale"]),
        evidence=evidence,
    )


def _evaluate_judge_metric(
    metric: str, case: EvaluationCase, config: EvaluatorConfig
) -> MetricResult:
    if config.judge == "stub":
        return _skipped(metric, STUB_SKIP_REASON)

    prompt = build_prompt(
        metric,
        input_text=_stringify(case.input),
        output_text=_stringify(case.output),
        context_text=_stringify(case.context) or None,
    )
    response = call_judge(prompt, config)
    result = parse_judge_response(metric, response)
    if result.skipped:
        return result

    version_note = f"prompt_version={prompt_hash(template_signature(metric))}"
    return result.model_copy(update={"evidence": [*result.evidence, version_note]})


def _make_judge_evaluator(
    metric: str,
) -> Callable[[EvaluationCase, EvaluatorConfig], MetricResult]:
    def _evaluator(case: EvaluationCase, config: EvaluatorConfig) -> MetricResult:
        return _evaluate_judge_metric(metric, case, config)

    return _evaluator


JUDGE_METRICS: list[Callable[[EvaluationCase, EvaluatorConfig], MetricResult]] = [
    _make_judge_evaluator(name) for name in JUDGE_METRIC_NAMES
]
