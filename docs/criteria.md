# Criteria YAML syntax

`--criteria criteria.yaml` is optional on both `compare` and `evaluate`. It
does two independent things: (1) narrows which built-in metrics run, and
(2) adds custom, free-text-defined metrics scored by a judge.

```yaml
# Optional: allowlist of built-in metric names. Omit this key (or the
# whole file) to run every built-in metric, same as before criteria.yaml
# existed. See docs/metrics.md for the full list of names.
metrics:
  - must_include
  - output_format
  - overall_quality

# Optional: custom criteria, scored by the judge (skipped under --judge
# stub, same as the built-in judge metrics).
criteria:
  # A plain string becomes a criterion named after a slug of its text
  # (e.g. "criteria.the_response_should_be_friendly").
  - "The response should be friendly and never blame the customer."

  # Or a structured entry with an explicit name and few-shot examples:
  - name: no_medical_advice
    description: >
      The response must not give medical advice or diagnose a condition.
    examples:
      - text: "That sounds like it could be the flu — see a doctor."
        label: negative
      - text: "I can't diagnose that, but a doctor can help you figure it out."
        label: positive
```

## How it's compiled

`evalitai.judge.criteria.compile_criteria` turns each `criteria` entry into
a `CriterionSpec` with a stable, unique `name` (explicit names win; a
duplicate name gets a numeric suffix). Each compiled criterion becomes one
`MetricResult` per case, named `criteria.<name>`, alongside the built-in
metrics — so it participates in `compare()`'s regression/improvement
diffing exactly like any other metric.

## Requires a real judge

Custom criteria are always **skipped** under `--judge stub` — there's no
deterministic way to score free-text criteria offline. Point `--judge` at
a real model (see [installation.md](./installation.md)) to have them
actually run.

## Metric allowlist semantics

`metrics: [...]` is an allowlist over **every** built-in metric name
(deterministic and judge). Unknown names are silently ignored. Custom
`criteria` entries always run regardless of the `metrics` allowlist — the
allowlist only governs built-ins.
