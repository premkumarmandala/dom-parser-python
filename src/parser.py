"""Handwritten DOM builder: token stream -> DocumentNode (no HTML libraries)."""

from __future__ import annotations

from attributes import parse_tag
from dom import DocumentNode, ElementNode, TextNode
from tokenizer import Token, TokenKind


def build_dom(tokens: list[Token]) -> DocumentNode:
    """Build a DOM tree from a token stream.

    OPEN_TAG creates an ElementNode (with parsed attributes) and pushes it
    onto the stack of open elements; TEXT is whitespace-trimmed and dropped
    when empty or when no element is open; CLOSE_TAG pops the stack.
    Elements left open at end of input stay in the tree.

    Args:
        tokens: Tokens produced by ``tokenize``.

    Returns:
        The document root. Never circular: parents hold children only.
    """
    document: DocumentNode = DocumentNode()
    stack: list[ElementNode] = []

    for token in tokens:
        if token.kind is TokenKind.OPEN_TAG:
            name: str
            attributes: list[tuple[str, str]]
            name, attributes = parse_tag(token.raw)
            if not name:
                continue
            element: ElementNode = ElementNode(tag=name, attributes=attributes)
            if stack:
                stack[-1].children.append(element)
            else:
                document.children.append(element)
            stack.append(element)
        elif token.kind is TokenKind.TEXT:
            text: str = token.raw.strip()
            # DocumentNode holds only elements, so text outside the root
            # element (stack empty) cannot be stored and is dropped.
            if not text or not stack:
                continue
            stack[-1].children.append(TextNode(text))
        elif token.kind is TokenKind.CLOSE_TAG:
            if stack:
                stack.pop()

    return document
