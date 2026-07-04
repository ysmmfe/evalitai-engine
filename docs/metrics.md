# Metrics reference

Every metric returns a `MetricResult` (`score: float | None` on a 0-100
scale, `confidence: float | None`, `rationale`, `evidence`, `skipped`,
`unstable`). A metric is `skipped` when its inputs aren't present for a
given case — skipped metrics never appear in a `compare()` diff.

## Deterministic metrics

No LLM call; pure checks. Run offline, always available regardless of
`--judge`.

| Name               | Runs when...                                  | Scoring                                          |
| ------------------ | ---------------------------------------------- | -------------------------------------------------- |
| `output_format`    | `ground_truth.output_format == "json"`          | 100 if `output` is valid JSON (dict/list, or a string that parses), else 0. |
| `must_include`     | `ground_truth.must_include` is a non-empty list | 100 if every term appears (case-insensitive) in `output`, else 0 with the missing terms as evidence. |
| `must_not_include` | `ground_truth.must_not_include` is a non-empty list | 100 if none of the terms appear in `output`, else 0 with the found terms as evidence. |
| `prohibited_terms` | `EvaluatorConfig.prohibited_terms` is set (not per-case) | Same as `must_not_include`, checked against a global config list rather than `ground_truth`. |
| `latency`          | `EvaluatorConfig.max_latency_ms` is set **and** `metadata.latency_ms` is present | 100 if `latency_ms <= max_latency_ms`, else 0. |

## LLM-judge metrics

Each sends one prompt to the configured `--judge` model, asking for a JSON
`{"score", "confidence", "rationale", "evidence"?}` response. **Skipped
whenever `--judge stub`** (the default) — there is no offline
approximation for these. A malformed or incomplete judge response is also
treated as `skipped` rather than raising.

| Name                    | What it rates                                                        |
| ------------------------ | ---------------------------------------------------------------------- |
| `overall_quality`        | Overall quality of the output as a response to the input.             |
| `instruction_adherence`  | How well the output follows the explicit instructions in the input.   |
| `completeness`           | How completely the output addresses everything the input asked for.   |
| `relevance`              | How relevant the output is; penalizes off-topic content.               |
| `tone`                   | Whether the tone is appropriate and professional for the input.        |
| `hallucination`          | Absence of fabricated/unsupported claims (100 = none, 0 = severe).     |
| `faithfulness`           | Faithfulness to `context`, when provided (100 = fully faithful).       |
| `tool_use`               | Whether any tool/function calls in the output are appropriate.         |

## Custom criteria

Free-text or structured entries from `criteria.yaml` compile into
`criteria.<name>` metrics with the same judge-backed shape (and the same
stub-skip behavior) as the table above — see
[criteria.md](./criteria.md).

## Prompt injection hardening

`input`/`output`/`context` are always wrapped in `<<<LABEL>>> ... <<<END_LABEL>>>`
delimited blocks in the judge prompt and never interpolated into the
instruction text, so untrusted case content can't be mistaken for
evaluator instructions.
