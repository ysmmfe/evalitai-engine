from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class EvaluationCase(BaseModel):
    """One row of a baseline/candidate JSONL file."""

    case_key: str
    output: Any
    input: dict[str, Any] | None = None
    context: dict[str, Any] | None = None
    ground_truth: dict[str, Any] | None = None


class Criteria(BaseModel):
    """Parsed contents of an (optional) criteria.yaml file.

    This is the raw, uncompiled form. Turning ``criteria`` free-text entries
    into a judge rubric is the criteria compiler's job (OE-05), not this
    contract's.
    """

    metrics: list[str] | None = None
    criteria: list[str] | None = None


class EvaluatorConfig(BaseModel):
    judge: str = "stub"
    temperature: float = 0.0
    seed: int | None = None


class MetricResult(BaseModel):
    name: str
    score: float
    confidence: float
    rationale: str
    evidence: list[str] = Field(default_factory=list)
    skipped: bool = False


class CaseEvaluation(BaseModel):
    case_key: str
    metrics: list[MetricResult]


class EvaluationResult(BaseModel):
    engine_version: str
    cases: list[CaseEvaluation]


class Verdict(StrEnum):
    REGRESSION = "regression"
    IMPROVEMENT = "improvement"
    STABLE = "stable"


class MetricComparison(BaseModel):
    metric: str
    baseline_score: float
    candidate_score: float
    delta: float
    confidence: float
    verdict: Verdict


class CaseComparison(BaseModel):
    case_key: str
    metrics: list[MetricComparison]


class ComparisonResult(BaseModel):
    engine_version: str
    baseline_case_count: int
    candidate_case_count: int
    compared_case_count: int
    comparisons: list[CaseComparison]
