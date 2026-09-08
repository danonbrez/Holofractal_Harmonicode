# Pass 219 Fresh Production Assistant Configuration-Parity Checkpoint — 2026-09-08

## Restart authority

- Repository: `danonbrez/Holofractal_Harmonicode`
- Recovery branch: `agent/pass219-fresh-production-bootstrap-73652c12-20260908`
- Exact production source authority: `main@73652c122ffff6a8b9bde9de00020610964d704c`
- Production host: `hhs-production-01` / `165.227.220.193`
- Production checkout: `/opt/hhs/app`
- Service identity: `hhs:hhs`
- Local + public HTTPS closure checkpoint: `a78c84fe042f1277c3b658419de5e9d5bebcf7bb`
- Read-only assistant diagnostic implementation: `fd8e392023d7a1289fdda5cab48ad0b6420e08c8`
- Prior assistant diagnostic checkpoint: `0c074e0e611acb64620f58df1fa5e23717bbf9ba`

## Frozen green production state

The fresh-host deployment is locally closed and publicly reachable at exact production SHA `73652c122ffff6a8b9bde9de00020610964d704c`.

Frozen successful boundaries include pinned SSH authority, clean exact-main checkout, Python/native C ABI, sealed Runtime OS activation, writable runtime-state isolation, immutable-agent SQLite integrity, guarded update timer, nginx, browser-trusted Let's Encrypt IP certificate, certificate renewal timer, healthy loopback API, valid initialization receipt, clean production Git worktree, and browser-trusted public HTTPS Runtime OS/system-status verification.

Do not rerun the full bootstrap or already-green mutating repairs without an impacted-surface reason.

## Read-only production assistant diagnostic

Workflow run `34286045347`, job `102261772214`, completed `SUCCESS` and proved no production mutation.

Observed live/precomputed evidence:

```text
assistant_ready=false
selected_provider=null
Gemma ready=false; configured model=gemma4-12b; registered models=0; connection refused
Native semantic membrane=true
Native bounded reasoner=true
Native word2vec_required=true
Native word2vec_ready=false
HHS_PASS166_STORAGE_DIR absent
HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC absent
port 9379 not listening
/opt/hhs/venv/bin/litert-lm present
/var/lib/hhs/pass166 absent
/root/.hhs/pass166 present but no registry and no active model
/opt/hhs/app/.hhs/pass166 absent
```

## Repository-authoritative correction to the initial diagnosis

The previous checkpoint treated an active Pass 166 model as mandatory for production native-assistant closure. Further exact-source inspection falsifies that assumption for the **hosted production** surface.

### Canonical hosted-production policy

`hhs_backend/production_server.py` states:

```python
# Hosted production must always have an executable language authority even when
# a large external LiteRT-LM model or Pass 166 vector package has not yet been
# provisioned. Gemma remains preferred whenever its registry is ready.
os.environ.setdefault("HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC", "0")
os.environ.setdefault("HHS_ASSISTANT_HEALTH_TIMEOUT_SECONDS", "5")
```

`bin/post_compile` independently enforces the same hosted-production policy:

```bash
export HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC="${HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC:-0}"
python3 tools/install_production_language_assets.py --install-if-configured --require-assistant
```

The production acceptance test `tests/test_hhs_production_public_app_v1.py` explicitly requires:

```text
native installation ready=true
word2vec_required=false
native health ok=true / online=true
selected_provider_id=provider:hhs.local.text
effective_mode=HHS_NATIVE_LITERT_COMPATIBLE
real assistant turn for AB=P^4 succeeds
message_root_hash72 present
provider_invocation_receipt_hash72 present
provider_result_ingress_root_hash72 present
turn_root_hash72 present
runtime_mutation_admitted=false
```

Therefore disabling the generic Word2Vec requirement is not a test bypass on hosted production; it is the repository-defined production policy.

### Entry-point parity defect

The deployed service starts:

```text
hhs_backend.production_visual_server:app
```

`production_visual_server.py` imports `runtime_os_visual_server.py`, which imports `visual_server.py`. That path does **not** import `production_server.py` before assistant service construction and therefore does not inherit the hosted-production `HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC=0` setup.

The DigitalOcean service unit also does not define that variable.

The live service thus fell through to the generic native-provider default:

```text
HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC=1
```

which explains the observed `assistant_ready=false` despite Pass 148 and Pass 151 already being ready.

## Pass 166 storage boundary

`hhs_runtime/pass166/service.py` defaults its storage root to `.hhs/pass166` and creates directories during service construction. Even though Word2Vec is optional for hosted production, the assistant/provider route may still instantiate the Pass 166 service for status/context. Production must therefore set:

```text
HHS_PASS166_STORAGE_DIR=/var/lib/hhs/pass166
```

before the first live assistant route is invoked, so provider initialization cannot dirty `/opt/hhs/app`.

## Correct blocker classification

```text
PRODUCTION_RUNTIME_OS_ENTRYPOINT_HOSTED_ASSISTANT_ENV_PARITY
+
PRODUCTION_PASS166_STATE_PATH_NOT_ISOLATED
```

A pretrained model installation is **not** required for the hosted native-assistant closure defined by exact source/tests. Gemma and Pass 166 models remain additive/preferred capabilities.

## Repair invariant

1. Preserve exact production source authority `73652c12` and clean Git worktree.
2. Do not install an arbitrary/fake/test Word2Vec model.
3. Configure the deployed service to match repository-defined hosted-production semantics:
   - `HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC=0`
   - `HHS_PASS166_STORAGE_DIR=/var/lib/hhs/pass166`
4. Keep Pass 166 writable state under `/var/lib/hhs`.
5. Restart only `hhs.service`; do not rerun the full bootstrap.
6. Only after restart, invoke canonical `/api/assistant/health`.
7. Require native provider selection and a real receipt-bearing production assistant turn matching the production acceptance contract.
8. Require the production worktree to remain clean and `.hhs` absent after health/turn execution.

## Exact next action

Create a scoped pinned-SSH repair that adds a dedicated systemd drop-in for the two hosted-assistant environment variables, creates `/var/lib/hhs/pass166` as `hhs:hhs`, restarts `hhs.service`, and then verifies:

- `/api/assistant/health` is `HHS_PRODUCTION_ASSISTANT_READY`;
- selected provider is `provider:hhs.local.text`;
- effective mode is `HHS_NATIVE_LITERT_COMPATIBLE`;
- native installation reports `ready=true` and `word2vec_required=false`;
- a real public HTTPS `/api/assistant/chat` turn for `AB=P^4` succeeds with nonempty answer plus message, provider invocation, provider ingress, and turn Hash72 receipts;
- `runtime_mutation_admitted=false`;
- `/opt/hhs/app` remains exact and clean with no `.hhs` state;
- `/var/lib/hhs/pass166` is the only Pass 166 production state root used by the service.

Checkpoint the result terminally if all gates pass. If a new boundary fails, checkpoint only that first new failure and repair forward.

## Validation remaining

- scoped hosted-assistant environment/state-path repair;
- canonical assistant health;
- real public HTTPS assistant turn with receipt verification;
- terminal repository-visible production checkpoint.

No full production-completion claim is valid until the assistant gate is green.
