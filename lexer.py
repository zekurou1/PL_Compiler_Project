"""
lexer.py — Hand-written lexical analyser for the toy language.

Design notes
============
* Inspired by the Java lexer in JetJustineEspanola/Tokenizer- but fully
  reimplemented in idiomatic Python.
* Keywords are loaded at construction time from keyword_manager.py.
* Returns a flat list of Token objects; the final token is always EOF.
* Line/column tracking is 1-based.
"""

from __future__ import annotations
from pathlib import Path
from typing import List

from tokens import Token, TokenType
from keyword_manager import KeywordManager
from error import LexicalError


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Single-character delimiters
_DELIMITERS: frozenset[str] = frozenset("(){};,")

# Operators, longest-match first (two-char before one-char)
_MULTI_OPS: tuple[str, ...] = ("==", "!=", "<=", ">=", "&&", "||", "**", "+=", "-=", "*=", "/=", "%=")
_SINGLE_OPS: frozenset[str] = frozenset("=+-*/<>!%")


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

class Lexer:
    """Converts source text into a list of Token objects."""

    def __init__(self, source: str, keyword_manager: KeywordManager | None = None):
        self._src: str = source
        self._pos: int = 0
        self._line: int = 1
        self._col: int = 1
        self._km: KeywordManager = keyword_manager or KeywordManager()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while not self._at_end():
            tok = self._next_token()
            if tok is not None:
                tokens.append(tok)
        tokens.append(Token(TokenType.EOF, "", self._line, self._col))
        return tokens

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _peek(self, offset: int = 0) -> str:
        idx = self._pos + offset
        return self._src[idx] if idx < len(self._src) else ""

    def _advance(self) -> str:
        ch = self._src[self._pos]
        self._pos += 1
        if ch == "\n":
            self._line += 1
            self._col = 1
        else:
            self._col += 1
        return ch

    def _at_end(self) -> bool:
        return self._pos >= len(self._src)

    def _snapshot(self) -> tuple[int, int]:
        """Return current (line, col) for token start recording."""
        return self._line, self._col

    # ------------------------------------------------------------------
    # Token recognisers
    # ------------------------------------------------------------------

    def _next_token(self) -> Token | None:
        self._skip_whitespace_and_comments()
        if self._at_end():
            return None

        line, col = self._snapshot()
        ch = self._peek()

        # String literal
        if ch == '"':
            return self._read_string(line, col)

        # Number literal
        if ch.isdigit():
            return self._read_number(line, col)

        # Identifier or keyword
        if ch.isalpha() or ch == "_":
            return self._read_identifier_or_keyword(line, col)

        # Two-character operator?
        two = self._peek(0) + self._peek(1)
        if two in _MULTI_OPS:
            self._advance(); self._advance()
            return Token(TokenType.OPERATOR, two, line, col)

        # Single-character operator
        if ch in _SINGLE_OPS:
            self._advance()
            return Token(TokenType.OPERATOR, ch, line, col)

        # Delimiter
        if ch in _DELIMITERS:
            self._advance()
            return Token(TokenType.DELIMITER, ch, line, col)

        # Unknown character
        self._advance()
        raise LexicalError(f"Unexpected character {ch!r}", line, col)

    # ------------------------------------------------------------------

    def _skip_whitespace_and_comments(self) -> None:
        while not self._at_end():
            ch = self._peek()
            if ch in " \t\r\n":
                self._advance()
            elif ch == "/" and self._peek(1) == "/":
                # Line comment — skip to end of line
                while not self._at_end() and self._peek() != "\n":
                    self._advance()
            else:
                break

    def _read_string(self, line: int, col: int) -> Token:
        self._advance()  # opening "
        buf: list[str] = []
        while not self._at_end():
            ch = self._peek()
            if ch == "\\":
                self._advance()
                esc = self._advance()
                mapping = {"n": "\n", "t": "\t", "\\": "\\", '"': '"'}
                buf.append(mapping.get(esc, esc))
            elif ch == '"':
                self._advance()  # closing "
                return Token(TokenType.STRING, "".join(buf), line, col)
            elif ch == "\n":
                raise LexicalError("Unterminated string literal", line, col)
            else:
                buf.append(self._advance())
        raise LexicalError("Unterminated string literal at end of file", line, col)

    def _read_number(self, line: int, col: int) -> Token:
        buf: list[str] = []
        is_float = False
        while not self._at_end() and self._peek().isdigit():
            buf.append(self._advance())
        if not self._at_end() and self._peek() == "." and self._peek(1).isdigit():
            is_float = True
            buf.append(self._advance())  # '.'
            while not self._at_end() and self._peek().isdigit():
                buf.append(self._advance())
        tok_type = TokenType.FLOAT if is_float else TokenType.INTEGER
        return Token(tok_type, "".join(buf), line, col)

    def _read_identifier_or_keyword(self, line: int, col: int) -> Token:
        buf: list[str] = []
        while not self._at_end() and (self._peek().isalnum() or self._peek() == "_"):
            buf.append(self._advance())
        word = "".join(buf)
        tok_type = TokenType.KEYWORD if self._km.is_keyword(word) else TokenType.IDENTIFIER
        return Token(tok_type, word, line, col)


# ---------------------------------------------------------------------------
# Convenience factory
# ---------------------------------------------------------------------------

def tokenize_file(path: str | Path) -> List[Token]:
    source = Path(path).read_text(encoding="utf-8")
    return Lexer(source).tokenize()


def tokenize_string(source: str) -> List[Token]:
    return Lexer(source).tokenize()
