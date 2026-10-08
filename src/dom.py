"""DOM node definitions (no HTML libraries)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class TextNode:
    """A run of character data (already trimmed by the parser)."""

    text: str


@dataclass(slots=True)
class ElementNode:
    """An element node.

    Nodes only ever reference their children, never their parent, so the
    structure is a tree and cannot contain cycles.
    """

    tag: str
    attributes: list[tuple[str, str]] = field(default_factory=list)
    children: list[ElementNode | TextNode] = field(default_factory=list)


@dataclass(slots=True)
class DocumentNode:
    """The document root ('.'), holding the top-level elements."""

    children: list[ElementNode] = field(default_factory=list)
