# Pass 219B I6 — Pass-Enforcement Correction

## Status

This document records the repair-forward correction applied after Pass 219B I6 candidate heads were rejected by repository workflow enforcement.

The failures are treated as pass-system constraint violations, not as generic runner errors.

## Violation identified

The rejected I6 candidate had incorrectly attempted to widen inherited `HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1` semantics in place. It modified frozen UQCEL 1.8/Pass 219 1.15 surfaces and shadowed/replaced an inherited public implementation symbol.

That violated the cumulative pass rules:

```text
later pass = additive extension
not reinterpretation of inherited ABI
not replacement of inherited public semantics
not a second mutation authority
```

Pass 219 1.8 also explicitly registers UQCEL as a quantization projection downstream of the native UCE and requires `FULL_SYMBOLIC_V1` to remain `UNSUPPORTED_DOMAIN` while its registered residual classes remain unresolved in that transport profile.

## Repair

The current I6 design restores the inherited files and semantics exactly:

```text
hhs_runtime/include/hhs_runtime_uqcel_1_8.h
hhs_runtime/c/hhs_runtime_uqcel_1_8_validate.inc
hhs_runtime/c/hhs_runtime_uqcel_1_8_receipt.inc
tests/pass219/test_pass219_monolithic_uqcel_residual_boundary_1_15.py
```

I6 now introduces a separate versioned structural projection:

```text
PI-UCE-N-D-HYDRATION-I6-v1
```

which binds:

```text
N global constraint source identity
D phase-quantization source identity
Pass-129 exact zero-sum family
inherited UQCEL integer/symmetric quantization subprojection
Pass-219 ordered phase and hydration coordinate
Pass-219 trinary gate
Pass-219B I1 phase-origin projection
Pass-219B I5 exact phase-locality witness
```

The I6 projection does not reinterpret projection equality as native identity and does not claim to serialize every term of the complete native global constraint Tensor.

## Required legacy probe

Every successful I6 structural witness must also prove that inherited UQCEL V1 still behaves as registered:

```text
profile = FULL_SYMBOLIC_V1
status = UNSUPPORTED_DOMAIN
decision = UNSUPPORTED_DOMAIN
reject_reason = FULL_SYMBOLIC_RESIDUAL
residual_mask = HHS_UQCEL_RESIDUAL_FULL_SOURCE
```

This probe is a preservation proof, not a statement that the global `N/D^4=D^4` relation is undefined.

## Authority

The I6 projection has:

```text
canonical_mutation_authority = 0
canonical_persistence_authority = 0
canonical_hash72_authority = 0
```

It exports no commit/admit/persist/Hash72 authority. Canonical state mutation remains in the inherited authorized VM81/kernel graph.

## Workflow enforcement

The I6 workflow now contains an explicit byte-semantic guard:

```text
git diff --exit-code <canonical-I5-main> -- <frozen UQCEL 1.8/1.15 files>
```

Any future mutation of those inherited surfaces rejects the I6 candidate before its new projection tests are considered.

The workflow failure state is therefore interpreted as:

```text
PASS_CONSTRAINT_VIOLATION_DETECTED
```

until the offending candidate state is repaired and the full exact/synthetic gate succeeds.
