# Pass 219 RML12 Reciprocal Route Optimizer — Restart Record

## Authoritative lineage

- Base main: `1b66fc81216e8c9a1540c0cbbf2e5e6007438573`
- Working branch: `agent/pass219-recursive-manifold-learning-20260909`
- Merge target: `main`
- Pull request: `#414`
- Parent RML11 green restart seal: `ec5aa8ac857bcd811fda1d3e388078653a0badb6`
- RML12 implementation: `1fb77c2750360a0f8b40d4188d9b0cab1d8d370c`
- RML12 tests: `85a185886ce1a0cdd3de7fdf3f05f4da0e21628c`
- RML12 initial contract: `6d671aed9952867774834e512b570349db64fa04`
- RML12 workflow / validated head: `7806163e541fa400ffbe2ad65a28cde6418d2ca3`
- RML12 contract validation seal: `f7d8b056dde95c5c66cca91d4f0ca5fa3e4afb77`

The unrelated temporary ref `agent/pass219-recursive-manifold-learning-20260909-rml9-temp` remains non-authoritative and is not a restart source.

## Parent validation frozen

RML11 remains dependency-scoped validated:

- Workflow: `Pass 219 Phase Clifford Intertwiner`
- Run: `34432290908`
- Job: `102730127210`
- Result: `15 passed, 0 failed, 1 inherited pytest-config warning in 21.35s`
- Validated head: `01bfb38b10976ac23dabc418441035522e656bc1`
- RML11 contract seal: `4a269beb765892ae8a3957dde21db4d01118cd91`
- RML11 green restart seal: `ec5aa8ac857bcd811fda1d3e388078653a0badb6`

Inherited RML11 finite partition remains:

```text
290 total generator cases
18 complete Clifford lifts
272 residual-u72 partial lifts
10 full Cl_(0,8) intertwiners
8 Clifford chirality swaps
4 Hopf same-base cases
286 Hopf-base-moving cases
0 inverse failures
```

## RML12 purpose

RML12 turns the independent RML7 Hopf and RML11 Clifford classifications into exact route metadata on the existing reversible RML5 transition graph.

It introduces no new transition authority. The selector constructs and ranks already-valid reversible routes only.

## Exact route construction

For any two RML5-admissible balanced-chirality states:

1. align chiral sign sectors with the existing self-inverse `u^36` reciprocal-pair flips;
2. traverse primitive generators in fixed order `x,y,z,w`;
3. move each primitive together with its dependent product:

```text
x -> xy
y -> yx
z -> zw
w -> wz
```

4. require every intermediate state to retain admissible reciprocal quarter-turn geometry;
5. execute the reverse edge sequence and require exact source restoration.

The route therefore inherits the constructive RML5 connectivity proof rather than replacing it.

## Exact deterministic selector

RML12 may materialize two bounded endpoint-equivalent candidates:

```text
SHORTEST_SIGNED_Z72
COMPLEMENTARY_WRAP_Z72
```

The `u^36` antipodal tie retains the positive shortest representative, matching the frozen RML5 path convention.

Candidate selection uses the exact lexicographic integer vector:

```text
[
  move_count,
  total_phase_transport_units,
  residual_u72_edges,
  hopf_base_moving_edges,
  clifford_chirality_swap_edges,
  policy_preference
]
```

No weighted scalar objective is constructed. No gradient descent, loss function, probabilistic search, floating score, or scalarized topology cost is used.

RML12 does **not** claim this bounded lexicographic route is a global geodesic of the complete transition graph.

## Orthogonal per-edge metadata

Every route edge retains two independent classification axes.

Hopf:

```text
FIBER_PRESERVING_SAME_HOPF_BASE
BASE_MOVING_HOPF_TRANSPORT
```

Clifford:

```text
FULL_CL08_MODULE_INTERTWINER
EVEN_CLIFFORD_CHIRALITY_SECTOR_PRESERVING
ODD_CLIFFORD_CHIRALITY_SECTOR_SWAPPING
RESIDUAL_U72_PHASE_PRESERVED_NO_COMPLETE_CLIFFORD_LIFT
```

Neither classifier may execute a transition or mutate canonical state.

## RML12 validation frozen green

- Workflow: `Pass 219 Reciprocal Route Optimizer`
- Run: `34436975540`
- Job: `102743988934`
- Validated head: `7806163e541fa400ffbe2ad65a28cde6418d2ca3`
- Result: `14 passed, 0 failed, 1 inherited pytest-config warning in 38.66s`

Inherited Pass188 native validation succeeded inside the same gate:

```text
HHS_PASS_188_BOTT_RUNTIME_PASS
states=1259712
active=629856
collapse=629856
checksum=11e3bbf0214751c3
coordinate_drift_states=0
```

C11/static/shared build, native x86_64 step, checked no-float disassembly, five native Python tests, HTTP/WebSocket/visual surface smoke, and Python compile checks also remained green.

## Observed 290-case Hopf x Clifford route-metadata cross-tab

The exhaustive inherited generator-family audit produced:

```text
BASE_MOVING_HOPF_TRANSPORT | FULL_CL08_MODULE_INTERTWINER
    6

BASE_MOVING_HOPF_TRANSPORT | ODD_CLIFFORD_CHIRALITY_SECTOR_SWAPPING
    8

BASE_MOVING_HOPF_TRANSPORT | RESIDUAL_U72_PHASE_PRESERVED_NO_COMPLETE_CLIFFORD_LIFT
    272

FIBER_PRESERVING_SAME_HOPF_BASE | FULL_CL08_MODULE_INTERTWINER
    4
```

Total: `290`.

Exact inverse failures: `0`.

This preserves the prior aggregate results exactly:

```text
Hopf:     4 same-base + 286 base-moving
Clifford: 10 full intertwiners + 8 chirality swaps + 272 residual-u72
```

The audit therefore demonstrates that the Hopf and Clifford labels are genuinely orthogonal metadata rather than aliases.

## Authority boundary

RML12 adds no:

- canonical VM81 mutation authority;
- Hash72 mint authority;
- Hash216 persistence authority;
- floating-point canonical authority;
- scalar-projection substitution authority.

The route optimizer cannot commit canonical state. Its selected route remains a candidate for the existing single VM81 authority.

## Files added

- `hhs_runtime/pass219/reciprocal_route_optimizer.py`
- `tests/pass219/test_pass219_reciprocal_route_optimizer.py`
- `contracts/pass219/PASS_219_RML12_RECIPROCAL_ROUTE_OPTIMIZER_1_0.json`
- `.github/workflows/pass219-reciprocal-route-optimizer.yml`
- `docs/operations/restart/PASS_219_RML12_RECIPROCAL_ROUTE_OPTIMIZER_RESTART_20260910.md`

## Required next action

RML12 is complete, dependency-scoped validated, and restartable.

The next bounded successor should bind the selected RML12 route and its orthogonal Hopf/Clifford edge metadata into a versioned pre-hash witness packet for the existing Pass169/VM81 admission path, without changing frozen historical hashes or granting the optimizer commit authority.

Before implementation, inspect the exact current Pass169/I168 native Hash216 issuance and replay payload surfaces and version the ABI rather than modifying frozen evidence in place.
