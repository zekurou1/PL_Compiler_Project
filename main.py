#!/usr/bin/env python3
"""
main.py — Compiler pipeline entry point.

Usage:
    python main.py <program.txt>
    python main.py --debug <program.txt>

Pipeline:
    Source → Lexer → Parser → SemanticAnalyzer → Interpreter → Output
"""

from __future__ import annotations
import sys
import os

# ---------------------------------------------------------------------------
# Make sub-packages importable from the project root
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(__file__))

from lexer     import Lexer
from parser    import Parser
from analyzer  import SemanticAnalyzer
from interpreter import Interpreter
from error import CompilerError


# ---------------------------------------------------------------------------
# Pretty banner helpers
# ---------------------------------------------------------------------------

def _banner(title: str) -> None:
    width = 60
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def _section(title: str) -> None:
    print(f"\n{'-' * 50}")
    print(f"  {title}")
    print(f"{'-' * 50}")


# ---------------------------------------------------------------------------
# Core pipeline
# ---------------------------------------------------------------------------

def run(source: str, debug: bool = False) -> list[str]:
    """
    Execute the full compiler pipeline.

    Returns:
        List of strings printed by the program.
    Raises:
        CompilerError subclass on any stage failure.
    """

    # ── Stage 1: Lexer ──────────────────────────────────────────────
    lexer  = Lexer(source)
    tokens = lexer.tokenize()

    if debug:
        _section("TOKENS")
        for tok in tokens:
            print(f"  {tok}")

    # ── Stage 2: Parser ─────────────────────────────────────────────
    parser = Parser(tokens)
    ast    = parser.parse()

    if debug:
        _section("AST")
        print(ast.pretty())

    # ── Stage 3: Semantic Analysis ──────────────────────────────────
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    if debug:
        _section("SEMANTIC ANALYSIS")
        print("  ✔  No semantic errors found.")

    # ── Stage 4: Interpretation ─────────────────────────────────────
    if debug:
        _section("OUTPUT")

    interpreter = Interpreter()
    output      = interpreter.execute(ast)

    return output


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    args = sys.argv[1:]

    debug = "--debug" in args
    args  = [a for a in args if a != "--debug"]

    if not args:
        print("Usage: python main.py [--debug] <program.txt>")
        print("       python main.py --debug tests/sample_program.txt")
        sys.exit(1)

    filepath = args[0]

    try:
        with open(filepath, encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    if debug:
        _banner(f"Compiling: {filepath}")

    try:
        run(source, debug=debug)
    except CompilerError as exc:
        print(f"\n{exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:          # pragma: no cover — unexpected crash
        print(f"\n[InternalError] {exc}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
