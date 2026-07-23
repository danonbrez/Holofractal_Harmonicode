# Known Issues — Pass 078

1. Fifteen functions declared in `hhs_runtime/include/HARMONICODE_VM_RUNTIME.h` have no matching definition in the scanned frozen translation units. They are retained as typed unresolved ABI declarations and are not falsely exposed as callable.
2. Internal static native functions are capability descriptors, not external calls. An ABI-safe future pass may add adapters outside the frozen source boundary only if it can do so without redefining native semantics.
3. The external E6 coordinate projection is a deterministic six-coordinate construction over VM81 relations; Pass 078 does not claim that it replaces or mutates any pre-existing kernel lattice semantics.
4. Repository-wide exhaustive tests were not run; the bounded Pass 077–078 chain was executed.
