# Pass 219 RML16 Clifford Generator Cache Candidate Result — 2026-09-10

## Scope

This record freezes the completed candidate experiment for process-local reuse of the immutable exact `Cl_(0,8)` generator tuple. The candidate was measured only after the RML16 cold-route profiler identified RML11 Clifford lift/classification as the dominant residual.

## Candidate validation

- Branch: `agent/pass219-rml16-cold-route-profile-20260910`
- Candidate benchmark commit: `18da51091a56cc26b0186f3779361ed17384d749`
- Candidate workflow/tested head: `9894af4b225519f35e6ed484f7d52211a9d52250`
- Workflow run: `34497417758`
- Job: `102939302172`
- Conclusion: `success`
- Artifact ID: `10160414458`
- Artifact ZIP SHA256: `b5a413a2cfa35d5034923528bd232b3276b51abb3e44e38f1ad2d4f77666d26d`

Validation evidence:

- inherited RML15 native route stack: PASS;
- RML10/RML11/RML12 reference semantics: 20 passed, 1 intentionally deselected expensive cross-tab;
- semantic identity gate: PASS;
- impacted production route semantics including RML16 route-cache behavior: 41 passed;
- candidate cache: 1 miss, 192 hits, maxsize 1, currsize 1;
- exact output equality required for 32 lifts + 32 classifiers + 32 edges + 8 shortest plans + 8 full bundles = 112 composed equality checks;
- no public RML10/RML11/RML12 ABI change;
- no VM81 mutation, Hash72 mint, Hash216 persistence, floating-point canonical, scalar projection substitution, or timing authority.

## Measured effect

| Surface | Reference median ns | Candidate median ns | Reduction |
|---|---:|---:|---:|
| RML11 Clifford classifier | 21,717,116 | 21,027,750 | 3.17% |
| RML11 Clifford lift | 21,002,253 | 20,301,630 | 3.33% |
| RML12 coupled edge | 27,381,055 | 26,764,215 | 2.25% |
| RML12 shortest plan | 113,627,411 | 110,603,625 | 2.66% |
| RML12 full bundle | 217,586,979 | 212,895,254 | 2.15% |

## Decision

The candidate is **validated but not integrated**.

The immutable generator reconstruction is real overhead, but its 2–3.3% end-to-end effect is too small to explain the measured ~20.75 ms RML11 lift residual. Integrating this optimization before identifying the dominant internal operation would violate the RML16 profile-first optimization rule.

The result therefore narrows the search: the remaining dominant cost is inside the repeated exact matrix work, classification checks, matrix hashing, or receipt construction performed after invariant generator acquisition.

## Next exact action

Continue from the dedicated internal profiler introduced at:

- benchmark commit: `67d32d47bcb206ec0c5150141b7dacbe6a089ec8`;
- workflow/test head: `2860388b739bdfc1b26ecfbf27065a04016d4a93`;
- workflow: `Pass 219 RML16 Clifford Lift Internal Profile`;
- run: `34497930227`;
- job: `102941035512`.

That profiler instruments the frozen production RML11 helper boundaries without changing production source and requires exact output equality for every profiled lift. Optimize only the measured dominant exclusive helper after that run is green.
