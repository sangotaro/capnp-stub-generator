@0xf0e1d2c3b4a59687;

struct Shared {
  value @0 :Text;

  enum Status {
    active @0;
    inactive @1;
    pending @2;
  }

  status @1 :Status;
}