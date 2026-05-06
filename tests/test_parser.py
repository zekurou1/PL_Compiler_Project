"""
test_parser.py - Comprehensive parser tests covering precedence and syntax.
"""
import pytest
from lexer import tokenize_string
from parser import Parser
from ast_nodes import (
    Program, VarDecl, Assignment, BinaryOp, UnaryOp, 
    NumberLiteral, Identifier, IfStmt, WhileStmt
)
from error import SyntaxError as LangSyntaxError


class TestParserBasics:
    """Basic parser functionality tests."""

    def test_parse_empty_program(self):
        """Empty program should produce empty statements list."""
        tokens = tokenize_string("")
        ast = Parser(tokens).parse()
        assert isinstance(ast, Program)
        assert len(ast.statements) == 0

    def test_parse_single_variable_declaration(self):
        """Parse simple variable declaration."""
        source = "let x = 42;"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        assert len(ast.statements) == 1
        stmt = ast.statements[0]
        assert isinstance(stmt, VarDecl)
        assert stmt.name == "x"
        assert isinstance(stmt.value, NumberLiteral)
        assert stmt.value.value == 42

    def test_parse_multiple_declarations(self):
        """Parse multiple variable declarations."""
        source = "let x = 1; let y = 2; let z = 3;"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        assert len(ast.statements) == 3
        for i, stmt in enumerate(ast.statements):
            assert isinstance(stmt, VarDecl)


class TestParserOperatorPrecedence:
    """Tests for correct operator precedence."""

    def test_addition_before_multiplication(self):
        """1 + 2 * 3 should parse as 1 + (2 * 3), not (1 + 2) * 3."""
        source = "let x = 1 + 2 * 3;"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        expr = ast.statements[0].value
        assert isinstance(expr, BinaryOp)
        assert expr.op == "+"
        # Right side should be 2 * 3
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.op == "*"

    def test_multiplication_before_subtraction(self):
        """10 - 2 * 3 should parse as 10 - (2 * 3)."""
        source = "let x = 10 - 2 * 3;"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        expr = ast.statements[0].value
        assert isinstance(expr, BinaryOp)
        assert expr.op == "-"
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.op == "*"

    def test_modulo_before_addition(self):
        """a + b % c should parse as a + (b % c)."""
        source = "let x = a + b % c;"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        expr = ast.statements[0].value
        assert isinstance(expr, BinaryOp)
        assert expr.op == "+"
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.op == "%"

    def test_unary_highest_precedence(self):
        """Unary operators should bind tightest: -2 * 3 → (-2) * 3."""
        source = "let x = -2 * 3;"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        expr = ast.statements[0].value
        assert isinstance(expr, BinaryOp)
        assert expr.op == "*"
        # Left should be unary negation
        assert isinstance(expr.left, UnaryOp)
        assert expr.left.op == "-"

    def test_logical_and_before_or(self):
        """a || b && c should parse as a || (b && c)."""
        source = "let x = a || b && c;"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        expr = ast.statements[0].value
        assert isinstance(expr, BinaryOp)
        assert expr.op == "||"
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.op == "&&"

    def test_equality_before_logical_and(self):
        """a && b == c should parse as a && (b == c)."""
        source = "let x = a && b == c;"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        expr = ast.statements[0].value
        assert isinstance(expr, BinaryOp)
        assert expr.op == "&&"
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.op == "=="

    def test_comparison_before_equality(self):
        """a == b > c should parse as a == (b > c)."""
        source = "let x = a == b > c;"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        expr = ast.statements[0].value
        assert isinstance(expr, BinaryOp)
        assert expr.op == "=="
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.op == ">"


class TestParserLogicalOperators:
    """Tests for logical operators && and ||."""

    def test_parse_logical_and(self):
        """Parse logical AND operator."""
        source = "let x = true && false;"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        expr = ast.statements[0].value
        assert isinstance(expr, BinaryOp)
        assert expr.op == "&&"

    def test_parse_logical_or(self):
        """Parse logical OR operator."""
        source = "let x = true || false;"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        expr = ast.statements[0].value
        assert isinstance(expr, BinaryOp)
        assert expr.op == "||"

    def test_parse_chained_and(self):
        """Parse chained AND operations (left-associative)."""
        source = "let x = a && b && c;"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        expr = ast.statements[0].value
        # Should parse as (a && b) && c
        assert isinstance(expr, BinaryOp)
        assert expr.op == "&&"
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.op == "&&"

    def test_parse_mixed_logical(self):
        """Parse mixed logical operations."""
        source = "let x = a && b || c && d;"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        expr = ast.statements[0].value
        # Should parse as (a && b) || (c && d)
        assert isinstance(expr, BinaryOp)
        assert expr.op == "||"


class TestParserModulo:
    """Tests for modulo operator."""

    def test_parse_modulo(self):
        """Parse modulo operator."""
        source = "let x = a % b;"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        expr = ast.statements[0].value
        assert isinstance(expr, BinaryOp)
        assert expr.op == "%"

    def test_modulo_precedence_vs_multiply(self):
        """Modulo and multiply have same precedence (left-associative)."""
        source = "let x = a % b * c;"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        expr = ast.statements[0].value
        # Should parse as (a % b) * c
        assert isinstance(expr, BinaryOp)
        assert expr.op == "*"
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.op == "%"


class TestParserParenthesizedExpressions:
    """Tests for parenthesized expressions overriding precedence."""

    def test_parenthesized_changes_precedence(self):
        """Parentheses should override precedence: (a + b) * c."""
        source = "let x = (a + b) * c;"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        expr = ast.statements[0].value
        # Should parse as (a + b) * c
        assert isinstance(expr, BinaryOp)
        assert expr.op == "*"
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.op == "+"

    def test_nested_parentheses(self):
        """Nested parentheses should work."""
        source = "let x = ((a + b) * (c - d));"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        expr = ast.statements[0].value
        assert isinstance(expr, BinaryOp)
        assert expr.op == "*"


class TestParserControlFlow:
    """Tests for if/while statement parsing."""

    def test_parse_if_statement(self):
        """Parse if statement."""
        source = "if (x > 5) { print(x); }"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        stmt = ast.statements[0]
        assert isinstance(stmt, IfStmt)

    def test_parse_if_else_statement(self):
        """Parse if-else statement."""
        source = "if (x > 5) { print(x); } else { print(y); }"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        stmt = ast.statements[0]
        assert isinstance(stmt, IfStmt)
        assert stmt.else_block is not None

    def test_parse_while_statement(self):
        """Parse while statement."""
        source = "while (x < 10) { x = x + 1; }"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        stmt = ast.statements[0]
        assert isinstance(stmt, WhileStmt)


class TestParserErrors:
    """Tests for parse error detection."""

    def test_missing_semicolon(self):
        """Missing semicolon should raise error."""
        source = "let x = 42"
        tokens = tokenize_string(source)
        with pytest.raises(LangSyntaxError):
            Parser(tokens).parse()

    def test_missing_closing_paren(self):
        """Missing closing paren in print statement."""
        source = "print(42;"
        tokens = tokenize_string(source)
        with pytest.raises(LangSyntaxError):
            Parser(tokens).parse()

    def test_unexpected_token_at_statement(self):
        """Unexpected token at statement level."""
        source = "+ 42;"
        tokens = tokenize_string(source)
        with pytest.raises(LangSyntaxError):
            Parser(tokens).parse()
