# Production recovery restart checkpoint — 2026-10-02 17:00Z

## Purpose

Freeze the current HHS/DigitalOcean recovery state after the 2026-10-01 production outage investigation and the 2026-10-02 repair-forward sequence.

This checkpoint is intentionally **non-mutating** with respect to production. It records the exact repository, workflow, receipt, service, and DigitalOcean state required to resume safely without repeating rollback experiments or weakening recovery proofs.

## Repository identity

Repository:

`danonbrez/Holofractal_Harmonicode`

Authoritative `main` at checkpoint creation:

`9def04c7c48e7398b5b74d3a3b645f06df3d1971`

Title:

`docs: refresh Hash216 repository dependency index`

Its parent is:

`70f2af11467fe10a3c848062bf8e197c2fbaa077`

The index-only commits after production repairs do not replace the already-merged repair semantics below.

### Restart branch

Read-only incident/recovery evidence branch:

`incident/network-ab-probe-20261002`

Pre-checkpoint branch head:

`fc095a8e28f70cf1c1e0e5bdcc04bb70576f1234`

Open draft PR:

`#680`

The branch currently owns:

- `.github/workflows/incident-network-ab-probe.yml`
- this restart checkpoint under `docs/operations/restart/`

PR #680 is an incident evidence surface. **Do not merge it to main.**

### Separate one-shot dispatcher branch

Branch:

`incident/exact-main-dispatch-20261002b`

Current head:

`d6ce098fd9723cb6928a1b2e790706d8a2e2eb88`

Open draft PR:

`#687`

It contains temporary workflow-dispatch/locator files. GitHub evaluates cumulative PR changed paths, so modifying this PR can retrigger the dispatcher. **Do not change PR #687 unless another Exact-Main dispatch is intentionally authorized.**

## Merged production repairs

The following repair sequence is already authoritative on `main`:

1. PR #679 — Lane 5 host ingress zero-bypass
   - merge: `b7d3de22193932d219c7db95d49293a6012822a9`
   - public HHS ingress is designed as nginx -> systemd-owned Lane 5 socket `:8715` -> private `:8080/:8720`;
   - first paint no longer bypasses Lane 5;
   - SSH remains independent;
   - Exact-Main/Application-VM/I044 share the production mutation lock.

2. PR #682 — bind Lane 5 ingress socket during promotion
   - merge: `deb60572fd45e922ae4d9a29a79bcb1bcf2ab93b`
   - fixed `LANE5_INGRESS_SOCKET: unbound variable`.

3. PR #683 — preserve exact candidate identity during moving-main deployments
   - merge: `36edd1d0139f86b26ac0f60e589c2649db46272b`
   - transient `HHS_EXACT_CANDIDATE_SHA` pins one synchronous promotion;
   - pinned SHA must remain on current `origin/main` ancestry;
   - pin is removed before the periodic updater timer resumes.

4. Candidate validator interpreter repair
   - `6fa5c1e0d8b773c91539154d3e53bfc1564cfc71`
   - candidate validation uses the production HHS venv with `pytest`, not bare `/usr/bin/python3`.

5. Host-ledger recovery/import repairs
   - `c04c6948b815474224e3bafc488cded22c15ebc9`
   - `66067d0f7c6aa5ffa06bf6c69cbd717748e86b50`
   - `e4ca14b108f68055413cf364183ec636af263fd3`
   - ledger recovery imports are explicitly rooted at the repository and have an installed-normalizer regression.

## DigitalOcean state

Production Droplet:

- name: `hhs-production-04`
- Droplet ID: `603583798`
- status: `active`
- public IPv4: `159.65.178.254`
- private IPv4: `10.108.0.5`
- region: NYC3

Current DigitalOcean connector metadata reports the Droplet image as:

- image ID: `247312238`
- image name: `hhs-production-04 2026-09-27:16`

A separate pre-rollback safety snapshot was previously created:

- image ID: `247938260`
- name: `hhs-production-04-pre-rollback-20261001`

Do **not** assume image `247938260` is the active disk state merely because it exists. Current Droplet metadata explicitly reports `247312238`.

Temporary clean/tagged network-control Droplets used for A/B diagnosis were deleted after the tests.

## Network diagnosis

Earlier external A/B testing established:

- fresh NYC3 Ubuntu control: SSH/22 reachable from GitHub;
- fresh control carrying `hhs-production` tag: SSH/22 reachable;
- production public `159.65.178.254`: previously timed out on 22/80/443/8080/8720;
- production private `10.108.0.5`: valid VPC route existed but application ports were not serving.

This ruled out:

- account-wide DigitalOcean network failure;
- GitHub-hosted-runner egress failure;
- a blocking policy attached merely through the `hhs-production` tag.

Later recovery runs proved production SSH became reachable again. Current incident inspection at 2026-10-02 16:59Z authenticated successfully over pinned SSH.

Therefore **do not resume the old "all ports unreachable" diagnosis as the current state**. The current blocker is inside recovery/promotion state.

