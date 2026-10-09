"""Tests for the DOM tree helpers."""

from __future__ import annotations

from dom import (
    DocumentNode,
    ElementNode,
    find_elements,
    find_root_elements,
    format_tree,
    get_text_content,
)
from parser import build_dom
from tokenizer import tokenize


def _doc(html: str) -> DocumentNode:
    return build_dom(tokenize(html))


def test_format_tree_pretty_prints_nested_elements() -> None:
    document: DocumentNode = _doc('<div class="hero"><p>Hi</p></div>')
    assert format_tree(document) == (
        '.\n└── div [class="hero"]\n    └── p\n        └── "Hi"'
    )


def test_format_tree_renders_empty_elements() -> None:
    document: DocumentNode = _doc("<div></div>")
    assert format_tree(document) == ".\n└── div"


def test_format_tree_matches_tree_command_picture() -> None:
    html: str = (
        "<html>\n"
        "  <body>\n"
        "    <h1>Hello</h1>\n"
        '    <p class="intro" id="first">Welcome to AI Karyashala</p>\n'
        '    <p class="note">Learn by doing</p>\n'
        "  </body>\n"
        "</html>"
    )
    assert format_tree(_doc(html)) == (
        ".\n"
        "└── html\n"
        "    └── body\n"
        "        ├── h1\n"
        '        │   └── "Hello"\n'
        '        ├── p [class="intro", id="first"]\n'
        '        │   └── "Welcome to AI Karyashala"\n'
        '        └── p [class="note"]\n'
        '            └── "Learn by doing"'
    )


def test_get_text_content_joins_lines() -> None:
    document: DocumentNode = _doc("<div><p>a</p><p>b</p></div>")
    assert get_text_content(document) == "a\nb"


def test_find_elements_by_tag_is_case_insensitive() -> None:
    document: DocumentNode = _doc("<div><p>x</p></div>")
    assert find_elements(document, tag="P") == [document.children[0].children[0]]


def test_find_elements_by_id() -> None:
    document: DocumentNode = _doc('<div><p id="main">x</p></div>')
    matches: list[ElementNode] = find_elements(document, id_="main")
    assert len(matches) == 1
    assert matches[0].tag == "p"


def test_find_elements_by_class_token() -> None:
    document: DocumentNode = _doc('<div class="btn btn-primary">x</div>')
    assert len(find_elements(document, class_name="btn")) == 1
    assert len(find_elements(document, class_name="btn-primary")) == 1
    assert find_elements(document, class_name="missing") == []


def test_find_elements_combines_filters() -> None:
    document: DocumentNode = _doc(
        '<a class="x" id="one">1</a><b class="x" id="two">2</b>'
    )
    assert len(find_elements(document, class_name="x", id_="two")) == 1


def test_find_elements_returns_in_document_order() -> None:
    document: DocumentNode = _doc("<div><p>1</p><p>2</p></div>")
    tags: list[str] = [element.tag for element in find_elements(document)]
    assert tags == ["div", "p", "p"]


def test_find_root_elements_skips_matches_nested_in_matches() -> None:
    document: DocumentNode = _doc("<div><div><p>x</p></div></div>")
    roots: list[ElementNode] = find_root_elements(document, tag="div")
    assert len(roots) == 1
    nested = roots[0].children[0]
    assert isinstance(nested, ElementNode)
    assert nested.tag == "div"


def test_find_root_elements_keeps_separate_matches() -> None:
    document: DocumentNode = _doc("<div><div>x</div></div><div>y</div>")
    assert len(find_root_elements(document, tag="div")) == 2


def test_find_root_elements_empty_when_nothing_matches() -> None:
    document: DocumentNode = _doc("<div><p>x</p></div>")
    assert find_root_elements(document, tag="h1") == []
