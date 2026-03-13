@0xc508eb99637af185;

# Test case: Consumer references Producer.Item, but Consumer appears
# before Producer in the schema. This ensures the generator handles
# out-of-order nested type references correctly.

struct Consumer {
  item @0 :Producer.Item;
}

struct Producer {
  name @0 :Text;

  struct Item {
    value @0 :Text;
    count @1 :UInt32;
  }

  items @1 :List(Item);
}
