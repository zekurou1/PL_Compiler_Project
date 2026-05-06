"""
test_integration.py - Full pipeline integration tests.
Tests complete source → tokens → AST → analysis → execution flow.
"""
import pytest
from tests.conftest import compile_and_run


class TestIntegrationBasicPrograms:
    """Integration tests with complete programs."""

    def test_simple_print(self, compile_and_run):
        """Simplest program: just print."""
        output = compile_and_run("print(42);")
        assert output == ["42"]

    def test_variable_and_print(self, compile_and_run):
        """Declare variable and print."""
        output = compile_and_run("let x = 42; print(x);")
        assert output == ["42"]

    def test_existing_sample_program(self, compile_and_run):
        """Verify existing sample program still works."""
        source = """
        let x = 10;
        let y = 3;
        let sum = x + y;
        print(sum);
        """
        output = compile_and_run(source)
        assert output == ["13"]


class TestIntegrationArithmetic:
    """Full programs using arithmetic."""

    def test_arithmetic_sequence(self, compile_and_run):
        """Multiple arithmetic operations."""
        source = """
        let a = 10;
        let b = 20;
        let c = a + b;
        let d = c * 2;
        print(d);
        """
        output = compile_and_run(source)
        assert output == ["60"]

    def test_modulo_in_full_program(self, compile_and_run):
        """Modulo in complete program."""
        source = """
        let x = 17;
        let remainder = x % 5;
        print(remainder);
        """
        output = compile_and_run(source)
        assert output == ["2"]


class TestIntegrationLogicalOperators:
    """Full programs using logical operators."""

    def test_and_in_full_program(self, compile_and_run):
        """Logical AND in complete program."""
        source = """
        let x = 5;
        let y = 10;
        let result = x < 10 && y > 5;
        print(result);
        """
        output = compile_and_run(source)
        assert output == ["true"]

    def test_or_in_full_program(self, compile_and_run):
        """Logical OR in complete program."""
        source = """
        let x = 15;
        let result = x < 10 || x > 12;
        print(result);
        """
        output = compile_and_run(source)
        assert output == ["true"]

    def test_mixed_logical_operators(self, compile_and_run):
        """Mixed logical operators."""
        source = """
        let a = true;
        let b = false;
        let c = a && b || a;
        print(c);
        """
        output = compile_and_run(source)
        assert output == ["true"]


class TestIntegrationControlFlow:
    """Full programs using control flow."""

    def test_if_with_logical_condition(self, compile_and_run):
        """If statement with logical operators."""
        source = """
        let x = 7;
        if (x > 5 && x < 10) {
            print("in range");
        }
        """
        output = compile_and_run(source)
        assert output == ["in range"]

    def test_if_else_with_logical(self, compile_and_run):
        """If-else with logical operators."""
        source = """
        let x = 3;
        if (x > 5 || x < 1) {
            print("out of range");
        } else {
            print("in range");
        }
        """
        output = compile_and_run(source)
        assert output == ["in range"]

    def test_while_with_modulo(self, compile_and_run):
        """While loop using modulo."""
        source = """
        let i = 0;
        while (i < 10) {
            if (i % 2 == 0) {
                print(i);
            }
            i = i + 1;
        }
        """
        output = compile_and_run(source)
        assert output == ["0", "2", "4", "6", "8"]

    def test_nested_control_flow(self, compile_and_run):
        """Nested if inside while."""
        source = """
        let i = 1;
        while (i <= 3) {
            if (i == 2) {
                print("two");
            } else {
                print(i);
            }
            i = i + 1;
        }
        """
        output = compile_and_run(source)
        assert output == ["1", "two", "3"]


class TestIntegrationScoping:
    """Integration tests for variable scoping."""

    def test_if_scope_shadowing(self, compile_and_run):
        """Variable shadowing in nested if block."""
        source = """
        let x = 10;
        print(x);
        if (true) {
            let x = 20;
            print(x);
        }
        print(x);
        """
        output = compile_and_run(source)
        assert output == ["10", "20", "10"]

    def test_if_block_scoping_integration(self, compile_and_run):
        """Scoping with if block."""
        source = """
        let x = 5;
        if (true) {
            let y = 10;
            print(x + y);
        }
        """
        output = compile_and_run(source)
        assert output == ["15"]

    def test_while_block_scoping_integration(self, compile_and_run):
        """Scoping with while block."""
        source = """
        let result = 0;
        let i = 1;
        while (i <= 3) {
            let temp = i * 10;
            result = result + temp;
            i = i + 1;
        }
        print(result);
        """
        output = compile_and_run(source)
        assert output == ["60"]


