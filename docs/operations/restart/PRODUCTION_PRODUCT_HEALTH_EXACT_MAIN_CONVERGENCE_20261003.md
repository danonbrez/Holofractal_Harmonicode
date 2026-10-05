# Production product-health and generated-main Exact-Main convergence repair — 2026-10-03

## Repository state

- repository: `danonbrez/Holofractal_Harmonicode`
- authoritative base: `54b869852452a632e78041a11392b966b9d8cca3`
- branch: `repair/product-health-index-exact-main-convergence-20261003`
- merge target: `main`
- triggering Exact-Main run: `37113182460`
- triggering deploy job: `111174928306`

## Proven predecessor state

PR #694 merged as:

`5165f18251a2e4a2e23d04dd08e632f84f7ffa82`

Its production candidate reached the guarded updater with the sealed warm-boot and
rollback repairs intact.

The failed production transaction proved:

- SSH authority and pinned host trust: PASS;
- exact Runtime OS build/seal and transfer: PASS;
- production service permission normalization: PASS;
- unified Hash72 ledger permission and recovery boundary: PASS;
- pre-promotion rollback service health: PASS;
- candidate production integration tests: **49 passed**;
- Pass 205 deterministic production receipt: PASS;
- application-studio inherited tests: **14 passed**;
- prebuilt Runtime OS bundle verification: PASS;
- candidate `/api/system/status`: HTTP 200;
- candidate `/`: HTTP 200;
- candidate `/api/health`: HTTP 200;
- candidate `/api/interface/status`: HTTP 200.

The guarded updater then exited before promotion. The next probe in
`validate-candidate.sh` is `/api/product/health`; no completed product-health
access log was emitted before the candidate was terminated. Public HTTPS was not
attempted.

## Product-health root cause boundary

`/api/product/health` calls `_assistant_health()`. That helper called the full
`ProductionAssistantService.health()`, which force-probes the complete provider
fabric, including optional external LiteRT and Pass 153 health surfaces.

The repository already proves a real hosted native assistant:

- local native installation ready;
- native provider health online;
- real prompt-response turn;
- receipt-bearing assistant message;
- provider invocation receipt;
- provider result ingress receipt;
- no canonical runtime mutation from model output.

Deployment liveness therefore does not need to block on optional provider health.

## Product-health repair

`ProductionAssistantService.deployment_health()` now:

- force-probes the guaranteed local native HHS assistant only;
- keeps full multi-provider `health()` unchanged for diagnostics;
- returns explicit deployment-liveness scope
  `NATIVE_HHS_LOCAL_EXECUTABLE_AUTHORITY`;
- marks optional provider health as deferred;
- preserves Hash72 status-root regeneration;
- does not widen VM81, Hash72, Hash216, or Lane 5 authority.

`production_server._assistant_health()` now wraps this path in an aggregate
8-second asyncio timeout.

Candidate validation was strengthened rather than weakened. Promotion requires:

- runtime authority `ok=true`;
- assistant `ok=true` and `online=true`;
- selected provider exactly `provider:hhs.local.text`;
- native deployment-liveness scope;
- optional-provider health explicitly deferred.

## Generated-main convergence root cause

The Hash216 repository-index workflow uses the GitHub Actions token to commit its
generated projection back to `main`. GitHub does not create ordinary push-triggered
workflow chains from that token. Thus its generated commit advanced main from
`5165f182...` to:

`54b869852452a632e78041a11392b966b9d8cca3`

without triggering a new Exact-Main deployment.

## Generated-main convergence repair

The index workflow already has `actions: write`.

After a generated projection is actually committed, it now:

1. records `committed=true` and the generated SHA as step outputs;
2. resolves the current remote main SHA;
3. explicitly dispatches
   `digitalocean-production-main.yml --ref main` with the repository token;
4. emits `HHS_HASH216_EXACT_MAIN_DISPATCHED=<current-main-sha>`.

