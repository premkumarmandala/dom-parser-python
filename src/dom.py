"""DOM node definitions and tree helpers (no HTML libraries)."""

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


Node = ElementNode | TextNode | DocumentNode


def _attribute(element: ElementNode, name: str) -> str | None:
    """Return the value of ``name`` on ``element``, or None if absent."""
    for key, value in element.attributes:
        if key == name:
            return value
    return None


def _node_label(node: Node) -> str:
    """Return the single-line label for a node, tree-style."""
    if isinstance(node, TextNode):
        return f'"{node.text}"'
    if isinstance(node, DocumentNode):
        return "."
    attrs: str = ", ".join(f'{key}="{value}"' for key, value in node.attributes)
    return f"{node.tag} [{attrs}]" if attrs else node.tag


def _child_nodes(node: Node) -> list[ElementNode | TextNode]:
    """Return a node's children (empty for text nodes)."""
    children: list[ElementNode | TextNode] = []
    if isinstance(node, (ElementNode, DocumentNode)):
        children.extend(node.children)
    return children


def _tree_lines(
    node: Node,
    prefix: str,
    is_last: bool,
    is_root: bool,
    lines: list[str],
) -> None:
    """Append a node and its subtree to ``lines`` using tree connectors."""
    if is_root:
        lines.append(_node_label(node))
        child_prefix: str = prefix
    else:
        connector: str = "└── " if is_last else "├── "
        lines.append(prefix + connector + _node_label(node))
        child_prefix = prefix + ("    " if is_last else "│   ")

    children: list[ElementNode | TextNode] = _child_nodes(node)
    for index, child in enumerate(children):
        _tree_lines(child, child_prefix, index == len(children) - 1, False, lines)


def format_tree(node: Node, indent: int = 0) -> str:
    """Render the in-memory DOM like the Linux ``tree`` command.

    The document root prints as ``.``; elements print as ``tag`` optionally
    followed by ``[key="value", ...]``; text nodes print quoted. Each line is
    prefixed with box-drawing connectors derived from the tree structure, not
    from the original source text.

    Args:
        node: Any node in the tree.
        indent: Number of leading spaces added to every line.

    Returns:
        The formatted representation, without a trailing newline.
    """
    lines: list[str] = []
    _tree_lines(node, "", True, True, lines)
    margin: str = " " * indent
    return "\n".join(margin + line for line in lines)


def get_text_content(node: Node) -> str:
    """Collect the text of every TextNode descendant, one per line.

    Args:
        node: Any node in the tree.

    Returns:
        Descendant text joined with newlines in document order.
    """
    texts: list[str] = []

    def collect(current: Node) -> None:
        if isinstance(current, TextNode):
            texts.append(current.text)
            return
        for child in current.children:
            collect(child)

    collect(node)
    return "\n".join(texts)


def _matches(
    element: ElementNode,
    *,
    tag: str | None,
    id_: str | None,
    class_name: str | None,
) -> bool:
    """Return True when ``element`` satisfies every non-None filter."""
    if tag is not None and element.tag.lower() != tag.lower():
        return False
    if id_ is not None and _attribute(element, "id") != id_:
        return False
    if class_name is not None:
        classes: list[str] = (_attribute(element, "class") or "").split()
        if class_name not in classes:
            return False
    return True


def _walk_filtered(
    node: Node,
    *,
    tag: str | None,
    id_: str | None,
    class_name: str | None,
    prune: bool,
) -> list[ElementNode]:
    """Walk ``node`` collecting matches.

    When ``prune`` is True, a matching element is recorded and its subtree is
    not searched further, so every result is a match with no matched ancestor.
    When False, every match anywhere in the tree is recorded.
    """
    matches: list[ElementNode] = []

    def walk(current: Node) -> None:
        if isinstance(current, ElementNode):
            if _matches(current, tag=tag, id_=id_, class_name=class_name):
                matches.append(current)
                if prune:
                    return
            for child in current.children:
                walk(child)
        elif isinstance(current, DocumentNode):
            for child in current.children:
                walk(child)

    walk(node)
    return matches


def find_elements(
    node: Node,
    *,
    tag: str | None = None,
    id_: str | None = None,
    class_name: str | None = None,
) -> list[ElementNode]:
    """Collect every element matching all provided filters.

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
    return _walk_filtered(node, tag=tag, id_=id_, class_name=class_name, prune=False)


def find_root_elements(
    node: Node,
    *,
    tag: str | None = None,
    id_: str | None = None,
    class_name: str | None = None,
) -> list[ElementNode]:
    """Collect outermmost matches: elements with no matching ancestor.

    A matched element's subtree is not searched again, so a match nested
    inside another match is represented by (and printed within) its ancestor
    rather than repeated at the top level.

    Args:
        node: Any node in the tree (search includes the node itself).
        tag: Tag name to match.
        id_: ``id`` attribute value to match.
        class_name: One class token to match.

    Returns:
        Outermost matching elements in document order.
    """
    return _walk_filtered(node, tag=tag, id_=id_, class_name=class_name, prune=True)
