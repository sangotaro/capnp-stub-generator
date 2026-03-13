"""Tests for out-of-order nested type references.

When a struct references a nested type from another struct that appears later
in the schema (e.g., Consumer references Producer.Item but Consumer is defined
first), the generator must ensure the parent struct is generated before
attempting to generate the nested type.
"""

from conftest import read_stub_file


def test_nested_type_from_later_struct_is_generated(basic_stubs):
    """Producer.Item should be fully generated even though Consumer appears first."""
    stub_file = basic_stubs / "parent_order_capnp.pyi"
    content = stub_file.read_text()

    # _ItemStructModule should exist inside _ProducerStructModule
    assert "_ItemStructModule" in content, "Item struct module should be generated"
    assert "type ItemReader = _ProducerStructModule._ItemStructModule.Reader" in content
    assert "type ItemBuilder = _ProducerStructModule._ItemStructModule.Builder" in content


def test_consumer_references_use_flat_aliases(basic_stubs):
    """Consumer.item field should use flat ItemReader/ItemBuilder aliases."""
    stub_file = basic_stubs / "parent_order_capnp.pyi"
    lines = read_stub_file(stub_file)

    # Consumer Reader should have: def item(self) -> ItemReader: ...
    assert any("def item(self) -> ItemReader" in line for line in lines), (
        "Consumer Reader should reference ItemReader"
    )

    # Consumer Builder should have: def item(self) -> ItemBuilder: ...
    # and setter: def item(self, value: ItemBuilder | ItemReader | dict[str, Any]) -> None: ...
    assert any("def item(self) -> ItemBuilder" in line for line in lines), (
        "Consumer Builder getter should reference ItemBuilder"
    )
    assert any("def item(self, value: ItemBuilder | ItemReader" in line for line in lines), (
        "Consumer Builder setter should reference ItemBuilder | ItemReader"
    )


def test_no_undefined_type_references(basic_stubs):
    """No 'Action'-style undefined references should appear."""
    stub_file = basic_stubs / "parent_order_capnp.pyi"
    content = stub_file.read_text()

    # Should NOT have bare "Item.Reader" or "Item.Builder" (variable path)
    # Should use flat aliases instead
    assert "Item.Reader" not in content, "Should use ItemReader flat alias, not Item.Reader"
    assert "Item.Builder" not in content, "Should use ItemBuilder flat alias, not Item.Builder"
