# dom-parser-python

A minimal HTML DOM parser written from scratch — **no `re`, no external HTML
parsing libraries**. It reads an HTML file, tokenizes it character by character,
builds a DOM tree in memory, and answers simple queries from the command line.

## Features

- Handwritten character-by-character tokenizer (tags + text).
- Stack-based DOM construction with parsed attributes.
- Linux `tree`-style rendering of the in-memory DOM.
- Queries by tag, `id`, and `class` (multi-class aware).
- Strict typing: `mypy --strict`, Ruff lint + format, pytest.

## Requirements

- Python 3.11 or newer.

## Setup

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

## Usage

```bash
domparser FILE [--tree | --text | --find-tag TAG | --find-id ID | --find-class CLASS]
```

With `uv` you can run the CLI without activating a shell:

```bash
uv run domparser example.html
```

### Output modes

| Flag | Description |
| --- | --- |
| *(none)* / `--tree` | Print the DOM tree (default). |
| `--text` | Print all text content, one text node per line. |
| `--find-tag TAG` | Print outermost elements with that tag (case-insensitive). |
| `--find-id ID` | Print the element with that `id`. |
| `--find-class CLASS` | Print outer elements carrying that class token. |

`--find-*` output is always rooted at `.`. A match nested inside another match
is shown within its ancestor, not repeated at the top level.

### Examples

Given `page.html`:

```html
<html>
  <body>
    <h1>Hello</h1>
    <p class="intro" id="first">Welcome to AI Karyashala</p>
    <p class="note">Learn by doing</p>
  </body>
</html>
```

```bash
$ uv run domparser page.html --tree
.
└── html
    └── body
        ├── h1
        │   └── "Hello"
        ├── p [class="intro", id="first"]
        │   └── "Welcome to AI Karyashala"
        └── p [class="note"]
            └── "Learn by doing"

$ uv run domparser page.html --text
Hello
Welcome to AI Karyashala
Learn by doing

$ uv run domparser page.html --find-id first
.
└── p [class="intro", id="first"]
    └── "Welcome to AI Karyashala"
```

Try the bundled fixtures: `example.html`, `page.html`, `attributes.html`,
`deep.html`.

## Development

```bash
uv run pytest                        # run the test suite
uv run ruff check .                  # lint
uv run ruff format --check .         # formatting
uv run mypy --strict .               # strict type check
```

Format in place with `uv run ruff format .`. See [CONTRIBUTING.md](CONTRIBUTING.md)
for contribution rules and [IMPLEMENTATION.md](IMPLEMENTATION.md) for how the
parser works internally.

## Project layout

```
src/
  tokenizer.py   raw HTML  -> list[Token]
  attributes.py  raw tag   -> (tag_name, attributes)
  parser.py      tokens    -> DocumentNode (stack-based)
  dom.py         DOM nodes + format/query helpers
  main.py        CLI entry point (domparser)
tests/           unit tests for each stage
example.html     sample input
```

## Configuration

- Entry point: `domparser = "main:main"` (`pyproject.toml`).
- Strict mypy over `src` and `tests`.
- Ruff: 88-column lines, double quotes, space indentation.

## License

MIT
