# Post-promotion filesystem-ledger restart checkpoint — 2026-10-03

## Repository state

- repository: `danonbrez/Holofractal_Harmonicode`
- authoritative base / current main at checkpoint creation:
  `341b31e9f3e7e6332d3cbb3c00c80a0b38e7d784`
- checkpoint branch:
  `checkpoint/post-promotion-filesystem-ledger-20261003`
- merge target for any subsequent repair:
  `main`
- prior production repair PR:
  `#695`
- PR #695 merge commit:
  `ed02cfef4c3fcb6230604d321447d9a6fe1bf9b5`
- generated Hash216 current-main commit:
  `341b31e9f3e7e6332d3cbb3c00c80a0b38e7d784`

## Completed delivery evidence

PR #695 exact-head gates were green before merge, including:

- Pass 219 Cumulative Pass 202 Membrane I122 exact + synthetic;
- DigitalOcean Production Exact Main deployment contract;
- Validate HHS Runtime OS Production Root;
- Pass 220 Unified Chatbot Lane 5 Model Fabric;
- HHS Hash216 Repository Dependency Index;
- HHS Source Text Integrity;
- Validate Full Application IDE.

PR #695 merged with expected-head protection as:

`ed02cfef4c3fcb6230604d321447d9a6fe1bf9b5`

The merge-triggered Hash216 repository-index workflow generated the new authoritative
main projection:

`341b31e9f3e7e6332d3cbb3c00c80a0b38e7d784`

The new generated-main convergence path worked as designed:

- Hash216 index run: `37126524628`
- generated projection commit: PASS
- `Dispatch Exact-Main for generated current main`: PASS
- explicit Exact-Main workflow-dispatch run:
  `37126717536`
- dispatched head SHA:
  `341b31e9f3e7e6332d3cbb3c00c80a0b38e7d784`
- deployment-contract job `111213398985`: PASS

This proves that a workflow-token-generated Hash216 main commit no longer leaves
production silently behind authoritative `main`.

## Production promotion evidence

Authoritative Exact-Main deploy job:

`111213440510`

The guarded updater promoted the exact authoritative SHA:

`341b31e9f3e7e6332d3cbb3c00c80a0b38e7d784`

Promotion receipt:

```json
{
  "branch": "main",
  "candidate_sha": "341b31e9f3e7e6332d3cbb3c00c80a0b38e7d784",
  "detail": "candidate and exact Runtime OS bundle activated and health-verified",
  "outcome": "PROMOTED",
  "phase": "promotion",
  "previous_sha": "cf2764c24e85ff4980d599f528218f1328b81627",
  "runtime_os_bundle_sha": "341b31e9f3e7e6332d3cbb3c00c80a0b38e7d784",
  "schema": "HHS_GUARDED_UPDATE_RECEIPT_V2"
}
```

Additional production evidence from the same authoritative run:

- SSH authority and pinned host trust: PASS;
- production mutation ownership claimed;
- exact-main updater ownership claimed;
- production checkout permissions: PASS;
- unified Hash72 ledger permissions: PASS;
- unified ledger recovery boundary: `LEDGER_VALID`;
- pre-promotion serving runtime health: PASS;
- candidate Runtime OS activated and health-verified;
- product-health blocker from the previous cycle is resolved;
- `/api/product/health`: HTTP 200 during production operation;
- `hhs-lane5-ingress.socket`: activated;
- `HHS_LANE5_HOST_INGRESS_READY=1`;
- nginx syntax: PASS;
- nginx Lane 5 gateway:
  `proxy_pass http://127.0.0.1:8715`;
- direct backend bypass:
  `False`;
- `HHS_LANE5_INGRESS_ZERO_BYPASS=1`;
- `HHS_LANE5_HOST_INGRESS_NGINX_ZERO_BYPASS=1`;
- Runtime OS static-first release root:
  `/var/lib/hhs/runtime-os/releases/341b31e9f3e7e6332d3cbb3c00c80a0b38e7d784`.

## Current blocker

The authoritative deployment failed **after successful promotion** during the
post-promotion checkout-integrity proof.

Exact failure:

```text
production checkout is dirty after promotion
 M data/runtime/hhs_filesystem_ledger.json
```

The GitHub Actions deploy job therefore concluded failure and skipped its public
HTTPS verification step, even though the guarded updater had already emitted a
`PROMOTED` receipt for the authoritative SHA.

## Root-cause boundary identified so far

The production service unit itself is correctly configured to externalize the
filesystem ledger:

`HHS_FILESYSTEM_LEDGER_PATH=/var/lib/hhs/data/runtime/hhs_filesystem_ledger.json`

The repository path helper falls back to the tracked checkout only when
`HHS_FILESYSTEM_LEDGER_PATH` is absent:

`repo_root() / "data" / "runtime" / "hhs_filesystem_ledger.json"`

