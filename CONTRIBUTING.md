# Contributing to dom-parser-python

Thanks for your interest in improving the project. This document covers the
rules, style, and checks expected of every contribution.

## Development setup

### With `uv` (recommended)

```bash
uv sync --group dev
```

### With `pip`

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pip install -e .
```

## Project invariants

These are non-negotiable; pull requests that break them will not be accepted:

- **No regular expressions.** Do not import or use `re` anywhere in `src/` or
  `tests/`. Parsing is character-by-character by design.
- **No external HTML parsing libraries.** `dependencies = []` in
  `pyproject.toml` must stay empty; do not add `lxml`, `html.parser`,
  BeautifulSoup, etc.
- **Acyclic DOM.** Nodes may reference their children only. Never add parent
  pointers or any back-reference that could introduce a cycle.
- **Strict typing.** All source must pass `mypy --strict`. Annotate every
  function, including tests.
- **Python 3.11+.** Use modern syntax supported by the pinned target
  (`StrEnum`, PEP 604 unions, `from __future__ import annotations`).

## Code style

- Run `ruff format` before committing; do not hand-format.
- Formatting rules from `pyproject.toml`: 88-column lines, double quotes, space
  indentation, LF line endings.
- Linting selects `E`, `W`, `F`, `I`, `UP`, `B`, `A`, `C4`, `SIM`, `RUF`,
  `PTH`, `TID`, `ARG`, `FA`, `ICN`, `PIE`, `RET`, `T20` (the CLI is the only
  file allowed to `print`).
- First-party imports: `attributes`, `dom`, `main`, `parser`, `tokenizer`.
- Add docstrings to public functions and classes. Prefer clear code over
  comments; do not add comments that restate the code.

## Required checks

All of the following must pass with zero warnings before a change is merged:

```bash
uv run pytest
uv run mypy --strict .
uv run ruff check .
uv run ruff format --check .
```

## Testing guidelines

- Add tests for any behavior change; bug fixes should include a regression test.
- Keep tests typed — `tests/` is type-checked with the same strictness as
  `src/` (only unused-argument and decorator rules are relaxed).
- Place tests in the matching module: tokenizer behavior in
  `tests/test_tokenizer.py`, parser/attribute behavior in
  `tests/test_parser.py`, DOM helpers in `tests/test_dom.py`, and CLI behavior
  in `tests/test_main.py`.
- Prefer exact-string assertions for CLI output so formatting regressions are
  caught.

## Sample fixtures

HTML files at the repository root are manual examples, not test fixtures (tests
create their own temporary files). If you add one:

- keep it small and focused on the feature it demonstrates;
- give it a descriptive name such as `deep.html` or `attributes.html`;
- do not rely on it from tests.

## Commits and pull requests

- Make small, focused commits with clear messages.
- Describe what changed and why; mention the affected module(s).
- Update `README.md` / `IMPLEMENTATION.md` when behavior or the CLI changes.
- Ensure the required checks listed above pass locally before opening a PR.

## Reporting issues

Please include the input HTML, the exact command you ran, the observed output,
and the output you expected.
