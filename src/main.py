"""CLI entry point for dom-parser-python."""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    """Run the domparser CLI.

    Args:
        argv: Argument list excluding the program name. Defaults to sys.argv[1:].

    Returns:
        Process exit code.
    """
    args = sys.argv[1:] if argv is None else argv
    if "--version" in args:
        print("domparser 0.1.0")
        return 0
    print("domparser: no HTML parsing libraries, parser not yet implemented.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
