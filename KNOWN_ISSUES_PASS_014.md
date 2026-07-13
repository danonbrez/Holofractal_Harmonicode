# KNOWN ISSUES PASS 014

1. Existing receipt chain still primarily consumes deterministic Hash72 projections; next pass should bind ledger propagation to `HHSHash72RingState`.
2. Tensor projection is deterministic and reversible as a carrier projection, but requires further refinement against the full 81-cell/toroidal outer-cell mapping spec.
3. Golay `24 + 4x12` partition is documented but not yet encoded as a C ABI validation layer.
4. `hhs_reverse_state` requires the rotation profile/key schedule; final digest alone remains intentionally non-reversible.
5. Existing C warnings in VM81 demo initializer code remain non-blocking.
