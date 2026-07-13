# INTEGRATION REPORT PASS 017 — GUI Runtime Contract Surface

## Objective
Ensure GUI/runtime transport no longer treats websocket/API payloads as loose legacy data when canonical contract metadata is available.

## Result
The frontend now has a dedicated contract-envelope adapter and representative runtime transport surfaces consume it.

## Boundary Rule
Frontend transport is not authority. It may validate and display contract state, but authoritative Hash72/u^72 validation remains server/kernel-side.

## Wired Surfaces
- `RuntimeKernelBridge.ts`
- `RuntimeSocketManager.ts`

## Contract Metadata Surfaced
- `contract_hash72`
- `payload_hash72`
- `contract_valid`
- `contract_reasons`
- kernel witness schema checks for `HHS_HASH72_KERNEL_WITNESS_V1`

## Remaining Migration Targets
- Command bar calculator/agent routes still target non-runtime endpoints and should be routed through guarded runtime services or explicit adapter routes in a later pass.
- GUI visual components should display receipt/kernel witness lineage in dedicated inspector panels.