No dispatch occurs for a stale projection or when the generated index is already
current.

This uses GitHub's explicit `workflow_dispatch` path rather than relying on a
suppressed bot-generated push event.

## Changed files

- `hhs_backend/runtime/hhs_production_assistant_v1.py`
- `hhs_backend/production_server.py`
- `deployment/digitalocean/guarded_auto_update/validate-candidate.sh`
- `tests/test_hhs_production_public_app_v1.py`
- `tests/test_runtime_os_production_root.py`
- `tests/test_hhs_guarded_auto_update_contract_v1.py`
- `.github/workflows/repository-hash216-dependency-index.yml`
- `.github/workflows/digitalocean-production-main.yml`
- `tests/test_hash216_exact_main_convergence_v1.py`
- this checkpoint

## Validation performed

Repository evidence was inspected through the connected GitHub API.

The failure boundary was derived from finalized production logs, not inferred from
a queued or partial run.

Source-level fail-closed assertions were added to the Exact-Main contract suite.

## Validation remaining

Before merge require:

1. Exact-Main deployment-contract job: PASS;
2. production/root health regressions: PASS;
3. source integrity: PASS;
4. Hash216/Lane 5 dependency-scoped validation affected by workflow change: PASS.

After merge require:

5. candidate product-health probe completes inside its bound;
6. candidate validation completes;
7. guarded promotion receipt is `PROMOTED`;
8. `hhs.service` active;
9. Lane 5 socket/service active;
10. nginx has no 8080/8720 public bypass and proxies through 8715;
11. public HTTPS Runtime OS verification: PASS;
12. if Hash216 generates a new main commit, explicit Exact-Main dispatch occurs and
    the dispatched current-main SHA is the final production identity.

## Environment state

- current repository main at branch creation:
  `54b869852452a632e78041a11392b966b9d8cca3`
- production remains fail-closed on the proven healthy rollback service;
- candidate `5165f182...` was not promoted;
- HTTPS verification was not reached;
- no production bypass was applied.

## Next action

Open the repair PR, validate the dependency-scoped gates, merge only on green, then
follow the push deployment and any generated-index Exact-Main redispatch until
production identity equals authoritative current main and HTTPS closes.


## Pass 202 successor reseal

The first PR membrane run `37114186609` failed only at
`Prove current successor-hardened Pass 202 deployment identities`.

Both exact and synthetic jobs passed:

- frozen I121 / accepted Pass 202 integration;
- historical Pass 202 source identities.

The intentional validator hardening changed the current successor blob:

- old current-successor validator blob:
  `0e74e2508c00507f7045dc8eecaab8a1a29f80ca`
- new validator blob:
  `188b72531eb72665fdf28cdbd96b73af44ea72ac`

Only the current successor seal in
`.github/workflows/pass219-cumulative-pass202-membrane-i122.yml` was updated.
Frozen historical identities remain unchanged.

At the time of this reseal, authoritative `main` had advanced by one generated
Hash216 projection commit to:

`2776a18c205ff188fdcffa6f69f72869e3b80655`

The drift touched generated repository-index artifacts only and did not overlap
the production/runtime implementation surfaces in PR #695.


## Pass 202 kernel-derived successor reseal

The next fresh Pass 202 run on head
`78c1972417750e0284c4f45532ca13ff967ae1ee` advanced through the workflow-level
current-successor identity gate and then failed in the kernel-derived membrane with:

```text
PASS202_SUCCESSOR_HARDENING_BLOB_DRIFT:
deployment/digitalocean/guarded_auto_update/validate-candidate.sh:
188b72531eb72665fdf28cdbd96b73af44ea72ac
```

This proved the second duplicate current-successor table in
`hhs_runtime/hhs_pass219_cumulative_pass_membrane_i122_pass202.py` still carried
the pre-repair validator blob.

Only that current-successor validator entry was changed to:

`188b72531eb72665fdf28cdbd96b73af44ea72ac`