## Live production checkout and service state

Read-only PR #680 inspection run:

`37037607834`

At 2026-10-02 16:59Z:

- live checkout HEAD:
  `cf2764c24e85ff4980d599f528218f1328b81627`
- tracked drift:
  `M data/runtime/hhs_filesystem_ledger.json`
- ledger diff scale:
  `13681` changed lines reported, with `6884 insertions` and `6797 deletions`;
- drift includes migration to:
  `HHS_FILESYSTEM_HASH72_APPEND_CHAIN_AUTHORITY_V1`;
- `hhs.service` reported `inactive`;
- no active `:8080` listener was printed by the read-only inspection.

The current service unit remains configured for:

`ExecStart=/opt/hhs/venv/bin/python -m uvicorn hhs_backend.production_visual_server:app --host 127.0.0.1 --port 8080 --workers 1`

with warm-boot verification in `ExecStartPre`.

## Guarded updater receipt lineage

Receipt log:

`/var/lib/hhs-guarded-update/receipts.jsonl`

Read-only inspection found:

- receipt count: `8`
- promoted receipt count: **`0`**

Relevant sequence:

1. `deb60572...` — candidate REJECTED
2. `63b40bbb...` — candidate REJECTED
3. `36edd1d...` — candidate REJECTED
4. `36edd1d...` — candidate REJECTED
5. `6fa5c1e0...` — candidate REJECTED
6. `bb09c1cb...` — candidate REJECTED
7. `fd5a1e12...` — candidate REJECTED
8. `d29d23e1750f9ac33c824e539b127e416b8c22b6` — **VALIDATED**

The validated record states:

- previous/rollback SHA:
  `cf2764c24e85ff4980d599f528218f1328b81627`
- candidate SHA:
  `d29d23e1750f9ac33c824e539b127e416b8c22b6`
- bundle SHA:
  `d29d23e1750f9ac33c824e539b127e416b8c22b6`
- phase: `validation`
- outcome: `VALIDATED`
- detail: `candidate and prebuilt Runtime OS bundle passed isolated validation`

No receipt proves `cf2764c...` as a prior `PROMOTED` boundary because this production boundary predates the current receipt history.

## Current recovery-verifier blocker

Current verifier:

`deployment/digitalocean/guarded_auto_update/verify-recovery-state.py`

For a latest `validation/VALIDATED` receipt it requires an earlier same-boundary:

`phase=promotion && outcome=PROMOTED && candidate_sha==previous_sha`

The live receipt history does not contain such a row for `cf2764c...`.

Therefore the current safe recovery path fails with:

`HHS_RECOVERY_VALIDATED_PREVIOUS_SHA_NOT_PROVEN_PROMOTED`

This is a provenance migration problem between a pre-receipt production boundary and the newer guarded-update receipt system. **Do not bypass or delete this check.**

## Warm-boot boundary evidence

Rollback warm manifest exists:

`/var/lib/hhs/warm-boot/releases/cf2764c24e85ff4980d599f528218f1328b81627.json`

Observed:

- schema: `HHS_PASS_220_I046_WARM_HYDRATED_VM_BOOT_V1`
- repository SHA: `cf2764c24e85ff4980d599f528218f1328b81627`
- manifest SHA-256:
  `b8589e9bac9510db9c6366108503c1f43ffd8f30acce48e73f77468dfe1f5c92`

Candidate `d29d23e...` also has a warm manifest:

- manifest SHA-256:
  `a19b606cdc9a47431e264e3f4bbb5665a28b2998aa4daab3f75c1462b8766623`

However, the read-only live verification:

```bash
HHS_DISABLE_C_AUTOBUILD=1 \
  /opt/hhs/venv/bin/python \
  /opt/hhs/app/deployment/digitalocean/warm_boot_manifest.py verify \
  --repo-root /opt/hhs/app \
  --manifest-root /var/lib/hhs/warm-boot/releases
```

currently fails with:

`HHS_WARM_BOOT_RUNTIME_OS_IDENTITY_MISMATCH`

Therefore the rollback manifest cannot currently be used as a valid substitute proof for a historical `PROMOTED` receipt.

## Exact-Main runs already investigated

Key live runs:

- `36998140903`
  - SSH recovered;
  - failed on unbound `LANE5_INGRESS_SOCKET`.

- `37019262541`
  - socket binding repaired;
  - failed because moving `origin/main` invalidated the sealed candidate identity.

- `37020198297`
  - exact candidate pin worked;
  - failed candidate validation because bare system Python lacked `pytest`.

- `37025100415`
  - candidate `d29d23e...` subsequently reached `VALIDATED`.

- `37036629539`
  - Exact-Main deployment contract PASS;
  - live deploy failed before installer/promotion completion;
  - current evidence identifies rollback/recovery-boundary verification as the active blocker.

Do not rerun old failed jobs as if their source were still authoritative; later repairs have superseded several of those failure causes.

