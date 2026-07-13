# Changelog — Pass 040

## Added

- Validation residue compressor for u^72/Hash72 previous-state-receipt compression.
- HHFS carrier adapter execution records for read/write/extract/embed/repair/reconstruct/convert surfaces.
- HHFS reconstruction protocol with witnessed ECC repair and silent-repair rejection.
- Runtime services and Make targets for all new Pass 040 modules.
- Documentation for validation residue compression, carrier reconstruction, and invariant-derived adapter execution.

## Security / coherence impact

Pass 040 prevents validator expansion caches from persisting as unbounded memory artifacts. It also prevents carrier reconstruction from becoming a hidden repair lane by requiring adapter receipts, transformation records, and compressed validation residue chains.
