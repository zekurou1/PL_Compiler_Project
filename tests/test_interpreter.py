"""
test_interpreter.py - Interpreter evaluation tests for all operators and expressions.
"""
import pytest
from tests.conftest import compile_and_run


class TestInterpreterArithmetic:
    """Tests for arithmetic operations."""

    def test_addition(self, compile_and_run):
        """Addition: 2 + 3 = 5."""
        output = compile_and_run("print(2 + 3);")
        assert output == ["5"]

    def test_subtraction(self, compile_and_run):
        """Subtraction: 10 - 4 = 6."""
        output = compile_and_run("print(10 - 4);")
        assert output == ["6"]

    def test_multiplication(self, compile_and_run):
        """Multiplication: 3 * 7 = 21."""
        output = compile_and_run("print(3 * 7);")
        assert output == ["21"]

    def test_division_exact(self, compile_and_run):
        """Division with exact result: 20 / 4 = 5."""
        output = compile_and_run("print(20 / 4);")
        assert output == ["5"]

    def test_division_float(self, compile_and_run):
        """Division with float result: 5 / 2 = 2.5."""
        output = compile_and_run("print(5 / 2);")
        assert output == ["2.5"]

    def test_division_by_zero(self, compile_and_run):
        """Division by zero should raise runtime error."""
        from error import RuntimeError as LangRuntimeError
        with pytest.raises(LangRuntimeError):
            compile_and_run("print(10 / 0);")

    def test_modulo(self, compile_and_run):
        """Modulo operator: 10 % 3 = 1."""
        output = compile_and_run("print(10 % 3);")
        assert output == ["1"]

    def test_modulo_zero(self, compile_and_run):
        """Modulo by zero should raise error."""
        from error import RuntimeError as LangRuntimeError
        with pytest.raises(LangRuntimeError):
            compile_and_run("print(10 % 0);")

    def test_operator_precedence_mult_before_add(self, compile_and_run):
        """Precedence: 2 + 3 * 4 = 14 (not 20)."""
        output = compile_and_run("print(2 + 3 * 4);")
        assert output == ["14"]

    def test_operator_precedence_modulo_same_as_mult(self, compile_and_run):
        """Modulo same precedence as multiply: 10 % 3 * 2 = (10 % 3) * 2 = 2."""
        output = compile_and_run("print(10 % 3 * 2);")
        assert output == ["2"]


class TestInterpreterStringOperations:
    """Tests for string operations."""

    def test_string_concatenation(self, compile_and_run):
        """String concatenation with +."""
        output = compile_and_run('print("Hello, " + "World!");')
        assert output == ["Hello, World!"]

    def test_string_number_concatenation(self, compile_and_run):
        """Concatenating string and number."""
        output = compile_and_run('print("Number: " + 42);')
        assert output == ["Number: 42"]

    def test_number_string_concatenation(self, compile_and_run):
        """Concatenating number and string."""
        output = compile_and_run('print(42 + " is the answer");')
        assert output == ["42 is the answer"]


class TestInterpreterComparison:
    """Tests for comparison operators."""

    def test_greater_than_true(self, compile_and_run):
        """Greater than: 10 > 5 = true."""
        output = compile_and_run("print(10 > 5);")
        assert output == ["true"]

    def test_greater_than_false(self, compile_and_run):
        """Greater than: 5 > 10 = false."""
        output = compile_and_run("print(5 > 10);")
        assert output == ["false"]

    def test_less_than(self, compile_and_run):
        """Less than: 5 < 10 = true."""
        output = compile_and_run("print(5 < 10);")
        assert output == ["true"]

    def test_greater_equal(self, compile_and_run):
        """Greater or equal: 10 >= 10 = true."""
        output = compile_and_run("print(10 >= 10);")
        assert output == ["true"]

    def test_less_equal(self, compile_and_run):
        """Less or equal: 5 <= 10 = true."""
        output = compile_and_run("print(5 <= 10);")
        assert output == ["true"]

    def test_equality(self, compile_and_run):
        """Equality: 42 == 42 = true."""
        output = compile_and_run("print(42 == 42);")
        assert output == ["true"]

    def test_inequality(self, compile_and_run):
        """Inequality: 42 != 43 = true."""
        output = compile_and_run("print(42 != 43);")
        assert output == ["true"]


class TestInterpreterLogicalOperators:
    """Tests for logical operators && and ||."""

    def test_logical_and_both_true(self, compile_and_run):
        """AND: true && true = true."""
        output = compile_and_run("print(true && true);")
        assert output == ["true"]

    def test_logical_and_one_false(self, compile_and_run):
        """AND: true && false = false."""
        output = compile_and_run("print(true && false);")
        assert output == ["false"]

    def test_logical_and_both_false(self, compile_and_run):
        """AND: false && false = false."""
        output = compile_and_run("print(false && false);")
        assert output == ["false"]

    def test_logical_or_both_true(self, compile_and_run):
        """OR: true || true = true."""
        output = compile_and_run("print(true || true);")
        assert output == ["true"]

    def test_logical_or_one_true(self, compile_and_run):
        """OR: true || false = true."""
        output = compile_and_run("print(true || false);")
        assert output == ["true"]

    def test_logical_or_both_false(self, compile_and_run):
        """OR: false || false = false."""
        output = compile_and_run("print(false || false);")
        assert output == ["false"]

    def test_logical_and_precedence_over_or(self, compile_and_run):
        """Precedence: true || false && false = true || (false && false) = true."""
        output = compile_and_run("print(true || false && false);")
        assert output == ["true"]

    def test_logical_with_comparisons(self, compile_and_run):
        """Logical with comparisons: 5 > 3 && 10 < 20."""
        output = compile_and_run("print(5 > 3 && 10 < 20);")
        assert output == ["true"]


