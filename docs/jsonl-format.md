# JSONL case format

`baseline`/`candidate` files passed to the CLI are JSONL: one JSON object
per line, each validating against `EvaluationCase`. Blank lines are
skipped; anything else that fails to parse raises an error naming the file
and line number.

```json
{"case_key": "reset-password", "input": {"question": "How do I reset my password?"}, "output": "Go to Settings, click Forgot Password, and check your email.", "ground_truth": {"must_include": ["email"]}}
```

| Field          | Type                    | Required | Meaning                                                                 |
| -------------- | ----------------------- | -------- | ------------------------------------------------------------------------ |
| `case_key`     | `string`                | yes      | Stable identifier used to match a case across baseline and candidate.    |
| `output`       | any JSON value          | yes      | The system output being evaluated. A `dict`/`list` or a string (parsed as JSON when a metric needs it, e.g. `output_format`). |
| `input`        | object                  | no       | The prompt/request that produced `output`. Shown to judge metrics.       |
| `context`      | object                  | no       | Retrieved context, if any (e.g. RAG). Used by `faithfulness`.            |
| `ground_truth` | object                  | no       | Per-case expectations consumed by deterministic metrics — see below.     |
| `metadata`     | object                  | no       | Free-form; currently used for `metadata.latency_ms` by the `latency` metric. |

## `ground_truth` keys deterministic metrics look for

| Key               | Type          | Consumed by         |
| ----------------- | ------------- | -------------------- |
| `output_format`   | `"json"`      | `output_format`       |
| `must_include`    | `list[string]` | `must_include`       |
| `must_not_include` | `list[string]` | `must_not_include`  |

A metric is `skipped` (excluded from `evaluate()`/`compare()` output and
from delta comparisons) whenever its required `ground_truth` key (or, for
`prohibited_terms`/`latency`, its `EvaluatorConfig` field) is absent for
that case — see [metrics.md](./metrics.md) for the full list.

Same `case_key`s should appear in both `baseline.jsonl` and
`candidate.jsonl` for `compare()` to diff them; a case present in only one
file is simply excluded from `compared_case_count`.
