# Pass 219 — Normalized Optimization Control v1

**Date:** 2026-09-16  
**Status:** normative optimization-control contract  
**Baseline evidence:** `docs/pass219/HHS_QINFO_THROUGHPUT_NORMALIZATION_V1_EVIDENCE.md`  
**Baseline main:** `e8accdc0d86d436ddbe9491ad6e96d9c76b6954d`

## 1. Purpose

Every optimization that claims to improve Lane 5, VM5184 routing, hydration, vector-store search, replay, or workload execution SHALL be evaluated against the same exact mathematical and runner-normalized control surface.

The control is deliberately multi-axis. An optimization may not trade away exactness, replay, authority separation, or contradiction rejection merely to improve elapsed time.

## 2. Frozen mathematical control

The following quantities are invariant controls:

```text
D_HHS = 72^72
H_addr = log2(D_HHS)
       = 444.23460010384649012933840792848557726141327470771727270562838225391814480238763 bits-equivalent
binary embedding width = 445 bits
native address width = 56 bytes
qudit factorization = 72 qudits × 72 levels
VM5184 factorization = 5184^36 = 72^72
route full-manifold address slots = 4
```

Derived information-density controls:

```text
Gamma_basis = R_c * H_addr
Gamma_route = R_c * 4 * H_addr
Gamma_qudit = R_c * 72
Gamma_VM5184 = R_c * 36
```

where `R_c` is the measured deterministic candidate-shot rate on the named runner.

These formulas SHALL remain unchanged across optimization comparisons unless a new versioned contract explicitly changes the route schema or logical manifold.

## 3. Frozen reference observation

The first executed runner-normalized reference is:

```text
runner label: ubuntu-24.04
CPU: Intel(R) Xeon(R) 6973P-C
logical CPUs: 4
active benchmark threads: 1
candidate count: 1,000,000
elapsed_ns: 3,090,640,549
R_ref: 323,557 candidates/s floor
Gamma_basis_ref: 143,735,214.50580025880677834725411700792197109492460487760481500247693099317782613 bits-equivalent/s
Gamma_route_ref: 574,940,858.02320103522711338901646803168788437969841951041926000990772397271130453 bits-equivalent/s
Gamma_qudit_ref: 23,296,104 coordinate-symbols/s
Gamma_VM5184_ref: 11,648,052 block-coordinates/s
stream state: 568 bytes
materialized intermediate states: 0
```

These values define normalization index `1.0` for the historical reference observation. They are not universal hardware constants.

## 4. Optimization record

Every optimization benchmark SHALL emit:

```text
exact commit/tree
runner/image/kernel/compiler identity
CPU model and logical CPU count
active benchmark thread count
candidate count and elapsed_ns
candidate-shot rate
Gamma_basis
Gamma_route
Gamma_qudit
Gamma_VM5184
working-set / stream-state bytes where applicable
materialized intermediate-state count
replay equality result
negative-control result
authority flags
```

## 5. Normalized indices

Against the frozen historical observation:

```text
I_shot  = R_candidate / R_ref
I_basis = Gamma_basis_candidate / Gamma_basis_ref
I_route = Gamma_route_candidate / Gamma_route_ref
I_qudit = Gamma_qudit_candidate / Gamma_qudit_ref
I_vm    = Gamma_VM5184_candidate / Gamma_VM5184_ref
```

Because the logical formulas are fixed, these performance indices are equal when the route schema/manifold are unchanged; they are recorded separately so later schema versions remain comparable.

For memory:

```text
I_memory = control_auxiliary_bytes / candidate_auxiliary_bytes
```

where values greater than `1` indicate reduced candidate-side auxiliary memory.

For exact work:

```text
I_work = control_exact_work_units / candidate_exact_work_units
```

where values greater than `1` indicate reduced exact work for the same verified result.

## 6. Paired same-runner control

Historical normalization is required for long-term tracking. Optimization acceptance SHOULD additionally use a paired control and candidate on the same fresh runner image whenever the modified surface can be benchmarked both ways.

The paired comparison SHALL use the same:

```text
runner class
compiler and optimization flags
thread count
candidate/workload corpus
input bytes
logical manifold/schema
measurement protocol
```

A performance claim SHALL NOT compare different hardware profiles without reporting both profiles and the normalization basis.

## 7. Acceptance membrane

An optimization may be accepted only if all exact conditions pass:

```text
replay_fidelity == 1
negative_controls_fail_closed == true
materialized_intermediate_states == 0 where Lane 5 direct routing requires it
canonical_vm81_mutation_authority == false for Lane 5
canonical_hash72_authority == false for Lane 5
canonical_hash216_authority == false for Lane 5
requires_signed_environmental_vm81_admission == true
```

Performance is then evaluated separately.

Default paired-run policy:

```text
primary performance ratio >= 0.95 of paired control
AND at least one declared optimization objective improves measurably
AND no exact authority/correctness invariant regresses
```

The `0.95` floor is a CI jitter budget, not a mathematical HHS constant. A pass-specific benchmark MAY tighten it or require statistically stronger repeated measurements.

## 8. Optimization objectives

Permitted optimization objectives include:

- higher deterministic-shot rate;
- higher normalized information-density rate;
- lower candidate auxiliary memory;
- fewer exact work units for identical output;
- lower serialized byte volume;
- lower persistence/index lookup work;
- lower end-to-end latency;
- better parallel utilization;
- higher cache reuse;
- lower hydration cost;
- reduced route depth once exact primitive-depth instrumentation exists.

An optimization SHALL declare which objective it targets before its result is interpreted.

## 9. Legacy/von Neumann control

For practical comparison, HHS SHALL also report ordinary memory/work controls such as:

```text
explicit coordinate materialization bytes = represented_items * 56
minimal 64-bit ID materialization bytes = represented_items * 8
fixed route-batch bytes = candidate_count * sizeof(HHSExactPass219Lane5UnboundedWorkloadRouteV1)
Lane 5 stream reducer bytes = sizeof(HHSExactPass219Lane5UnboundedWorkloadStreamV1)
```

These are ordinary von Neumann storage/work quantities and make the effect of zero intermediate materialization understandable without invoking quantum hardware.

## 10. Control rule

The normalized mathematical equations and the executed reference observation SHALL be treated as the optimization control until superseded by a versioned contract plus a new sealed evidence record.
