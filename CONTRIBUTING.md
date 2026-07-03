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
