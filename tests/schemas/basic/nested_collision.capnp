@0xd7c679e775aabf82;

# Test schema for nested struct naming collision.
# Two parent structs each contain a nested struct named "ProcessState".
# The generated type aliases must not collide.

struct ManagerState {
  processes @0 :List(ProcessState);

  struct ProcessState {
    name @0 :Text;
    running @1 :Bool;
  }
}

struct DebugInfo {
  processes @0 :List(ProcessState);

  struct ProcessState {
    pid @0 :UInt32;
    memory @1 :UInt64;
  }
}
