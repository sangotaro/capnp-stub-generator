"""TypedDict field types should be narrowed (no Builder/Reader) for invariance friendliness.

Setters still accept the wide union (Builder | Reader | XxxDict | ...), but the TypedDict
fields themselves use only the python-native input form. This keeps consumer-side TypedDict
mirror patterns (where users declare their own TypedDict with native types like list[float])
compatible under pyright's TypedDict invariance.
"""

from __future__ import annotations


def _extract_typed_dict_block(content: str, class_name: str) -> str:
    """Return the body of `class {class_name}(typing.TypedDict, total=False):` until the next blank line / next class."""
    lines = content.splitlines()
    in_block = False
    body: list[str] = []
    header = f"class {class_name}(typing.TypedDict, total=False):"
    for line in lines:
        if line.startswith(header):
            in_block = True
            continue
        if in_block:
            if line.startswith("class ") or (line and not line.startswith(" ") and not line.startswith("\t")):
                break
            body.append(line)
    return "\n".join(body)


def test_struct_field_in_typed_dict_is_dict_only(basic_stubs):
    """Non-list struct field in TypedDict should be XxxDict, not Builder|Reader|XxxDict."""
    stub_file = basic_stubs / "mid_features_capnp.pyi"
    block = _extract_typed_dict_block(stub_file.read_text(), "MidFeatureContainerDict")
    assert "nested: ReadOnly[MidFeatureContainerNestedDict]" in block, (
        f"Struct field should narrow to ReadOnly[XxxDict]. Block:\n{block}"
    )
    assert "Builder" not in block, f"TypedDict block must not contain Builder. Block:\n{block}"
    assert "Reader" not in block, f"TypedDict block must not contain Reader. Block:\n{block}"


def test_struct_list_field_in_typed_dict_is_sequence_of_dict(basic_stubs):
    """Struct list field in TypedDict should be Sequence[XxxDict]."""
    stub_file = basic_stubs / "mid_features_capnp.pyi"
    block = _extract_typed_dict_block(stub_file.read_text(), "MidFeatureContainerDict")
    assert "nestedList: ReadOnly[Sequence[MidFeatureContainerNestedDict]]" in block, (
        f"Struct list should narrow to ReadOnly[Sequence[XxxDict]]. Block:\n{block}"
    )


def test_primitive_list_field_in_typed_dict_is_sequence_of_primitive(basic_stubs):
    """Primitive list field in TypedDict should be Sequence[primitive]."""
    stub_file = basic_stubs / "mid_features_capnp.pyi"
    block = _extract_typed_dict_block(
        stub_file.read_text(), "MidFeatureContainerMidFeatureContainerChoiceDict"
    )
    assert "nums: ReadOnly[Sequence[int]]" in block, (
        f"Primitive list should narrow to ReadOnly[Sequence[primitive]]. Block:\n{block}"
    )
    assert "ListBuilder" not in block
    assert "ListReader" not in block


def test_enum_list_field_in_typed_dict_is_sequence_of_literal(basic_stubs):
    """Enum list field in TypedDict should be Sequence[XxxLiteral]."""
    stub_file = basic_stubs / "mid_features_capnp.pyi"
    block = _extract_typed_dict_block(stub_file.read_text(), "MidFeatureContainerDict")
    assert "enumList: ReadOnly[Sequence[TopEnumLiteral]]" in block, (
        f"Enum list should narrow to ReadOnly[Sequence[XxxLiteral]]. Block:\n{block}"
    )
    # The wide setter-style union must not appear in TypedDict
    assert "int |" not in block, f"TypedDict block must not contain enum-int union. Block:\n{block}"
    assert "TopEnumEnum" not in block or "TopEnumEnumDict" in block  # Enum class type itself absent


def test_single_enum_field_in_typed_dict_is_literal(basic_stubs):
    """Single enum field in TypedDict should be XxxLiteral, not XxxEnum class."""
    stub_file = basic_stubs / "mid_features_capnp.pyi"
    block = _extract_typed_dict_block(stub_file.read_text(), "MidFeatureContainerDict")
    assert "mode: ReadOnly[TopEnumLiteral]" in block, (
        f"Single enum should narrow to ReadOnly[XxxLiteral]. Block:\n{block}"
    )


def test_readonly_import_emitted_when_typed_dict_present(basic_stubs):
    """ReadOnly must be imported from typing_extensions when TypedDict is generated."""
    content = (basic_stubs / "mid_features_capnp.pyi").read_text()
    assert "from typing_extensions import ReadOnly" in content, (
        "ReadOnly import is required when TypedDict definitions are present"
    )


def test_setter_signature_unchanged_by_narrowing(basic_stubs):
    """Setter signatures must still accept the wide union (Builder | Reader | XxxDict | ...)."""
    content = (basic_stubs / "mid_features_capnp.pyi").read_text()
    # Struct setter still accepts Builder | Reader | XxxDict
    assert (
        "def nested(self, value: MidFeatureContainerNestedBuilder | "
        "MidFeatureContainerNestedReader | MidFeatureContainerNestedDict)"
    ) in content, "Struct setter signature must remain wide (Builder | Reader | XxxDict)"
    # Enum setter still accepts int | Literal | Enum
    assert "def mode(self, value: int | TopEnumLiteral | TopEnumEnum)" in content, (
        "Enum setter signature must remain wide (int | XxxLiteral | XxxEnum)"
    )
