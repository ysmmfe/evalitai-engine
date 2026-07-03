"""Compiles ``Criteria.criteria`` entries (free-text or structured) into a
rubric of named criteria: one MetricResult per criterion, each backed by a
judge call with the criterion's own positive/negative examples folded in
as few-shot examples.
"""

import re

from evalitai.core.models import (
    Criteria,
    CriterionSpec,
    EvaluationCase,
    EvaluatorConfig,
    MetricResult,
)
from evalitai.judge.metrics import (
    STUB_SKIP_REASON,
    _skipped,
    _stringify,
    parse_judge_response,
)
from evalitai.judge.prompts import (
    build_custom_prompt,
    custom_criterion_signature,
    prompt_hash,
)
from evalitai.judge.provider import call_judge

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(text: str) -> str:
    slug = _SLUG_RE.sub("_", text.strip().lower()).strip("_")
    return slug or "criterion"


def compile_criteria(criteria: Criteria | None) -> list[CriterionSpec]:
    """Turn free-text and/or structured criteria entries into a uniform
    list of named CriterionSpec, one per evaluated criterion.

    Plain strings become a criterion named after a slug of their text.
    Duplicate names (from a repeated string or an explicit ``name``) are
    disambiguated with a numeric suffix so every criterion in the rubric
    maps to exactly one MetricResult.
    """
    if criteria is None or not criteria.criteria:
        return []

    compiled: list[CriterionSpec] = []
    seen_names: set[str] = set()
    for entry in criteria.criteria:
        spec = (
            entry
            if isinstance(entry, CriterionSpec)
            else CriterionSpec(description=entry)
        )
        base_name = spec.name or _slugify(spec.description)
        name = base_name
        suffix = 2
        while name in seen_names:
            name = f"{base_name}_{suffix}"
            suffix += 1
        seen_names.add(name)
        compiled.append(spec.model_copy(update={"name": name}))
    return compiled


def evaluate_custom_criterion(
    criterion: CriterionSpec, case: EvaluationCase, config: EvaluatorConfig
) -> MetricResult:
    name = f"criteria.{criterion.name}"
    if config.judge == "stub":
        return _skipped(name, STUB_SKIP_REASON)

    prompt = build_custom_prompt(
        description=criterion.description,
        examples=criterion.examples,
        input_text=_stringify(case.input),
        output_text=_stringify(case.output),
        context_text=_stringify(case.context) or None,
    )
    response = call_judge(prompt, config)
    result = parse_judge_response(name, response)
    if result.skipped:
        return result

    signature = custom_criterion_signature(criterion.description, criterion.examples)
    version_note = f"prompt_version={prompt_hash(signature)}"
    return result.model_copy(update={"evidence": [*result.evidence, version_note]})
