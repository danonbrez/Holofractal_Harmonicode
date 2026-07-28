# HHS PASS 166 — WORD2VEC LANGUAGE-MODALITY MODEL ACQUISITION AND PREINSTALLATION SERVICE

## Verified Download, Canonical Model Import, 5,184-Bit Language Projection Registration, Offline Activation, Shell and API Control, and Receipt-Closed Installation

# 1. Normative metadata

| Field | Normative value |
|---|---|
| Contract identifier | `HHS-P166-W2V-LMVS-MAIS` |
| Pass number | `166` |
| Canonical pass name | `WORD2VEC_LANGUAGE_MODALITY_VECTOR_STORE_MODEL_ACQUISITION_IMPORT_AND_PREINSTALLATION_SERVICE` |
| Short name | `P166 Word2Vec Preinstaller` |
| Contract version | `1.0.0` |
| Repository | `danonbrez/Holofractal_Harmonicode` |
| Authoritative repository baseline | Pass 165 contract commit and all inherited authoritative repository history |
| Immediate inheritance parent | Complete authoritative Pass 165 inherited pass-history nucleus |
| Target application service | Pass 165 language-modality vector store |
| Primary control surfaces | Shell command, HTTP API, and internal callable API |
| Installation mode | Explicit, verified, resumable, idempotent, and rollback-capable |
| Runtime mode after installation | Local and offline-capable |
| Canonical commit authority | Exactly one VM81 runtime authority kernel |
| Model identity | Content digest plus normalized model-manifest root |
| Historical evidence | Hash72 installation receipt and Hash216 operation identity |
| Delivery model | Additive, incremental, source-oriented, append-only |
| Validation policy | Dependency-scoped, bounded stage-gate, repair-forward |
| Initial status | `CONTRACT_AUTHORIZED — IMPLEMENTATION REQUIRED` |

# 2. Normative language

The terms **SHALL**, **SHALL NOT**, **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative.

This document defines implementation requirements. It does not itself constitute implementation, successful download, model installation, activation, runtime validation, or terminal verification.

# 3. Required result

Pass 166 SHALL implement a shell command and equivalent API function that:

1. resolve an authorized Word2Vec package;
2. download the package into a quarantine staging area;
3. verify its source, declared size, and cryptographic digest;
4. detect and validate its vector-file format;
5. install the required local Word2Vec loading runtime;
6. import the pretrained vocabulary and vectors;
7. convert vectors into the canonical Pass 165 representation;
8. register the model inside the language-modality vector store;
9. build deterministic lookup and nearest-neighbor indexes;
10. activate the model for offline language ingestion;
11. generate installation, import, and activation receipts;
12. support deterministic replay, repair, rollback, and removal.

The canonical flow SHALL be:

```text
authorized install request
→ model-source resolution
→ license and manifest inspection
→ resumable download
→ quarantine storage
→ byte-length verification
→ cryptographic digest verification
→ archive safety validation
→ format detection
→ Word2Vec runtime installation
→ source-vector decoding
→ vocabulary normalization
→ canonical vector conversion
→ 5184-bit projection registration
→ vector-index construction
→ compatibility tests
→ VM81 admission
→ atomic activation
→ Hash72/Hash216 receipts
```

# 4. Word2Vec package definition

Pass 166 SHALL distinguish between:

```text
WORD2VEC_RUNTIME
WORD2VEC_PRETRAINED_MODEL
```

The runtime is the local implementation capable of reading and querying Word2Vec vectors.

The pretrained model is the external vocabulary and associated vector matrix.

Installing the runtime alone SHALL NOT constitute successful model installation. Downloading a vector file without validating and registering it SHALL NOT constitute successful preinstallation.

A model package SHALL bind:

```text
Word2VecPackage = (
    package_id,
    display_name,
    provider,
    source_uri,
    source_version,
    license_id,
    license_uri,
    expected_byte_length,
    expected_digest_algorithm,
    expected_digest,
    archive_type,
    vector_format,
    vector_dimension,
    vocabulary_size,
    character_encoding,
    normalization_profile,
    import_profile,
    compatibility_requirements
)
```

# 5. Canonical shell command

The primary shell command SHALL be equivalent to:

```bash
hhs model install word2vec
```

The explicit language-modality form SHALL be:

```bash
hhs modality language model install word2vec
```

The command SHALL accept options equivalent to:

```bash
hhs model install word2vec \
  --model <registered-model-id> \
  --source <authorized-uri-or-manifest> \
  --sha256 <expected-digest> \
  --license-accept \
  --activate \
  --offline-ready
```

Required command variants SHALL include:

```bash
hhs model word2vec list
hhs model word2vec inspect <model-id>
hhs model word2vec install <model-id>
hhs model word2vec verify <model-id>
hhs model word2vec activate <model-id>
hhs model word2vec deactivate <model-id>
hhs model word2vec repair <model-id>
hhs model word2vec remove <model-id>
hhs model word2vec receipt <operation-id>
```

