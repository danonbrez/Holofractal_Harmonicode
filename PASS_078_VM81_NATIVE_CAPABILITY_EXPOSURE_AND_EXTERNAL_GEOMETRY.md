# Pass 078 — VM81 Native Capability Exposure and External Plastic/E6 Geometry

## Canonical boundary

Pass 078 freezes the existing native kernel sources, inventories their complete function surface, distinguishes callable ABI symbols from internal native capabilities, binds higher-level lanes to the 81-cell VM81 manifold, and derives plastic-constant/E6 geometry outside the kernel.

The exposure layer is not a semantic replacement. Direct ABI entries call existing exported symbols. Internal static functions are exposed only as witnessed capability descriptors until a future ABI-safe adapter can invoke them without changing frozen semantics.

## Authority chain

`higher-level lane → mandatory VM81 binding → exposed native ABI or capability descriptor → frozen native semantics → receipt/provenance`

External geometry follows:

`witnessed VM81 state → exact plastic recurrence / E6 coordinate derivation → candidate wave propagation → native VM81 admission required`

## Implemented invariants

- Kernel source hashes are recorded and verified without mutation.
- Every detected native C function is catalogued.
- Direct-call exposure is limited to symbols actually defined with external linkage and declared in an ABI header.
- Internal static capabilities are not falsely advertised as directly callable.
- Nine higher-level lanes cover all 81 cells exactly once.
- Every cell records row, column, subgrid, Lo Shu slot, reciprocal, rotation, and phase relations.
- Plastic scaling uses the exact integer recurrence associated with `p³ = p + 1`; no floating-point approximation is introduced by Pass 078.
- Wave outputs remain candidates and cannot self-authorize canonical state.
