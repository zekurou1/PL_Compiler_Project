"""
token.py — Token type definitions and Token data class.
Inspired by the Java tokenizer structure in JetJustineEspanola/Tokenizer-,
reimplemented cleanly in Python.
"""

from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    # Literals
    INTEGER    = auto()
    FLOAT      = auto()
    STRING     = auto()

    # Identifiers & Keywords
    IDENTIFIER = auto()
    KEYWORD    = auto()

    # Operators
    OPERATOR   = auto()

    # Delimiters
    DELIMITER  = auto()

    # Special
    EOF        = auto()
    UNKNOWN    = auto()


@dataclass
class Token:
    """Represents a single lexical unit with its type, value, and source position."""
    type:   TokenType
    value:  str
    line:   int
    column: int

    def __repr__(self) -> str:
        return (
            f"Token(type={self.type.name:<12} "
            f"value={self.value!r:<20} "
            f"line={self.line}, col={self.column})"
        )