## Validation already completed

Completed/green before this checkpoint:

- Lane 5 host-ingress native contract;
- I045 first-paint contract;
- I046 warm-boot contract in repository CI;
- Application-VM control plane;
- HTTPS closure contract;
- Exact-Main deployment contract;
- I044 shared production-lock/verify-only package contract;
- candidate-pin regression;
- production-venv validator regression;
- explicit-repository-root ledger recovery regressions;
- source-text integrity on the current incident evidence branch before the latest read-only probe.

Important distinction:

Repository tests for the warm-boot mechanism are green, while the **specific live rollback artifact** currently fails Runtime OS identity verification. Do not conflate those two facts.

## Commands/actions executed during this recovery stage

Representative live/read-only commands already exercised:

```bash
git -C /opt/hhs/app rev-parse HEAD
git -C /opt/hhs/app status --porcelain=v1 --untracked-files=normal
git -C /opt/hhs/app diff -- data/runtime/hhs_filesystem_ledger.json

systemctl is-active hhs.service
systemctl is-failed hhs.service
ss -H -ltnp 'sport = :8080'

python3 deployment/digitalocean/guarded_auto_update/verify-recovery-state.py \
  --receipt-log /var/lib/hhs-guarded-update/receipts.jsonl \
  --current-head <live-head> \
  --repository-root /opt/hhs/app \
  --branch main

HHS_DISABLE_C_AUTOBUILD=1 \
  /opt/hhs/venv/bin/python \
  /opt/hhs/app/deployment/digitalocean/warm_boot_manifest.py verify \
  --repo-root /opt/hhs/app \
  --manifest-root /var/lib/hhs/warm-boot/releases
```

Exact-Main has also exercised:

- pinned SSH preflight;
- shared production mutation lock;
- isolated bootstrap worktrees;
- host-drift preservation/reconciliation;
- exact Runtime OS bundle transfer;
- transient candidate pinning;
- candidate validation using the HHS venv.

## Active blocker

The current blocking condition is:

```text
live rollback boundary = cf2764c...
receipt history has 0 PROMOTED records
latest candidate d29d23e... is VALIDATED
recovery verifier requires proof that cf2764c... was promoted
rollback warm manifest exists
BUT live warm manifest verification fails:
HHS_WARM_BOOT_RUNTIME_OS_IDENTITY_MISMATCH
```

This must be resolved before another production promotion is authorized.

## Next action

**Read-only first. Do not dispatch Exact-Main yet.**

Inspect the rollback Runtime OS artifact identity:

1. Parse `cf2764c...` warm manifest and record:
   - `artifacts.runtime_os.root`
   - `artifacts.runtime_os.index`
   - `artifacts.runtime_os.index_sha256`
   - `artifacts.native_runtime.path`
   - `artifacts.native_runtime.sha256`.

2. Inspect without mutation:
   - `readlink -f /var/lib/hhs/runtime-os/current`
   - existing Runtime OS release directories;
   - SHA-256 of the rollback manifest's referenced `index.html`;
   - SHA-256 of its referenced native runtime;
   - whether failed candidate attempts moved only the `current` symlink or actually replaced/deleted rollback artifacts.

3. If the original sealed rollback artifacts still exist and exactly match the manifest:
   - restore **only the authoritative reference/symlink needed for verification**, after dependency-scoped proof;
   - rerun warm-manifest verification;
   - then extend recovery classification only if the verified manifest can provide a typed legacy-boundary witness.

4. If rollback artifacts do not match or no longer exist:
   - do **not** synthesize a `PROMOTED` receipt;
   - preserve the mismatch evidence and choose a new recovery strategy from verified artifacts.

5. Only after rollback provenance closes:
   - rerun the guarded recovery verifier;
   - authorize one Exact-Main dispatch;
   - require a new `PROMOTED` receipt;
   - verify `hhs.service`, Lane 5 socket/service `:8715`, nginx zero-bypass, local `:8080`, and public HTTPS.

## Explicit do-not-repeat list

Until the blocker above is resolved:

- do not restore older DigitalOcean backups again;
- do not rebuild/delete the production Droplet;
- do not weaken `StrictHostKeyChecking`;
- do not bypass the recovery verifier;
- do not fabricate a historical `PROMOTED` receipt;
- do not overwrite the evolved filesystem ledger with the Git copy;
- do not modify PR #687 unless another deployment dispatch is intentionally wanted;
- do not delete the rollback/candidate warm manifests or guarded-update receipts.

## Restart instruction

On the next task, begin with:

> Continue production recovery from `docs/operations/restart/PRODUCTION_RECOVERY_CHECKPOINT_20261002_1700Z.md`. First perform the read-only rollback Runtime OS/native artifact identity inspection. Do not dispatch Exact-Main until `HHS_WARM_BOOT_RUNTIME_OS_IDENTITY_MISMATCH` is explained and rollback provenance is proven.

