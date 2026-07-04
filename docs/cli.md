# CLI usage

## `evalitai compare`

Compares `candidate` against `baseline` case by case and metric by metric.

```bash
evalitai compare \
  --baseline baseline.jsonl \
  --candidate candidate.jsonl \
  --judge stub \
  --criteria criteria.yaml \
  --output comparison.json
```

| Option              | Default | Meaning                                                                 |
| -------------------- | ------- | ------------------------------------------------------------------------ |
| `--baseline`         | required | Path to the baseline JSONL file.                                        |
| `--candidate`        | required | Path to the candidate JSONL file.                                       |
| `--criteria`         | none     | Optional `criteria.yaml` — see [criteria.md](./criteria.md).             |
| `--judge`            | `stub`   | Judge provider identifier passed through to LiteLLM (see [installation](./installation.md)). |
| `--baseline-judge`   | none     | Use a different judge for the baseline run than for the candidate; a mismatch is surfaced as a `warnings` entry. |
| `--threshold`        | `5.0`    | Minimum absolute score delta (0-100 scale) to classify a regression/improvement instead of `stable`. |
| `--confidence-floor` | `0.5`    | Minimum judge confidence required to trust a verdict.                    |
| `--output`           | none     | Write the `ComparisonResult` JSON here instead of printing to stdout.     |

Cases are matched by `case_key`; metrics are matched by name within each
case. See [contract.md](./contract.md) for the exact shape of the result.

## `evalitai evaluate`

Runs metrics against `candidate` cases without a baseline — useful for a
one-off quality check or a pass/fail gate.

```bash
evalitai evaluate \
  --candidate candidate.jsonl \
  --judge stub \
  --output result.json
```

| Option        | Default | Meaning                                             |
| ------------- | ------- | ---------------------------------------------------- |
| `--candidate` | required | Path to the candidate JSONL file.                  |
| `--criteria`  | none     | Optional `criteria.yaml`.                          |
| `--judge`     | `stub`   | Judge provider identifier.                          |
| `--output`    | none     | Write the `EvaluationResult` JSON here instead of stdout. |

## `evalitai version`

Prints the installed `evalitai-engine` version.

## Exit codes

Both commands exit non-zero if a required input file doesn't exist or fails
to parse (invalid JSON line, or a case that doesn't validate against
`EvaluationCase`); the offending file and line number are included in the
error.
