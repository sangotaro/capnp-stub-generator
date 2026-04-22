"""Test enum type generation and usage."""

import subprocess


def test_enum_types_exist(calculator_stubs):
    """Test that XxxEnum class and XxxLiteral alias are generated."""
    stub_file = calculator_stubs / "calculator_capnp.pyi"
    content = stub_file.read_text()

    # CalculatorOperatorEnum is the runtime class (narrow)
    assert "class CalculatorOperatorEnum(_DynamicEnum):" in content
    # CalculatorOperatorLiteral is the narrow str Literal alias
    assert 'type CalculatorOperatorLiteral = typing.Literal["add", "subtract", "multiply", "divide"]' in content


def test_xxx_literal_accepts_valid_str(calculator_stubs):
    """XxxLiteral (narrow str alias) accepts valid string literals."""
    test_code = '''
import calculator_capnp

def use_operator(op: calculator_capnp.CalculatorOperatorLiteral):
    pass

use_operator("add")
use_operator("subtract")
use_operator("multiply")
use_operator("divide")
'''

    test_file = calculator_stubs / "test_literal_accepts_str.py"
    test_file.write_text(test_code)

    result = subprocess.run(["pyright", str(test_file)], capture_output=True, text=True)
    assert result.stdout.count("error:") == 0, f"Type checking failed: {result.stdout}"


def test_xxx_literal_rejects_int(calculator_stubs):
    """XxxLiteral (narrow str alias) rejects integer values."""
    test_code = '''
import calculator_capnp

def use_operator(op: calculator_capnp.CalculatorOperatorLiteral):
    pass

use_operator(0)
'''

    test_file = calculator_stubs / "test_literal_rejects_int.py"
    test_file.write_text(test_code)

    result = subprocess.run(["pyright", str(test_file)], capture_output=True, text=True)
    assert result.stdout.count("error:") > 0, f"Expected error: {result.stdout}"


def test_xxx_literal_rejects_invalid_str(calculator_stubs):
    """XxxLiteral rejects strings not in the enum."""
    test_code = '''
import calculator_capnp

def use_operator(op: calculator_capnp.CalculatorOperatorLiteral):
    pass

use_operator("invalid")
'''

    test_file = calculator_stubs / "test_literal_rejects_invalid.py"
    test_file.write_text(test_code)

    result = subprocess.run(["pyright", str(test_file)], capture_output=True, text=True)
    assert result.stdout.count("error:") > 0, f"Expected error for invalid literal: {result.stdout}"


def test_setter_union_accepts_all_forms(calculator_stubs):
    """The inline setter union (int | XxxLiteral | XxxEnum) accepts all valid forms."""
    test_code = '''
import calculator_capnp

# Function mirrors the setter signature shape
def use_operator(
    op: int
    | calculator_capnp.CalculatorOperatorLiteral
    | calculator_capnp.CalculatorOperatorEnum,
) -> None:
    pass

# Should accept int values
use_operator(0)
# Should accept enum module Literal[N] values
use_operator(calculator_capnp.Calculator.Operator.add)
# Should accept str literals
use_operator("add")
use_operator("subtract")
'''

    test_file = calculator_stubs / "test_setter_union_accepts.py"
    test_file.write_text(test_code)

    result = subprocess.run(["pyright", str(test_file)], capture_output=True, text=True)
    assert result.stdout.count("error:") == 0, f"Type checking failed: {result.stdout}"


def test_setter_union_rejects_invalid_str(calculator_stubs):
    """The inline setter union rejects strings not in the enum."""
    test_code = '''
import calculator_capnp

def use_operator(
    op: int
    | calculator_capnp.CalculatorOperatorLiteral
    | calculator_capnp.CalculatorOperatorEnum,
) -> None:
    pass

use_operator("invalid")
'''

    test_file = calculator_stubs / "test_setter_union_rejects_invalid.py"
    test_file.write_text(test_code)

    result = subprocess.run(["pyright", str(test_file)], capture_output=True, text=True)
    assert result.stdout.count("error:") > 0, f"Expected error: {result.stdout}"
