# Production recovery checkpoint — 2026-10-02 Lane 5 / rollback boundary

## Scope

Restartable incident checkpoint for the DigitalOcean production recovery and
Lane 5 host-ingress repair.

Repository:
`danonbrez/Holofractal_Harmonicode`

Production:
- droplet: `hhs-production-04`
- droplet ID: `603583798`
- public IPv4: `159.65.178.254`
- private IPv4: `10.108.0.5`
- preserved pre-rollback safety snapshot image: `247938260`
- account billing/status previously verified active with no outstanding balance.

Do not delete the preserved production snapshot until production has been
successfully promoted and verified end to end.

## Repository authority

Authoritative `main` has advanced through multiple repair and Hash216 index
refresh commits. At the time of this checkpoint, the latest observed main tip
was:

`70f2af11467fe10a3c848062bf8e197c2fbaa077`

Recent substantive production repairs already merged to main include:

1. PR #678 — production runner/resource/concurrency hardening.
2. PR #679 — Lane 5 host ingress zero-bypass membrane.
3. PR #682 — bind `LANE5_INGRESS_SOCKET` before strict-shell use.
4. PR #683 — transient exact candidate pin across harmless `main` drift.
5. `6fa5c1e0d8b773c91539154d3e53bfc1564cfc71` —
   run guarded candidate validation in the production HHS virtualenv.
6. later ledger-recovery repairs on main explicitly root ledger normalization at
   the repository and add installed-normalizer simulation coverage.

Hash216 repository dependency-index refresh commits may advance main after a
substantive repair. Exact-Main now pins the already-authorized dispatch SHA
transiently through the updater and proves that pin remains on current main
ancestry, so such index-only drift must not switch deployment candidates.

## Production mutation topology

All known workflows directly pinned to the production host are serialized by:

`/run/lock/hhs-production-mutation.lock`

This includes:
- DigitalOcean Production Exact Main;
- manual Application-VM production;
- manual I044 Real Ubuntu Guest integration.

Application-VM production no longer installs the desktop/NetworkManager stack.
I044 production runs in verify-only host-package mode and cannot apt-install
QEMU/cloud packages during the integration transaction.

## Lane 5 host-ingress invariant

Merged architecture:

```text
public 80/443
-> nginx
-> systemd-owned 127.0.0.1:8715 socket
-> hhs_backend.lane5_ingress_gateway
-> exact ordered-byte/provenance Lane 5 1.48 mediation
-> private 127.0.0.1:8080 or 127.0.0.1:8720
-> inherited signed environmental VM81 admission where canonical mutation occurs
```

Key properties:
- no direct public nginx proxy to `:8080` or `:8720`;
- first-paint HTML/assets no longer bypass Lane 5;
- `:8715` is systemd socket activated independently of `hhs.service`;
- backend failure should degrade to a Lane-5-mediated 503 instead of releasing
  the ingress socket;
- SSH/22 remains an independent recovery plane;
- semantic `lane5_zero_bypass_interposer=1` is not accepted as a substitute for
  host ingress ownership.

## Network diagnosis

A clean Ubuntu 24.04 control droplet in NYC3 with the same authorized SSH keys
was reachable on port 22 from GitHub-hosted runners.

A second clean control carrying the exact `hhs-production` tag was also
reachable on port 22.

Production public IP `159.65.178.254` initially timed out on
22/80/443/8080/8720 from GitHub.

Inside the same VPC, a clean control had a valid route to production private IP
`10.108.0.5`. The production private ports failed immediately while the public
IP timed out, proving the account/region and production tag were not the cause.

Later Exact-Main runs proved production SSH became reachable again. Therefore
the active blocker moved from DigitalOcean network reachability into guarded
promotion/recovery semantics.

Temporary control droplets used for the A/B test were deleted after diagnosis.

## Live production checkout / rollback boundary

Read-only incident inspection on PR #680 proved:

- live checkout HEAD:
  `cf2764c24e85ff4980d599f528218f1328b81627`;
- the only tracked drift in the live checkout is:
  `data/runtime/hhs_filesystem_ledger.json`;
- that ledger has evolved from the repository copy into a chained Hash72
  filesystem ledger, including `chain_authority` and updated parent/entry
  witness relationships;
- no candidate in the guarded-update receipt log has ever reached
  `promotion/PROMOTED`;
- candidate `d29d23e1750f9ac33c824e539b127e416b8c22b6` reached
  `validation/VALIDATED` but did not promote.

The live checkout is therefore still on the rollback lineage.

## Guarded updater failures already repaired

### 1. Missing Lane 5 socket binding

Live Exact-Main failed with:

```text
LANE5_INGRESS_SOCKET: unbound variable
```

Repair merged in PR #682.

### 2. Candidate identity race

A sealed Runtime OS bundle could be invalidated if an automated Hash216 index
commit advanced `origin/main` while the deployment was already running.

Repair merged in PR #683:
- Exact-Main supplies a transient `HHS_EXACT_CANDIDATE_SHA`;
- the updater requires the pin to remain on current main ancestry;
- bundle SHA must equal selected candidate;
- pin is removed before periodic timer resumes;
- no persistent timer pin is written.

