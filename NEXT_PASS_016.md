# NEXT PASS 016 — Hash72 Witness Propagation Across Runtime Contracts

## Priority
Propagate kernel-backed Hash72 witness metadata into runtime contracts, API envelopes, IO records, and semantic/vector records.

## Goal
The receipt digest should not merely be kernel-derived internally; downstream consumers should be able to inspect the associated Digital DNA witness where relevant.

## Candidate Work
- Add optional `hash72_kernel_witness` field to canonical contract objects.
- Attach witness metadata to unified ledger entries, not only ledger tips.
- Update IO gateway and API response contracts to expose kernel authority metadata.
- Audit remaining authoritative `hash72_digest` imports.
