"""LLM provider abstraction for judge calls, via LiteLLM.

LiteLLM lets ``EvaluatorConfig.judge`` name a local model (e.g.
``ollama/llama3``, ``vllm/...``) or a hosted one (e.g. ``gpt-4o-mini``) using
a user-supplied API key from the environment — the caller is agnostic to
which.
"""

import time
from dataclasses import dataclass

import litellm

from evalitai.core.models import EvaluatorConfig
from evalitai.judge.prompts import SYSTEM_PROMPT


@dataclass(frozen=True)
class JudgeResponse:
    raw_content: str
    latency_ms: float
    cost_usd: float | None


def call_judge(prompt: str, config: EvaluatorConfig) -> JudgeResponse:
    started = time.perf_counter()
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
