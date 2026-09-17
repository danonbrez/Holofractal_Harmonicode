# Pass 219 — Server Projector Production v1

## Status

Implementation contract for the production application-service bridge above the already validated Pass 219 live acquisition/replay worker and approved external projector.

This surface is **candidate-only**. It does not acquire canonical VM81, canonical Hash72, 216-symbol Hash216, truth/action, learning-commit, or permanent-prune authority.

## Purpose

Remove the manual copy/paste boundary between approved external model execution and the persistent acquisition service while preserving the existing authority membrane.

The production click-through path is:

```text
immutable source descriptor
→ provider-derived pinned HTTPS fetch
→ exact byte length + SHA-256 verification
→ verified RepositoryArtifact
→ isolated approved projector subprocess
→ exact sealed EXTERNAL_EVIDENCE_V1
→ same captured verified source bytes
→ persistent acquisition job + replay bundle
→ network-free/model-free replay
```

## 1. Verify before inference

The approved subprocess SHALL receive source bytes only through `ExternalProjector.project(RepositoryArtifact)` after `LiveAcquisitionReplayWorker.execute_live()` has completed source URL/status/length/SHA validation.

A source length or SHA mismatch SHALL result in:

- zero model executions;
- zero persistent acquisition jobs from this bridge;
- zero candidate promotion.

## 2. Exactly one live fetch and one model execution

The server bridge SHALL perform exactly one provider fetch and one approved external model execution for a successful request.

Persistence SHALL reuse the captured verified `FetchResponse` through a static transport. It SHALL NOT perform a second network fetch.

Persistence SHALL consume the already sealed `EXTERNAL_EVIDENCE_V1` row. It SHALL NOT execute the model a second time.

The response MUST expose counters proving:

- `network_fetch_count == 1`;
- `external_model_execution_count == 1`;
- `persistence_network_fetch_count == 0`;
- `persistence_external_model_execution_count == 0`.

## 3. Isolated runtime

The FastAPI/VM81 application process SHALL NOT import PyTorch or `sentence-transformers` as part of normal server startup.

Approved inference SHALL execute as a subprocess using:

```text
/opt/hhs/pass219-projector-venv/bin/python
```

The dependency environment SHALL be isolated from `/opt/hhs/venv`.

Production dependency pin:

```text
sentence-transformers==5.1.1
```

The model cache SHALL live under:

```text
/var/lib/hhs/models/huggingface
```

## 4. Approved profile

Production server execution v1 admits only:

```text
MULTILINGUAL_MPNET_TEXT_V1
```

with the previously admitted immutable model:

```text
sentence-transformers/paraphrase-multilingual-mpnet-base-v2
revision 79f2382ceacceacdf38563d7c5d16b9ff8d725d6
Apache-2.0
```

`MULTILINGUAL_CLIP_IMAGE_TEXT_V1` remains blocked until the companion image-model license boundary is explicitly resolved and validated.

No API caller can override the admitted model repository or revision.

## 5. Runtime hardening

The subprocess SHALL inherit a bounded server-controlled timeout and device selection.

Default production settings:

```text
HHS_P219_PROJECTOR_TIMEOUT_SECONDS=900
HHS_P219_PROJECTOR_DEVICE=cpu
TOKENIZERS_PARALLELISM=false
OMP_NUM_THREADS=1
MKL_NUM_THREADS=1
```

The projector continues to require:

- `trust_remote_code=False`;
- safetensors request;
- finite vectors;
- non-zero norms;
- matching vector dimensions;
- bounded exact-rational similarity witness after empirical floating observation.

## 6. API

The production API SHALL expose:

```text
POST /api/v1/pass174/acquisition/jobs/execute
```

The request supplies:

- the same immutable `source` descriptor used by acquisition jobs;
- an `execution` object containing the approved profile ID, pivot text/language, and optional semantic labels/translation chain.

Source language and modality used by inference SHALL be derived from the verified `RepositoryArtifact`, not independently trusted from projection evidence.

The execution route MUST be registered before the dynamic `/jobs/{job_id}` route.

## 7. Mobile control

The production mobile acquisition panel SHALL offer three distinct paths:

1. **Approved server projector** — one-click verify → infer → persist.
2. **Verify source only** — no semantic model execution.
3. **Manual sealed evidence** — retained as an expert/debug fallback.

Raw diagnostic JSON SHALL be collapsed by default behind an explicit details control. Primary job state, classification, receipt, profile, and replay closure SHALL be visible as normal UI fields.

## 8. Replay

A completed server-executed job SHALL persist the same replay bundle format already established by the acquisition job service.

Offline replay SHALL prove:

```text
network_fetch_performed == false
external_model_execution_performed == false
```

and SHALL reproduce the expected replay closure.

## 9. Deployment

Exact-main deployment installs the normal HHS service independently of the heavy ML runtime.

After `DigitalOcean Production Exact Main` succeeds, the dedicated Pass 219 production workflow SHALL:

1. prove the production checkout SHA equals the promoted exact-main SHA;
2. create/reuse the isolated projector venv;
3. install the exact dependency pin when its requirements digest changes;
4. warm the immutable model into the durable Hugging Face cache;
5. prove `/acquisition/status` reports `runtime_ready=true`;
6. run a real immutable-source server projection;
7. require a completed translation-invariant candidate job;
8. replay it offline with no network/model execution;
9. verify the public HTTPS control surface reports the projector ready.

Failure of the isolated projector install/warm/proof does not mutate canonical VM81 state. The production application remains fail-closed for `/jobs/execute` until `runtime_ready=true`.

## 10. Rollback compatibility

The isolated ML runtime is not inserted into the guarded updater's canonical rollback command and does not mutate the main HHS venv. Older application commits may ignore the dedicated projector venv/cache without requiring its removal.

## 11. Required negative cases

Validation SHALL include at minimum:

- source digest/length mismatch prevents model execution;
- blocked profile prevents network and model execution;
- projector subprocess failure preserves its classification and creates no persisted job;
- execute route precedes the dynamic job route;
- replay performs no network fetch and no model execution;
- canonical Hash72/Hash216/VM81 authority remains false.

## 12. Authority statement

Successful execution means only that a pinned external model produced candidate semantic evidence from already verified source bytes and that the evidence was persisted/replayed consistently.

It does **not** mean:

- the model output is canonical truth;
- a VM81 transition was committed;
- canonical Hash72 was minted;
- 216-symbol canonical Hash216 was minted;
- canonical learning was committed;
- irreversible pruning was authorized.
