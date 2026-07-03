# evalitai-engine

Open-source evaluation engine for LLM-based systems. Compares `candidate`
output against a `baseline`, with optional natural-language `criteria`, and
reports what regressed, improved, or stayed stable — deterministically and
offline.

```bash
pip install evalitai-engine
evalitai compare --baseline baseline.jsonl --candidate candidate.jsonl --judge local:ollama/llama3
```

## What it does

- Runs deterministic checks (format validation, required/forbidden content)
  and LLM-as-a-judge metrics (quality, hallucination, tone, faithfulness,
  instruction adherence, and more).
- Accepts free-text or YAML criteria and compiles them into a rubric for the
  judge — no need to hand-write prompts.
- Diffs `candidate` against `baseline` case by case and metric by metric,
  classifying each as a regression, an improvement, or stable.
- Runs 100% locally: no network calls are required unless you point it at a
  hosted LLM provider yourself.

## Status

Early alpha. The public contract (`compare()` / `evaluate()`) is not yet
frozen — see the issue tracker for progress.

## License

Apache-2.0 — see [`LICENSE`](./LICENSE) and [`NOTICE`](./NOTICE).
