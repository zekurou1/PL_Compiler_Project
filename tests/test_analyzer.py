"""
test_analyzer.py - Semantic analysis tests (scoping, declarations, etc).
"""
import pytest
from lexer import tokenize_string
from parser import Parser
from analyzer import SemanticAnalyzer
from error import SemanticError


class TestAnalyzerBasics:
    """Basic semantic analysis tests."""

    def test_valid_variable_declaration(self):
        """Valid variable declaration should pass analysis."""
        source = "let x = 42;"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        # Should not raise
        SemanticAnalyzer().analyze(ast)

    def test_undeclared_variable_use(self):
        """Using undeclared variable should raise error."""
        source = "print(x);"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        with pytest.raises(SemanticError):
            SemanticAnalyzer().analyze(ast)

    def test_declared_variable_use(self):
        """Using declared variable should pass."""
        source = "let x = 42; print(x);"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        # Should not raise
        SemanticAnalyzer().analyze(ast)


class TestAnalyzerScopingRules:
    """Tests for lexical scoping."""

    def test_variable_shadowing_in_if(self):
        """Inner scope can shadow outer scope variable (via if block)."""
        source = """
        let x = 10;
        if (true) {
            let x = 20;
            print(x);
        }
        """
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        # Should not raise
        SemanticAnalyzer().analyze(ast)

    def test_outer_scope_access_in_if(self):
        """Inner scope can access outer scope variables."""
        source = """
        let x = 10;
        if (true) {
            print(x);
        }
        """
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        # Should not raise
        SemanticAnalyzer().analyze(ast)

    def test_if_block_scoping(self):
        """If block creates new scope."""
        source = """
        let x = 10;
        if (true) {
            let x = 20;
            print(x);
        }
        print(x);
        """
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        # Should not raise
        SemanticAnalyzer().analyze(ast)

    def test_while_block_scoping(self):
        """While block creates new scope."""
        source = """
        let x = 10;
        while (x > 0) {
            let x = x - 1;
            print(x);
        }
        """
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        # Should not raise
        SemanticAnalyzer().analyze(ast)


class TestAnalyzerDuplicateDeclarations:
    """Tests for duplicate declaration detection."""

    def test_duplicate_in_same_scope(self):
        """Duplicate declarations in same scope should raise error."""
        source = "let x = 10; let x = 20;"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        with pytest.raises(SemanticError):
            SemanticAnalyzer().analyze(ast)

    def test_shadowing_allowed_in_if_scope(self):
        """Same name in nested if scope is allowed (shadowing)."""
        source = """
        let x = 10;
        if (true) {
            let x = 20;
        }
        """
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        # Should not raise
        SemanticAnalyzer().analyze(ast)

    def test_duplicate_in_if_scope(self):
        """Duplicate in same if scope should raise error."""
        source = """
        if (true) {
            let x = 10;
            let x = 20;
        }
        """
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        with pytest.raises(SemanticError):
            SemanticAnalyzer().analyze(ast)


class TestAnalyzerAssignment:
    """Tests for assignment validation."""

    def test_assignment_to_declared_variable(self):
        """Assignment to declared variable should pass."""
        source = "let x = 10; x = 20;"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        # Should not raise
        SemanticAnalyzer().analyze(ast)

    def test_assignment_to_undeclared_variable(self):
        """Assignment to undeclared variable should raise error."""
        source = "x = 20;"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        with pytest.raises(SemanticError):
            SemanticAnalyzer().analyze(ast)

    def test_assignment_in_if_scope(self):
        """Assignment to outer scope variable from if scope."""
        source = """
        let x = 10;
        if (true) {
            x = 20;
        }
        """
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        # Should not raise
        SemanticAnalyzer().analyze(ast)


class TestAnalyzerExpressions:
    """Tests for expression validation."""

    def test_expression_with_undeclared_identifier(self):
        """Expression with undeclared identifier should raise error."""
        source = "let y = x + 10;"
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        with pytest.raises(SemanticError):
            SemanticAnalyzer().analyze(ast)

    def test_complex_expression_with_all_vars_declared(self):
        """Complex expression with all variables declared should pass."""
        source = """
        let x = 10;
        let y = 20;
        let z = x + y * 2 - x / 2;
        """
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        # Should not raise
        SemanticAnalyzer().analyze(ast)

    def test_logical_operators_expression(self):
        """Logical operators with declared variables."""
        source = """
        let a = true;
        let b = false;
        let c = a && b || a;
        """
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        # Should not raise
        SemanticAnalyzer().analyze(ast)


class TestAnalyzerComplexPrograms:
    """Tests with realistic program structures."""

    def test_nested_if_scoping(self):
        """Nested if blocks."""
        source = """
        let x = 1;
        if (true) {
            let y = 2;
            if (true) {
                let z = 3;
                print(x);
                print(y);
                print(z);
            }
        }
        """
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        # Should not raise
        SemanticAnalyzer().analyze(ast)

    def test_if_else_with_scoping(self):
        """If-else with proper scoping."""
        source = """
        let x = 10;
        if (x > 5) {
            let y = 20;
            print(y);
        } else {
            let y = 30;
            print(y);
        }
        """
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        # Should not raise
        SemanticAnalyzer().analyze(ast)

    def test_while_loop_body_scoping(self):
        """While loop with local variables."""
        source = """
        let i = 0;
        while (i < 10) {
            let temp = i * 2;
            print(temp);
            i = i + 1;
        }
        """
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        # Should not raise
        SemanticAnalyzer().analyze(ast)