class TestInterpreterUnary:
    """Tests for unary operators."""

    def test_unary_negation(self, compile_and_run):
        """Unary negation: -5 = -5."""
        output = compile_and_run("print(-5);")
        assert output == ["-5"]

    def test_unary_negation_of_expression(self, compile_and_run):
        """Unary negation of expression: -(2 + 3) = -5."""
        output = compile_and_run("print(-(2 + 3));")
        assert output == ["-5"]

    def test_logical_not_true(self, compile_and_run):
        """NOT true = false."""
        output = compile_and_run("print(!true);")
        assert output == ["false"]

    def test_logical_not_false(self, compile_and_run):
        """NOT false = true."""
        output = compile_and_run("print(!false);")
        assert output == ["true"]

    def test_logical_not_number_zero(self, compile_and_run):
        """NOT 0 = true (0 is falsy)."""
        output = compile_and_run("print(!0);")
        assert output == ["true"]

    def test_logical_not_number_nonzero(self, compile_and_run):
        """NOT 1 = false (non-zero is truthy)."""
        output = compile_and_run("print(!1);")
        assert output == ["false"]


class TestInterpreterVariables:
    """Tests for variable declaration and assignment."""

    def test_variable_declaration_and_use(self, compile_and_run):
        """Declare variable and use it."""
        output = compile_and_run("let x = 42; print(x);")
        assert output == ["42"]

    def test_variable_assignment(self, compile_and_run):
        """Assign to variable and use it."""
        output = compile_and_run("let x = 10; x = 20; print(x);")
        assert output == ["20"]

    def test_multiple_variables(self, compile_and_run):
        """Multiple variables."""
        output = compile_and_run("let x = 10; let y = 20; print(x); print(y);")
        assert output == ["10", "20"]

    def test_variable_expression_evaluation(self, compile_and_run):
        """Variable in expression: let x = 2; print(x * 3);."""
        output = compile_and_run("let x = 2; print(x * 3);")
        assert output == ["6"]


class TestInterpreterControlFlow:
    """Tests for if and while statements."""

    def test_if_true_condition(self, compile_and_run):
        """If with true condition executes."""
        output = compile_and_run("if (true) { print(1); }")
        assert output == ["1"]

    def test_if_false_condition(self, compile_and_run):
        """If with false condition doesn't execute."""
        output = compile_and_run("if (false) { print(1); }")
        assert output == []

    def test_if_else_true(self, compile_and_run):
        """If-else with true condition."""
        output = compile_and_run("if (true) { print(1); } else { print(2); }")
        assert output == ["1"]

    def test_if_else_false(self, compile_and_run):
        """If-else with false condition."""
        output = compile_and_run("if (false) { print(1); } else { print(2); }")
        assert output == ["2"]

    def test_while_loop_basic(self, compile_and_run):
        """While loop: count to 3."""
        source = """
        let i = 1;
        while (i <= 3) {
            print(i);
            i = i + 1;
        }
        """
        output = compile_and_run(source)
        assert output == ["1", "2", "3"]

    def test_while_loop_false_condition(self, compile_and_run):
        """While loop with false condition doesn't execute."""
        output = compile_and_run("let i = 1; while (false) { print(i); }")
        assert output == []

    def test_while_sum(self, compile_and_run):
        """While loop summing 1 to 5."""
        source = """
        let sum = 0;
        let i = 1;
        while (i <= 5) {
            sum = sum + i;
            i = i + 1;
        }
        print(sum);
        """
        output = compile_and_run(source)
        assert output == ["15"]


class TestInterpreterComplexExpressions:
    """Tests for complex expressions."""

    def test_nested_arithmetic(self, compile_and_run):
        """Nested arithmetic: (2 + 3) * (4 - 1) = 15."""
        output = compile_and_run("print((2 + 3) * (4 - 1));")
        assert output == ["15"]

    def test_all_operators_in_expression(self, compile_and_run):
        """Expression with all operators: 2 + 3 * 4 % 5 == 5 && true."""
        output = compile_and_run("print(2 + 3 * 4 % 5 == 5 && true);")
        # 3 * 4 = 12, 12 % 5 = 2, 2 + 2 = 4, 4 == 5 is false, false && true = false
        assert output == ["false"]

    def test_precedence_example_1(self, compile_and_run):
        """Example: 1 + 2 * 3 - 4 / 2 = 1 + 6 - 2 = 5."""
        output = compile_and_run("print(1 + 2 * 3 - 4 / 2);")
        assert output == ["5"]

    def test_precedence_example_2(self, compile_and_run):
        """Example: 5 < 10 && 10 < 20 || 1 == 1."""
        output = compile_and_run("print(5 < 10 && 10 < 20 || 1 == 1);")
        assert output == ["true"]
