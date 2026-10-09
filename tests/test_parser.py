"""Tests for the DOM builder."""

from __future__ import annotations

from dom import DocumentNode, ElementNode, TextNode
from parser import build_dom
from tokenizer import Token, TokenKind, tokenize


def test_prompt_example() -> None:
    document: DocumentNode = build_dom(tokenize("<div><p>Hi</p></div>"))
    assert document == DocumentNode(
        children=[
            ElementNode(
                tag="div",
                children=[ElementNode(tag="p", children=[TextNode(text="Hi")])],
            )
        ]
    )


def test_empty_input_yields_empty_document() -> None:
    assert build_dom([]) == DocumentNode()


def test_whitespace_only_text_is_dropped() -> None:
    document: DocumentNode = build_dom(tokenize("<div>\n   \n</div>"))
    assert document == DocumentNode(
        children=[ElementNode(tag="div", attributes=[], children=[])]
    )


def test_text_is_trimmed() -> None:
    document: DocumentNode = build_dom(tokenize("<p>  Hi there  </p>"))
    assert document.children[0].children == [TextNode(text="Hi there")]


def test_attributes_are_parsed() -> None:
    document: DocumentNode = build_dom(tokenize('<div class="hero" id="main">Hi</div>'))
    element: ElementNode = document.children[0]
    assert element.tag == "div"
    assert element.attributes == [("class", "hero"), ("id", "main")]
    assert element.children == [TextNode(text="Hi")]


def test_double_quoted_attribute() -> None:
    document: DocumentNode = build_dom(tokenize('<a href="x">y</a>'))
    assert document.children[0].attributes == [("href", "x")]


def test_single_quoted_attribute() -> None:
    document: DocumentNode = build_dom(tokenize("<a href='x'>y</a>"))
    assert document.children[0].attributes == [("href", "x")]


def test_unquoted_attribute() -> None:
    document: DocumentNode = build_dom(tokenize("<input type=text>"))
    assert document.children[0].attributes == [("type", "text")]


def test_boolean_attribute_has_empty_value() -> None:
    document: DocumentNode = build_dom(tokenize("<button disabled>Go</button>"))
    assert document.children[0].attributes == [("disabled", "")]


def test_whitespace_around_equals_is_ignored() -> None:
    document: DocumentNode = build_dom(tokenize('<a href = "x">y</a>'))
    assert document.children[0].attributes == [("href", "x")]


def test_self_closing_tag_strips_trailing_slash() -> None:
    document: DocumentNode = build_dom(tokenize('<img src="pic.jpg" />'))
    assert document.children[0].tag == "img"
    assert document.children[0].attributes == [("src", "pic.jpg")]


def test_tag_and_attribute_names_are_lowercased() -> None:
    document: DocumentNode = build_dom(tokenize('<DIV CLASS="hero">x</DIV>'))
    assert document.children[0].tag == "div"
    assert document.children[0].attributes == [("class", "hero")]


def test_multiple_attributes_keep_source_order() -> None:
    document: DocumentNode = build_dom(
        tokenize('<a id="main" class="btn primary" href="/x">link</a>')
    )
    assert document.children[0].attributes == [
        ("id", "main"),
        ("class", "btn primary"),
        ("href", "/x"),
    ]


def test_text_before_root_element_is_dropped() -> None:
    assert build_dom(tokenize("just text")) == DocumentNode()


def test_multiple_root_elements() -> None:
    document: DocumentNode = build_dom(tokenize("<a>1</a><b>2</b>"))
    assert [element.tag for element in document.children] == ["a", "b"]


def test_nested_elements() -> None:
    document: DocumentNode = build_dom(tokenize("<a><b><c>x</c></b></a>"))
    a: ElementNode = document.children[0]
    child_of_a = a.children[0]
    assert isinstance(child_of_a, ElementNode)
    child_of_b = child_of_a.children[0]
    assert isinstance(child_of_b, ElementNode)
    assert [a.tag, child_of_a.tag, child_of_b.tag] == ["a", "b", "c"]


def test_unclosed_elements_stay_in_tree() -> None:
    document: DocumentNode = build_dom(tokenize("<div><p>Hi"))
    assert document == DocumentNode(
        children=[
            ElementNode(
                tag="div",
                children=[ElementNode(tag="p", children=[TextNode(text="Hi")])],
            )
        ]
    )


def test_close_tag_without_open_is_ignored() -> None:
    assert build_dom([Token(TokenKind.CLOSE_TAG, "</div>")]) == DocumentNode()


def test_mismatched_close_tag_pops_stack() -> None:
    document: DocumentNode = build_dom(tokenize("<a><b></a>"))
    assert [element.tag for element in document.children] == ["a"]
