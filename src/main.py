"""CLI entry point for dom-parser-python (Section 5)."""

from __future__ import annotations

import sys
from enum import StrEnum
from pathlib import Path
from typing import NamedTuple

from dom import (
    DocumentNode,
    ElementNode,
    find_root_elements,
    format_tree,
    get_text_content,
)
from parser import build_dom
from tokenizer import Token, tokenize

USAGE: str = (
    "Usage: domparser FILE [--tree | --text | --find-tag TAG | "
    "--find-id ID | --find-class CLASS]"
)


class Mode(StrEnum):
    """Output mode selected on the command line."""

    TREE = "--tree"
    TEXT = "--text"
    FIND_TAG = "--find-tag"
    FIND_ID = "--find-id"
    FIND_CLASS = "--find-class"


_VALUE_MODES: frozenset[Mode] = frozenset(
    {Mode.FIND_TAG, Mode.FIND_ID, Mode.FIND_CLASS}
)
_PLAIN_MODES: frozenset[Mode] = frozenset({Mode.TREE, Mode.TEXT})


class ParsedArgs(NamedTuple):
    """Validated command-line arguments."""

    path: str
    mode: Mode | None
    value: str | None


def _mode_from(token: str) -> Mode | None:
    """Return the Mode for a flag token, or None if it is not a known flag."""
    try:
        return Mode(token)
    except ValueError:
        return None


def _parse_args(args: list[str]) -> ParsedArgs | None:
    """Validate CLI arguments.

    Args:
        args: Argument list excluding the program name.

    Returns:
        The parsed arguments, or None if the arguments are missing/invalid.
    """
    if not args or args[0].startswith("-"):
        return None
    path = args[0]
    rest = args[1:]
    if not rest:
        return ParsedArgs(path, None, None)
    if len(rest) == 1:
        mode = _mode_from(rest[0])
        if mode is None or mode not in _PLAIN_MODES:
            return None
        return ParsedArgs(path, mode, None)
    if len(rest) == 2:
        mode = _mode_from(rest[0])
        if mode is None or mode not in _VALUE_MODES:
            return None
        value = rest[1]
        if value.startswith("-"):
            return None
        return ParsedArgs(path, mode, value)
    return None


def _read_file(path: str) -> str | None:
    """Read a text file.

    Args:
        path: Path of the file to read.

    Returns:
        The file content, or None if the file cannot be opened.
    """
    try:
        return Path(path).read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError):
        return None


def _format_matches(elements: list[ElementNode]) -> str:
    """Render outermost matches as a document rooted at '.'.

    The synthetic document means the output always starts with '.', even
    when nothing matched, and each outer match keeps its full subtree.
    """
    return format_tree(DocumentNode(children=elements))


def _render(document: DocumentNode, parsed: ParsedArgs) -> str:
    """Render a document according to the selected output mode.

    Args:
        document: The parsed document tree.
        parsed: Validated command-line arguments.

    Returns:
        The text to print, or '' when there is nothing to show.
    """
    if parsed.mode is Mode.TEXT:
        return get_text_content(document)
    if parsed.mode is Mode.FIND_TAG:
        return _format_matches(find_root_elements(document, tag=parsed.value))
    if parsed.mode is Mode.FIND_ID:
        return _format_matches(find_root_elements(document, id_=parsed.value))
    if parsed.mode is Mode.FIND_CLASS:
        return _format_matches(find_root_elements(document, class_name=parsed.value))
    return format_tree(document)


def main(argv: list[str] | None = None) -> int:
    """Run the domparser CLI.

    Args:
        argv: Argument list excluding the program name. Defaults to sys.argv[1:].

    Returns:
        Process exit code (0 on success, 1 on usage or I/O errors).
    """
    args: list[str] = sys.argv[1:] if argv is None else argv
    parsed: ParsedArgs | None = _parse_args(args)
    if parsed is None:
        print(USAGE, file=sys.stderr)
        return 1
    content: str | None = _read_file(parsed.path)
    if content is None:
        print(f"Cannot open file: {parsed.path}", file=sys.stderr)
        return 1
    tokens: list[Token] = tokenize(content)
    document: DocumentNode = build_dom(tokens)
    rendered: str = _render(document, parsed)
    if rendered:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