The default install command SHALL resolve only a model registered in an authoritative package manifest. It SHALL NOT download an arbitrary moving target from an unpinned URL.

# 6. Shell exit contract

The command SHALL return stable exit classes:

| Exit | Meaning |
|---:|---|
| `0` | Installation or idempotent verification succeeded |
| `2` | Invalid arguments or unsupported profile |
| `3` | Authorization or license requirement failed |
| `4` | Source resolution or network transfer failed |
| `5` | Size, digest, or archive-integrity verification failed |
| `6` | Unsupported or malformed Word2Vec data |
| `7` | Canonical conversion failed |
| `8` | Vector-index construction failed |
| `9` | VM81 admission or activation failed |
| `10` | Receipt or deterministic replay closure failed |
| `11` | Local storage or resource bound exceeded |
| `12` | Repair required because an existing installation is inconsistent |

Human-readable and machine-readable output SHALL be separated:

```bash
hhs model install word2vec --output text
hhs model install word2vec --output json
```

# 7. HTTP API

The external API SHALL expose operations equivalent to:

```http
POST   /v1/modalities/language/models/word2vec/install
GET    /v1/modalities/language/models/word2vec
GET    /v1/modalities/language/models/word2vec/{model_id}
POST   /v1/modalities/language/models/word2vec/{model_id}/verify
POST   /v1/modalities/language/models/word2vec/{model_id}/activate
POST   /v1/modalities/language/models/word2vec/{model_id}/deactivate
POST   /v1/modalities/language/models/word2vec/{model_id}/repair
DELETE /v1/modalities/language/models/word2vec/{model_id}
GET    /v1/model-operations/{operation_id}
GET    /v1/model-operations/{operation_id}/receipt
```

The canonical install request SHALL be equivalent to:

```json
{
  "model_id": "word2vec-default",
  "source_manifest_id": "registered-word2vec-default-v1",
  "expected_sha256": "<required-pinned-digest>",
  "accept_license": true,
  "activate": true,
  "offline_ready": true,
  "replace_existing": false
}
```

The API SHALL reject an unpinned remote source unless an authorized manifest supplies its expected identity and policy.

# 8. Internal callable API

The implementation SHALL expose a versioned callable surface equivalent to:

```c
hhs_status hhs_word2vec_resolve(
    hhs_runtime *runtime,
    const hhs_word2vec_install_request *request,
    hhs_word2vec_package_manifest *manifest_out
);

hhs_status hhs_word2vec_download(
    hhs_runtime *runtime,
    const hhs_word2vec_package_manifest *manifest,
    hhs_download_result *result_out
);

hhs_status hhs_word2vec_verify(
    hhs_runtime *runtime,
    const hhs_download_result *download,
    hhs_verification_result *result_out
);

hhs_status hhs_word2vec_import(
    hhs_runtime *runtime,
    const hhs_verified_artifact *artifact,
    hhs_word2vec_import_result *result_out
);

hhs_status hhs_word2vec_activate(
    hhs_runtime *runtime,
    const hhs_model_identity *model,
    hhs_activation_receipt *receipt_out
);

hhs_status hhs_word2vec_install(
    hhs_runtime *runtime,
    const hhs_word2vec_install_request *request,
    hhs_word2vec_install_receipt *receipt_out
);
```

Bindings MAY expose equivalent Python, TypeScript, Java, Kotlin, or HARMONICODE functions, but all bindings SHALL enter the same authoritative installation path.

# 9. Installation lifecycle

Every model installation SHALL occupy an explicit lifecycle state:

```text
UNRESOLVED
→ RESOLVED
→ DOWNLOAD_PENDING
→ DOWNLOADING
→ QUARANTINED
→ BYTE_VERIFIED
→ DIGEST_VERIFIED
→ FORMAT_VERIFIED
→ IMPORTING
→ INDEXING
→ VALIDATED
→ INSTALLED
→ ACTIVE
```

Failure states SHALL include:

```text
DOWNLOAD_FAILED
INTEGRITY_FAILED
FORMAT_REJECTED
IMPORT_FAILED
INDEX_FAILED
ADMISSION_REJECTED
ACTIVATION_FAILED
REPAIR_REQUIRED
REMOVED
```

Only a model in `VALIDATED` or `INSTALLED` state may transition to `ACTIVE`.

# 10. Download requirements

The downloader SHALL support:

- HTTPS transport;
- resumable range downloads when supported;
- bounded retries;
- explicit timeouts;
- temporary partial-file suffixes;
- free-space preflight checks;
- maximum download bounds;
- redirect policy;
- proxy configuration;
- cancellation;
- progress reporting;
- deterministic finalization.

A partial transfer SHALL never be visible as an installed model.

