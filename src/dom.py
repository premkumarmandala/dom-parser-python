"""DOM node definitions and tree helpers (no HTML libraries)."""

from __future__ import annotations

from dataclasses import dataclass, field

INDENT: int = 2


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


Node = ElementNode | TextNode | DocumentNode


def _attribute(element: ElementNode, name: str) -> str | None:
    """Return the value of ``name`` on ``element``, or None if absent."""
    for key, value in element.attributes:
        if key == name:
            return value
    return None


def format_tree(node: Node, indent: int = 0) -> str:
    """Pretty-print a node and its descendants with two-space indentation.

    Elements render as ``<tag attrs>`` ... ``</tag>`` with one nested level
    per depth; text nodes render as their (already trimmed) content. The
    document root prints only its children.

    Args:
        node: Any node in the tree.
        indent: Number of leading spaces for the node's own line.

    Returns:
        The formatted representation, without a trailing newline.
    """
    if isinstance(node, TextNode):
        return " " * indent + node.text
    if isinstance(node, DocumentNode):
        return "\n".join(format_tree(child, indent) for child in node.children)

    pad: str = " " * indent
    attrs: str = "".join(f' {key}="{value}"' for key, value in node.attributes)
    lines: list[str] = [f"{pad}<{node.tag}{attrs}>"]
    lines.extend(format_tree(child, indent + INDENT) for child in node.children)
    lines.append(f"{pad}</{node.tag}>")
    return "\n".join(lines)


def get_text_content(node: Node) -> str:
    """Recursively concatenate the text of every descendant TextNode.

    Args:
        node: Any node in the tree.

    Returns:
        All descendant text joined in document order.
    """
    if isinstance(node, TextNode):
        return node.text
    return "".join(get_text_content(child) for child in node.children)


def find_elements(
    node: Node,
    *,
    tag: str | None = None,
    id_: str | None = None,
    class_name: str | None = None,
) -> list[ElementNode]:
    """Collect elements matching every provided filter.

    Filters combine with AND semantics; ``None`` filters are ignored. Tag
    comparison is case-insensitive, ``id_`` matches the ``id`` attribute,
    and ``class_name`` matches any single class within a space-separated
    ``class`` attribute.

    Args:
        node: Any node in the tree (search includes the node itself).
        tag: Tag name to match.
        id_: ``id`` attribute value to match.
        class_name: One class token to match.

    Returns:
        Matching elements in document order.
    """
    matches: list[ElementNode] = []

    def matches_filters(element: ElementNode) -> bool:
        if tag is not None and element.tag.lower() != tag.lower():
            return False
        if id_ is not None and _attribute(element, "id") != id_:
            return False
        if class_name is not None:
            classes: list[str] = (_attribute(element, "class") or "").split()
            if class_name not in classes:
                return False
        return True

    def walk(current: Node) -> None:
        if isinstance(current, ElementNode):
            if matches_filters(current):
                matches.append(current)
            for child in current.children:
                walk(child)
        elif isinstance(current, DocumentNode):
            for child in current.children:
                walk(child)

    walk(node)
    return matches
