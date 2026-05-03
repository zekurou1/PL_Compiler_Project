"""
analyzer.py — Semantic analysis pass.

Responsibilities:
  * Build a symbol table (scoped)
  * Detect use of undeclared variables
  * Detect duplicate declarations within the same scope
  * Walk every node in the AST (visitor pattern)
"""

from __future__ import annotations
from typing import Any

from ast_nodes import (
    ASTNode, Program, VarDecl, Assignment, PrintStmt,
    IfStmt, WhileStmt, Block, BinaryOp, UnaryOp,
    NumberLiteral, StringLiteral, BoolLiteral, NullLiteral, Identifier,
)
from error import SemanticError


# ---------------------------------------------------------------------------
# Symbol table
# ---------------------------------------------------------------------------

class SymbolTable:
    """Lexically scoped symbol table using a chain of dicts."""

    def __init__(self, parent: SymbolTable | None = None):
        self._symbols: dict[str, Any] = {}
        self._parent = parent

    def declare(self, name: str, line: int, col: int) -> None:
        if name in self._symbols:
            raise SemanticError(f"Duplicate declaration of '{name}'", line, col)
        self._symbols[name] = True

    def resolve(self, name: str, line: int, col: int) -> None:
        """Raise SemanticError if name is not declared in any enclosing scope."""
        if name in self._symbols:
            return
        if self._parent is not None:
            return self._parent.resolve(name, line, col)
        raise SemanticError(f"Use of undeclared variable '{name}'", line, col)

    def child(self) -> "SymbolTable":
        return SymbolTable(parent=self)


# ---------------------------------------------------------------------------
# Analyzer
# ---------------------------------------------------------------------------

class SemanticAnalyzer:
    """
    AST visitor that performs semantic checks.

    Usage::

        SemanticAnalyzer().analyze(ast)   # raises SemanticError on failure
    """

    def __init__(self):
        self._scope: SymbolTable = SymbolTable()

    def analyze(self, node: ASTNode) -> None:
        method = "_visit_" + type(node).__name__
        visitor = getattr(self, method, self._visit_generic)
        visitor(node)

    # ------------------------------------------------------------------
    # Visitors
    # ------------------------------------------------------------------

    def _visit_Program(self, node: Program) -> None:
        for stmt in node.statements:
            self.analyze(stmt)

    def _visit_VarDecl(self, node: VarDecl) -> None:
        # Evaluate expression first (RHS may reference existing vars)
        self.analyze(node.value)
        self._scope.declare(node.name, node.line, node.col)

    def _visit_Assignment(self, node: Assignment) -> None:
        self._scope.resolve(node.name, node.line, node.col)
        self.analyze(node.value)

    def _visit_PrintStmt(self, node: PrintStmt) -> None:
        self.analyze(node.expr)

    def _visit_IfStmt(self, node: IfStmt) -> None:
        self.analyze(node.condition)
        self._analyze_block(node.then_block)
        if node.else_block:
            self._analyze_block(node.else_block)

    def _visit_WhileStmt(self, node: WhileStmt) -> None:
        self.analyze(node.condition)
        self._analyze_block(node.body)

    def _analyze_block(self, block: "Block") -> None:
        """Blocks introduce a new scope."""
        outer = self._scope
        self._scope = self._scope.child()
        for stmt in block.statements:
            self.analyze(stmt)
        self._scope = outer

    def _visit_Block(self, node: "Block") -> None:
        self._analyze_block(node)

    def _visit_BinaryOp(self, node: BinaryOp) -> None:
        self.analyze(node.left)
        self.analyze(node.right)

    def _visit_UnaryOp(self, node: UnaryOp) -> None:
        self.analyze(node.operand)

    def _visit_Identifier(self, node: Identifier) -> None:
        self._scope.resolve(node.name, node.line, node.col)

    # Literals — no checks required
    def _visit_NumberLiteral(self, _: NumberLiteral) -> None: pass
    def _visit_StringLiteral(self, _: StringLiteral) -> None: pass
    def _visit_BoolLiteral(self,   _: BoolLiteral)   -> None: pass
    def _visit_NullLiteral(self,   _: NullLiteral)   -> None: pass

    def _visit_generic(self, node: ASTNode) -> None:
        raise SemanticError(
            f"Unknown AST node type: {type(node).__name__}", 0, 0
        )
