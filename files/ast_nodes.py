"""
ast_nodes.py — AST node hierarchy for the toy language.

Every grammar production has a corresponding node class.
All nodes inherit from ASTNode and support pretty-printing.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, List, Optional


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class ASTNode:
    """Abstract base for all AST nodes."""

    def pretty(self, indent: int = 0) -> str:
        raise NotImplementedError

    def _pad(self, indent: int) -> str:
        return "  " * indent

    def __repr__(self) -> str:
        return self.pretty()


# ---------------------------------------------------------------------------
# Program
# ---------------------------------------------------------------------------

@dataclass
class Program(ASTNode):
    statements: List[ASTNode] = field(default_factory=list)

    def pretty(self, indent: int = 0) -> str:
        p = self._pad(indent)
        body = "\n".join(s.pretty(indent + 1) for s in self.statements)
        return f"{p}Program(\n{body}\n{p})"


# ---------------------------------------------------------------------------
# Statements
# ---------------------------------------------------------------------------

@dataclass
class VarDecl(ASTNode):
    """let <name> = <expr> ;"""
    name:  str
    value: ASTNode
    line:  int = 0
    col:   int = 0

    def pretty(self, indent: int = 0) -> str:
        p = self._pad(indent)
        return f"{p}VarDecl({self.name!r},\n{self.value.pretty(indent + 1)}\n{p})"


@dataclass
class Assignment(ASTNode):
    """<name> = <expr> ;"""
    name:  str
    value: ASTNode
    line:  int = 0
    col:   int = 0

    def pretty(self, indent: int = 0) -> str:
        p = self._pad(indent)
        return f"{p}Assign({self.name!r},\n{self.value.pretty(indent + 1)}\n{p})"


@dataclass
class PrintStmt(ASTNode):
    """print ( <expr> ) ;"""
    expr: ASTNode
    line: int = 0

    def pretty(self, indent: int = 0) -> str:
        p = self._pad(indent)
        return f"{p}Print(\n{self.expr.pretty(indent + 1)}\n{p})"


@dataclass
class IfStmt(ASTNode):
    """if ( <cond> ) <then_block> [else <else_block>]"""
    condition:  ASTNode
    then_block: "Block"
    else_block: Optional["Block"] = None
    line:       int = 0

    def pretty(self, indent: int = 0) -> str:
        p = self._pad(indent)
        cond = self.condition.pretty(indent + 1)
        then = self.then_block.pretty(indent + 1)
        els = (
            f"\n{p}Else(\n{self.else_block.pretty(indent + 1)}\n{p})"
            if self.else_block else ""
        )
        return f"{p}If(\n{cond},\n{then}{els}\n{p})"


@dataclass
class WhileStmt(ASTNode):
    """while ( <cond> ) <block>"""
    condition: ASTNode
    body:      "Block"
    line:      int = 0

    def pretty(self, indent: int = 0) -> str:
        p = self._pad(indent)
        cond = self.condition.pretty(indent + 1)
        body = self.body.pretty(indent + 1)
        return f"{p}While(\n{cond},\n{body}\n{p})"


@dataclass
class Block(ASTNode):
    """{ statement* }"""
    statements: List[ASTNode] = field(default_factory=list)

    def pretty(self, indent: int = 0) -> str:
        p = self._pad(indent)
        body = "\n".join(s.pretty(indent + 1) for s in self.statements)
        return f"{p}Block(\n{body}\n{p})"


# ---------------------------------------------------------------------------
# Expressions
# ---------------------------------------------------------------------------

@dataclass
class BinaryOp(ASTNode):
    """<left> op <right>"""
    op:    str
    left:  ASTNode
    right: ASTNode
    line:  int = 0
    col:   int = 0

    def pretty(self, indent: int = 0) -> str:
        p = self._pad(indent)
        return (
            f"{p}BinaryOp({self.op!r},\n"
            f"{self.left.pretty(indent + 1)},\n"
            f"{self.right.pretty(indent + 1)}\n"
            f"{p})"
        )


@dataclass
class UnaryOp(ASTNode):
    """op <operand>"""
    op:      str
    operand: ASTNode
    line:    int = 0
    col:     int = 0

    def pretty(self, indent: int = 0) -> str:
        p = self._pad(indent)
        return f"{p}UnaryOp({self.op!r},\n{self.operand.pretty(indent + 1)}\n{p})"


@dataclass
class NumberLiteral(ASTNode):
    value: int | float
    line:  int = 0
    col:   int = 0

    def pretty(self, indent: int = 0) -> str:
        return f"{self._pad(indent)}Number({self.value!r})"


@dataclass
class StringLiteral(ASTNode):
    value: str
    line:  int = 0
    col:   int = 0

    def pretty(self, indent: int = 0) -> str:
        return f"{self._pad(indent)}String({self.value!r})"


@dataclass
class BoolLiteral(ASTNode):
    value: bool
    line:  int = 0
    col:   int = 0

    def pretty(self, indent: int = 0) -> str:
        return f"{self._pad(indent)}Bool({self.value!r})"


@dataclass
class NullLiteral(ASTNode):
    line: int = 0
    col:  int = 0

    def pretty(self, indent: int = 0) -> str:
        return f"{self._pad(indent)}Null()"


@dataclass
class Identifier(ASTNode):
    name: str
    line: int = 0
    col:  int = 0

    def pretty(self, indent: int = 0) -> str:
        return f"{self._pad(indent)}Identifier({self.name!r})"