The candidate validator launches its temporary production gateway with only:

- `HHS_RUNTIME_OS_ASSET_ROOT`;
- `HHS_PASS205_DB`;

and does **not** currently supply an isolated/external
`HHS_FILESYSTEM_LEDGER_PATH`.

Relevant candidate-launch source:

`deployment/digitalocean/guarded_auto_update/validate-candidate.sh`

This makes candidate validation the leading source of the tracked ledger mutation.
The production service itself should not be reclassified as the writer without
additional evidence.

## Important authority constraints

Do not repair this by ignoring a dirty production checkout.

Required invariant remains:

- committed repository source is immutable production authority;
- mutable runtime state must live outside the repository checkout;
- post-promotion checkout must be clean;
- candidate validation must not mutate the canonical live repository;
- VM81 / Hash72 / Hash216 / Lane 5 authority must not be widened;
- nginx zero-bypass must remain intact.

Do not weaken the final checkout-integrity assertion.

## Separate non-blocking item

The Pass 220 LiteRT1 Native Model Runtime workflow has an independent C++ compile
defect under:

`native_projects/hhs_pass220_litert_native_model_runtime`

It is not caused by PR #695 and remains a separate repair-forward item.

## Changed files in this checkpoint

- `docs/operations/restart/POST_PROMOTION_FILESYSTEM_LEDGER_RESTART_20261003.md`

No runtime, deployment, validator, workflow, or canonical HHS implementation file
is changed by this checkpoint.

## Commands / repository operations already executed

Through the connected GitHub API:

- inspected PR #695 and exact-head Actions;
- verified all required #695 gates green;
- compared main drift and confirmed generated Hash216 index-only changes;
- merged PR #695 with expected-head protection;
- followed merge-triggered Exact-Main and Hash216 workflows;
- verified Hash216 generated-main explicit Exact-Main redispatch;
- followed authoritative Exact-Main workflow-dispatch run;
- inspected guarded-updater production logs;
- inspected production service unit;
- inspected host-drift preservation script;
- inspected candidate validator launch environment;
- inspected filesystem-ledger path authority.

No direct host shell mutation was performed outside the repository-defined Exact-Main
workflow.

## Validation completed

- PR #695 required exact-head CI: green;
- Pass 202 historical/current successor identities: green;
- generated-main Exact-Main redispatch: proven;
- authoritative current-main deployment-contract: green;
- guarded production promotion: proven by `PROMOTED` receipt;
- Lane 5 host ingress: ready;
- nginx zero-bypass: proven;
- product-health previous hang: resolved;
- post-promotion checkout cleanliness: FAILED only because tracked
  `data/runtime/hhs_filesystem_ledger.json` changed.

## Validation remaining

After the next narrow repair:

1. candidate validation must externalize or isolate
   `HHS_FILESYSTEM_LEDGER_PATH`;
2. candidate validation must still prove all current health and assistant contracts;
3. post-promotion `git status` must be clean;
4. promotion receipt must remain `PROMOTED`;
5. production checkout SHA must equal authoritative current `main`;
6. hhs.service must be active;
7. Lane 5 socket/service must be active;
8. exactly one expected 8080 backend listener and 8715 ingress listener;
9. nginx must proxy public dynamic ingress through 8715;
10. nginx must not introduce direct 8080/8720 bypass;
11. public HTTPS Runtime OS verification must complete green;
12. any subsequent Hash216 generated-main commit must again explicitly dispatch
    Exact-Main and become final production identity.

## Environment state

- authoritative repository main:
  `341b31e9f3e7e6332d3cbb3c00c80a0b38e7d784`
- authoritative Runtime OS bundle SHA:
  `341b31e9f3e7e6332d3cbb3c00c80a0b38e7d784`
- guarded updater emitted `PROMOTED`;
- previous production SHA before promotion:
  `cf2764c24e85ff4980d599f528218f1328b81627`;
- public HTTPS verification did not run because the post-promotion clean-check failed;
- production repository currently requires integrity repair/normalization before
  final closure can be claimed.

## Next action

Create a narrow repair branch from authoritative main
`341b31e9f3e7e6332d3cbb3c00c80a0b38e7d784`.

First inspect all filesystem-ledger writes reachable during
`validate-candidate.sh`. Then bind candidate validation to an isolated external
ledger path under the guarded-update state root or another explicitly disposable
candidate state directory.

Add executable regression coverage proving:

- candidate boot does not mutate tracked
  `data/runtime/hhs_filesystem_ledger.json`;
- production service still uses
  `/var/lib/hhs/data/runtime/hhs_filesystem_ledger.json`;
- final checkout-integrity assertion remains fail-closed.

Then run dependency-scoped validation, commit, open/merge the repair PR only after
green gates, and re-run Exact-Main through public HTTPS closure.
