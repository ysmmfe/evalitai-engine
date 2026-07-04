## What this does

<!-- Summary of the change. -->

## Why

<!-- The problem or motivation. Link an issue if there is one. -->

## If this changes metric scoring, judge prompts, or the regression-classification rule

<!-- Include a before/after test case and explain why the new behavior is more accurate, not just different. Required per CONTRIBUTING.md's accuracy review standard. -->

## Checklist

- [ ] Commits are signed off (`git commit -s`) — see `CONTRIBUTING.md`.
- [ ] `uv run ruff check .` passes.
- [ ] `uv run mypy src` passes.
- [ ] `uv run pytest` passes, and new metrics/comparison logic have test coverage.
- [ ] Works fully offline (local judge or the user's own API key) — no new network dependency beyond the configured LLM provider.
