# HHS Control-Flow Transition Audit — Pass 041

## Purpose

Pass 041 upgrades control-flow auditing so IF/LOOP gates cannot lock based on scalar proxy audits when the branch result or loop step is a richer state transition.

Earlier behavior could audit a scalar-compatible projection while storing richer post-state information. Pass 041 makes the full transition itself the audited object.

## Invariant

```text
control-flow lock
→ full pre-state hash
→ full post-state hash
→ result hash
→ condition/variant hash
→ transition root
→ compressed validation residue chain
```

Not:

```text
control-flow lock
→ scalar proxy audit only
→ rich state transition accepted implicitly
```

## Transition Audit Fields

```text
schema
version
gate
label
transition_index
decision
pre_state_hash72
post_state_hash72
result_hash72
condition_hash72
variant_hash72
transition_root_hash72
scalar_proxy_used
rich_transition_audited
residue_chain_root_hash72
state_machine
hash_authority
```

## Rejection Codes

```text
REJECT_CONTROL_FLOW_SCALAR_PROXY_ONLY
REJECT_CONTROL_FLOW_FLOAT_STATE
REJECT_CONTROL_FLOW_RAW_TRANSITION_CACHE
REJECT_CONTROL_FLOW_TRANSITION_HASH_MISMATCH
REJECT_CONTROL_FLOW_MISSING_RESIDUE_CHAIN
```

## Integration

`hhs_control_flow_gates_v1.py` now calls `make_control_flow_transition_audit()` for:

```text
audited_if selected branch result
audited_loop each committed step
```

Each accepted transition is compressed into the Pass 040 validation-residue previous/state/receipt chain.

## Service

```text
control_flow.transition_audit_self_test
```

## Make target

```text
make control-flow-transition-audit
```
