# Known Issues — Pass 076

1. The interpreter intentionally admits only `PURE_SYMBOLIC` effects. Audited mutation and external-provider effects remain unavailable.
2. Repair execution is restricted to exact replacement operations over committed product-local source artifacts. Structural AST patching is deferred.
3. Interpreter test execution produces evidence candidates; canonical test-record admission still occurs through the unified mutation API.
4. Compiler and emulator operations remain typed unavailable for Passes 077 and 078.
5. The exhaustive repository-wide test suite was not run. This is recorded as `TYPED_UNRESOLVED_NEVER_ZERO`; bounded dedicated and inherited chains were used.
