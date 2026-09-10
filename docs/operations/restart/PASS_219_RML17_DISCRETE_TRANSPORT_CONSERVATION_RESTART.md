# Pass 219 RML17 discrete transport conservation restart

## Repository-visible restart state

- Base commit: `f41f7cec2e126d2d2114bc3463dfbc0e9b7518ec`
- Base lineage: `agent/pass219-recursive-manifold-learning-20260909`
- Working branch: `agent/pass219-rml17-discrete-transport-conservation-20260910`
- Merge target: `agent/pass219-recursive-manifold-learning-20260909`
- Pass: `219`
- Iteration: `RML17_DISCRETE_TRANSPORT_CONSERVATION`

## Contract

RML17 is additive and read-only above the validated RML16 deterministic
reciprocal-route cache. It does not modify the frozen RML12 selector, the
RML15 reverse/replay ABI, the RML16 signed-permutation Clifford successor, or
VM81/Hash72/Hash216 authority.

The executable operator contract is:

```text
Div_H(s) = 0
J(s,d) = -J(T_H(s,d), d^-1)
C(s) = 1 and T_H(s,d) = s' => C(s') = 1
nu_H L_H = 0
R^-1(R(s)) = s
Delta_loss = 0
```

Latency is explicitly excluded from the viscosity definition.

## Finite address surface

The validation manifold is exactly:

```text
4 x 64 x 72 x 81 = 1,492,992 addresses
```

RML17 exhaustively scans this address surface and requires:

- exact encode/decode bijection;
- zero signed local divergence;
- reciprocal operation/phase/cell neighborhood edges;
- exact antisymmetric edge flux;
- no authority expansion from the address-neighborhood witness.

Lane identity is retained by the address-neighborhood audit. RML17 does not
invent cross-lane transition authority.

## RML16 route surface

For selected RML16 routes, RML17 requires:

- every source and successor remains admitted;
- edge source/target hashes compose without gaps;
- every directed edge carries an exact inverse witness;
- every forward/reverse transport-flux pair sums to zero;
- only inherited exact reversible RML12 edge kinds participate;
- gradient, loss, floating-score, probabilistic, smoothing, averaging, and
  relaxation authority remain absent from the canonical route;
- RML15 retained edge ancestry restores the exact predecessor phase state;
- Hash216 cryptographic inversion is not used;
- structural information loss is zero;
- admitted multi-route compositions preserve all of the same properties.

## Files

- `hhs_runtime/pass219/discrete_transport_conservation.py`
- `tests/pass219/test_pass219_rml17_discrete_transport_conservation.py`
- `.github/workflows/pass219-rml17-discrete-transport-conservation.yml`
- `docs/operations/restart/PASS_219_RML17_DISCRETE_TRANSPORT_CONSERVATION_RESTART.md`

## Validation

Required dependency-scoped sequence:

```bash
make -C native_projects/hhs_pass219_rml15_route_reverse_replay validate

PYTHONPATH="$PWD" python -m pytest -q \
  tests/pass219/test_pass219_rml16_reciprocal_route_cache.py \
  tests/pass219/test_pass219_rml16_signed_permutation_clifford_integration.py

PYTHONPATH="$PWD" python -m pytest -q \
  tests/pass219/test_pass219_rml17_discrete_transport_conservation.py

PYTHONPATH="$PWD" python -m pytest -q \
  tests/pass219/test_pass219_reciprocal_route_optimizer.py \
  tests/pass219/test_pass219_rml15_route_reverse_replay.py \
  -k 'not complete_290_case_route_metadata_cross_tab_is_reversible'
```

## Validation state at initial checkpoint

- Static Python syntax compilation of the new module and tests: PASS.
- Standalone exhaustive address-manifold audit with the repository-independent
  constants/functions: PASS; 1,492,992 addresses, zero failures across
  bijection, divergence, reciprocal-neighbor, and reciprocal-flux gates.
- Exact repository dependency-scoped execution: pending GitHub Actions because
  the interactive container has no network-mounted repository checkout.
- Do not claim RML17 validated or merge-ready until exact-head CI is green.

## Next action

1. Run the exact-head RML17 workflow.
2. Repair forward only if the new contract or an impacted dependency fails.
3. When green, update this restart record with the run/commit evidence.
4. Merge the complete RML17 history into
   `agent/pass219-recursive-manifold-learning-20260909`.
5. Verify the resulting lineage head and preserve RML16/RML17 evidence.
