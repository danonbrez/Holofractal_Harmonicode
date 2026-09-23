# Pass 220 I044 — Real Ubuntu Guest Integration Restart Checkpoint

## Repository identity

- repository: `danonbrez/Holofractal_Harmonicode`
- base main: `6287ca3051e64ff6d0d3353299ead7f66f0c1c55` (merged I043)
- branch: `pass220/i044-real-ubuntu-guest-integration-v1`
- merge target: `main`

## Implemented state

I044 now contains:

```text
hhs_runtime/pass220/ubuntu_guest_runtime.py
deployment/ubuntu/guest_runtime/ubuntu-24.04-amd64-image.json
deployment/ubuntu/guest_runtime/prepare-real-guest.sh
deployment/ubuntu/guest_runtime/run-real-guest-integration.sh
tests/pass220/test_pass220_i044_real_ubuntu_guest_integration.py
.github/workflows/pass220-i044-real-ubuntu-guest.yml
docs/pass220/PASS_220_I044_REAL_UBUNTU_GUEST_INTEGRATION_V1.md
docs/operations/restart/PASS_220_I044_REAL_UBUNTU_GUEST_INTEGRATION_20260923.md
```

## Image identity

Pinned released Ubuntu artifact:

- release: `20260911`
- file: `ubuntu-24.04-server-cloudimg-amd64.img`
- format: QCOW2
- SHA-256:
  `612b2c0cc1bc413a6cb8c38fd611794caf0f2b436c50013d8b3794db12ad7354`

I043 was extended additively with optional `HHS_GUEST_SEED_IMAGE` support.
When configured, the seed must exist and is attached read-only as a raw virtio
drive.

## Real guest bootstrap

`prepare-real-guest.sh`:

- requires an exact target Git SHA;
- installs missing host QEMU/cloud-image tools when necessary;
- downloads/verifies the pinned Ubuntu base;
- creates target-specific SSH client and host ED25519 keys;
- writes strict loopback known_hosts;
- writes a NoCloud seed;
- checks out the exact HHS target inside the guest;
- creates `/opt/hhs/venv`;
- installs the inherited application VM control plane headlessly;
- writes a release-specific I043 runtime environment and preparation receipt.

`run-real-guest-integration.sh`:

- stops a prior managed guest before reusing the loopback SSH port;
- verifies/prepares/starts the I043 guest;
- waits for strict SSH and cloud-init completion;
- verifies guest repository HEAD equals target SHA;
- verifies `hhs-application-vm.service`;
- verifies application VM health/status and single VM81 authority;
- proves a command through the real SSH-backed PTY;
- seals an I044 integration receipt;
- promotes `/var/lib/hhs/ubuntu-guest/current` only after closure.

## Production execution policy

The workflow:

```text
.github/workflows/pass220-i044-real-ubuntu-guest.yml
```

has:

- pull-request contract validation;
- manual `workflow_dispatch`;
- a boolean `run_real_guest` input;
- no automatic real-host mutation on merge.

The real-host job reuses the repository's pinned DigitalOcean SSH secret and
known-hosts contract.

## Infrastructure observation

Read-only DigitalOcean inspection during this cycle reported:

- existing Droplet: `hhs-production-01`;
- region: `nyc3`;
- host profile: 2 vCPU / 4 GiB / 120 GiB;
- Droplet status: `off`;
- account status: `locked`.

No power action, resize, rebuild, Droplet creation, deletion, or billing-changing
action was taken.

The default I044 guest profile is therefore bounded to:

```text
2 vCPU
2048 MiB RAM
loopback SSH port 2222
```

Actual host execution remains blocked until the DigitalOcean account/host is
operational.

## Validation next action

1. Open the I044 pull request.
2. Run the dependency-scoped PR contract job.
3. Repair only I044/I043-seed regressions if any.
4. Merge when the exact head is green and mergeable.
5. Verify main contains the I044 artifacts.
6. Do **not** dispatch `run_real_guest=true` while the production account/host
   remains locked/off.
7. Once infrastructure is restored, dispatch the real-host job on exact main.
8. Accept I044 real-host closure only from its final integration receipt.
