"""
conftest.py - Shared pytest fixtures and utilities.
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path so we can import compiler modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from lexer import Lexer, tokenize_string
from parser import Parser
from analyzer import SemanticAnalyzer
from interpreter import Interpreter


@pytest.fixture
def lexer():
    """Factory fixture for creating Lexer instances."""
    def _lexer(source: str):
        return Lexer(source)
    return _lexer


@pytest.fixture
def parser():
    """Factory fixture for creating Parser instances."""
    def _parser(source: str):
        tokens = tokenize_string(source)
        return Parser(tokens)
    return _parser


@pytest.fixture
def semantic_analyzer():
    """Factory fixture for creating SemanticAnalyzer instances."""
    return SemanticAnalyzer()


@pytest.fixture
def interpreter():
    """Factory fixture for creating Interpreter instances."""
    return Interpreter()


@pytest.fixture
def compile_and_run():
    """
    Full pipeline fixture: source → tokens → AST → analysis → execution.
    Returns output lines.
    """
    def _compile_and_run(source: str):
        tokens = tokenize_string(source)
        ast = Parser(tokens).parse()
        SemanticAnalyzer().analyze(ast)
        output = Interpreter().execute(ast)
        return output
    return _compile_and_run
