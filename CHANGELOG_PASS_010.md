# Changelog — Pass 010

## Focus
Persistence/data export containment.

## Added
- `hhs_runtime/hhs_persistence_guard_v1.py`
- `persistence.guard_self_test` guarded service registry entry
- `make persistence-guard`
- `tests/test_hhs_persistence_guard_v1.py`

## Behavior
- JSON artifact writes now have a canonical egress wrapper.
- JSON artifact reads now have a canonical ingress wrapper.
- Text exports now have a canonical egress wrapper.
- Generic database/file persistence propagation can be committed through the same IO gateway.

## Non-goals
- No kernel semantics changed.
- No Hash72 alphabet or invariant definitions changed.
- No broad deletion/renaming of persistence modules performed.
