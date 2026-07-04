from types import SimpleNamespace

from evalitai.core.models import EvaluatorConfig
from evalitai.judge.provider import call_judge


def _fake_response(content: str) -> SimpleNamespace:
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


def test_call_judge_returns_content_latency_and_cost(monkeypatch) -> None:
    monkeypatch.setattr(
        "litellm.completion", lambda **kwargs: _fake_response('{"score": 90}')
    )
    monkeypatch.setattr("litellm.completion_cost", lambda **kwargs: 0.0002)

    response = call_judge("prompt", EvaluatorConfig(judge="fake-model"))

    assert response.raw_content == '{"score": 90}'
    assert response.latency_ms >= 0
    assert response.cost_usd == 0.0002


def test_call_judge_tolerates_missing_cost_data(monkeypatch) -> None:
    def raise_cost_error(**kwargs: object) -> float:
        raise ValueError("cost unavailable for this model")

    monkeypatch.setattr(
        "litellm.completion", lambda **kwargs: _fake_response('{"score": 50}')
    )
    monkeypatch.setattr("litellm.completion_cost", raise_cost_error)

    response = call_judge("prompt", EvaluatorConfig(judge="fake-model"))

    assert response.cost_usd is None


def test_call_judge_handles_empty_content(monkeypatch) -> None:
    monkeypatch.setattr("litellm.completion", lambda **kwargs: _fake_response(None))
    monkeypatch.setattr("litellm.completion_cost", lambda **kwargs: None)

    response = call_judge("prompt", EvaluatorConfig(judge="fake-model"))

    assert response.raw_content == ""
