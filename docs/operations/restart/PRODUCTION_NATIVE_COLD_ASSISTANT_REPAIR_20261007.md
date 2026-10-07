# Production Native Cold Assistant Repair Checkpoint — 2026-10-07

## Restart identity

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base `main`: `813b1cdcd212fd219a0f7c1e476c01e87b74038f`
- Repair branch: `repair/production-native-cold-assistant-20261007`
- Pull request: #734 — `Repair production native assistant cold-turn timeout`
- Code-bearing head before this checkpoint: `d06bf06f3121530541238cb064b87624eb1e24ac`
- Merge target: `main`
- Triggering Exact-Main run: `37613735841`
- Triggering deploy job: `112769670934`
- State: IMPLEMENTED; CI ACTIVE; PRODUCTION ACCEPTANCE NOT CLOSED

## Frozen failure evidence

Exact-Main run `37613735841` promoted SHA
`813b1cdcd212fd219a0f7c1e476c01e87b74038f` far enough to prove:

- `validate-deployment-contract`: PASS
- `validate-production-backend-closure`: PASS
- Python compilation: PASS
- native C/C++ compilation/execution: PASS
- production assistant import closure: PASS
- in-process two-turn backend closure: PASS
- dependency-scoped regressions: PASS
- Runtime OS bundle build/transfer: PASS
- `HHS_P174_BOOT_READY`: reached
- `/api/system/status`: HTTP 200
- `/api/interface/status`: HTTP 200
- `/api/runtime/services`: HTTP 200
- `/`: HTTP 200
- exact SHA present in deployed Runtime OS path

The first direct deployed assistant request then failed with:

```text
RuntimeError: assistant request failed: TimeoutError: timed out
```

The failure was the first `POST /api/assistant/chat` against
`127.0.0.1:8080`, producing workflow exit 25. The Lane 5 `:8715` probe,
public HTTPS verification, and Chromium acceptance were not reached.

## Repaired boundary

The cold native path had two avoidable readiness costs before the exact-memory
fast path:

1. `ProductionAssistantService.send_message()` performed a native
   `health()` preflight before attempting the selected native provider.
2. Native `health() -> list_models() -> installation_status()` imported and
   probed Pass 166 Word2Vec even when production declares Word2Vec optional.
3. The synchronous installation closure ran inside async coroutines, so
   `asyncio.wait_for` could not preempt a cold synchronous import.

The actual native turn already performs fail-closed readiness plus provider
proposal/policy, Native Lean admission, provider receipt, and result ingress.
Therefore the preflight duplicated readiness rather than supplying authority.

## Implemented changes

### `hhs_backend/runtime/hhs_native_litert_lm_provider_v1.py`

- Optional Word2Vec is now genuinely lazy during installation status.
- Pass 166 Word2Vec is still checked when required or explicitly injected.
- Optional status reports `OPTIONAL_WORD2VEC_STATUS_DEFERRED`.
- `list_models()` runs `_require_ready` with `asyncio.to_thread`.
- `chat_completion()` runs `_require_ready` with `asyncio.to_thread`.
- Full installation closure remains required before model admission.

### `hhs_backend/runtime/hhs_production_assistant_v1.py`

- Native-first production no longer performs duplicate native health preflight.
- It executes the selected governed native turn directly.
- The native transport still performs readiness and all authority gates.
- Failed/incomplete native turns still enter the existing fail-closed fallback
  path and only then probe Pass 153.

### Production service

`deploy/digitalocean/hhs-pass196-integrated-environment.service` now explicitly
sets:

```text
HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC=0
```

This matches the existing guarded updater/deployment production contract.

### Dependency-scoped regressions

Updated:

- `tests/pass220/test_hhs_pass220_unified_chatbot_lane5_model_fabric.py`
  - native-first success performs zero native health preflights;
  - failed native execution still probes and uses Pass 153;
  - one witnessed user message is preserved across failover.
- `tests/pass220/test_hhs_pass220_i009_native_causal_rag_generation.py`
  - optional Word2Vec cannot be imported by cold readiness;
  - exact-memory acknowledgement remains admitted through native readiness.
- `tests/test_hhs_digitalocean_promotion_rollback_repair_v1.py`
  - production runtime service must explicitly preserve Word2Vec optionality.

## Commit chain

- `4311767d0f83a2c5edea34a6740dd7d92bd69da4` — defer optional Word2Vec readiness on cold assistant path
- `51cb7d47c9ac793333d07a81c9e08be632456a4e` — execute native-first assistant before health preflight
- `643e5c1ad194f099f332b9748739cfe048884dcf` — set production Word2Vec optionality explicitly
- `3fe1ff4c8350957785979c6ed2e3912d4ddeabd6` — cover native-first execution without health preflight
- `74e8d649534ca826613039748cf05776a31b13e9` — regress cold exact-memory readiness without Word2Vec
- `d06bf06f3121530541238cb064b87624eb1e24ac` — assert production runtime Word2Vec optionality

## Validation state

Repository diff against base:

- 6 files changed
- 118 additions
- 11 deletions
- branch ahead by 6 commits
- branch behind by 0 commits

PR-triggered CI for code-bearing head `d06bf06f...` started immediately.
Relevant observed runs:

- `37632158898` — Pass 220 Unified Chatbot Lane 5 Model Fabric — IN PROGRESS at checkpoint
- `37632159127` — DigitalOcean Production Exact Main — QUEUED at checkpoint
- `37632159321` — LiteRT-LM Gemma 4 Assistant — QUEUED at checkpoint
- `37632159113` — Validate HHS Runtime OS Production Root — QUEUED at checkpoint
- `37632159050` — Pass 196 I130 Repair Validation — QUEUED at checkpoint

No CI result is claimed green by this checkpoint.

## Exact next action

1. Read PR #734 current head and current `main`; reconcile only if either moved.
2. Inspect the newest CI runs for the current PR head.
3. Repair only failures attributable to these six changed files.
4. When dependency-scoped gates are green, merge PR #734.
5. Verify merged `main` exactly.
6. Follow Exact-Main through, in order:
   - guarded promotion;
   - direct `127.0.0.1:8080` two-turn assistant probe;
   - Lane 5 `127.0.0.1:8715` two-turn assistant probe;
   - public HTTPS Runtime OS;
   - public service registry;
   - Chromium full workspace and two-turn assistant memory acceptance.
7. Do not raise the 30-second direct assistant timeout, bypass Lane 5, weaken
   native readiness, or waive Chromium acceptance.

## Blocker

Only external CI/deployment execution is pending at this checkpoint. The repair
is repository-visible and restartable from the branch/PR state above.
