# Post-merge ingress delivery repair-forward — 2026-09-27

## Restart identity

- Repository: `danonbrez/Holofractal_Harmonicode`
- Repair branch: `agent/post-merge-repair-forward-20260927`
- Merge target: `main`
- Branch base: `541fe3f73f2c8227e5ae57de3c74f503fc53976a`
- Ingress repair merge verified in current main ancestry:
  - PR #612 merge: `182806dab03d067b045ae64d7942a7a996db821f`
  - PR #613 merge: `fdb4644e7870bf87b533711c800552f962fde9a1`
- Standard Frontend Ingress Compatibility repair run `36336686047`: **SUCCESS**
  - compile ingress surfaces: success
  - combined standard + legacy ingress contracts: success

Main continued advancing concurrently after this branch was cut. Latest main observed during this checkpoint was `f947411757575e2290df44738a4d07b07850ed12`.

## Verified merge state

`main` is a descendant of `fdb4644e7870bf87b533711c800552f962fde9a1`; the ingress repair is not merely present on an orphan branch.

The repaired ingress contract remains:

```text
legacy / Linux / browser representation
  -> compatibility translation
  -> reversible JSON-safe envelope where required
  -> workspace.ingress.register
  -> canonical modality adapter
  -> native HHS backend authority
```

## Concrete failures found after merge

### 1. Pass 217 Current Main Integration

Run `36336918974`, job `108669419057`:

```text
2 failed, 85 passed
assert 29 == 24
```

The five new compatibility ingress API surfaces increased the validated API-route inventory from 24 to 29, while two Pass 217 tests still hard-coded the old count.

Repair:
- derive expected API-route count from `API_ROUTE_SURFACES`,
  `COMPATIBILITY_ALIAS_SURFACES`, and `SERVICE_ROUTE_BINDINGS`;
- do not freeze a stale numeric count.

Commit: `725fdcdfaf11fe6a44dba74d74ce41148576d162`.

### 2. Hash216 repository index red-noise race

Run `36337033983`, job `108669742572` generated and validated the graph successfully, then refused to commit because main advanced while it was running:

```text
main advanced from 87b6ae... to 541fe3f...
refusing stale generated projection
```

Refusing the stale projection is correct. Marking that safe no-op as a failed workflow is not.

Repair:
- retain the exact-head guard;
- retain refusal to push stale generated state;
- exit successfully with an explicit notice when a newer main already exists.

Commit: `e0c12000effb7c10eff895154f864ca77bda1614`.

### 3. Production workflows target a retired host

Latest failing deployment runs before this repair:

- DigitalOcean Exact Main `36337529153`;
- Pass 220 Ubuntu Application VM Production `36337529166`.

The earlier diagnostic runs showed the workflows connecting to `165.227.220.193` and receiving:

```text
REMOTE HOST IDENTIFICATION HAS CHANGED
Host key verification failed
```

DigitalOcean account state now exposes exactly one active production droplet:

```text
name: hhs-production-04
id: 603583798
region: nyc3
image: Ubuntu 24.04 LTS x86_64
public IPv4: 159.65.178.254
status: active
tag: github-deploy-key-bound
```

The retired `165.227.220.193` fallback was therefore an obsolete deployment target, not a reason to disable strict host verification.

Repair:
- production Runtime OS workflow pins `159.65.178.254`;
- production Application VM workflow pins `159.65.178.254`;
- real Ubuntu guest workflow pins `159.65.178.254`;
- mobile-control deployment contract now requires the active address and rejects the retired one;
- Application VM deployment receipt now derives its public OpenAPI URL from the actual pinned production host rather than embedding the retired address.

Commits:
- `8699b341d202811a1af1539b8726c203679d9df9`
- `45535e3073d1351731197395200ad0ae3075eac9`
- `f53e23b6abf2854eebd81a381db1dbfa65dcd8a0`
- `059f2cb95ef54ee81ff3cd31959dd05a2864dfb1`
- `bc95f3694d6318a2e3dc2bed64f7f2030c4daf47`
- `3bc94f4209742ddff049ec73c1c2621a1af3f2b1`
- `e0918dd63feaa805fe556550f1de52a4d5f36ccd`

## SSH trust boundary

Strict host verification remains mandatory.

This repair **does not** introduce `ssh-keyscan`, TOFU, disabled host checking, or a blind trust refresh.

DigitalOcean currently lists the GitHub deployment keys and the active droplet carries the `github-deploy-key-bound` tag, but the private GitHub Actions secret `HHS_DIGITALOCEAN_KNOWN_HOSTS` cannot be read or rewritten through the available repository connector.

Therefore the next exact-main run has two legitimate outcomes:

1. the secret already contains the audited `159.65.178.254` host entry and deployment proceeds; or
2. the workflow fails closed at the pinned-host check, proving that the secret must be rotated out-of-band to the audited host key for `hhs-production-04`.

No source change should bypass that condition.

## Regression guard

`tests/test_hhs_guarded_auto_update_contract_v1.py` now verifies:

- active production host is version-pinned in all three production workflows;
- hidden `HHS_DIGITALOCEAN_HOST` variables cannot silently redirect those workflows;
- the retired production address is absent from the exact-main workflow;
- mobile deployment validation rejects the retired address;
- stale Hash216 generation remains non-promoting but is a successful no-op.

Commit: `273047ef2ffe7b6d4f4b91754fd84f58bb001ccc`.

## Next closure sequence

1. Open PR and integrate current main drift.
2. Run dependency-scoped PR validation.
3. Repair any concrete test/compile failure.
4. Merge once restartable and mergeable; do not wait on unrelated slow CI.
5. Verify exact main ancestry.
6. Observe the first exact-main production run against `hhs-production-04`.
7. If strict host verification reports that `HHS_DIGITALOCEAN_KNOWN_HOSTS` lacks the audited current host entry, rotate that secret rather than weakening SSH verification.
