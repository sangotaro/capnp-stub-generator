"""Tests that list field setters accept Sequence of element types."""

from __future__ import annotations

import subprocess


def test_struct_list_setter_accepts_sequence(basic_stubs):
    """Struct list field setter should accept Sequence[Reader | Builder | dict]."""
    stub_file = basic_stubs / "mid_features_capnp.pyi"
    content = stub_file.read_text()

    # nestedList: List(Nested) setter should accept Sequence of element types
    assert (
        "def nestedList(self, value: NestedListBuilder | NestedListReader "
        "| Sequence[MidFeatureContainerNestedReader | MidFeatureContainerNestedBuilder | dict[str, typing.Any]]"
    ) in content


def test_enum_list_setter_accepts_sequence(basic_stubs):
    """Enum list field setter should accept Sequence[EnumType]."""
    stub_file = basic_stubs / "mid_features_capnp.pyi"
    content = stub_file.read_text()

    # enumList: List(TopEnum) setter should accept Sequence of enum values
    assert (
        "def enumList(self, value: TopEnumEnumListBuilder | TopEnumEnumListReader "
        "| Sequence[TopEnumEnum]"
    ) in content


def test_primitive_list_setter_accepts_sequence(basic_stubs):
    """Primitive list field setter should accept Sequence[primitive_type]."""
    stub_file = basic_stubs / "mid_features_capnp.pyi"
    content = stub_file.read_text()

    # nums: List(Int32) setter should accept Sequence[int]
    assert (
        "def nums(self, value: Int32ListBuilder | Int32ListReader "
        "| Sequence[int]"
    ) in content


def test_list_setter_no_bare_dict(basic_stubs):
    """List field setters should NOT have bare dict[str, typing.Any] (only inside Sequence)."""
    stub_file = basic_stubs / "mid_features_capnp.pyi"
    content = stub_file.read_text()

    # Find all setter lines for list fields
    for line in content.splitlines():
        if ".setter" in line:
            continue
        if "ListBuilder |" in line and "ListReader |" in line and "def " in line:
            # This is a list field setter - should not end with "| dict[str, typing.Any])"
            assert "ListReader | dict[str, typing.Any])" not in line, (
                f"List field setter should not have bare dict[str, typing.Any]: {line.strip()}"
            )


def test_list_setter_type_checking(basic_stubs):
    """Test that pyright accepts list assignment to list fields."""
    test_code = """\
from typing import Any
import mid_features_capnp

def test_list_assignments():
    builder = mid_features_capnp.MidFeatureContainer.new_message()

    # Assign Python list of dicts to struct list field
    builder.nestedList = [{"flag": True, "count": 1}]

    # Assign Python list of enum values to enum list field
    builder.enumList = ["alpha", "gamma"]

    # Assign Python list of ints to primitive list field (via union)
    builder.choice.nums = [1, 2, 3]
"""

    test_file = basic_stubs / "test_list_setter_usage.py"
    test_file.write_text(test_code)

    result = subprocess.run(
        ["pyright", str(test_file)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)

    assert result.returncode == 0, f"Type checking failed: {result.stdout}"
