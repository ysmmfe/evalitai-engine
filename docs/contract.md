# The compare/evaluate contract

`evalitai.core.contract` exposes two pure functions. The CLI is a thin
wrapper around them — you can call them directly from Python instead.

```python
from evalitai.core.contract import compare, evaluate
from evalitai.core.models import EvaluatorConfig
```

## `evaluate(candidate, criteria=None, config=None) -> EvaluationResult`

Runs every effective metric (built-in + compiled custom criteria) against
each case in `candidate`, independent of any baseline.

```python
class EvaluationResult(BaseModel):
    engine_version: str
    judge: str
    cases: list[CaseEvaluation]  # case_key + list[MetricResult]
```

## `compare(baseline, candidate, criteria=None, config=None, baseline_config=None) -> ComparisonResult`

Internally calls `evaluate()` on both sides, then diffs them:

1. Cases are matched by `case_key` — only the ones present in **both**
   inputs are compared (`compared_case_count` records how many).
2. Within a matched case, metrics are matched by name; `skipped` metrics
   (e.g. a judge metric under `--judge stub`, or a check with no matching
   `ground_truth` field) are excluded from comparison entirely.
3. For each shared metric: `delta = candidate_score - baseline_score`,
   `confidence = min(baseline_confidence, candidate_confidence)`.
4. **Verdict** (`_classify`): `stable` if either side was `unstable` or
   confidence is below `EvaluatorConfig.confidence_floor` (default `0.5`);
   otherwise `regression` if `delta <= -threshold`, `improvement` if
   `delta >= threshold`, else `stable`. `threshold` is
   `EvaluatorConfig.regression_threshold` (default `5.0`, on the metric's
   0-100 scale).
5. **Severity** (`_severity`): assigned only to non-`stable` verdicts, by
   `abs(delta)`:

   | `abs(delta)` ≥ | Severity  |
   | -------------- | --------- |
   | 50             | critical  |
   | 25             | high      |
   | 10             | medium    |
   | otherwise      | low       |

6. **Warnings**: `baseline_config` lets you evaluate the baseline with a
   different judge than the candidate (e.g. re-scoring an older run without
   re-running it). If the two runs used different judges, or different
   `engine_version`s, that's surfaced as a string in `ComparisonResult.warnings`
   rather than silently skewing verdicts.

```python
class ComparisonResult(BaseModel):
    engine_version: str
    baseline_case_count: int
    candidate_case_count: int
    compared_case_count: int
    comparisons: list[CaseComparison]  # case_key + list[MetricComparison]
    warnings: list[str]

class MetricComparison(BaseModel):
    metric: str
    baseline_score: float
    candidate_score: float
    delta: float
    confidence: float
    verdict: Verdict          # "regression" | "improvement" | "stable"
    severity: Severity | None  # "low" | "medium" | "high" | "critical" | None
```

## Stability

`compare()`/`evaluate()` and every model above are the public contract this
project is built around (frozen shape, per the "freeze compare/evaluate
contract" commit) — additive changes (new optional fields, new metrics) are
expected; breaking changes will bump the major version once the project
leaves alpha. See the [README status section](../README.md#status) for the
current stability stance.
