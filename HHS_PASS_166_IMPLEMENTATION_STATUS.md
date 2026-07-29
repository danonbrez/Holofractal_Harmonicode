# HHS Pass 166 implementation status

## Scope

Pass 166 implements the executable Word2Vec language-modality model acquisition, import, preinstallation, offline query, and governed activation surface required by `HHS-P166-W2V-LMVS-MAIS`.

## Implemented runtime

The Python service provides:

- authoritative registered package manifests with pinned byte length and SHA-256;
- explicit license acceptance and source-resolution receipts;
- resumable local and HTTPS acquisition into partial and quarantine directories;
- redirect-host controls, package bounds, byte verification, and digest verification;
- safe ZIP, TAR, and TAR.GZ extraction with traversal, symlink, device, duplicate-entry, and decompression-bound rejection;
- strict Word2Vec text and binary readers;
- exact decimal parsing and exact IEEE-754 binary32 bit decoding;
- deterministic signed Q16.16 half-even canonical conversion without host-float identity authority;
- immutable dense-vector identities distinct from 5,184-bit Pass 165 activation frames;
- deterministic language-vector objects, alias maps, projection roots, provenance roots, and exact index roots;
- exact token lookup, source/canonical vector retrieval, similarity ranking, nearest-neighbor search, analogy, and projection retrieval;
- local offline verification and deterministic replay from the installed source package;
- idempotent reinstall, explicit replacement, repair, deactivate, remove, and historical receipt preservation;
- validate-then-commit model activation through the singleton inherited VM81 runtime;
- rollback before VM81 admission without changing the prior active model or VM81 state;
- append-only checksummed Hash72/Hash216 operation receipts and restart verification.

## Control surfaces

```text
python tools/hhs_model.py model install word2vec <model-id> ...
python tools/hhs_model.py modality language model install word2vec <model-id> ...
uvicorn hhs_backend.pass166_server:app --host 0.0.0.0 --port 8000
```

The HTTP API is rooted at:

```text
/v1/modalities/language/models/word2vec
/v1/modalities/language/vectors
/v1/modalities/language/similarity
/v1/modalities/language/nearest
/v1/modalities/language/analogy
/v1/modalities/language/project
```

## Native ABI

The strict C11 companion provides bounded manifest geometry validation, exact rational Q16.16 conversion, checked integer dot products, and fixed 5,184-bit projection frame operations. It has no model activation authority.

## Validation state

The source, tests, workflow, and bounded evidence surfaces are present. Repository-level execution is pending the Pass 166 pull-request workflow.

## Classification

```text
HHS_PASS_166_CONTRACT_BOUND
HHS_PASS_166_WORD2VEC_ACQUISITION_IMPORT_AND_PREINSTALLATION_IMPLEMENTED
```

Not yet claimed:

```text
HHS_PASS_166_WORD2VEC_LANGUAGE_MODALITY_MODEL_ACQUISITION_IMPORT_PREINSTALLATION_AND_OFFLINE_ACTIVATION_VERIFIED
```
