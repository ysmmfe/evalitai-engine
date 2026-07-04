# Contributing to evalitai-engine

Thanks for considering a contribution.

## Developer Certificate of Origin (DCO)

Every commit must be signed off:

```bash
git commit -s -m "your message"
```

This adds a `Signed-off-by` trailer certifying you wrote the change (or
otherwise have the right to submit it under this project's license). It's
lighter-weight than a CLA but gives the project unambiguous rights to use
and relicense contributions. PRs with unsigned commits are blocked by CI.

## Before you open a PR

1. `uv sync --extra dev` to install dependencies.
2. `uv run ruff check .` — lint.
3. `uv run mypy src` — type check.
4. `uv run pytest` — tests. New metrics or comparison logic need test
   coverage; PRs without tests won't be merged.

## Review standard for accuracy-affecting changes

Changes that touch metric scoring, judge prompts, or the
regression-classification rule are held to a higher bar than typical PRs:
"looks reasonable" isn't enough. Include a test case that demonstrates the
before/after behavior, and explain in the PR description why the new
behavior is more accurate, not just different.

## Scope

This package must keep working 100% offline (local judge or your own API
key). Do not add code that assumes a network dependency beyond the LLM
provider the user configures.

## Where things live

```
src/evalitai/
  cli.py                  # `evalitai compare|evaluate|init` entry points
  core/
    models.py              # EvaluationCase and other shared data models
    contract.py             # compare()/evaluate() — the frozen public API
  io/jsonl.py               # baseline/candidate JSONL reading
  judge/
    provider.py             # LiteLLM call wrapper (the only network boundary)
    prompts.py               # judge prompt templates
    criteria.py               # compiles criteria.yaml into a custom rubric metric
    metrics.py                 # LLM-judge metrics (overall_quality, tone, ...)
  metrics/
    registry.py               # maps metric name -> implementation
    deterministic/checks.py    # non-LLM checks (output_format, must_include, ...)
```

**Adding a new deterministic metric**: implement it in
`metrics/deterministic/checks.py`, register it in `metrics/registry.py`, add
tests in `tests/test_deterministic_metrics.py`, and document it in
`docs/metrics.md`.

**Adding a new LLM-judge metric**: add the prompt in `judge/prompts.py`, the
scoring logic in `judge/metrics.py`, register it, and add tests in
`tests/test_judge.py` (mock the provider — don't call a real LLM in tests).

**Changing the `compare()`/`evaluate()` contract** in `core/contract.py`: this
is the frozen public API — see the "Review standard for accuracy-affecting
changes" above, and update `docs/contract.md` in the same PR.
