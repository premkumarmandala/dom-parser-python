"""Handwritten HTML tokenizer (no regex, no HTML libraries)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TokenKind(StrEnum):
    """Classification of a token produced by the character scan."""

    OPEN_TAG = "OPEN_TAG"
    CLOSE_TAG = "CLOSE_TAG"
    TEXT = "TEXT"


@dataclass(frozen=True, slots=True)
class Token:
    """A single lexeme: its kind and the exact source slice it came from."""

    kind: TokenKind
    raw: str


def tokenize(html: str) -> list[Token]:
    """Scan raw HTML character-by-character into a token stream.

    A tag starts with '<' and ends with '>'; '</' marks a close tag, any
    other '<' marks an open tag. Everything outside tags is TEXT, kept
    verbatim, including whitespace and newlines. A '<' that is never
    terminated by '>' makes the remainder of the input TEXT.

    Args:
        html: Raw input string.

    Returns:
        The tokens in source order; empty for empty input.
    """
    tokens: list[Token] = []
    length: int = len(html)
    i: int = 0
    text_start: int = 0

    while i < length:
        char: str = html[i]
        if char != "<":
            i += 1
            continue

        if text_start < i:
            tokens.append(Token(TokenKind.TEXT, html[text_start:i]))

        j: int = i + 1
        while j < length and html[j] != ">":
            j += 1

        if j >= length:
            tokens.append(Token(TokenKind.TEXT, html[i:]))
            text_start = length
            break

        raw: str = html[i : j + 1]
        kind: TokenKind = (
            TokenKind.CLOSE_TAG if raw.startswith("</") else TokenKind.OPEN_TAG
        )
        tokens.append(Token(kind, raw))
        i = j + 1
        text_start = i

    if text_start < length:
        tokens.append(Token(TokenKind.TEXT, html[text_start:]))

    return tokens
