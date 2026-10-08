"""Tests for the handwritten tokenizer."""

from __future__ import annotations

from tokenizer import Token, TokenKind, tokenize


def test_prompt_example() -> None:
    assert tokenize("<div><p>Hi</p></div>") == [
        Token(TokenKind.OPEN_TAG, "<div>"),
        Token(TokenKind.OPEN_TAG, "<p>"),
        Token(TokenKind.TEXT, "Hi"),
        Token(TokenKind.CLOSE_TAG, "</p>"),
        Token(TokenKind.CLOSE_TAG, "</div>"),
    ]


def test_empty_input() -> None:
    assert tokenize("") == []


def test_text_only() -> None:
    assert tokenize("Hi") == [Token(TokenKind.TEXT, "Hi")]


def test_whitespace_and_newlines_are_preserved() -> None:
    assert tokenize("<a>\n  x\n</a>") == [
        Token(TokenKind.OPEN_TAG, "<a>"),
        Token(TokenKind.TEXT, "\n  x\n"),
        Token(TokenKind.CLOSE_TAG, "</a>"),
    ]


def test_adjacent_tags_produce_no_text_token() -> None:
    assert tokenize("<p></p>") == [
        Token(TokenKind.OPEN_TAG, "<p>"),
        Token(TokenKind.CLOSE_TAG, "</p>"),
    ]


def test_close_tag_detection() -> None:
    assert tokenize("</p>")[0].kind is TokenKind.CLOSE_TAG


def test_open_tag_detection() -> None:
    assert tokenize("<p>")[0].kind is TokenKind.OPEN_TAG


def test_unterminated_tag_is_text() -> None:
    assert tokenize("<div") == [Token(TokenKind.TEXT, "<div")]


def test_raw_is_verbatim_source_slice() -> None:
    tokens: list[Token] = tokenize("  <img src='x'>  ")
    assert tokens[0] == Token(TokenKind.TEXT, "  ")
    assert tokens[1] == Token(TokenKind.OPEN_TAG, "<img src='x'>")
    assert tokens[2] == Token(TokenKind.TEXT, "  ")
