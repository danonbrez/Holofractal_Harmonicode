# Pass 166 Word2Vec acquisition and offline runtime

## Storage layout

The default local root is `.hhs/pass166`. Set `HHS_PASS166_STORAGE_DIR` or use `--storage-root` to select another governed location.

```text
downloads/partial/
downloads/quarantine/
models/word2vec/packages/
models/word2vec/active/
models/word2vec/registry.json
receipts/operations.jsonl
```

Partial and quarantined files are never treated as installed models. Large pretrained packages remain external installation artifacts and are not committed to Git.

## Register a pinned manifest

```bash
python tools/hhs_model.py model word2vec register-manifest manifest.json
```

A manifest must bind the source URI, source version, license identity, expected byte length, SHA-256, archive type, Word2Vec format, dimension, vocabulary count, normalization profile, quantization profile, projection version, and index version.

Only `file:` and `https:` sources are accepted. Remote redirects must remain on the source host or an explicitly allowed host.

## Install

Both documented command forms enter the same implementation:

```bash
python tools/hhs_model.py model install word2vec word2vec-default \
  --manifest manifest.json \
  --license-accept \
  --activate \
  --offline-ready \
  --output json
```

```bash
python tools/hhs_model.py modality language model install word2vec word2vec-default \
  --manifest manifest.json \
  --license-accept \
  --activate \
  --offline-ready
```

Installation performs resolution, license binding, acquisition, byte and digest verification, archive validation, text or binary parsing, exact canonical conversion, deterministic index construction, Pass 165 compatibility validation, VM81 admission, local package persistence, and atomic active-registry update.

## Exact numeric conversion

Text components are parsed through decimal arithmetic and converted to exact rational values. Binary components are decoded directly from their IEEE-754 binary32 bit patterns into exact rational values. Both enter the registered conversion profile:

```text
HHS-P166-Q16_16-HALF_EVEN-1.0.0
```

Canonical vector identity uses signed 32-bit integer components with denominator `65536`. NaN, positive infinity, negative infinity, overflow, and inconsistent dimensions are rejected.

The dense Word2Vec vector remains immutable external numeric evidence. It is not replaced by the fixed Pass 165 projection:

```text
Word2Vec dense vector != 5,184-bit activation frame
```

## Offline query

After installation, these operations use only local registry, vector, index, package, and receipt state:

```bash
python tools/hhs_model.py model word2vec vector language
python tools/hhs_model.py model word2vec similarity language model
python tools/hhs_model.py model word2vec nearest language --top-k 16
python tools/hhs_model.py model word2vec analogy --positive king --positive woman --negative man
python tools/hhs_model.py model word2vec project language
python tools/hhs_model.py model word2vec verify word2vec-default
python tools/hhs_model.py model word2vec replay word2vec-default
```

Similarity and nearest-neighbor ordering use an exact sign plus squared-cosine rational key. The implementation does not use host floating point as canonical ranking authority.

## Lifecycle management

```bash
python tools/hhs_model.py model word2vec list
python tools/hhs_model.py model word2vec inspect word2vec-default
python tools/hhs_model.py model word2vec activate word2vec-default
python tools/hhs_model.py model word2vec deactivate word2vec-default
python tools/hhs_model.py model word2vec repair word2vec-default
python tools/hhs_model.py model word2vec remove word2vec-default
python tools/hhs_model.py model word2vec receipt <operation-id>
```

Ordinary removal preserves the append-only receipt and provenance history. Package residency is deleted only when `--purge-package` is explicitly supplied.

## HTTP server

```bash
uvicorn hhs_backend.pass166_server:app --host 0.0.0.0 --port 8000
```

The service composes all inherited Pass 165 routes and adds the Pass 166 management and language-vector query endpoints defined by the formal contract.

## Authority boundary

Downloaders, archive readers, format parsers, index builders, HTTP handlers, shell clients, and native C helpers create candidates only. They cannot activate a model directly. Activation is admitted through one inherited VM81 runtime using the `P166_MODEL_ACTIVATION` capability scope.
