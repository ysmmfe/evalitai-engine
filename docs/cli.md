# CLI usage

## `evalitai init`

Scaffolds `baseline.jsonl`, `candidate.jsonl`, `criteria.yaml`, and `.env`
in the current directory, pre-filled with a runnable example. Never
overwrites a file that already exists — reruns are safe, and it tells you
which files it skipped. Edit the scaffolded files in place, then run
`compare`/`evaluate` with no flags at all.

## `evalitai compare`

Compares `candidate` against `baseline` case by case and metric by metric.

```bash
evalitai compare
```

Reads `baseline.jsonl`, `candidate.jsonl`, and `criteria.yaml` (if present)
from the current directory by convention — no flags needed once you've run
`evalitai init` and filled them in. Pass a flag to override any of them:

```bash
evalitai compare --baseline other-baseline.jsonl --output comparison.json
```

| Option              | Default | Meaning                                                                 |
| -------------------- | ------- | ------------------------------------------------------------------------ |
| `--baseline`         | `./baseline.jsonl` | Path to the baseline JSONL file.                              |
| `--candidate`        | `./candidate.jsonl` | Path to the candidate JSONL file.                            |
| `--criteria`         | `./criteria.yaml` if it exists, else none | See [criteria.md](./criteria.md).      |
| `--judge`            | none     | Judge provider identifier passed through to LiteLLM (see [installation](./installation.md)). Overrides `criteria.yaml`'s `judge:` field if both are set; falls back to `stub` (offline, no LLM calls) if neither is set. |
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
evalitai evaluate
```

| Option        | Default | Meaning                                             |
| ------------- | ------- | ---------------------------------------------------- |
| `--candidate` | `./candidate.jsonl` | Path to the candidate JSONL file.            |
| `--criteria`  | `./criteria.yaml` if it exists, else none | Optional `criteria.yaml`. |
| `--judge`     | none     | Judge provider identifier. Same precedence as `compare`'s `--judge` (flag > `criteria.yaml` > `stub`). |
| `--output`    | none     | Write the `EvaluationResult` JSON here instead of stdout. |

## `evalitai version`

Prints the installed `evalitai-engine` version.

## Exit codes

Both commands exit non-zero if a required input file doesn't exist or fails
to parse (invalid JSON line, or a case that doesn't validate against
`EvaluationCase`); the offending file and line number are included in the
error.
