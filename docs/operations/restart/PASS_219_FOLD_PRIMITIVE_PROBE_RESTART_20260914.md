# Pass 219 Fold Primitive Probe — Restart Record

## Base and branch

- Repository: `danonbrez/Holofractal_Harmonicode`
- Exact base: `main @ e94d00d242c25e915989be0013e0124e478dc005`
- Branch: `agent/pass219-fold-primitive-discovery-20260914`
- Validated implementation head: `95872a3305359537426304131473d9b1540a9da8`
- Pull request: `#455`

## Purpose

Isolate the candidate fold mechanics discussed across the existing RML4/RML5/SPI/I160 surfaces, test each independently, then compose them without rewriting the canonical HARMONICODE equation manifold.

The probe deliberately preserves the distinction between the full directional/non-commutative source relations and their weaker commutative scalar shadows.

## Implemented surfaces

- `hhs_runtime/pass219/fold_primitive_probe.py`
- `tests/pass219/test_pass219_fold_primitive_probe.py`
- `.github/workflows/pass219-fold-primitive-probe.yml`

## Focused validation

GitHub Actions:

- workflow: `Pass 219 Fold Primitive Probe`
- run: `34857187798`
- job: `104019667503`
- conclusion: `SUCCESS`
- focused test surface: 9 tests
- exact combined probe step: `SUCCESS`

An earlier workflow attempt failed before testing because the new workflow omitted the explicit pytest installation used by inherited Pass 219 workflows. Commit `95872a3305359537426304131473d9b1540a9da8` repaired only that workflow dependency; the subsequent targeted run is green.

## Individual results

The probe independently verifies:

1. typed pair inversions are exact order-2 operations for the tested role pairs `x<->y`, `z<->w`, `a<->b`, `p<->q`, `A<->B`, and `P+<->P-`;
2. directed ratios remain distinct and invert exactly: `A/B <-> B/A` and `xy/wz <-> zw/yx`;
3. the supplied orthogonal polarity pair `(P^2,2P^2)` / `(2P^2,P^2)` shares the exact fixed magnitude `c^2=3P^2` and closes in both orientations;
4. the ordered `pq` / `qp` roles remain distinct while the weaker integer projection retains `p+q=2P` and `pq=P^2-1` for the tested boundary construction;
5. the weaker I160 product shadow `AB=P^4` remains true without evaluating the full directional source `P^4=(A^2(A/B)*B^2(B/A))/P^2` as ordinary commutative arithmetic;
6. each validated RML5 chiral pair performs an exact self-inverse `u^36` half-turn while preserving admitted product geometry;
7. both chiral-pair half-turns compose and reverse without phase/sign loss;
8. `P -> -P` retains the exact `P^2` magnitude;
9. `u^36` is the deterministic shortest antipodal displacement in the existing `Z_72` route rule.

## Primitive classification exposed by the probe

The combined result separates **operations** from **invariants/selection witnesses**.

### Operational candidates

1. `TYPED_ORDER_2_PAIR_FLIP`
   - common structural signature across the typed polarity pairs;
2. `DIRECTED_RATIO_RECIPROCAL_FLIP`
   - preserves ordered forward/reverse ratio identity rather than collapsing it;
3. `SELF_INVERSE_U36_CHIRAL_PAIR_ROTATION`
   - existing executable RML5 phase realization of the reciprocal product-pair fold.

### Invariant / routing witnesses

4. `FIXED_ORTHOGONAL_MAGNITUDE_WITNESS`
   - `c^2=3P^2` remains shared through the `a^2:b^2` polarity inversion;
5. `COMMUTATIVE_SHADOW_INVARIANT`
   - weaker scalar witnesses such as `AB=P^4` remain useful for fiber membership without replacing directional source semantics;
6. `EXACT_SHORTEST_Z72_ANTIPODAL_DISPLACEMENT`
   - deterministic route-selection property, not a separate state mutation primitive.

Therefore the current evidence suggests a smaller mechanical core than the number of visible equations: three operation classes plus three invariant/selection classes. This is a probe result, not yet a canonical reduction of the full monolithic equation manifold.

## Authority boundary

This iteration is diagnostic/read-only:

- no canonical equation rewrite;
- no commutative collapse authority;
- no VM81 mutation;
- no Hash72 minting;
- no Hash216 persistence;
- no floating-point authority.

## Next exact cycle

Test whether the three operational candidate classes are algebraically independent or whether `DIRECTED_RATIO_RECIPROCAL_FLIP` and the typed pair inversion can be derived from one synchronized gyroscope fold operator. Then bind the same experiment to the full 5184 tensor shape and verify exact round-trip serialization across the `81x64`, `144x36`, and `72x72` views before granting any stronger primitive status.
