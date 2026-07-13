# CHANGELOG PASS 014 — Hash72 u^72 Digital DNA Kernel

## Summary
Pass 014 upgrades Hash72 from a deterministic receipt projection shell toward the kernel-native `u^72` Digital DNA state machine required by the HHS mathematical foundation.

## Added
- `HHSHash72RingState` C ABI structure.
- `hhs_hash72_ring_init` for zero-sum closure initialization.
- `hhs_hash72_ring_rotate(index, delta)` with toroidal compensatory propagation to `index + 1 mod 72`.
- `hhs_hash72_dna_validate()` enforcing `sum(V(S_i)) == 0 mod 72`.
- `hhs_hash72_tensor_project()` projecting the 72-position ring into an 81-cell tensor carrier.
- `hhs_hash72_reverse_state()` using the rotation profile as the reversible key schedule.
- `HHSHash72RingBridge` Python ctypes wrapper.
- `make hash72-u72`.
- Targeted tests for ring initialization, rotation, reverse reconstruction, and tensor projection.

## Preserved
- Existing runtime receipt chain behavior.
- Existing ABI runtime/receipt/tensor structs.
- Existing VM81 build and verification path.
- Existing Python/C runtime bridge behavior.

## Architectural Correction
Hash72 is now represented in the C ABI as a positional state machine:

```text
positions[72] + rotation_profile[72] -> Digital DNA projection
```

The 72-symbol string is a projection of the ring state, not the sole identity object.
