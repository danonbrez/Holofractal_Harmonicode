# Pass 220 I068 — D-Wave Dual-Rail Candidate Bridge Restart Record

Date: 2026-10-03

## Repository state

```text
repository: danonbrez/Holofractal_Harmonicode
base main: 88989c7d4b0a85f3209f2ab964f430d37ae17b24
branch: pass220/i068-dwave-dual-rail-candidate-bridge-20261003
merge target: main
delivery mode: append-only / repair-forward / no rebase / no squash / no force-push
```

The branch was created directly from the listed authoritative main commit.

## Implemented files

```text
hhs_runtime/hhs_pass220_i068_dwave_dual_rail_candidate_bridge_v1.py
tests/pass220/test_hhs_pass220_i068_dwave_dual_rail_candidate_bridge_v1.py
formal/wolfram/pass220_i068_dwave_dual_rail_candidate_bridge_v1.wl
evidence/pass220/i068_dwave_dual_rail_wolfram_20261003_v1.output.json
contracts/pass220/PASS_220_I068_DWAVE_DUAL_RAIL_CANDIDATE_BRIDGE_V1.json
docs/pass220/PASS_220_I068_DWAVE_DUAL_RAIL_CANDIDATE_BRIDGE.md
.github/workflows/pass220-i068-dwave-dual-rail-candidate-bridge.yml
docs/operations/restart/PASS_220_I068_DWAVE_DUAL_RAIL_CANDIDATE_BRIDGE_RESTART_20261003.md
```

## Repository-visible source checkpoints

```text
1bc3d655cfe060317c061d338591cb2c0eb02d7f
feat(pass220): add D-Wave dual-rail candidate bridge

73d18f96bc3da80755db618d57a29bf37af3b0b2
test(pass220): validate D-Wave dual-rail candidate bridge

c80e64b101cc8d3943235be52c329c5a549677e1
formal(pass220): prove I068 dual-rail ordered mapping

4fc57da81c0e3e9bb4508db8d5772e81281ae212
evidence(pass220): freeze I068 Wolfram proof

89582f4f2f2223f5f7944e2217e1e2984a3a0a8a
contract(pass220): bind I068 dual-rail candidate authority

476e3b7cfd05b5b6359a011b0f0acb7140441e86
docs(pass220): document I068 D-Wave candidate bridge

ca8c6cde46c1777a4a74071a772e6ed469192895
ci(pass220): validate I068 dual-rail bridge
```

## Implemented capability

I068 provides an exact, candidate-only ingress membrane for D-Wave Leap QCDL
dual-rail simulator results.

The runtime:

1. accepts explicit measurement register order and ordered control/target identity;
2. preserves `0`, `1`, and detected-erasure `*` outcomes;
3. rejects post-selected-only result ingestion;
4. rejects floating-point values from candidate identity;
5. binds exact shot, clean-shot, erasure-shot, per-register erasure, and exact
   reduced-yield evidence;
6. maps ordered `{0,1,*} x {0,1,*}` pairs bijectively to the inherited I027
   outcome range `0..8`;
7. creates a three-lane 216-glyph candidate receipt from configuration, result,
   and authority-boundary Hash72 lanes;
8. exposes a lazy optional `LeapQCDLSimulator` live runner without storing
   credentials or requiring the SDK for core validation;
9. compares a candidate nine-bin histogram against a caller-supplied canonical
   VM81 histogram and canonical receipt without granting mutation authority.

## Authority boundary

The external simulator remains non-authoritative:

```text
candidate_only                         = true
canonical_vm81_mutation_authority      = false
canonical_hash72_commit_authority      = false
canonical_hash216_commit_authority     = false
canonical_persistence_authority        = false
external_egress_authority              = false
floating_point_authority               = false
```

Raw erasure provenance is mandatory. `get_counts(post_select=False)` is the
documented ingestion route encoded by the bridge. A post-selected-only transcript
fails closed.

## Validation completed

Dependency-scoped local validation before repository checkpoint:

```text
python -m pytest -q tests/pass220/test_hhs_pass220_i068_dwave_dual_rail_candidate_bridge_v1.py
12 passed in 0.07s

python -m hhs_runtime.hhs_pass220_i068_dwave_dual_rail_candidate_bridge_v1
status = PASS
checks = 8 / 8
```

Connected Wolfram Language kernel:

```text
schema = HHS_PASS_220_I068_DWAVE_DUAL_RAIL_WOLFRAM_V1
status = PASS
checks = 7 / 7
failed = {}
outcomes = {0,1,2,3,4,5,6,7,8}
shots = 5
erased = 2
clean = 3
exact yield = 3/5
```

## Validation remaining

```text
branch GitHub Actions workflow
pull-request dependency-scoped workflow
merge verification on authoritative main
repository-index refresh/verification if triggered by main automation
```

## Environment state

No D-Wave beta credential is required for the core bridge, tests, self-test, or
formal proof. Live Leap execution is optional and lazy-loaded. No token, profile,
or simulator response has been persisted.

## Next action

1. run the I068 branch workflow;
2. repair forward only if dependency-scoped validation identifies divergence;
3. open the I068 pull request against `main`;
4. require green dependency-scoped checks;
5. merge using a normal merge commit;
6. verify the merged I068 lineage on the latest authoritative `main`;
7. leave the external D-Wave surface candidate-only unless a later separately
   proven canonical admission pass explicitly changes that authority boundary.
