# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Deterministic metrics: `output_format`, `must_include`, `must_not_include`,
  `prohibited_terms`, `latency`.
- LLM-as-a-judge metrics via a LiteLLM provider abstraction: `overall_quality`,
  `instruction_adherence`, `completeness`, `relevance`, `tone`,
  `hallucination`, `faithfulness`, `tool_use`.
- Criteria compiler: free-text or structured `criteria.yaml` compiles into a
  custom rubric metric plus a metric allowlist.
- Regression classification with confidence-aware severity buckets
  (low/medium/high/critical) and baseline/candidate judge-version warnings.
- `evalitai compare` / `evalitai evaluate` CLI commands.
- Engine documentation (`docs/`) and a runnable offline example
  (`examples/offline-chatbot/`).

## [0.1.0] - 2026-07-03

### Added

- Initial package scaffold, CLI entry point, and CI.
- Frozen `compare()` / `evaluate()` public contract and JSONL I/O.
