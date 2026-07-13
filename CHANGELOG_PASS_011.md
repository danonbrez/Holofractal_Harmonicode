# CHANGELOG — PASS 011

## Focus
Canonical Runtime Contract.

Pass 011 converts the guarded runtime surfaces from merely receipt-protected to schema-standardized. The objective is to prevent schema/interface drift across backend routes, services, IO records, receipts, vector cache records, persistence records, events, and future GUI/API consumers.

## Added
- `hhs_runtime/hhs_runtime_contract_v1.py`
  - `HHSExecutionRequest`
  - `HHSRuntimePacket`
  - `HHSReceiptContract`
  - `HHSServiceDescriptorContract`
  - `HHSEventContract`
  - `HHSVectorCacheEntryContract`
  - `HHSPersistenceRecordContract`
  - `validate_contract()` / `assert_contract()`
  - `runtime_contract_self_test()`
- `make runtime-contract`
- `tests/test_hhs_runtime_contract_v1.py`

## Wired
- Guarded service registry now exposes canonical service descriptor contracts.
- Guarded service dispatch now emits canonical execution request and runtime packet contracts.
- Canonical IO gateway records now carry a runtime packet contract projection.
- Default service registry now includes `runtime_contract.self_test`.

## Preserved
- No change to kernel semantics.
- No change to Hash72 meaning.
- No bypass around authority gate, IO gateway, service registry, or receipt chain.
- Existing response schemas remain backward-compatible while gaining contract fields.
