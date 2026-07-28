# Pass 165 multimodal ingestion runtime

## Start

```bash
uvicorn hhs_backend.pass165_server:app --host 0.0.0.0 --port 8000
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
