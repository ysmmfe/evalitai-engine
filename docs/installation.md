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

## Optional: a real judge provider

`evalitai` works fully offline out of the box using `--judge stub`, a
deterministic judge that always skips LLM-backed metrics — no API key
needed. To run the LLM-as-a-judge metrics for real, point `--judge` at any
model [LiteLLM](https://docs.litellm.ai/docs/providers) supports:

- **Local, no API key**: run [Ollama](https://ollama.com) and pass
  `--judge ollama/llama3` (or any model you've pulled).
- **Hosted**: pass a LiteLLM model string (e.g. `--judge gpt-4o-mini`) and
  set the provider's API key in the environment (e.g. `OPENAI_API_KEY`).

## Development install

```bash
git clone https://github.com/ysmmfe/evalitai-engine
cd evalitai-engine
uv sync --extra dev
uv run pytest
```
