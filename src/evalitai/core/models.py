from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field


class EvaluationCase(BaseModel):
    """One row of a baseline/candidate JSONL file."""

    case_key: str
    output: Any
    input: dict[str, Any] | None = None
    context: dict[str, Any] | None = None
    ground_truth: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class CriterionExample(BaseModel):
    """A positive or negative few-shot example for a custom criterion."""

    text: str
    label: Literal["positive", "negative"]


class CriterionSpec(BaseModel):
    """A single structured entry in ``criteria.yaml``'s ``criteria`` list.

    ``name`` is optional on input — the criteria compiler (OE-05) assigns
    one from ``description`` when omitted, so ``criteria.yaml`` authors can
    skip it for simple cases.
    """

    name: str = ""
    description: str
    examples: list[CriterionExample] = Field(default_factory=list)


class Criteria(BaseModel):
    """Parsed contents of an (optional) criteria.yaml file.

    This is the raw, uncompiled form: ``criteria`` entries may be plain
    strings or structured ``CriterionSpec`` objects. Turning them into a
    judge rubric (assigning stable names, resolving effective metrics) is
    the criteria compiler's job (OE-05), not this contract's.
    """

    metrics: list[str] | None = None
    criteria: list[str | CriterionSpec] | None = None


class EvaluatorConfig(BaseModel):
    judge: str = "stub"
    temperature: float = 0.0
    seed: int | None = None
    prohibited_terms: list[str] | None = None
    max_latency_ms: float | None = None
    regression_threshold: float = 5.0
    confidence_floor: float = 0.5


class MetricResult(BaseModel):
    name: str
    score: float | None
    confidence: float | None
    rationale: str
    evidence: list[str] = Field(default_factory=list)
    skipped: bool = False
    unstable: bool = False


class CaseEvaluation(BaseModel):
    case_key: str
    metrics: list[MetricResult]


class EvaluationResult(BaseModel):
    engine_version: str
    judge: str
    cases: list[CaseEvaluation]


class Verdict(StrEnum):
    REGRESSION = "regression"
    IMPROVEMENT = "improvement"
    STABLE = "stable"


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MetricComparison(BaseModel):
    metric: str
    baseline_score: float
    candidate_score: float
    delta: float
    confidence: float
    verdict: Verdict
    severity: Severity | None = None


class CaseComparison(BaseModel):
    case_key: str
    metrics: list[MetricComparison]


class ComparisonResult(BaseModel):
    engine_version: str
    baseline_case_count: int
    candidate_case_count: int
    compared_case_count: int
    comparisons: list[CaseComparison]
    warnings: list[str] = Field(default_factory=list)
