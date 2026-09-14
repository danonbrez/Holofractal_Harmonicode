# Pass 219 RML17 discrete transport conservation restart

## Repository-visible restart state

- Base commit: `f41f7cec2e126d2d2114bc3463dfbc0e9b7518ec`
- Base lineage: `agent/pass219-recursive-manifold-learning-20260909`
- Working branch: `agent/pass219-rml17-discrete-transport-conservation-20260910`
- Merge target: `agent/pass219-recursive-manifold-learning-20260909`
- Initial implementation commit: `37856b278dec0a71b587568977501e113b6240d5`
- Endpoint-identity repair commit: `904c01ac3340641c95b43271b6580dc2dc0f5def`
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
- internal generated edge SHA256 ancestry composes without gaps;
- internal ambient-state ancestry composes without gaps;
- every directed edge carries an exact inverse witness;
- every forward/reverse transport-flux pair sums to zero;
- only inherited exact reversible RML12 edge kinds participate;
- gradient, loss, floating-score, probabilistic, smoothing, averaging, and
  relaxation authority remain absent from the canonical route;
- RML15 retained edge ancestry restores the exact predecessor phase state;
- Hash216 cryptographic inversion is not used;
- structural information loss is zero;
- admitted multi-route compositions preserve all of the same properties.

RML17 preserves the inherited RML12 endpoint identity semantics. A generated
terminal transition state may have a transition-derived `state_id` and SHA256
that differ from the separately supplied target receipt while still being the
same exact phase state. Therefore:

- generated edge ancestry is checked by SHA256 and ambient index internally;
- terminal route equality is checked by the inherited exact phase geometry /
  ambient identity;
- the supplied target SHA256 remains independently bound to the route plan;
- RML15 independently validates and reverses the supplied target receipt.

The repair does not weaken receipt identity; it removes an invalid equality
between two deliberately distinct identity layers.

## Files

- `hhs_runtime/pass219/discrete_transport_conservation.py`
- `tests/pass219/test_pass219_rml17_discrete_transport_conservation.py`
- `.github/workflows/pass219-rml17-discrete-transport-conservation.yml`
- `docs/operations/restart/PASS_219_RML17_DISCRETE_TRANSPORT_CONSERVATION_RESTART.md`
- `evidence/pass219_rml17/PASS_219_RML17_DISCRETE_TRANSPORT_CONSERVATION_RECEIPT.json`

## Validation commands

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

## Validation evidence

### Initial exact-head run

Dedicated workflow run `34507670537` at implementation head
`37856b278dec0a71b587568977501e113b6240d5` correctly exposed an RML17-only
endpoint identity defect after inherited validation was green:

- native RML13 -> RML14 -> RML15 rebuild/ABI: PASS;
- RML16 cache + signed-permutation integration: 10 passed;
- RML17: 10 passed, 3 failed;
- impacted trailing route regression: skipped after the RML17 failure.

The failed predicate incorrectly required a transition-generated terminal
state SHA256 to equal the separately supplied target state SHA256. RML12 exact
route equality is phase/sign/ambient equality, while generated transition
state identity and supplied target receipt identity are intentionally distinct.

### Repair-forward run

Dedicated workflow run `34508463313` at exact repair head
`904c01ac3340641c95b43271b6580dc2dc0f5def`: **PASS**.

Validated results:

- native RML13 -> RML14 -> RML15 rebuild and ABI checks: PASS;
- RML16 cache + exact signed-permutation successor: **10 passed**;
- RML17 discrete transport contract: **13 passed**;
- exhaustive `4 x 64 x 72 x 81` address scan participated in the RML17 test
  gate and completed green across all **1,492,992 addresses**;
- impacted RML12 optimizer + RML15 reverse/replay regression:
  **12 passed, 1 intentionally deselected** (the known expensive 290-case
  cross-tab excluded from this dependency-scoped run).

The RML17 green gate therefore covers the five required executable invariants:
zero discrete divergence, reciprocal edge balance, admission preservation,
zero canonical diffusion, and composed reverse closure with zero structural
information loss.

The pytest configuration emitted the inherited unknown `asyncio_mode` warning;
it did not affect test results. GitHub Actions also emitted the platform Node
runtime deprecation warning for `actions/checkout@v4` / `actions/setup-python@v5`;
it did not affect validation.

## Validation remaining

The implementation and dependency-scoped validation are complete at
`904c01ac3340641c95b43271b6580dc2dc0f5def`. This restart/evidence update is a
documentation-only checkpoint above that validated implementation. If a final
exact-head workflow is triggered by this documentation commit, it is follow-up
confirmation rather than a reason to reopen the already-green implementation.

## Next action

1. Open the integration PR from
   `agent/pass219-rml17-discrete-transport-conservation-20260910` into
   `agent/pass219-recursive-manifold-learning-20260909`.
2. Preserve the two-commit implementation/repair history; do not squash it.
3. Merge once branch integration requirements permit.
4. Verify the canonical RML lineage head contains RML16 unchanged plus the
   additive RML17 conservation membrane and evidence.
