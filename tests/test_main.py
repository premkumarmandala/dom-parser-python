"""Tests for the domparser CLI entry point."""

from __future__ import annotations

import pytest

from main import main


def test_main_returns_zero() -> None:
    assert main([]) == 0


def test_main_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--version"]) == 0
    assert "domparser 0.1.0" in capsys.readouterr().out