class TestIntegrationStringConcatenation:
    """Integration tests for string operations."""

    def test_string_with_arithmetic(self, compile_and_run):
        """String concatenation with computed values."""
        source = """
        let x = 5;
        let y = 3;
        print("sum = " + (x + y));
        """
        output = compile_and_run(source)
        assert output == ["sum = 8"]

    def test_multiple_string_concatenations(self, compile_and_run):
        """Chained string concatenations."""
        source = """
        print("a" + "b" + "c");
        """
        output = compile_and_run(source)
        assert output == ["abc"]


class TestIntegrationComplexPrograms:
    """Complex programs combining multiple features."""

    def test_fibonacci_sequence(self, compile_and_run):
        """Compute Fibonacci numbers."""
        source = """
        let a = 0;
        let b = 1;
        let i = 0;
        while (i < 5) {
            print(a);
            let temp = a + b;
            a = b;
            b = temp;
            i = i + 1;
        }
        """
        output = compile_and_run(source)
        assert output == ["0", "1", "1", "2", "3"]

    def test_multiplication_table(self, compile_and_run):
        """Generate 3x3 multiplication table."""
        source = """
        let i = 1;
        while (i <= 3) {
            let j = 1;
            while (j <= 3) {
                print(i * j);
                j = j + 1;
            }
            i = i + 1;
        }
        """
        output = compile_and_run(source)
        expected = ["1", "2", "3", "2", "4", "6", "3", "6", "9"]
        assert output == expected

    def test_sum_even_numbers(self, compile_and_run):
        """Sum even numbers from 1 to 10."""
        source = """
        let sum = 0;
        let i = 1;
        while (i <= 10) {
            if (i % 2 == 0) {
                sum = sum + i;
            }
            i = i + 1;
        }
        print(sum);
        """
        output = compile_and_run(source)
        assert output == ["30"]

    def test_boolean_logic_chain(self, compile_and_run):
        """Complex boolean logic."""
        source = """
        let x = 5;
        let y = 10;
        let z = 15;
        let result = (x < y && y < z) || (x == y || y == z);
        print(result);
        """
        output = compile_and_run(source)
        assert output == ["true"]

    def test_nested_if_scoping_complex(self, compile_and_run):
        """Complex nested if scoping scenario."""
        source = """
        let x = 1;
        if (true) {
            let y = 2;
            if (true) {
                let z = 3;
                print(x + y + z);
                if (true) {
                    let x = 10;
                    print(x);
                }
                print(x);
            }
        }
        """
        output = compile_and_run(source)
        assert output == ["6", "10", "1"]


class TestIntegrationPrecedenceComplete:
    """Integration tests for operator precedence."""

    def test_precedence_arithmetic_logical(self, compile_and_run):
        """Precedence: arithmetic before logical."""
        source = """
        print(1 + 2 * 3 == 7 && 4 / 2 == 2);
        """
        output = compile_and_run(source)
        # 2 * 3 = 6, 1 + 6 = 7, 7 == 7 is true
        # 4 / 2 = 2, 2 == 2 is true
        # true && true = true
        assert output == ["true"]

    def test_precedence_modulo_multiply(self, compile_and_run):
        """Modulo and multiply same precedence."""
        source = """
        print(20 * 1 % 6 == 2);
        """
        output = compile_and_run(source)
        # 20 * 1 = 20, 20 % 6 = 2, 2 == 2 is true
        assert output == ["true"]

    def test_precedence_logical_or_and(self, compile_and_run):
        """OR precedence lower than AND."""
        source = """
        print(false || true && false);
        """
        output = compile_and_run(source)
        # true && false = false, false || false = false
        assert output == ["false"]
