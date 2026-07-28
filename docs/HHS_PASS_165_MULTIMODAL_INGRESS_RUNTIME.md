# Pass 165 multimodal ingestion runtime

## Start

In-memory bounded reference mode:

```bash
uvicorn hhs_backend.pass165_server:app --host 0.0.0.0 --port 8000
```

Durable append-only mode:

```bash
HHS_PASS165_STORAGE_DIR=.hhs/runtime/pass165 \
uvicorn hhs_backend.pass165_server:app --host 0.0.0.0 --port 8000
```

The durable directory contains:

```text
ingestion.journal.jsonl   append-only checksummed complete records
frontier.json             atomically replaced admitted frontier
quarantine.log            incomplete-tail and stale-frontier evidence
```

## Ingest

`POST /api/runtime/multimodal-ingress/ingest`

```json
{
  "source_b64": "YWxwaGEgYWxwaGE=",
  "declared_media_type": "TEXT",
  "provenance": "local-upload",
  "authorization_scope": "KNOWLEDGE_INGEST"
}
```

The API accepts source bytes only through a bounded Base64 envelope. Original bytes are retained and are never replaced by tokens, interpretations, projections, or learned weights.

Tokenizers, modality adapters, invariant extractors, and backward-credit workers produce derived objects and proposals. They cannot commit canonical state. Exact weight deltas are admitted only through the singleton inherited `VMRCRuntime`.

Repeated source hashes reuse the prior ingestion receipt. Projection is sparse and fixed at 648 bytes. Weight updates are residual-only, exact rational, dependency-scoped, contradiction-aware, and bounded to `1/16` per ingestion epoch.

## Operations

```text
GET  /api/runtime/multimodal-ingress/status
POST /api/runtime/multimodal-ingress/ingest
GET  /api/runtime/multimodal-ingress/invariants
GET  /api/runtime/multimodal-ingress/receipts/{source_hash}
POST /api/runtime/multimodal-ingress/replay
POST /api/runtime/multimodal-ingress/recover
```

`recover` is available only when durable mode is enabled. Recovery verifies every complete journal record, deterministically replays it through VM81 admission, repairs stale frontier metadata, quarantines incomplete tails, and rejects altered complete records.

## Terminal validation

The repository terminal matrix constructs PDF, PNG, WAV, and MP4 fixtures from repository source at test time. It validates each format independently before Pass 165 ingestion. Generated media are not committed.

```bash
python -m pytest -q \
  tests/test_hash72_digest_v1.py \
  tests/test_hhs_pass163_vmrc_v1.py \
  tests/test_hhs_pass164_gcmsl_v1.py \
  tests/test_hhs_pass165_multimodal_ingress_v1.py \
  tests/test_hhs_pass165_terminal_v1.py

python tools/pass165_terminal_evidence.py \
  --output /tmp/P165_TERMINAL_EXECUTION.json

make -C native_projects/hhs_pass163_vmrc clean test
make -C native_projects/hhs_pass164_gcmsl clean test
make -C native_projects/hhs_pass165_mmvs clean test
```

Terminal evidence is recorded in:

```text
evidence/pass165/P165_TERMINAL_EXECUTION.json
evidence/pass165/P165_COMPLETION_RECEIPT.json
```

Terminal classification:

```text
HHS_PASS_165_LIGHTWEIGHT_5184BIT_MULTIMODAL_VECTOR_STORE_INGESTION_TOKENIZATION_INVARIANT_EXTRACTION_AND_GOVERNED_BACKPROPAGATION_VERIFIED
```