The canonical path SHALL separate:

```text
downloads/partial/
downloads/quarantine/
models/word2vec/packages/
models/word2vec/active/
```

The repository SHALL contain manifests, source code, tests, and small fixtures only. Large pretrained model binaries SHALL remain external installation artifacts rather than ordinary Git history.

# 11. Integrity and supply-chain controls

Before extraction or parsing, the service SHALL verify:

```text
actual_byte_length == expected_byte_length
actual_digest == expected_digest
```

At minimum, SHA-256 SHALL be supported.

The package manifest SHALL be incorporated into the Hash216 installation-operation identity.

The service SHALL reject:

- digest mismatch;
- truncated transfer;
- ambiguous archive roots;
- path traversal;
- absolute archive paths;
- symbolic-link escape;
- device files;
- decompression bombs;
- duplicate conflicting entries;
- unsupported compression;
- undeclared executable payloads;
- model-dimension mismatch;
- vocabulary-count mismatch;
- malformed numeric values.

Network success SHALL NOT imply integrity success.

# 12. Supported Word2Vec formats

The importer SHALL support versioned readers for at least:

```text
WORD2VEC_BINARY
WORD2VEC_TEXT
```

Optional adapters MAY support compatible keyed-vector containers, provided the original format and adapter version are recorded.

Each decoded source vector SHALL preserve:

```text
SourceVector = (
    source_token_bytes,
    decoded_token,
    source_row,
    source_dimension,
    source_numeric_encoding,
    source_values,
    source_model_root
)
```

Malformed vectors, non-finite values, inconsistent dimensions, and duplicate-token ambiguity SHALL be handled according to a declared import policy rather than silently repaired.

# 13. Vocabulary normalization

The original token identity SHALL be preserved.

Normalized lookup aliases MAY be generated through registered profiles such as:

```text
VERBATIM
UNICODE_NFC
UNICODE_NFKC
CASE_FOLDED
LANGUAGE_SPECIFIC
```

The canonical record SHALL distinguish:

```text
source_token != normalized_alias
```

Alias collisions SHALL reference all source tokens involved and SHALL NOT silently collapse them into one historical object.

# 14. Canonical vector conversion

Downloaded Word2Vec components are external numeric evidence. They SHALL be converted into a deterministic HHS representation before authoritative use.

For source component `x`, the conversion SHALL produce:

```text
Q(x) = canonical_quantize(x, profile_id)
```

The conversion profile SHALL bind:

```text
numeric source encoding
target integer width
scale or denominator
rounding rule
clipping bounds
zero rule
sign rule
non-finite rejection rule
normalization rule
```

The imported vector SHALL bind both:

```text
source_vector_digest
canonical_vector_digest
```

Host-specific floating-point parsing SHALL NOT be allowed to produce different canonical model identities on different architectures.

# 15. Pass 165 vector-store integration

Each imported lexical object SHALL become a registered language-modality object:

```text
LanguageVectorObject = (
    lexical_object_id,
    source_token_identity,
    normalized_aliases,
    canonical_vector_identity,
    dimensionality,
    source_model_identity,
    projection_5184_root,
    relation_index_root,
    provenance_root
)
```

Word2Vec dimensions SHALL NOT be confused with the fixed 5,184-bit shared projection.

The distinction is binding:

```text
Word2Vec dense parameter vector
!=
Pass 165 canonical 5184-bit activation frame
```

The dense vector SHALL be stored as an immutable referenced parameter object. The 5,184-bit frame SHALL express registered activation, routing, relation, authority, and feature states associated with that object.

# 16. Projection and routing

The language modality SHALL project Word2Vec-derived features into the Pass 165 geometry:

```text
P[token][p][t] ∈ {0,1}
81 × 64 = 5184 bits
```

Projection SHALL be deterministic under a registered projection version.

Projection MAY encode:

- lexical presence;
- vocabulary membership;
- semantic-neighborhood membership;
- relation class;
- similarity band;
- dimensional partition activation;
- invariant association;
- provenance state;
- confidence band;
- contradiction state;
- model identity;
- validation status.

The projection SHALL NOT discard the underlying dense vector.

# 17. Vector indexes

Installation SHALL build indexes sufficient for:

```text
exact token lookup
normalized alias lookup
nearest-neighbor query
analogy or vector-offset query
source-vector retrieval
canonical-vector retrieval
5184-bit projection retrieval
provenance retrieval
```

The index implementation MAY use exact or approximate nearest-neighbor acceleration, but the selected method and parameters SHALL be versioned.

Approximate search results SHALL be identified as approximate. Approximate indexes SHALL NOT redefine the immutable source vectors.

# 18. Query API after installation

The activated model SHALL support calls equivalent to:

```http
GET  /v1/modalities/language/vectors/{token}
POST /v1/modalities/language/similarity
POST /v1/modalities/language/nearest
POST /v1/modalities/language/analogy
POST /v1/modalities/language/project
```

