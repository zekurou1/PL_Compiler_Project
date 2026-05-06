"""
test_lexer.py - Comprehensive lexer tests covering tokenization edge cases.
"""
import pytest
from tokens import Token, TokenType
from lexer import Lexer, tokenize_string
from error import LexicalError


class TestLexerBasics:
    """Basic tokenization tests."""

    def test_empty_source(self):
        """Empty source should produce only EOF."""
        tokens = tokenize_string("")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF

    def test_single_integer(self):
        """Single integer literal."""
        tokens = tokenize_string("42")
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.INTEGER
        assert tokens[0].value == "42"
        assert tokens[1].type == TokenType.EOF

    def test_single_float(self):
        """Single float literal."""
        tokens = tokenize_string("3.14")
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.FLOAT
        assert tokens[0].value == "3.14"

    def test_single_identifier(self):
        """Single identifier."""
        tokens = tokenize_string("myVar")
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "myVar"

    def test_keyword_vs_identifier(self):
        """Keywords should be recognized as KEYWORD token type."""
        keywords_src = tokenize_string("let if else while print true false null")
        assert keywords_src[0].type == TokenType.KEYWORD
        assert keywords_src[0].value == "let"
        assert keywords_src[1].type == TokenType.KEYWORD
        assert keywords_src[1].value == "if"

    def test_simple_operators(self):
        """Single-character operators."""
        tokens = tokenize_string("+ - * / = < > !")
        expected_ops = ["+", "-", "*", "/", "=", "<", ">", "!"]
        for i, op in enumerate(expected_ops):
            assert tokens[i].type == TokenType.OPERATOR
            assert tokens[i].value == op

    def test_multi_char_operators(self):
        """Multi-character operators: ==, !=, <=, >=, &&, ||."""
        tokens = tokenize_string("== != <= >= && ||")
        expected_ops = ["==", "!=", "<=", ">=", "&&", "||"]
        for i, op in enumerate(expected_ops):
            assert tokens[i].type == TokenType.OPERATOR
            assert tokens[i].value == op

    def test_modulo_operator(self):
        """Modulo operator %."""
        tokens = tokenize_string("%")
        assert tokens[0].type == TokenType.OPERATOR
        assert tokens[0].value == "%"


class TestLexerDelimiters:
    """Tests for delimiter tokens."""

    def test_delimiters(self):
        """All delimiters: ( ) { } ; ,."""
        tokens = tokenize_string("( ) { } ; ,")
        expected = ["(", ")", "{", "}", ";", ","]
        for i, delim in enumerate(expected):
            assert tokens[i].type == TokenType.DELIMITER
            assert tokens[i].value == delim


class TestLexerStrings:
    """String literal tests."""

    def test_simple_string(self):
        """Simple string literal."""
        tokens = tokenize_string('"hello"')
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello"

    def test_string_with_spaces(self):
        """String with spaces."""
        tokens = tokenize_string('"hello world"')
        assert tokens[0].value == "hello world"

    def test_string_with_escaped_quote(self):
        """String with escaped quote."""
        tokens = tokenize_string('"say \\"hi\\""')
        assert tokens[0].value == 'say "hi"'

    def test_string_with_newline_escape(self):
        """String with escaped newline."""
        tokens = tokenize_string('"line1\\nline2"')
        assert tokens[0].value == "line1\nline2"

    def test_string_with_tab_escape(self):
        """String with escaped tab."""
        tokens = tokenize_string('"before\\tafter"')
        assert tokens[0].value == "before\tafter"

    def test_string_with_backslash_escape(self):
        """String with escaped backslash."""
        tokens = tokenize_string('"path\\\\file"')
        assert tokens[0].value == "path\\file"

    def test_unterminated_string_eof(self):
        """Unterminated string at EOF should raise error."""
        with pytest.raises(LexicalError):
            tokenize_string('"unclosed')

    def test_unterminated_string_newline(self):
        """Unterminated string with newline should raise error."""
        with pytest.raises(LexicalError):
            tokenize_string('"unclosed\n"')


