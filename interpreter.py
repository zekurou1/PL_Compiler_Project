"""
interpreter.py — Tree-walking interpreter.

Walks a semantically validated AST and evaluates it.
Maintains a runtime environment (variable store) with lexical scope.
"""

from __future__ import annotations
from typing import Any

from ast_nodes import (
    ASTNode, Program, VarDecl, Assignment, PrintStmt,
    IfStmt, WhileStmt, Block, BinaryOp, UnaryOp,
    NumberLiteral, StringLiteral, BoolLiteral, NullLiteral, Identifier,
)
from error import RuntimeError as LangRuntimeError


# ---------------------------------------------------------------------------
# Runtime environment
# ---------------------------------------------------------------------------

class Environment:
    """Lexically scoped variable store."""

    def __init__(self, parent: Environment | None = None):
        self._vars: dict[str, Any] = {}
        self._parent = parent

    def define(self, name: str, value: Any) -> None:
        self._vars[name] = value

    def assign(self, name: str, value: Any, line: int = 0, col: int = 0) -> None:
        if name in self._vars:
            self._vars[name] = value
            return
        if self._parent is not None:
            self._parent.assign(name, value, line, col)
            return
        raise LangRuntimeError(f"Undefined variable '{name}'", line, col)

    def get(self, name: str, line: int = 0, col: int = 0) -> Any:
        if name in self._vars:
            return self._vars[name]
        if self._parent is not None:
            return self._parent.get(name, line, col)
        raise LangRuntimeError(f"Undefined variable '{name}'", line, col)

    def child(self) -> "Environment":
        return Environment(parent=self)


# ---------------------------------------------------------------------------
# Interpreter
# ---------------------------------------------------------------------------

class Interpreter:
    """
    Evaluates an AST produced by Parser + SemanticAnalyzer.

    Usage::

        output_lines = Interpreter().execute(ast)
    """

    def __init__(self):
        self._env: Environment = Environment()
        self._output: list[str] = []

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def execute(self, node: ASTNode) -> list[str]:
        """Run the program and return all printed lines."""
        self._output = []
        self._eval(node)
        return self._output

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def _eval(self, node: ASTNode) -> Any:
        method = "_eval_" + type(node).__name__
        handler = getattr(self, method, None)
        if handler is None:
            raise LangRuntimeError(f"Cannot evaluate node: {type(node).__name__}", 0, 0)
        return handler(node)

    # ------------------------------------------------------------------
    # Statement evaluators
    # ------------------------------------------------------------------

    def _eval_Program(self, node: Program) -> None:
        for stmt in node.statements:
            self._eval(stmt)

    def _eval_VarDecl(self, node: VarDecl) -> None:
        value = self._eval(node.value)
        self._env.define(node.name, value)

    def _eval_Assignment(self, node: Assignment) -> None:
        value = self._eval(node.value)
        self._env.assign(node.name, value, node.line, node.col)

    def _eval_PrintStmt(self, node: PrintStmt) -> None:
        value = self._eval(node.expr)
        text = self._to_string(value)
        self._output.append(text)
        print(text)

    def _eval_IfStmt(self, node: IfStmt) -> None:
        if self._is_truthy(self._eval(node.condition)):
            self._eval_block(node.then_block)
        elif node.else_block is not None:
            self._eval_block(node.else_block)

    def _eval_WhileStmt(self, node: WhileStmt) -> None:
        iteration_limit = 1_000_000  # guard against infinite loops
        count = 0
        while self._is_truthy(self._eval(node.condition)):
            self._eval_block(node.body)
            count += 1
            if count >= iteration_limit:
                raise LangRuntimeError(
                    "Iteration limit exceeded (possible infinite loop)", node.line, 0
                )

    def _eval_Block(self, node: Block) -> None:
        self._eval_block(node)

    def _eval_block(self, node: Block) -> None:
        outer = self._env
        self._env = self._env.child()
        for stmt in node.statements:
            self._eval(stmt)
        self._env = outer

    # ------------------------------------------------------------------
    # Expression evaluators
    # ------------------------------------------------------------------

    def _eval_BinaryOp(self, node: BinaryOp) -> Any:
        left  = self._eval(node.left)
        right = self._eval(node.right)
        op    = node.op

        # Arithmetic
        if op == "+":
            if isinstance(left, str) or isinstance(right, str):
                return self._to_string(left) + self._to_string(right)
            return self._num(left, op, node) + self._num(right, op, node)
        if op == "-": return self._num(left, op, node) - self._num(right, op, node)
        if op == "*": return self._num(left, op, node) * self._num(right, op, node)
        if op == "/":
            r = self._num(right, op, node)
            if r == 0:
                raise LangRuntimeError("Division by zero", node.line, node.col)
            l = self._num(left, op, node)
            result = l / r
            # Return int if result is whole number
            return int(result) if isinstance(result, float) and result == int(result) else result
        if op == "%":
            r = self._num(right, op, node)
            if r == 0:
                raise LangRuntimeError("Modulo by zero", node.line, node.col)
            return self._num(left, op, node) % r
        if op == "**":
            return self._num(left, op, node) ** self._num(right, op, node)

        # Comparison
        if op == ">":  return left > right
        if op == "<":  return left < right
        if op == ">=": return left >= right
        if op == "<=": return left <= right
        if op == "==": return left == right
        if op == "!=": return left != right

        # Logical (bonus)
        if op == "&&": return self._is_truthy(left) and self._is_truthy(right)
        if op == "||": return self._is_truthy(left) or  self._is_truthy(right)

        raise LangRuntimeError(f"Unknown operator '{op}'", node.line, node.col)

    def _eval_UnaryOp(self, node: UnaryOp) -> Any:
        operand = self._eval(node.operand)
        if node.op == "-":
            if not isinstance(operand, (int, float)):
                raise LangRuntimeError(
                    f"Unary '-' requires a number, got {type(operand).__name__}",
                    node.line, node.col,
                )
            return -operand
        if node.op == "!":
            return not self._is_truthy(operand)
        raise LangRuntimeError(f"Unknown unary operator '{node.op}'", node.line, node.col)

    def _eval_NumberLiteral(self, node: NumberLiteral) -> int | float:
        return node.value

    def _eval_StringLiteral(self, node: StringLiteral) -> str:
        return node.value

    def _eval_BoolLiteral(self, node: BoolLiteral) -> bool:
        return node.value

    def _eval_NullLiteral(self, _: NullLiteral) -> None:
        return None

    def _eval_Identifier(self, node: Identifier) -> Any:
        return self._env.get(node.name, node.line, node.col)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def _is_truthy(value: Any) -> bool:
        if value is None:    return False
        if value is False:   return False
        if value == 0:       return False
        if value == "":      return False
        return True

    @staticmethod
    def _to_string(value: Any) -> str:
        if value is None:  return "null"
        if value is True:  return "true"
        if value is False: return "false"
        if isinstance(value, float) and value == int(value):
            return str(int(value))
        return str(value)

    @staticmethod
    def _num(value: Any, op: str, node: BinaryOp) -> int | float:
        if not isinstance(value, (int, float)):
            raise LangRuntimeError(
                f"Operator '{op}' requires numbers, got {type(value).__name__}",
                node.line, node.col,
            )
        return value
