"""LLM provider abstraction for judge calls, via LiteLLM.

LiteLLM lets ``EvaluatorConfig.judge`` name a local model (e.g.
``ollama/llama3``, ``vllm/...``) or a hosted one (e.g. ``gpt-5-mini``) using
a user-supplied API key from the environment — the caller is agnostic to
which.
"""

import time
from dataclasses import dataclass

import litellm
from openai import OpenAIError

from evalitai.core.models import EvaluatorConfig
from evalitai.judge.prompts import SYSTEM_PROMPT

# Silence LiteLLM's own "Give Feedback / Get Help" banner on errors - we
# already surface a friendlier message via JudgeCallError.
litellm.suppress_debug_info = True


class JudgeCallError(RuntimeError):
    """Raised when the configured judge model can't be reached or fails.

    Wraps LiteLLM/provider SDK exceptions (missing/invalid API key, network
    failure, rate limit, ...) so the CLI can show one friendly line instead
    of the full provider stack trace.
    """


@dataclass(frozen=True)
class JudgeResponse:
    raw_content: str
    latency_ms: float
    cost_usd: float | None


def call_judge(prompt: str, config: EvaluatorConfig) -> JudgeResponse:
    started = time.perf_counter()
    try:
        response = litellm.completion(
            model=config.judge,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=config.temperature,
            seed=config.seed,
            response_format={"type": "json_object"},
        )
    except OpenAIError as exc:
        raise JudgeCallError(
            f"Judge model '{config.judge}' call failed: {exc}\n"
            "Check that the matching API key is set in .env (or your "
            "environment), or run with --judge stub to test offline "
            "without any LLM-judge metrics."
        ) from exc
    latency_ms = (time.perf_counter() - started) * 1000
    content = response.choices[0].message.content or ""

    try:
        cost_usd = litellm.completion_cost(completion_response=response)
    except Exception:
        # Cost data is unavailable for some local/self-hosted models —
        # cost tracking is best-effort, not required for a valid result.
        cost_usd = None

    return JudgeResponse(
        raw_content=content, latency_ms=latency_ms, cost_usd=cost_usd
    )
