# Installation

Requires Python 3.12+.

```bash
pip install evalitai-engine
```

This installs the `evalitai` CLI and the `evalitai` Python package.

Verify the install:

```bash
evalitai version
```

## Scaffold a project

```bash
evalitai init
```

Creates `baseline.jsonl`, `candidate.jsonl`, `criteria.yaml`, and `.env` in
the current directory, pre-filled with a runnable example — edit them in
place rather than creating anything from scratch. Safe to rerun: it never
overwrites a file that already exists.

## Set up a judge provider

The LLM-judge metrics are the main point of `evalitai` — pick any model
[LiteLLM](https://docs.litellm.ai/docs/providers) supports and set it in
the scaffolded `criteria.yaml`'s `judge:` field (see
[criteria.md](./criteria.md)) — set it once, reused across every run;
`--judge` on the command line overrides it for a single run.

- **Hosted**: use a LiteLLM model string (e.g. `gpt-4o-mini`,
  `claude-haiku-4-5`, `gemini-2.5-flash`) and set the provider's API key.
- **Local, no API key**: run [Ollama](https://ollama.com) and use
  `ollama/llama3` (or any model you've pulled).

### API keys via `.env`

`evalitai` calls `python-dotenv`'s `load_dotenv()` on startup, so it reads
a `.env` file from your current directory automatically — no need to
`export` keys into your shell. `evalitai init` scaffolds a `.env` with a
line for each supported provider; fill in the one you picked above and
leave the rest blank.

`.env` is gitignored by default in this repo; never commit real keys.

### Offline smoke test

No judge configured yet? `--judge stub` is a deterministic judge that
always skips the LLM-backed metrics — useful to verify the pipeline and
your JSONL files are well-formed before wiring up a real model, and for
CI. It does **not** run `overall_quality`, `hallucination`, etc. — see
[metrics.md](./metrics.md).

## Development install

```bash
git clone https://github.com/ysmmfe/evalitai-engine
cd evalitai-engine
uv sync --extra dev
uv run pytest
```
