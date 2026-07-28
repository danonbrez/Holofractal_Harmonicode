# HHS Creative Writing

This directory contains human-readable creative artifacts produced for, or regenerated through, the governed VM81 creative-writing runtime.

## Novel runtime surface

External callers use one endpoint only:

```text
POST /api/runtime/creative/novel
```

The command-line client at `tools/vm81_generate_novel.py` calls that VM81 runtime API. It does not call LiteRT-LM, Gemma, or a filesystem API directly.

Generated novels are persisted beneath:

```text
creative_writing/novels/
```

The runtime-configured root is controlled by `HHS_CREATIVE_WRITING_ROOT`; callers cannot supply an arbitrary output directory. The persistence step is performed through `hhs_runtime.hhs_persistence_guard_v1.export_text_artifact`, which emits the HHS egress and ledger evidence before writing the manuscript.

## Included reference novel

`novels/THE_NINTH_ARCHIVE.md` is a complete original seed manuscript committed alongside the runtime implementation. Its front matter deliberately records `runtime_execution_receipt: null`: the repository connector used to create this pass could not reach the deployed LiteRT-LM provider, so no live VM81 generation receipt is fabricated. Once the provider is available, the same path can be regenerated through the API.

## Run

Start the Pass 162 runtime composition:

```bash
python -m uvicorn hhs_backend.pass162_server:app \
  --host 0.0.0.0 \
  --port 8080 \
  --ws websockets
```

Generate or replace the reference novel through VM81:

```bash
python tools/vm81_generate_novel.py \
  --runtime-url http://127.0.0.1:8080 \
  --title "The Ninth Archive" \
  --chapters 9 \
  --target-words 9000 \
  --filename THE_NINTH_ARCHIVE.md
```

The JSON response includes the outline root, chapter roots, complete manuscript root, persistence evidence, VM81 authorized-tick projection, I/O records, word count, elapsed time, and optimization metadata.
