import json
from pathlib import Path

import yaml
from pydantic import BaseModel

from evalitai.core.models import Criteria, EvaluationCase


def read_cases(path: Path) -> list[EvaluationCase]:
    """Read a baseline/candidate JSONL file: one EvaluationCase per line."""
    cases: list[EvaluationCase] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON") from exc
            cases.append(EvaluationCase.model_validate(payload))
    return cases


def read_criteria(path: Path | None) -> Criteria | None:
    """Read an optional criteria.yaml file into its raw (uncompiled) form."""
    if path is None:
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return Criteria.model_validate(data)


def write_json(model: BaseModel, path: Path) -> None:
    path.write_text(model.model_dump_json(indent=2), encoding="utf-8")
