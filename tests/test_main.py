"""Tests for the domparser CLI entry point (Section 5)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from main import USAGE, main

CONTENT: str = "<html>\n  <body>hello</body>\n</html>\n"
EXPECTED_TOKEN_LINES: str = (
    "OPEN_TAG: '<html>'\n"
    "TEXT: '\\n  '\n"
    "OPEN_TAG: '<body>'\n"
    "TEXT: 'hello'\n"
    "CLOSE_TAG: '</body>'\n"
    "TEXT: '\\n'\n"
    "CLOSE_TAG: '</html>'\n"
    "TEXT: '\\n'\n"
)


@pytest.fixture()
def page(tmp_path: Path) -> Path:
    """Write a sample page and return its path."""
    path = tmp_path / "page.html"
    path.write_text(CONTENT, encoding="utf-8")
    return path


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["--tree"],
        ["page.html", "--bogus"],
        ["page.html", "--tree", "--text"],
        ["page.html", "--text", "--tree"],
        ["page.html", "--find-tag"],
        ["page.html", "--find-tag", "--tree"],
        ["page.html", "--find-id"],
        ["page.html", "--find-class"],
        ["page.html", "--find-tag", "div", "extra"],
        ["page.html", "--find-id", "main", "extra"],
        ["page.html", "--find-tag", "div", "--find-id", "main"],
    ],
)
def test_invalid_arguments_print_usage_to_stderr(
    argv: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(argv) == 1
    captured = capsys.readouterr()
    assert captured.err == USAGE + "\n"
    assert captured.out == ""


@pytest.mark.parametrize(
    "mode",
    [
        [],
        ["--tree"],
        ["--text"],
        ["--find-tag", "div"],
        ["--find-id", "main"],
        ["--find-class", "hero"],
    ],
)
def test_valid_arguments_print_token_stream(
    page: Path, mode: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    argv: list[str] = [str(page), *mode]
    assert main(argv) == 0
    captured = capsys.readouterr()
    assert captured.out == EXPECTED_TOKEN_LINES
    assert captured.err == ""


def test_missing_file_error_message(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing: str = str(tmp_path / "nope.html")
    assert main([missing]) == 1
    captured = capsys.readouterr()
    assert captured.err == f"Cannot open file: {missing}\n"
    assert captured.out == ""


@pytest.mark.skipif(
    os.name != "posix" or os.geteuid() == 0,
    reason="file permissions are not enforced for root",
)
def test_permission_error_message(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path: Path = tmp_path / "locked.html"
    path.write_text(CONTENT, encoding="utf-8")
    path.chmod(0o000)
    try:
        assert main([str(path)]) == 1
        captured = capsys.readouterr()
        assert captured.err == f"Cannot open file: {path}\n"
        assert captured.out == ""
    finally:
        path.chmod(0o600)
