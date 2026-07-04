# evalitai-engine

Open-source evaluation engine for LLM-based systems. Compares `candidate`
output against a `baseline`, with optional natural-language `criteria`, and
reports what regressed, improved, or stayed stable — deterministically and
offline.

```bash
pip install evalitai-engine
evalitai compare --baseline baseline.jsonl --candidate candidate.jsonl --judge ollama/llama3
```

## What it does

- Runs **deterministic metrics** — no LLM call, pure checks against
  `ground_truth`/config: `output_format` (valid JSON), `must_include`,
  `must_not_include`, `prohibited_terms`, `latency`.
- Runs **LLM-as-a-judge metrics** via a LiteLLM provider abstraction (any
  provider LiteLLM supports, plus a deterministic `stub` judge for offline
  testing): `overall_quality`, `instruction_adherence`, `completeness`,
  `relevance`, `tone`, `hallucination`, `faithfulness`, `tool_use`.
- Accepts free-text or structured `criteria.yaml` and compiles it into a
  custom rubric metric for the judge — no need to hand-write prompts — and
  can restrict which built-in metrics run via an allowlist.
- Diffs `candidate` against `baseline` case by case and metric by metric,
  classifying each as a `regression`, `improvement`, or `stable`, with a
  `severity` (low/medium/high/critical) and warnings (e.g. judge/version
  mismatches between baseline and candidate runs).
- Runs 100% locally: no network calls are required unless you point it at a
  hosted LLM provider yourself.

## CLI

```bash
# Compare candidate against baseline
evalitai compare --baseline baseline.jsonl --candidate candidate.jsonl \
  --judge stub --criteria criteria.yaml --output comparison.json

# Evaluate candidate cases without a baseline
evalitai evaluate --candidate candidate.jsonl --judge stub --output result.json
```

`baseline`/`candidate` are JSONL files, one `EvaluationCase` per line
(`case_key`, `output`, and optional `input`, `context`, `ground_truth`,
`metadata`). See `--help` on either command for the full option list
(regression `--threshold`, `--confidence-floor`, `--baseline-judge`, etc.).

## Docs and examples

Full documentation is in [`docs/`](./docs/README.md) (installation, CLI
reference, the compare/evaluate contract, JSONL format, criteria YAML
syntax, metrics reference). A runnable, fully offline walkthrough is in
[`examples/offline-chatbot/`](./examples/offline-chatbot/README.md).

## Status

Early alpha. The public contract (`compare()` / `evaluate()`) is not yet
frozen — see the issue tracker for progress.

## License

Apache-2.0 — see [`LICENSE`](./LICENSE) and [`NOTICE`](./NOTICE).
