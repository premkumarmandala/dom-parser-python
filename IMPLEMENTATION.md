# Implementation

This document describes how `dom-parser-python` transforms raw HTML into a DOM
tree and how the CLI answers queries. It is written from scratch: there is **no
`re`** anywhere in the source and **no external HTML parsing library**.

## Pipeline

```
FILE (raw HTML text)
  │
  ▼  tokenize(html)                       src/tokenizer.py
[Token(kind, raw), ...]                   OPEN_TAG | CLOSE_TAG | TEXT
  │
  ▼  build_dom(tokens)                    src/parser.py
       └─ parse_tag(raw)                  src/attributes.py
DocumentNode tree                         src/dom.py
  │
  ├─ format_tree(...)        ▲  src/main.py dispatches on CLI mode
  ├─ get_text_content(...)   │
  └─ find_root_elements(...) ┘
  │
  ▼
stdout
```

Every stage consumes only the output of the previous one, which keeps each
module independently testable.

## Module map

| Module | Responsibility |
| --- | --- |
| `src/tokenizer.py` | Scan characters into `Token(kind, raw)` lexemes. |
| `src/attributes.py` | Parse a raw tag slice into `(tag_name, attributes)`. |
| `src/parser.py` | Build the `DocumentNode` tree from tokens using a stack. |
| `src/dom.py` | Node dataclasses plus format / text / query helpers. |
| `src/main.py` | Argument parsing, file reading, mode dispatch, exit codes. |

## 1. Tokenizer (`src/tokenizer.py`)

A single left-to-right scan. `TokenKind` is a `StrEnum` with `OPEN_TAG`,
`CLOSE_TAG`, and `TEXT`; `Token` is a frozen, slotted dataclass holding the kind
and the exact source slice.

Algorithm:

1. Walk to the next `<`.
2. Emit any pending characters as a `TEXT` token (kept verbatim, including
   whitespace and newlines).
3. Scan forward to the next `>`. If there is none, the remainder of the input is
   one final `TEXT` token (an unterminated tag is not a tag).
4. Otherwise emit `CLOSE_TAG` when the slice starts with `</`, else `OPEN_TAG`.
5. Continue after the `>`.

`tokenize(html) -> list[Token]` returns tokens in source order; empty input
returns an empty list.

## 2. Stack-based DOM construction (`src/parser.py`)

`build_dom(tokens: list[Token]) -> DocumentNode` makes one pass over the tokens
while maintaining `stack: list[ElementNode]`, the currently open elements.

- **OPEN_TAG** — call `parse_tag` to get `(name, attributes)`. Skip the token if
  the name is empty. Build `ElementNode(tag=name, attributes=attributes)`,
  append it to `stack[-1].children` (or to `document.children` when the stack is
  empty), then push it.
- **TEXT** — `token.raw.strip()`. Drop it entirely when empty; otherwise append
  a `TextNode(text)` to `stack[-1].children`. Text with no open element (a
  non-element root) is dropped because `DocumentNode` holds elements only.
- **CLOSE_TAG** — `stack.pop()` guarded by `if stack`, so a stray close tag
  cannot raise.

Elements still open at end of input stay in the tree. A mismatched close tag
simply pops the current top, matching the tolerant, non-validating design.

### No cycles

Nodes reference **children only** — there are no parent pointers. The structure
is therefore always a tree and cannot contain a reference cycle.

## 3. Character-by-character attribute parsing (`src/attributes.py`)

`parse_tag(raw) -> tuple[str, list[tuple[str, str]]]` also avoids `re`. Steps:

1. Strip the leading `<` and any `/`, the trailing `>`, and trailing
   whitespace; drop a trailing `/` (self-closing marker).
2. The tag name is the first run of non-whitespace characters, **lowercased**.
3. Loop over the rest:
   - Skip whitespace, stop at end.
   - Read the attribute name up to whitespace or `=` / `/`, lowercased. A stray
     `=`/`/` with no name is skipped so the scan always advances.
   - Skip whitespace, then:
     - `key="value"` or `key='value'` — read to the matching quote.
     - `key=value` — read to the next whitespace.
     - `key` — boolean attribute, value is `""`.
   - Append `(name, value)`.

Examples: `<div class="hero" id="main">` →
`("div", [("class", "hero"), ("id", "main")])`; `<button disabled>` →
`("button", [("disabled", "")])`; `<img src="pic.jpg" />` →
`("img", [("src", "pic.jpg")])`.

## 4. DOM helpers (`src/dom.py`)

`TextNode`, `ElementNode`, and `DocumentNode` are slotted dataclasses;
`DocumentNode` represents the root (`.`) and holds top-level elements. `Node` is
the union of all three.

### `format_tree(node, indent=0) -> str`

Renders the **in-memory tree** like the Linux `tree` command, never by
re-formatting source text:

- Document root prints as `.`.
- Element prints as `tag` or `tag [key="value", ...]`.
- Text prints quoted, e.g. `"Hello"`.

Box-drawing connectors come from a recursive helper `_tree_lines(node, prefix,
is_last, is_root, lines)`: each child is prefixed by `├── ` or `└── `, and the
prefix passed to descendants is extended with `│   ` when the parent was not the
last child, or `    ` when it was.

### `get_text_content(node) -> str`

Collects every `TextNode` in document order and joins them with newlines.

### `find_elements` vs `find_root_elements`

Both accept keyword filters `tag`, `id_`, and `class_name` that combine with AND
semantics; `None` filters are ignored. Tag matching is case-insensitive, `id_`
matches the `id` attribute, and `class_name` matches any single token in the
space-separated `class` attribute.

- `find_elements` records **every** match.
- `find_root_elements` records only **outermost** matches: once an element
  matches, its subtree is not searched again. A match nested inside another
  match is therefore rendered within its ancestor instead of being repeated at
  the top level. The CLI uses this for `--find-*`.

## 5. CLI (`src/main.py`)

`main(argv=None) -> int` validates arguments, reads the file, then dispatches on
the selected mode:

| Mode | Output |
| --- | --- |
| *(default)* / `--tree` | `format_tree(document)` |
| `--text` | `get_text_content(document)` |
| `--find-tag TAG` | `format_tree(DocumentNode(find_root_elements(document, tag=...)))` |
| `--find-id ID` | same, `id_=...` |
| `--find-class CLASS` | same, `class_name=...` |

Exit codes and exact messages:

- Invalid or missing arguments → the `USAGE` string to **stderr**, exit `1`.
- `FileNotFoundError` / `PermissionError` → `Cannot open file: FILE` to
  **stderr**, exit `1`.
- Success → rendered output to stdout, exit `0`. Empty results print nothing.

Because find modes render a synthetic `DocumentNode`, their output always starts
with `.`.

## Invariants

- **No `re`** — all parsing is character-by-character.
- **No external HTML parsing libraries** — `dependencies = []`.
- **Acyclic DOM** — child-only references; no parent pointers.
- **`mypy --strict`** over `src` and `tests`, Python 3.11+.
- **Ruff** clean, 88-column lines, double quotes, space indentation.

## Testing

Four pytest modules cover each stage:

| File | Focus |
| --- | --- |
| `tests/test_tokenizer.py` | Token kinds, verbatim text, unterminated tags. |
| `tests/test_parser.py` | Tag/text nesting, attribute variants, edge cases. |
| `tests/test_dom.py` | `format_tree`, `get_text_content`, find helpers. |
| `tests/test_main.py` | CLI modes, output, usage and I/O errors. |

Run them with `uv run pytest`.
