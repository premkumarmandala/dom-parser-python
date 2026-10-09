"""Handwritten tag/attribute parser (no regex, no HTML libraries)."""

from __future__ import annotations

_QUOTES: frozenset[str] = frozenset({'"', "'"})
_WHITESPACE: frozenset[str] = frozenset(" \t\n\r\f\v")


def parse_tag(raw: str) -> tuple[str, list[tuple[str, str]]]:
    """Parse a raw OPEN_TAG slice into a name and attribute pairs.

    The scan is character-by-character and supports double-quoted,
    single-quoted and unquoted values, boolean (valueless) attributes,
    whitespace around ``=`` and the trailing slash of a self-closing tag.
    Tag and attribute names are lowercased; attribute values are kept
    verbatim.

    Args:
        raw: Raw token text such as ``'<img src="pic.jpg" />'``.

    Returns:
        A ``(tag_name, attributes)`` pair. The name is '' if the slice
        holds no name; attributes are in source order.
    """
    inner: str = raw
    if inner.startswith("<"):
        inner = inner[1:]
    if inner.startswith("/"):
        inner = inner[1:]
    if inner.endswith(">"):
        inner = inner[:-1]
    inner = inner.rstrip()
    if inner.endswith("/"):
        inner = inner[:-1]

    length: int = len(inner)
    i: int = 0
    while i < length and inner[i] not in _WHITESPACE:
        i += 1
    tag_name: str = inner[:i].lower()

    attributes: list[tuple[str, str]] = []
    while i < length:
        while i < length and inner[i] in _WHITESPACE:
            i += 1
        if i >= length:
            break

        name_start: int = i
        while i < length and inner[i] not in _WHITESPACE and inner[i] not in "=/":
            i += 1
        name: str = inner[name_start:i].lower()
        if not name:
            # A stray '=' or '/' with no preceding name; skip it so the
            # scan always makes progress.
            i += 1
            continue

        while i < length and inner[i] in _WHITESPACE:
            i += 1

        value: str = ""
        if i < length and inner[i] == "=":
            i += 1
            while i < length and inner[i] in _WHITESPACE:
                i += 1
            if i < length and inner[i] in _QUOTES:
                quote: str = inner[i]
                i += 1
                value_start: int = i
                while i < length and inner[i] != quote:
                    i += 1
                value = inner[value_start:i]
                if i < length:
                    i += 1
            else:
                value_start = i
                while i < length and inner[i] not in _WHITESPACE:
                    i += 1
                value = inner[value_start:i]

        attributes.append((name, value))

    return tag_name, attributes