The historical Pass 202 validator identity
`82250c50fa9d20a82d0b957d2637398760b1c416` remains unchanged.

At this checkpoint authoritative `main` is:

`c1a40f2ce26656c2f9ebb98d8fc279cca68661fc`

Compared with the branch base `54b869852452a632e78041a11392b966b9d8cca3`,
main is ahead by two commits and every changed path is generated Hash216 repository
index material. No production/runtime implementation file in PR #695 overlaps that
drift.


## 2026-10-05 serialized delivery repair

Authoritative main advanced through generated Hash216 projection commits
`ad1f995c6d5e7d7fdac9f8f5a467ec03f8ae2993` and
`7bd585a0a0c9a2a964fee4f56d58baeafda2932e` after the I077 merge
`c54a9d5d0b57e113f895091065c76b5f4e21e998`.

The preceding Exact-Main transaction was cancelled as newer main state appeared,
and the exact-`7bd585a0` transaction then reached the host while
`/run/lock/hhs-production-mutation.lock` was still occupied. Promotion did not
complete and public HTTPS verification was skipped.

The repair changes repository orchestration rather than weakening the host lock:

1. every non-PR Exact-Main run, whether push-triggered or explicitly dispatched,
   uses one concurrency group: `hhs-production-main-delivery`;
2. that group uses `cancel-in-progress: false`, so an active remote mutation
   transaction cannot be cancelled by later main movement;
3. authoritative Hash216 index refresh uses the same non-PR concurrency group;
4. the Hash216 workflow no longer advances main independently on every main push;
5. after Exact-Main reaches a matching `PROMOTED` receipt and public HTTPS
   Runtime OS/service-registry verification, it explicitly queues the Hash216
   refresh;
6. if that refresh creates a generated current-main commit, it explicitly queues
   Exact-Main for that generated SHA;
7. PR validation for both workflows remains in PR-specific concurrency groups and
   therefore cannot occupy the production delivery mutex.

This creates the closed chain:

```text
development main
-> Exact-Main promotion
-> PROMOTED receipt
-> public HTTPS + service registry verification
-> queued Hash216 index refresh
-> optional generated-main commit
-> queued Exact-Main promotion
-> convergence
```

The production bundle build also runs the Runtime OS workspace, live GUI E2E
source, and frontend telemetry source verification before sealing the frontend.
The inherited production integration continues to hydrate every descriptor
returned by `GET /api/runtime/services` into the frontend registry and route
execution through guarded backend dispatch.

Restart state:

- base: `7bd585a0a0c9a2a964fee4f56d58baeafda2932e`
- branch: `repair/serialized-production-delivery-20261005`
- merge target: `main`
- changed authority: repository orchestration only; host mutation authority remains
  the shared `/run/lock/hhs-production-mutation.lock`
- post-merge acceptance remains fail-closed on exact SHA `PROMOTED`, local
  service-registry verification, public service-registry verification, and public
  HTTPS Runtime OS verification.


## 2026-10-05 generated-successor terminal closure

The serialized delivery chain must terminate after the generated Hash216 successor
itself reaches Exact-Main production. The generated index projection embeds its
bound source commit in projection artifacts, so unconditionally refreshing the
index after a generated-only successor could otherwise produce another generated
successor indefinitely.

Exact-Main now recognizes the canonical generated projection commit subject
`docs: refresh Hash216 repository dependency index`. After that SHA has passed
the same `PROMOTED`, local registry, public registry, and public HTTPS gates, the
workflow emits
`HHS_EXACT_MAIN_HASH216_INDEX_TERMINAL_GENERATED_SUCCESSOR=<sha>` and does not
queue another Hash216 refresh.

Non-generated development/merge commits retain the normal post-promotion index
refresh path. Thus the closed chain is finite:

```text
development main
-> verified Exact-Main
-> one Hash216 refresh
-> generated successor
-> verified Exact-Main
-> terminal closure
```