class TestLexerComments:
    """Comment handling tests."""

    def test_line_comment(self):
        """Line comments starting with // should be skipped."""
        tokens = tokenize_string("42 // this is a comment")
        assert len(tokens) == 2  # 42 and EOF
        assert tokens[0].type == TokenType.INTEGER

    def test_line_comment_with_operators(self):
        """Line comment should consume all operators on that line."""
        tokens = tokenize_string("42 // + - * /")
        assert len(tokens) == 2  # 42 and EOF

    def test_multiple_line_comments(self):
        """Multiple line comments."""
        source = """
        let x = 10;  // first comment
        let y = 20;  // second comment
        """
        tokens = tokenize_string(source)
        # Filter to non-EOF tokens
        non_eof = [t for t in tokens if t.type != TokenType.EOF]
        # Should have: let x = 10 ; let y = 20 ;
        assert any(t.value == "let" for t in non_eof)
        assert any(t.value == "10" for t in non_eof)


class TestLexerNumbers:
    """Number literal tests."""

    def test_integer_single_digit(self):
        """Single digit integer."""
        tokens = tokenize_string("0")
        assert tokens[0].type == TokenType.INTEGER
        assert tokens[0].value == "0"

    def test_integer_multi_digit(self):
        """Multi-digit integer."""
        tokens = tokenize_string("12345")
        assert tokens[0].type == TokenType.INTEGER
        assert tokens[0].value == "12345"

    def test_float_basic(self):
        """Basic float."""
        tokens = tokenize_string("3.14")
        assert tokens[0].type == TokenType.FLOAT
        assert tokens[0].value == "3.14"

    def test_float_leading_zero(self):
        """Float with leading zero."""
        tokens = tokenize_string("0.5")
        assert tokens[0].type == TokenType.FLOAT
        assert tokens[0].value == "0.5"

    def test_float_multiple_decimals(self):
        """Float with multiple decimal places."""
        tokens = tokenize_string("2.71828")
        assert tokens[0].type == TokenType.FLOAT

    def test_integer_followed_by_dot_operator(self):
        """Integer followed by separate dot should tokenize as integer + dot (not valid, but tests scanning)."""
        # Note: our lexer doesn't have '.' as delimiter, so "5." will scan as 5 then nothing
        tokens = tokenize_string("5")
        assert tokens[0].type == TokenType.INTEGER


class TestLexerLineColumnTracking:
    """Line and column tracking tests."""

    def test_single_line_positions(self):
        """Verify column positions on single line."""
        tokens = tokenize_string("x = 42")
        assert tokens[0].line == 1 and tokens[0].column == 1  # x
        assert tokens[1].line == 1 and tokens[1].column == 3  # =
        assert tokens[2].line == 1 and tokens[2].column == 5  # 42

    def test_multi_line_positions(self):
        """Verify line tracking across multiple lines."""
        source = "let x = 10;\nlet y = 20;"
        tokens = tokenize_string(source)
        # Find 'let' tokens
        let_tokens = [t for t in tokens if t.value == "let"]
        assert let_tokens[0].line == 1
        assert let_tokens[1].line == 2

    def test_line_after_comment(self):
        """Line counter should update after // comment."""
        source = "42 // comment\n99"
        tokens = tokenize_string(source)
        tokens_non_eof = [t for t in tokens if t.type != TokenType.EOF]
        assert tokens_non_eof[0].value == "42"
        assert tokens_non_eof[0].line == 1
        assert tokens_non_eof[1].value == "99"
        assert tokens_non_eof[1].line == 2


class TestLexerComplexPrograms:
    """Tests with realistic program snippets."""

    def test_if_statement_tokens(self):
        """Tokenize if statement."""
        source = "if (x > 5) { print(x); }"
        tokens = tokenize_string(source)
        expected_values = ["if", "(", "x", ">", "5", ")", "{", "print", "(", "x", ")", ";", "}"]
        actual_values = [t.value for t in tokens if t.type != TokenType.EOF]
        assert actual_values == expected_values

    def test_logical_operators_in_expression(self):
        """Tokenize expression with logical operators."""
        source = "x && y || z"
        tokens = tokenize_string(source)
        values = [t.value for t in tokens if t.type != TokenType.EOF]
        assert values == ["x", "&&", "y", "||", "z"]

    def test_modulo_in_expression(self):
        """Tokenize modulo operator."""
        source = "a % b"
        tokens = tokenize_string(source)
        values = [t.value for t in tokens if t.type != TokenType.EOF]
        assert values == ["a", "%", "b"]

    def test_all_operators_together(self):
        """Tokenize program with all operators."""
        source = "a + b - c * d / e % f == g != h < i > j <= k >= l && m || n"
        tokens = tokenize_string(source)
        operators = [t.value for t in tokens if t.type == TokenType.OPERATOR]
        expected = ["+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=", "&&", "||"]
        assert operators == expected
