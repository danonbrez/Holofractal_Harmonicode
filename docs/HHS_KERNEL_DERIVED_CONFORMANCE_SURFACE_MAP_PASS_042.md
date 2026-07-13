# HHS Kernel-Derived Conformance Surface Map — Pass 042

Pass 042 makes active runtime reachability depend on invariant derivation.

A surface is canonical only when this chain is complete:

```text
kernel invariant
  -> derived doctrine
  -> runtime surface
  -> contract schema
  -> witness type
  -> validator
  -> admission/rejection code
  -> service/API/control-flow binding
```

Importability, registration, or test coverage alone is not sufficient for runtime canonicity.
