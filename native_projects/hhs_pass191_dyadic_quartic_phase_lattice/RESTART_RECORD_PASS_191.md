# Pass 191 restart record

Base commit: `992b4e92a54d4656d66af4edfab7e03922addca6`

Branch: `agent/pass191-dyadic-quartic-phase-lattice`

Merge target: `main`

Draft pull request: `#124`

Deployment acceptance: DigitalOcean/self-hosted runtime is authoritative. Vercel status is external and excluded from Pass 191 acceptance.

## Implemented authority path

```text
exact manifold source and typed nesting witnesses
    -> Pass 189 81 x 64 x 243 x 41 contextual address authority
    -> 51,648,192-state native streaming epoch
    -> exact Delta, cubic, idempotent, AB=P^4, Lo Shu, and modulus witnesses
    -> deterministic top-16 residual frontier
    -> Pass 186 x86_64 Q144 noncommutative projection
    -> Pass 175 Hash216 VM5184 x G243 hydration
    -> Pass 174 singleton VM81 admission
    -> singular Hash72 commit stream and deterministic replay
    -> PROVED, FALSIFIED, or OBSTRUCTED outcome
```

## Implemented files

- `src/hhs_pass191_manifold_scan.c`: strict C11 streaming traversal of the complete Pass 189 contextual fabric with bounded memory, exact residual ranking, deterministic checksum, and continuation cursor.
- `hhs_pass191_manifold_kernel_v1.py`: exact source identity, non-destructive depth membranes, ordered operator identities, Lo Shu reduction, candidate certificates, outer-envelope witnesses, and committed-scan verification.
- `hhs_pass191_integrated_manifold_engine_v2.py`: complete epoch execution followed by VM81/Hash216 hydration of the retained frontier.
- `hhs_pass191_runner_v4.py`: deterministic evidence generation, completion receipt, replay validation, and dependency-scoped legacy evidence retention.
- `Makefile`: Pass 186 ABI build, Pass 189-backed scanner build, scanner smoke, tests, full epoch, evidence replay, bundle validation, and sandbox-drift check.
- `.github/workflows/pass191-dyadic-quartic-phase-lattice.yml`: installs `requirements-core.txt`, including the Pass 174 authenticated-snapshot dependency, before validation.

## Exact manifold relations

Canonical inherited constants:

```text
b^2=2
c^2=3
u^72=1
xy=1
A=B=P^2
```

The nested matrix reduction is exact:

```text
((b^2(c^2+b^2))-(c^2-b^2))/sqrt(c^4) = 3
((c^2b^6)-c^2)/3 = 7
((b^6-xy)(b^4+c^2))/7 = 7

[[b^4, c^4, c^2-u^72],
 [c^2, 5/u^72, nested],
 [2c^2+b^2, 2/b^2, b^2c^2]]
=
[[4,9,2],[3,5,7],[8,1,6]]
```

Every row, column, and diagonal sums to 15. Every scanned state checks `A*B=P^4`, `AB/P^2=P^2`, and `sqrt(AB)=P^2` exactly.

The contextual search evaluates:

```text
Delta = P^2-pq
t^3-t
m^2-m
residual_1 = (t^3-t)-Delta
residual_2 = Delta-(m^2-m)
```

Exact residuals are preserved. The global modulus `1,259,713` is recorded only as an outer witness and never destructively replaces an interior value.

## Formal decision state

The finite contextual-epoch proposition is `PROVED` only when every address in the selected interval is visited with zero coordinate drift and all exact kernel checks succeed.

The Riemann-hypothesis transfer remains formally `OBSTRUCTED` in `CURRENT_REGISTERED_RULE_GRAPH` until either:

1. an exact registered rule proves `ZETA_ZERO(sigma,t) => 2*sigma-1=0`; or
2. an exact nontrivial off-axis zeta-zero certificate proves `ZETA_ZERO(sigma,t)` with `2*sigma-1!=0`.

This obstruction is a scoped decision certificate. It does not weaken or bypass the complete finite manifold search.

## Validation command

```bash
make -C native_projects/hhs_pass191_dyadic_quartic_phase_lattice validate
```

The command performs:

1. Pass 186 exhaustive `1,259,712`-state roundtrip and no-float disassembly validation.
2. Strict Pass 191 scanner compilation against the inherited Pass 189 ABI.
3. Dependency-scoped runtime bootstrap, smoke, and regression validation.
4. Pass 191 unit and integration tests.
5. One complete `51,648,192`-state contextual epoch.
6. Hash72 artifact verification without repeating the complete epoch.
7. Release-bundle and sandbox-drift validation.

## Repository-visible continuation state

The generated integrated artifact stores:

- epoch number;
- scan start/end and completed cursor;
- exact state count and exact-chain-hit count;
- deterministic FNV-1a checksum;
- top-16 ordered residual frontier;
- candidate Hash72 identities;
- next epoch number;
- VM81/Hash216 hydration receipt;
- theorem decision and missing bridge.

## Restart rule

Resume from the latest head of `agent/pass191-dyadic-quartic-phase-lattice`. Inspect the newest `Pass 191 Dyadic Quartic Phase Lattice` workflow run, repair only the failing dependency scope, and rerun the Pass 191 gate. When the final generated-evidence head passes, mark PR #124 ready, merge it to `main`, and verify the same Pass 191 workflow on the merged main commit. Do not use Vercel status as an acceptance gate.