Example:

```json
{
  "model_id": "word2vec-default",
  "token": "language",
  "top_k": 16,
  "include_projection_5184": true,
  "include_provenance": true
}
```

Every result SHALL identify the model, model version, import profile, and vector identity used.

# 19. Idempotence and existing installations

Repeated installation of an identical package SHALL return the existing verified model identity rather than duplicate the full model.

The idempotence key SHALL include:

```text
package digest
manifest root
runtime version
import profile
quantization profile
projection version
index configuration
```

A differing profile SHALL produce a new versioned installation rather than silently mutating the existing model.

# 20. Offline operation

After successful preinstallation, all required runtime files, canonical vectors, vocabularies, indexes, manifests, and receipts SHALL be locally available.

The following operations SHALL NOT require network access:

```text
token lookup
vector retrieval
similarity
nearest-neighbor search
language projection
Pass 165 ingestion
receipt inspection
deterministic model verification
```

Network access after activation SHALL require a distinct update, repair, or replacement operation.

# 21. Authority boundary

Download workers, archive readers, parsers, model loaders, and index builders may create candidate artifacts.

They SHALL NOT directly activate a model.

The required path is:

```text
candidate model installation
→ integrity validation
→ format validation
→ canonical conversion
→ index validation
→ Pass 165 compatibility validation
→ VM81 admission
→ atomic active-model registry update
→ permanent Hash72/Hash216 evidence
```

# 22. Receipts

Pass 166 SHALL emit separate receipts for:

```text
SOURCE_RESOLUTION
LICENSE_ACCEPTANCE
DOWNLOAD
INTEGRITY_VERIFICATION
FORMAT_VERIFICATION
IMPORT
CANONICAL_CONVERSION
INDEX_BUILD
COMPATIBILITY_VALIDATION
ACTIVATION
ROLLBACK
REMOVAL
```

The terminal installation receipt SHALL bind:

```text
operation_id
package_id
source_uri_identity
package_digest
manifest_root
license_identity
runtime_version
source_vector_format
source_dimension
source_vocabulary_size
canonical_conversion_profile
canonical_model_root
projection_registry_version
index_root
Pass 165 vector-store frontier
incoming Hash72 root
outgoing Hash72 root
Hash216 installation identity
activation state
replay result
```

# 23. Rollback and removal

Activation SHALL be atomic.

If activation fails, the previously active language model SHALL remain unchanged.

Removal SHALL distinguish:

```text
DEACTIVATE
REMOVE_INDEXES
REMOVE_CANONICAL_IMPORT
REMOVE_DOWNLOADED_PACKAGE
PURGE_ALL_NONHISTORICAL_RESIDENCY
```

Permanent receipts and committed provenance SHALL NOT be erased by ordinary model removal.

# 24. Required positive tests

Implementation evidence SHALL demonstrate:

1. successful manifest resolution;
2. resumable fixture download;
3. digest verification;
4. safe archive extraction;
5. Word2Vec text import;
6. Word2Vec binary import;
7. exact vocabulary count;
8. exact dimensionality validation;
9. deterministic canonical conversion;
10. identical model roots across supported architectures;
11. deterministic 5,184-bit projection;
12. exact token lookup;
13. nearest-neighbor query;
14. offline query operation;
15. idempotent reinstall;
16. activation rollback;
17. shell/API equivalence;
18. Hash72 receipt closure;
19. Hash216 operation identity;
20. deterministic replay.

# 25. Required negative tests

Pass 166 SHALL reject or safely contain:

```text
unpinned moving download
digest mismatch
truncated file
redirect to disallowed host
insufficient storage
archive traversal
decompression bomb
malformed Word2Vec header
mixed vector dimensions
invalid token encoding
duplicate-token conflict
NaN
positive infinity
negative infinity
numeric overflow
unsupported quantization profile
nondeterministic conversion
stale Pass 165 frontier
unauthorized activation
direct downloader commit
index/model identity mismatch
offline dependency omission
receipt mismatch
replay divergence
```

# 26. Completion condition

Pass 166 is complete only when executable evidence establishes:

```text
shell command implemented
HTTP API implemented
internal callable API implemented
verified model acquisition
safe local preinstallation
Word2Vec format parsing
deterministic canonical conversion
Pass 165 language-store registration
5184-bit projection compatibility
offline lookup and similarity
atomic VM81-governed activation
rollback and repair
Hash72/Hash216 receipt closure
cross-architecture deterministic replay
```

The terminal implementation receipt SHALL be:

```text
HHS_PASS_166_WORD2VEC_LANGUAGE_MODALITY_MODEL_ACQUISITION_IMPORT_PREINSTALLATION_AND_OFFLINE_ACTIVATION_VERIFIED
```