### 3. Candidate validator interpreter

Candidate validation later failed because `/usr/bin/python3` could not import
`pytest`.

Repair merged:
- guarded validation uses `/opt/hhs/venv/bin/python`;
- installer verifies pytest is importable there;
- validated interpreter is persisted in guarded-update environment.

### 4. Ledger recovery/import root

Subsequent live failures exposed ledger recovery/import path assumptions.
Current main contains explicit repository-root ledger normalization/import repair
and corresponding regression/simulation coverage.

## Current recovery deadlock being investigated

The live service may be inactive when Exact-Main begins recovery.

`verify-recovery-state.py` accepts a terminal
`validation/VALIDATED` receipt only if it can prove the rollback boundary was
previously `promotion/PROMOTED`.

Current live facts:
- rollback/current HEAD = `cf2764c24e85ff4980d599f528218f1328b81627`;
- latest admissible-looking terminal receipt is
  `validation/VALIDATED` for `d29d23e...`;
- receipt log contains no historical `PROMOTED` receipt for `cf2764c...`
  because that rollback boundary predates the current guarded-update receipt
  history.

The verifier therefore exits 2 with the equivalent condition:

`HHS_RECOVERY_VALIDATED_PREVIOUS_SHA_NOT_PROVEN_PROMOTED`

This is a provenance migration deadlock, not evidence that `cf2764c...` is
untrusted.

## Existing positive rollback-boundary witness

Pass 220 I046 warm-boot manifests are SHA-scoped and bind:
- repository SHA;
- native runtime file and SHA-256 identity;
- Runtime OS root/index/assets identity;
- persistent state roots;
- manifest SHA-256;
- no-autobuild/no-rehydrate restart policy.

`warm_boot_manifest.py verify` fails closed on repository SHA, manifest digest,
native runtime identity, Runtime OS identity, state-root binding, or missing
state roots.

This is the candidate mechanism for a one-time legacy pre-receipt rollback
boundary proof. Do not weaken the normal requirement for prior `PROMOTED`
receipts. Any repair should admit a legacy boundary only after the existing
warm-boot manifest verifies the live checkout/artifacts/state roots exactly.

## Incident branches / PRs

PR #680:
- branch: `incident/network-ab-probe-20261002`;
- retained as read-only incident evidence;
- latest added diagnostic commit before this checkpoint:
  `9f16aa039381589ad7d3b4a468d0395716395f0b`;
- added live `hhs.service` state reporting and
  `warm_boot_manifest.py verify` against the production rollback boundary.

Do not overwrite or repurpose PR #680; preserve it as evidence.

PR #687:
- branch: `incident/exact-main-dispatch-20261002b`;
- temporary one-shot Exact-Main dispatcher and read-only locator;
- used only to invoke the authoritative existing Exact-Main workflow;
- not a production implementation branch.

## Last authoritative Exact-Main evidence before this checkpoint

Exact-Main run `37036629539`, target
`70f2af11467fe10a3c848062bf8e197c2fbaa077`:

- deployment contract: PASS;
- SSH: PASS;
- production mutation lock: acquired;
- bootstrap worktree for target: created;
- live remote shell exited code 2 before installer/promotion;
- timing and control flow indicate the recovery-state verifier path when
  `hhs.service` is inactive is the leading cause;
- live receipt inspection independently confirms the exact verifier deadlock
  described above.

## Immediate next action

1. Wait for/read the newest PR #680 read-only run containing:
   - `systemctl is-active hhs.service`;
   - port-8080 listener state;
   - exact `warm_boot_manifest.py verify` output for live
     `cf2764c...`.
2. If warm-boot verification succeeds:
   - implement a narrowly scoped legacy rollback-boundary admission in
     `verify-recovery-state.py`;
   - require exact warm-manifest verification for the current live SHA;
   - preserve the ordinary prior-`PROMOTED` receipt requirement for all
     non-legacy/post-receipt boundaries;
   - add positive/negative tests for manifest digest, repository SHA, native
     runtime identity, Runtime OS identity, and state-root mismatch;
   - run dependency-scoped Exact-Main + I046 + guarded updater tests;
   - merge and dispatch Exact-Main again.
3. If warm-boot verification fails:
   - do not bypass recovery verification;
   - repair the specific failed manifest/artifact/state-root boundary first.
4. Continue repair-forward until one Exact-Main receipt reaches
   `promotion/PROMOTED`, then verify:
   - live checkout = promoted target;
   - clean tracked working tree;
   - `hhs.service` active;
   - `hhs-lane5-ingress.socket` active;
   - `hhs-lane5-ingress.service` active;
   - exactly one listener on 8080 and 8715;
   - nginx has no direct public 8080/8720 proxy;
   - public HTTPS returns `X-HHS-Lane5-Ingress: mediated`;
   - root HTML is the HHS Visual Runtime OS Workspace;
   - local service registry is non-empty.

## Closure invariant

Do not claim production recovery complete until a live Exact-Main run produces a
`PROMOTED` receipt and the post-promotion public Lane 5/HTTPS verification
passes.

