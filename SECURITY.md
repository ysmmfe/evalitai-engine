# Security Policy

## Supported Versions

evalitai-engine is in early alpha (`0.x`). Security fixes are only
guaranteed for the latest published release on PyPI.

## Reporting a Vulnerability

Please do **not** open a public GitHub issue for security vulnerabilities
(e.g., prompt injection into the judge that leaks secrets, unsafe handling
of API keys, path traversal in file I/O).

Instead, report privately:

- Email: ysmmfe13@alu.ufc.br
- Or use [GitHub's private vulnerability reporting](https://github.com/ysmmfe/evalitai-engine/security/advisories/new)
  for this repository.

Include steps to reproduce, the affected version, and potential impact.
You should receive an acknowledgment within a few days. Once a fix is
available, we'll coordinate disclosure timing with you before it's made
public.

## Scope

This project runs fully offline aside from the LLM provider call you
configure. Reports about the third-party LLM provider itself (OpenAI,
Anthropic, Ollama, etc.) should go to that provider directly, not here.
