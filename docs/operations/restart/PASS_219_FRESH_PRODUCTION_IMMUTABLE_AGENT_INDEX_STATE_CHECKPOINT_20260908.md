# Pass 219 Fresh Production Immutable Agent Index State Checkpoint — 2026-09-08

## Restart authority

- Repository: `danonbrez/Holofractal_Harmonicode`
- Branch: `agent/pass219-fresh-production-bootstrap-73652c12-20260908`
- Branch head before this checkpoint: `052cc0433cb3f34c6d9c1163ec6e9d887c6ba06a`
- Exact production source authority: `main@73652c122ffff6a8b9bde9de00020610964d704c`
- Production host: `hhs-production-01` / `165.227.220.193`
- Production checkout: `/opt/hhs/app`
- Service identity: `hhs:hhs`

## Frozen completed state

The fresh-host deployment has already passed the following boundaries:

1. pinned Ed25519 host identity validation;
2. deployment private-key/public-key authentication after explicit enrollment in `/root/.ssh/authorized_keys`;
3. exact production checkout at `73652c122ffff6a8b9bde9de00020610964d704c` on `main` with a clean worktree;
4. Python environment installation;
5. native C ABI build with `/opt/hhs/app/hhs_runtime/builds/libhhs_runtime.so` present;
6. exact Runtime OS build, seal, transfer, stage and activation input preservation;
7. runtime-certification writable state isolated from the immutable checkout through `/var/lib/hhs/runtime-certification`;
8. Storybook Reel writable state redirected through its native `HHS_STORYBOOK_REEL_ARTIFACT_ROOT` override;
9. Runtime OS exact-release traversal repaired by changing the already verified release root from inherited `mkdtemp` mode `0700` to service-readable `0755`, without changing sealed payload files.

## Current failure

GitHub Actions run `34271872609`, job `102215168017`, passed checkout, script validation, pinned SSH authority, and exact partial-state verification, then failed during the scoped repair health gate.

The service now reaches FastAPI lifespan initialization and the guarded deterministic runtime and graph substrate initialize successfully. Startup then fails in:

`hhs_backend/runtime/immutable_agent_index_hooks_v1.py`
→ `hhs_backend/runtime/immutable_agent_sql_index_v1.py`
→ SQLite initialization

with:

```text
sqlite3.OperationalError: unable to open database file
```

The authoritative immutable-agent-index workflow defines the runtime database explicitly as:

```text
HHS_AGENT_INDEX_DB=${{ runner.temp }}/hhs-agent-index.sqlite3
```

The production service unit does not currently define `HHS_AGENT_INDEX_DB`. This is therefore a fresh-host state-path configuration defect, not a source-code or SQLite-schema failure.

## Invariant

Do not make `/opt/hhs/app` generally writable and do not alter exact source authority `73652c12` to repair this host-state defect.

Production writable state belongs under `/var/lib/hhs` and must remain writable by `hhs:hhs` while the repository checkout remains clean and immutable.

## Exact next action

Extend `deployment/digitalocean/fresh_host_runtime_certification_repair.sh` so it:

1. creates `/var/lib/hhs/immutable-agent-index` as `hhs:hhs` mode `0750`;
2. adds `Environment=HHS_AGENT_INDEX_DB=/var/lib/hhs/immutable-agent-index/hhs-agent-index.sqlite3` to the existing `hhs.service` drop-in;
3. preserves the existing runtime-certification bind, Storybook state override, and Runtime OS release traversal repair;
4. restarts `hhs.service`;
5. requires `/api/system/status` health;
6. verifies the SQLite index exists under `/var/lib/hhs/immutable-agent-index`, is owned by `hhs:hhs`, and that the service can access it;
7. requires the production Git worktree to remain clean;
8. only after this repair passes, resume the exact-main fresh-host bootstrap and remaining initialization/public-HTTPS gates.

## Validation remaining

- scoped immutable-agent-index state-path repair health gate;
- resumed exact-main fresh-host bootstrap;
- initialization receipt verification;
- local API authority verification;
- guarded update timer verification;
- nginx and certificate renewal timer verification;
- browser-trusted public HTTPS exact-main verification;
- production assistant authority verification.

## Blocker classification

`FRESH_HOST_RUNTIME_STATE_PATH_CONFIGURATION / HHS_AGENT_INDEX_DB`

No production-completion claim is valid until the remaining gates above pass.
