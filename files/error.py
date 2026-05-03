"""
error.py — Structured error types for every compiler stage.

Each error carries:
  * message  — human-readable description
  * line     — 1-based source line (0 = unknown)
  * column   — 1-based source column (0 = unknown)
"""

from __future__ import annotations


class CompilerError(Exception):
    """Base class for all compiler errors."""

    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line    = line
        self.column  = column
        super().__init__(str(self))

    def __str__(self) -> str:
        stage = self._stage_label()
        if self.line > 0:
            loc = f" (line {self.line}, col {self.column})"
        else:
            loc = ""
        return f"[{stage}]{loc} {self.message}"

    def _stage_label(self) -> str:
        return "Error"


# ---------------------------------------------------------------------------

class LexicalError(CompilerError):
    def _stage_label(self) -> str:
        return "LexicalError"


class SyntaxError(CompilerError):
    def _stage_label(self) -> str:
        return "SyntaxError"


class SemanticError(CompilerError):
    def _stage_label(self) -> str:
        return "SemanticError"


class RuntimeError(CompilerError):
    def _stage_label(self) -> str:
        return "RuntimeError"
