# Pass 220 — DigitalOcean Production Host Rebind Restart

Date: 2026-09-25

## Repository state

- repository: `danonbrez/Holofractal_Harmonicode`
- base main: `789065b0c66f83a08b2fa8372d96324398b0206a`
- branch: `pass220/digitalocean-production-host-rebind-20260925`
- merge target: `main`

## Trigger

Post-merge deployment of PR #589 failed after local build/backend validation because both production workflows attempted SSH to the retired host `165.227.220.193:22`.

The connected DigitalOcean control plane reports the current production droplet:

```text
name: hhs-production-04
status: active
region: nyc3
public IPv4: 159.65.178.254
tags include: hhs-production, github-deploy-key-bound
```

The DigitalOcean account itself is active and the HHS GitHub Actions deploy public key remains registered.

## Implemented repository repair

Active workflow/test defaults were rebound from `165.227.220.193` to `159.65.178.254` in:

```text
.github/workflows/digitalocean-mobile-control-ingress.yml
.github/workflows/pass220-i044-real-ubuntu-guest.yml
.github/workflows/digitalocean-production-main.yml
.github/workflows/pass220-ubuntu-application-vm-production.yml
tests/pass220/test_pass220_i045_startup_first_paint_parallel.py
tests/pass220/test_pass220_ubuntu_application_vm_control_plane.py
```

Historical restart records were intentionally left unchanged.

A non-mutating strict SSH preflight was added:

```text
.github/workflows/pass220-digitalocean-host-rebind-preflight.yml
```

It preserves:

```text
BatchMode=yes
StrictHostKeyChecking=yes
UserKnownHostsFile=<repository secret projection>
UpdateHostKeys=no
no ssh-keyscan
no runtime host-key discovery
```

## Validation result

Preflight run:

```text
Pass 220 DigitalOcean Host Rebind Preflight
run: 36201750843
job: 108289694303
conclusion: failure
```

The failure is intentional/fail-closed evidence:

```text
HHS_DIGITALOCEAN_KNOWN_HOSTS has no audited entry for 159.65.178.254.
```

The private deploy-key secret is present; the preflight failed before network authentication because the new host is not in the pinned known-hosts secret.

## External blocker

The repository connector cannot mutate GitHub Actions secrets.

Required external secret rotation:

1. obtain the SSH host public key/fingerprint for `159.65.178.254` from an authenticated/audited DigitalOcean console or other trusted host-provisioning record;
2. add its exact known_hosts entry to repository secret `HHS_DIGITALOCEAN_KNOWN_HOSTS`;
3. do not remove still-required historical entries unless separately retired;
4. optionally set repository variable `HHS_DIGITALOCEAN_HOST=159.65.178.254` so the workflow does not depend on the source fallback.

Do not use `ssh-keyscan` as a trust bootstrap for this repair.

## Next deterministic action

After the audited known-host entry is installed:

1. rerun `Pass 220 DigitalOcean Host Rebind Preflight`;
2. require both pinned-host lookup and SSH echo to pass;
3. merge the host-rebind PR;
4. rerun/promote exact main through:
   - `DigitalOcean Production Exact Main`;
   - `Pass 220 Ubuntu Application VM Production`;
5. verify public HTTPS and `/api/assistant/health`;
6. verify a nontrivial chatbot prompt reports the unified selected model path and Lane 5 tooling remains governed/read-only.
