# CHANGELOG PASS 015 — Hash72 Kernel-Backed Ledger Authority

## Summary
Pass 015 moves the unified Hash72 ledger authority from the prior deterministic projection shell into the C-backed `u^72` Digital DNA ring bridge introduced in Pass 014.

## Added
- `hhs_runtime/hhs_hash72_kernel_authority_v1.py`
- `HHSHash72KernelWitness`
- `make_hash72_kernel_witness()`
- `hash72_kernel_digest()`
- `hash72_kernel_authority_self_test()`
- `hash72.kernel_authority_self_test` guarded service
- `make hash72-kernel-authority`
- `tests/test_hhs_hash72_kernel_authority_v1.py`

## Changed
- `hhs_unified_hash72_ledger_v1` now derives entry and ledger digests through the C `u^72` Digital DNA ring bridge.
- Ledger files now declare `hash72_authority: HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1`.
- Whole-ledger hash projection now uses ordered entry-hash summaries rather than repeatedly refeeding all nested payloads.
- Legacy ledgers without kernel authority metadata are rebuilt before accepting new propagation.

## Preserved
- Existing C kernel ABI from Pass 014.
- Existing service registry dispatch semantics.
- Existing HHS-M001..M007 Foundational Standards path.
- Four-invariant authority gate semantics.
