# evalitai-engine

[![CI](https://github.com/ysmmfe/evalitai-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/ysmmfe/evalitai-engine/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/evalitai-engine.svg)](https://pypi.org/project/evalitai-engine/)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](./LICENSE)

Open-source evaluation engine for LLM-based systems. Compares `candidate`
output against a `baseline`, using an LLM judge (your choice of model) plus
optional natural-language `criteria`, and reports what regressed, improved,
or stayed stable.

## Quickstart: zero to hero

**1. Install**

```bash
pip install evalitai-engine
```

**2. Scaffold a project in the current directory**

```bash
evalitai init
```

This creates four files, pre-filled with a runnable example — edit them
in place, nothing to write from scratch:

| File               | What to fill in                                                                 |
| ------------------ | ---------------------------------------------------------------------------------- |
| `.env`             | The API key for whichever provider you pick below (only that one line).            |
| `criteria.yaml`    | Its `judge:` field — any model string [LiteLLM](https://docs.litellm.ai/docs/providers) supports: hosted (`gpt-4o-mini`, `claude-haiku-4-5`, `gemini-2.5-flash`, ...) or local via [Ollama](https://ollama.com) (`ollama/llama3`, no API key needed). |
| `baseline.jsonl`   | Replace the sample case(s) with your system's known-good outputs.                  |
| `candidate.jsonl`  | Same `case_key`s, with the new outputs you want to check for regressions.          |

**3. Run it**

```bash
evalitai compare
```

`compare` and `evaluate` pick up `baseline.jsonl`, `candidate.jsonl`, and
`criteria.yaml` from the current directory automatically. You'll get a
JSON report with `overall_quality`, `hallucination`, `tone`, and the rest
of the LLM-judge metrics for each case, scored by the model you configured
in step 2 — see [docs/metrics.md](./docs/metrics.md) for the full list.
Pass `--baseline`/`--candidate`/`--criteria`/`--output` to use different
files, or `--judge <model>` to override `criteria.yaml`'s judge for one run.

No API key handy right now? Set `judge: stub` in `criteria.yaml` to
smoke-test the pipeline fully offline — useful for CI, but it only runs
the deterministic checks (`must_include`, `output_format`, ...), not the
LLM-judge metrics that are the actual point of the tool. A larger, fully
offline dataset is bundled at
[`examples/offline-chatbot/`](./examples/offline-chatbot/README.md).

## What it does

- Runs **LLM-as-a-judge metrics** via a LiteLLM provider abstraction — any
  model, any provider LiteLLM supports — to score things a deterministic
  check can't: `overall_quality`, `instruction_adherence`, `completeness`,
  `relevance`, `tone`, `hallucination`, `faithfulness`, `tool_use`.
- Accepts free-text or structured `criteria.yaml` and compiles it into a
  custom rubric metric for that judge — no need to hand-write prompts —
  and lets you set the judge model itself once (`judge:`), reused across
  runs.
- Also runs **deterministic metrics** for the checks that genuinely don't
  need a judge — `output_format` (valid JSON), `must_include`,
  `must_not_include`, `prohibited_terms`, `latency` — so you're not paying
  for an LLM call to verify a JSON schema.
- Diffs `candidate` against `baseline` case by case and metric by metric,
  classifying each as a `regression`, `improvement`, or `stable`, with a
  `severity` (low/medium/high/critical) and warnings (e.g. judge/version
  mismatches between baseline and candidate runs).

## CLI

```bash
# Compare candidate against baseline (reads ./baseline.jsonl, ./candidate.jsonl, ./criteria.yaml)
evalitai compare

# Evaluate candidate cases without a baseline
evalitai evaluate

# Override any of the conventional filenames, or write to a file instead of stdout
evalitai compare --baseline other-baseline.jsonl --output comparison.json
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
