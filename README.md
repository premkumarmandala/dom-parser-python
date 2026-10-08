# dom-parser-python

A minimal DOM parser written from scratch — no HTML parsing libraries.

## Development

```bash
uv sync --group dev
uv run ruff check . && uv run ruff format --check .
uv run mypy
uv run pytest
uv run domparser
```
