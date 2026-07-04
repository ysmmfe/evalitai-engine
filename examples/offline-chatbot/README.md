# Example: offline chatbot regression check

A tiny support-chatbot dataset that reproduces a comparison report with
flagged regressions — fully offline, no LLM provider or API key required.

## Files

- `baseline.jsonl` — 4 cases with the "known-good" candidate outputs.
- `candidate.jsonl` — the same 4 `case_key`s with a new candidate's outputs.
  Three of them regress on purpose (a dropped required term, a violated
  forbidden term, and a broken JSON contract); one stays stable.
- `criteria.yaml` — optional: shows how to restrict which built-in metrics
  run via an allowlist, plus a free-text custom criterion (skipped offline
  since it needs a real judge — see [`docs/criteria.md`](../../docs/criteria.md)).

## Run it

```bash
evalitai compare \
  --baseline examples/offline-chatbot/baseline.jsonl \
  --candidate examples/offline-chatbot/candidate.jsonl \
  --judge stub
```

`--judge stub` is the default deterministic judge, so this reproduces
identically with no network access. Expect `compared_case_count: 4` and
three `"verdict": "regression"` entries, all `"severity": "critical"`:

| case_key            | metric           | why it regressed                                    |
| ------------------- | ---------------- | ----------------------------------------------------- |
| `reset-password`    | `must_include`   | candidate dropped the required word "email"          |
| `refund-policy`     | `must_not_include` | candidate said "no refunds", a forbidden phrase     |
| `order-status-json` | `output_format`  | candidate replied in prose instead of JSON            |
| `greeting`          | `must_include`   | unchanged — stays `stable`                            |

To also apply the metric allowlist from `criteria.yaml`:

```bash
evalitai compare \
  --baseline examples/offline-chatbot/baseline.jsonl \
  --candidate examples/offline-chatbot/candidate.jsonl \
  --judge stub \
  --criteria examples/offline-chatbot/criteria.yaml
```

To see the LLM-judge metrics (`overall_quality`, `hallucination`, etc.) and
the custom criterion actually run instead of being skipped, point `--judge`
at a real model, e.g. `--judge ollama/llama3` (local, needs
[Ollama](https://ollama.com) running) or `--judge gpt-5-mini` (needs
`OPENAI_API_KEY` set).
