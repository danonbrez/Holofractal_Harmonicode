# NEXT PASS 015 — Hash72 Receipt Chain Binding

## Goal
Make the existing receipt/ledger authority consume the C-native `u^72` Hash72 Digital DNA ring state rather than treating Hash72 as a static digest/string projection.

## Required Work
1. Add a Python authority adapter that converts canonical payload projections into ring rotations.
2. Emit rotation trace receipts for every Hash72 transition.
3. Block ledger propagation unless `hhs_hash72_dna_validate()` passes.
4. Add Golay partition witness scaffolding: `24 + 12 + 12 + 12 + 12`.
5. Add Lo Shu/tensor projection witness metadata to receipts.
6. Update IO gateway / service dispatch / semantic memory guards to include Hash72 ring witness summaries.

## Non-Negotiable Rule
No data may enter, propagate, or exit as Hash72-authorized unless it is backed by either:

- a receipt-chain record, or
- a validated vector-cache record carrying a receipt-backed Hash72 ring witness.
