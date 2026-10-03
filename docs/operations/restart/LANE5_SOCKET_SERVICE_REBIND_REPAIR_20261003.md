# Lane 5 socket/service deterministic rebind restart — 2026-10-03

## Authority

- repository: `danonbrez/Holofractal_Harmonicode`
- authoritative base/current main: `50da26883afaa4aae47b14224bba0a101bfc8d22`
- repair branch: `repair/lane5-socket-service-restart-order-20261003`
- merge target: `main`
- preceding diagnostic PR: `#697`
- PR #697 merge: `8f40341dece6ba9189e968712c1bbdbba171ac38`
- Hash216 generated current main: `50da26883afaa4aae47b14224bba0a101bfc8d22`

## Production evidence

PR #697 made Exact-Main emit the failing guarded-updater journal and receipts.

Both the merge-SHA run and the authoritative generated-main run proved:

- candidate validation completed;
- guarded updater systemd result: `success`;
- guarded updater `ExecMainStatus=0`;
- exact candidate was promoted;
- Runtime OS activation and warm-boot identity completed;
- production `hhs.service` reached `HHS_P174_BOOT_READY`;
- a `PROMOTED` guarded-update receipt was written;
- the periodic `hhs-guarded-update.timer` is active after the updater;
- installer then failed before emitting `HHS_LANE5_HOST_INGRESS_READY=1`.

Authoritative generated-main promotion receipt observed:

```text
candidate_sha=50da26883afaa4aae47b14224bba0a101bfc8d22
outcome=PROMOTED
phase=promotion
detail=candidate and exact Runtime OS bundle activated and health-verified
```

The failure therefore occurs after successful updater promotion in the Lane 5 host-ingress activation portion of `install.sh`, not in candidate validation, filesystem-ledger isolation, updater health, native promotion, or Runtime OS activation.

## Root cause and repair

The prior installer sequence was:

```text
enable hhs-lane5-ingress.socket
restart hhs-lane5-ingress.socket
restart hhs-lane5-ingress.service
```

After the first successful Lane 5 installation, the socket-activated service can remain running with the inherited listening descriptor for `127.0.0.1:8715`. Rebinding the socket before releasing the existing ingress owners creates a repeat-deployment collision boundary.

The repaired deterministic sequence is fail-closed:

```text
enable socket
stop socket
stop service
start socket
start service
health proof
nginx zero-bypass proof
```

Each stop/start operation now has Lane 5 socket/service status, journal, and listener diagnostics on failure.

## Changed files

- `deployment/digitalocean/guarded_auto_update/install.sh`
- `tests/test_hhs_guarded_auto_update_contract_v1.py`
- `.github/workflows/pass219-cumulative-pass202-membrane-i122.yml`
- `hhs_runtime/hhs_pass219_cumulative_pass_membrane_i122_pass202.py`
- this restart record

## Pass 202 identity

Historical Pass 202 identities remain unchanged.

Only the current successor installer blob advances:

- previous: `51fb5fab508324f42acf2da1caf5202ab39bd2bb`
- repaired: `eb91cf2bc4019abf9db5ac7abd5ce7e375e9f43e`

The new current successor is resealed in both the workflow and kernel membrane tables.

## Repair commits before this restart record

- `720b3681c1435c078be49f742df7b513128ca230` — deterministic Lane 5 socket/service rebind.
- `5d529599d7d6f6c9c46ccbcace65c1a7e51ee346` — rebind-order regression.
- `1f378c164af9757f0094973ce18251d9155aa6fc` — workflow successor reseal.
- `86a5d2624a5886b54751eeccb84bc133160ac4b0` — kernel membrane successor reseal.

## Required closure

1. exact-head Pass 202 exact/synthetic and deployment regressions green;
2. Exact-Main contract, Source Integrity, Hash216, Lane 5 provider, full IDE/other path-required gates green;
3. expected-head merge;
4. follow Hash216 generated-main commit and explicit Exact-Main redispatch;
5. require guarded-update `PROMOTED` receipt for final current main;
6. require installer to emit `HHS_LANE5_HOST_INGRESS_READY=1`;
7. require socket/service active and exactly one `:8715` listener;
8. require nginx `proxy_pass http://127.0.0.1:8715` with no direct `:8080`/`:8720` bypass;
9. require production checkout clean;
10. require public HTTPS Runtime OS verification green.
