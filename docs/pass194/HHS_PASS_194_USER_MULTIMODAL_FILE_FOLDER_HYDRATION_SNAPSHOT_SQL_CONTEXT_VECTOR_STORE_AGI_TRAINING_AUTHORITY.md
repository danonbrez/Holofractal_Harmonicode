# HHS PASS 194 — USER MULTIMODAL FILE AND FOLDER HYDRATION SNAPSHOT, SQL CONTEXT GRAPH, ENCRYPTED VECTOR STORE, AND AGI TRAINING-CYCLE DATASET AUTHORITY

## Content-addressed source preservation, versioned folder topology, immutable hydration snapshots, relational contextual metadata, compatible vector spaces, explicit training consent, dataset lineage, fine-tuning cycles, checkpoint evidence, deletion propagation, and deterministic replay

# 1. Normative metadata

| Field | Normative value |
|---|---|
| Contract identifier | `HHS-P194-UMFFHS-SQLCG-EVS-AGITC-VM81-H72-H216` |
| Pass number | `194` |
| Canonical pass name | `USER_MULTIMODAL_FILE_FOLDER_HYDRATION_SNAPSHOT_SQL_CONTEXT_VECTOR_STORE_AGI_TRAINING_CYCLE_DATASET_AUTHORITY` |
| Short name | `P194 Multimodal Storage and Training Snapshot Authority` |
| Contract version | `1.0.0` |
| Repository | `danonbrez/Holofractal_Harmonicode` |
| Authoritative contract baseline | `main @ 31aad2b8281c9a68c5f810948dac630dd5a387e0` |
| Merge target | `main` |
| Inherited scope | Genesis and every compatible accepted requirement through Pass 193 |
| Canonical source language | HARMONICODE |
| Canonical metadata authority | Versioned SQL relational context graph |
| Canonical source-byte authority | Immutable content-addressed blob identity |
| Canonical retrieval projection | Versioned encrypted vector spaces derived from admitted source and metadata |
| Canonical mutation authority | Exactly one admitted VM81 authority |
| Canonical identity authorities | Hash216 object, snapshot, dataset, and model identity; Hash72 receipt lineage |
| Canonical training input | Frozen authorized dataset release derived from an immutable hydration snapshot |
| Privacy default | Private storage; training, fine-tuning, sharing, and public release denied unless explicitly authorized |
| Floating-point policy | Embedding and model-compute compatibility values are non-authoritative projections linked to exact source identities |
| Initial classification | `CONTRACT_AUTHORIZED — FULL IMPLEMENTATION REQUIRED` |
| Contract completion classification | `HHS_PASS_194_MULTIMODAL_STORAGE_TRAINING_SNAPSHOT_CONTRACT_FROZEN` |
| Runtime completion classification | `HHS_PASS_194_MULTIMODAL_STORAGE_TRAINING_CYCLE_RUNTIME_VERIFIED` |

# 2. Normative language and claim boundary

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** are normative.

This document is an open developer implementation specification defining storage objects, SQL schemas, upload workflows, folder topology, snapshot semantics, metadata provenance, embedding compatibility, access policy, training authorization, dataset release, fine-tuning lineage, deletion propagation, APIs, command-line surfaces, negative cases, tests, receipts, and completion evidence.

The repository baseline does not expose a top-level license file. This contract does not choose or modify the project license. Maintainers MUST add an explicit license and correct SPDX identifier before claiming legal open-source distribution rights. User-uploaded source and derived datasets retain their own rights, consent, privacy, and license constraints independently of the repository source license.

The mandatory distinction is:

```text
CONTRACT PRESENT
!= IMPLEMENTATION PRESENT
!= IMPLEMENTATION VERIFIED
```

No section of this contract claims that all runtime, database, vector, training, model, interface, or deployment surfaces are already implemented.

# 3. Purpose

Pass 194 defines the canonical memory and dataset boundary between user-controlled multimodal files and folders and every later retrieval, adaptation, AGI training, fine-tuning, evaluation, and checkpoint cycle.

It unifies:

1. user file and folder uploads;
2. immutable original-byte preservation;
3. versioned file and folder identity;
4. content-addressed blob storage;
5. modality classification and deterministic tokenization;
6. typed contextual metadata;
7. SQL relationship authority;
8. encrypted vector storage;
9. immutable hydration snapshots;
10. governed dataset releases;
11. explicit consent and licensing closure;
12. training and fine-tuning lifecycle records;
13. model checkpoint lineage;
14. deletion, revocation, quarantine, replay, and audit.

The governing architecture is:

```text
USER FILE OR FOLDER
→ IMMUTABLE SOURCE OBSERVATION
→ CONTENT-ADDRESSED BLOB
→ VERSIONED FILE/FOLDER GRAPH
→ MODALITY HYDRATION
→ CHUNKS + DERIVED ARTIFACTS + CONTEXT
→ SQL CANONICAL METADATA AUTHORITY
→ VERSIONED ENCRYPTED VECTOR SPACE
→ IMMUTABLE HYDRATION SNAPSHOT
→ AUTHORIZED DATASET RELEASE
→ TRAINING / FINE-TUNING / EVALUATION
→ MODEL CHECKPOINT LINEAGE
→ HASH72 RECEIPTS + HASH216 IDENTITY + REPLAY
```

# 4. Full inherited authority

Pass 194 inherits every compatible accepted requirement through Pass 193, including:

1. exact source preservation and meaning conservation;
2. zero-bypass runtime interposition;
3. one singleton VM81 admission and serialized commit authority;
4. Hash72 receipt continuity and deterministic replay;
5. Hash216 ordered object identity;
6. no-float canonical identity;
7. exact `List(...)`, reciprocal-factorial, phase, and membrane preservation;
8. Pass 145 ingestion, database, CLI, and receipt foundations;
9. Pass 163 persistent snapshot and VMRC foundations;
10. Pass 165 multimodal ingress authority;
11. Pass 174 encrypted persistent vector storage and Visual IDE authority;
12. Pass 189 repository-wide object registry;
13. Pass 190 operation registry, HARMONICODE shell, OpenAPI, SDK, and interface parity;
14. Pass 191 full repository hydration;
15. Pass 192 exact nested parent/child and inherited membrane authority;
16. Pass 193 fractal lineage, native packaging, license manifests, and safe executable provenance;
17. restartability, bounded lifecycle jobs, explicit failure states, cancellation, retry, rollback, and authoritative-main closure.

Pass 194 is additive. It SHALL NOT create an independent storage truth, vector truth, training truth, or model-lineage truth outside the inherited authority path.

# 5. Existing foundation integration

Pass 194 SHALL extend and reconcile existing repository functionality rather than replace it with incompatible parallel systems.

The inherited multimodal tokenizer/database substrate already supports:

```text
file bytes
→ deterministic fingerprint
→ modality classification
→ deterministic byte chunks
→ Hash72 token records
→ invariant admission
→ commit or quarantine
→ ledger receipt and replay
```

The inherited persistent vector substrate already supports:

```text
SQLite persistence
AES-GCM authenticated encryption
WAL journaling
full synchronization
Hash216 verification
quarantine state
restart recovery
```

Pass 194 MUST migrate or adapt these objects into one canonical schema while preserving their identities and evidence.

Legacy JSON database records, Pass 174 vector objects, prior upload receipts, and existing token records MUST be classified as:

```text
MIGRATED
COMPATIBLE_READ_ONLY
QUARANTINED
DEPRECATED_WITH_REPLACEMENT
UNRESOLVED
```

No legacy object may disappear silently.

# 6. Four-store separation

A conforming implementation MUST preserve four linked but distinct storage concerns:

```text
BLOB STORE
SQL CONTEXT GRAPH
VECTOR STORE
SNAPSHOT STORE
```

## 6.1 Blob store

The blob store retains immutable original and derived bytes addressed by content identity.

## 6.2 SQL context graph

The SQL database is authoritative for identity, ownership, hierarchy, versions, relationships, provenance, permissions, consent, licenses, retention, datasets, runs, checkpoints, receipts, and tombstones.

## 6.3 Vector store

The vector store is a derived retrieval and similarity projection. It is never the sole authority for source identity, ownership, permissions, consent, or training eligibility.

## 6.4 Snapshot store

The snapshot store freezes exact manifests describing the source, metadata, adapter, vector, permission, and dataset state consumed by a downstream operation.

The governing rule is:

```text
VECTOR PRESENCE
!= SOURCE AUTHORITY
!= TRAINING AUTHORIZATION
```

# 7. Storage root and workspace model

Every object MUST exist under an explicit workspace and storage root.

Required identities include:

```text
user_id
workspace_id
storage_root_id
folder_id
folder_version_id
file_id
file_version_id
blob_id
```

A storage root declares:

```text
root type
physical or remote locator
workspace ownership
access policy
capacity policy
encryption policy
retention policy
backup policy
availability state
```

Supported root classes MAY include:

```text
LOCAL_FILESYSTEM
OBJECT_STORAGE
ENCRYPTED_VOLUME
DATABASE_BLOB
REMOTE_CONNECTOR
READ_ONLY_IMPORT
ARCHIVAL_TIER
```

Physical paths and remote URLs are locators, not canonical identity.

# 8. Immutable source-byte authority

Every uploaded source file MUST retain its original bytes read-only.

```text
SOURCE_FILE_VERSION
⇒ ORIGINAL_BYTES_PRESERVED
∧ CONTENT_HASH_PRESERVED
∧ ORIGINAL_FILENAME_PRESERVED
∧ RELATIVE_PATH_PRESERVED
∧ UPLOAD_CONTEXT_PRESERVED
```

The canonical blob record MUST include:

```text
blob_id
byte_length
content_hash_sha256
content_hash72
media_type_observation
compression_observation
encryption_envelope
storage_locator
created_at
integrity_status
Hash216_identity
```

Blob writes MUST be atomic. A blob is admitted only after complete-byte hashing and integrity verification.

A content hash collision, truncated upload, unsupported encryption state, or byte-count mismatch MUST quarantine the candidate.

# 9. Source and derived-artifact separation

The following are derived artifacts and MUST NOT overwrite or masquerade as the original source:

```text
OCR text
speech transcription
captions
summaries
translations
thumbnails
waveforms
spectrograms
video keyframes
scene segmentation
image regions
PDF text layers
archive expansion
code ASTs
3D mesh simplifications
embeddings
labels
model-generated annotations
converted formats
```

Every derived artifact MUST retain:

```text
derived_artifact_id
parent_file_version_id
parent_chunk_id where applicable
producer_operation_id
producer_version
input identities
parameters
output blob identity
determinism class
quality or confidence metadata
rights inheritance
created receipt
```

# 10. Folder hydration and topology

A folder upload MUST become a versioned object graph rather than a flat collection of files.

Required preservation includes:

```text
relative path
parent folder
child folder relationships
file membership
empty directories
archive membership
symbolic link classification
source platform
case-sensitivity observation
file mode observation
timestamps as non-authoritative observations
sibling order where semantically meaningful
ignore and exclusion rules
```

A folder snapshot is equivalent to:

```text
FolderVersion(
  folder identity,
  parent folder version,
  child folder edges,
  file-version edges,
  metadata,
  policy,
  manifest root
)
```

A path rename or move creates a new contextual version without necessarily creating a new blob.

A byte change creates a new file version and blob identity.

# 11. Files, aliases, duplicates, and links

The schema MUST distinguish:

```text
same logical file, new version
same bytes, different logical files
same file, moved path
hard-link relationship
symbolic-link relationship
archive member
copy relationship
derived relationship
exact duplicate
near duplicate
```

Duplicate bytes MAY share one immutable blob while retaining separate file identities, ownership, paths, permissions, and contextual metadata.

A symbolic link MUST NOT be followed outside the authorized upload root without explicit policy and cycle detection.

# 12. Upload lifecycle

Every upload session MUST use a finite-state lifecycle:

```text
CREATED
→ RECEIVING
→ RECEIVED
→ HASHING
→ CLASSIFYING
→ ADMITTING
→ HYDRATING
→ INDEXING
→ SNAPSHOT_READY
→ COMPLETED
```

Failure states include:

```text
REJECTED
QUARANTINED
CANCELLED
TIMED_OUT
FAILED_RETRYABLE
FAILED_TERMINAL
```

Every session MUST have:

```text
session_id
workspace_id
uploader_id
source type
expected size where known
received size
file count
folder count
state
failure code
retry count
created time
updated time
cancellation state
receipt chain
```

No upload job may remain indefinitely in an unbounded `PROCESSING` state.

# 13. Modality registry

Pass 194 MUST support a versioned modality registry.

Minimum modality classes are:

```text
TEXT
MARKDOWN
SOURCE_CODE
JSON
CSV
TABLE
PDF
DOCUMENT
IMAGE
AUDIO
VIDEO
ARCHIVE
BINARY
THREE_D_MESH
THREE_D_SCENE
APPLICATION_PROJECT
HARMONICODE
RUNTIME_RECEIPT
DATABASE_EXPORT
SENSOR_STREAM
```

Classification MUST record:

```text
observed media type
filename suffix
magic-byte result
classifier identity
classifier version
confidence or deterministic rule
conflicts
final admitted class
```

A suffix alone MUST NOT be treated as definitive when byte inspection contradicts it.

# 14. Hydration adapter contract

Every modality adapter MUST declare:

```text
adapter_id
adapter_version
supported media types
input schema
lossless observations
derived outputs
chunk coordinate system
external dependencies
determinism class
resource limits
privacy implications
failure modes
sandbox requirements
rights propagation policy
```

Adapters MUST be versioned. A change to parsing, chunking, extraction, coordinate systems, or normalization MUST create a new adapter version.

Adapters SHALL NOT gain canonical authority. They produce candidates for admission.

# 15. Deterministic chunk identity

Chunks MUST be deterministically reproducible from:

```text
file_version_id
source blob identity
adapter identity and version
chunking policy identity
chunk coordinates
chunk source bytes or exact source span
```

A chunk record MUST contain:

```text
chunk_id
file_version_id
modality
ordinal
byte_start
byte_end
coordinate_type
coordinate_payload
source_hash72
source_hash_sha256
text projection where authorized
preview policy
parent chunk
child chunk relations
Hash216_identity
created receipt
```

Coordinate types MAY include:

```text
BYTE_INTERVAL
CHARACTER_INTERVAL
LINE_INTERVAL
PAGE_REGION
IMAGE_REGION
AUDIO_TIME_INTERVAL
VIDEO_TIME_INTERVAL
VIDEO_FRAME_INTERVAL
TABLE_RANGE
ARCHIVE_MEMBER
CODE_SYMBOL
AST_NODE
MESH_COMPONENT
SCENE_NODE
APPLICATION_OBJECT
```

# 16. SQL canonical context graph

The SQL database is the canonical metadata and relationship authority.

A conforming implementation MUST provide relational tables or equivalent strongly constrained relations for at least:

```text
users
workspaces
storage_roots
upload_sessions
folders
folder_versions
folder_edges
files
file_versions
file_locations
blobs
modalities
adapters
chunks
chunk_relations
derived_artifacts
metadata_namespaces
metadata_values
object_relations
embeddings
vector_spaces
snapshots
snapshot_members
datasets
dataset_members
dataset_splits
permissions
consent_records
license_records
retention_policies
exclusion_rules
training_plans
training_runs
fine_tuning_runs
evaluation_runs
model_checkpoints
deployment_candidates
deletion_requests
tombstones
quarantine_records
receipts
replay_records
```

The initial reference profile MAY use SQLite. Production deployments SHOULD support PostgreSQL-compatible transactional semantics without changing canonical object identities.

# 17. SQL integrity requirements

The SQL authority MUST enforce:

```text
foreign keys enabled
unique canonical identities
non-null ownership and workspace scope
version monotonicity
immutable admitted source versions
transactional snapshot creation
transactional policy checks
restricted cascades
explicit tombstones
bounded queries
migration versioning
```

SQLite reference deployments MUST enable at least:

```sql
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = FULL;
```

Database schema migration MUST be versioned, reversible where feasible, and receipt-linked.

# 18. File-version record

A canonical file-version record MUST contain at least:

```text
file_id
file_version_id
workspace_id
parent_folder_version_id
relative_path
original_filename
source_blob_id
size_bytes
media_type
modality
upload_session_id
source_platform
creation_time_observation
modification_time_observation
owner_id
permission_policy_id
consent_policy_id
license_policy_id
retention_policy_id
status
quarantine_state
supersedes_version_id
Hash216_identity
created_receipt_hash72
```

The filesystem path MUST NOT be the primary key.

# 19. Contextual metadata authority

Metadata MUST support exact typed values and typed relationships.

Required metadata origins are:

```text
USER_SUPPLIED
FILE_EMBEDDED
SYSTEM_OBSERVED
DETERMINISTIC_DERIVATION
MODEL_INFERRED
EXTERNAL_IMPORT
MIGRATED_LEGACY
```

A metadata record MUST contain:

```text
metadata_id
subject_object_id
namespace
key
typed value
origin
producer identity
producer version
confidence where applicable
source evidence
created time
supersedes metadata id
permission visibility
Hash216_identity
receipt reference
```

Model-inferred metadata MUST NOT silently become equivalent to user-declared or deterministic fact.

# 20. Relationship vocabulary

The context graph MUST support extensible typed relationships, including:

```text
CONTAINS
VERSION_OF
SUPERSEDES
DERIVED_FROM
DUPLICATE_OF
NEAR_DUPLICATE_OF
REFERENCES
AUTHORED_BY
BELONGS_TO_PROJECT
DEPICTS
TRANSCRIBES
TRANSLATES
PAIRED_WITH
TEMPORAL_PREDECESSOR
SPATIAL_PARENT
CONTINUES
ANNOTATES
TRAINING_LABEL_FOR
GENERATED_FROM
LICENSED_UNDER
CONSENTED_FOR
EXCLUDED_FROM
```

Relationships MUST preserve direction, subject, object, origin, version, and evidence.

# 21. Context inheritance

Folder-level metadata and policy MAY be inherited by child objects, but inherited and local values MUST remain distinguishable.

```text
EFFECTIVE_CONTEXT
= ANCESTOR_CONTEXT
+ LOCAL_CONTEXT
- EXPLICIT_OVERRIDES
```

Every effective-policy query MUST be reproducible from the exact ancestor chain and policy versions.

# 22. Encrypted vector-store authority

Embeddings and vector indexes MUST be treated as derived, versioned, encrypted projections.

Every vector object MUST bind:

```text
embedding_id
subject chunk or object id
vector_space_id
encoder identity
encoder version
input projection identity
vector dimension
storage encoding
normalization policy
distance metric
encryption envelope
created snapshot or operation
quarantine state
Hash216_identity
receipt reference
```

Authenticated encryption is REQUIRED for persistent private vectors unless an explicit storage policy provides an equivalent or stronger control.

# 23. Vector-space compatibility

Every vector space MUST declare:

```text
vector_space_id
modality
encoder identity
encoder version
dimension
normalization policy
distance metric
quantization policy
chunking policy
input projection policy
encryption policy
created time
supersedes vector space
```

The governing invariant is:

```text
VECTOR COMPARISON
⇒ SAME VECTOR SPACE
OR EXPLICIT VALIDATED BRIDGE
```

Vectors generated by incompatible encoders, dimensions, normalization rules, or modality policies MUST NOT be compared as though they occupy one semantic space.

# 24. Float classification for embeddings

Model and embedding libraries commonly use floating-point tensors. Pass 194 permits these only as tagged compatibility projections.

Canonical identity MUST derive from:

```text
source identities
encoder identity and version
input projection identity
exact configuration
serialized vector bytes
vector-space identity
```

A floating-point vector value SHALL NOT replace the exact source, metadata, policy, or snapshot graph.

Non-finite vector values MUST be rejected.

# 25. Search and retrieval

Search MAY combine:

```text
exact metadata filters
full-text search
path and hierarchy filters
Hash72 and Hash216 identity lookup
vector similarity
relation traversal
temporal filters
permission filters
snapshot filters
```

Every result MUST be permission-filtered before disclosure.

Retrieval responses SHOULD expose:

```text
source object
matched chunk
match type
score where applicable
vector-space identity
context path
provenance
snapshot identity
permission decision
```

A similarity score is not a truth score.

# 26. Immutable hydration snapshot

Training, fine-tuning, evaluation, export, and reproducible retrieval MUST consume a frozen snapshot rather than a mutable live directory.

A snapshot constructor is equivalent to:

```harmonicode
HydrationSnapshot(
  workspace = Workspace(...),
  roots = SelectedFoldersAndFiles,
  fileVersions = FrozenClosure,
  metadataSchemas = FrozenVersions,
  adapters = FrozenVersions,
  chunks = FrozenIdentities,
  vectorSpaces = FrozenIdentities,
  rights = Validate,
  consent = Validate,
  exclusions = Apply,
  identity = Hash216,
  receipt = Hash72
)
```

# 27. Snapshot record

Every snapshot MUST contain:

```text
snapshot_id
workspace_id
parent_snapshot_id
SQL transaction identity
schema migration version
selected root objects
folder-version closure
file-version closure
blob identities
chunk identities
derived-artifact identities
metadata namespace and value versions
relation versions
adapter versions
tokenizer versions
encoder identities
vector-space identities
permission closure
consent closure
license closure
retention closure
exclusion closure
snapshot manifest blob
Hash216 snapshot root
Hash72 creation receipt
created by
created time
```

Snapshot creation MUST be atomic relative to the canonical SQL graph.

# 28. Incremental snapshots

A new snapshot SHOULD reuse unchanged content-addressed objects.

```text
SNAPSHOT N+1
= SNAPSHOT N
+ ADDED VERSIONS
+ MODIFIED VERSIONS
- EXCLUDED VERSIONS
+ METADATA REVISIONS
+ POLICY REVISIONS
+ ADAPTER OR VECTOR REVISIONS
```

The system MUST provide a deterministic diff reporting at least:

```text
files added
files modified
files moved
files removed
folders changed
metadata changed
relationships changed
permissions changed
consent changed
licenses changed
embeddings regenerated
adapters changed
training eligibility changed
```

# 29. Snapshot replay

Replaying a snapshot MUST recreate the same selected object and policy closure, subject to verified availability of referenced immutable blobs and versioned adapters.

A missing blob, incompatible adapter, failed integrity check, or missing encryption key MUST produce an explicit replay failure rather than silent substitution.

# 30. Privacy and authorization defaults

A user upload MUST default to:

```text
PRIVATE_STORAGE = ALLOWED
USER_RETRIEVAL = ALLOWED
ASSISTANT_CONTEXT = USER_CONTROLLED
TRAINING = DENIED
FINE_TUNING = DENIED
EVALUATION = DENIED
SHARING = DENIED
PUBLIC_RELEASE = DENIED
```

The mandatory rule is:

```text
FILE PRESENT IN STORAGE
!= FILE AUTHORIZED FOR TRAINING
```

No global setting may silently broaden an object whose local policy is more restrictive.

# 31. Policy classes

Minimum policy classes are:

```text
PRIVATE_STORAGE_ONLY
RETRIEVAL_ALLOWED
ASSISTANT_CONTEXT_ALLOWED
TRAINING_ALLOWED
FINE_TUNING_ALLOWED
EVALUATION_ALLOWED
EXPORT_ALLOWED
SHARING_ALLOWED
PUBLIC_DATA
EXCLUDED
QUARANTINED
LEGAL_HOLD
DELETE_PENDING
DELETED_TOMBSTONE
```

Policy evaluation MUST include user, workspace, object, ancestor, dataset, and operation scope.

# 32. Consent records

Training consent MUST be explicit, attributable, versioned, and revocable.

A consent record MUST contain:

```text
consent_id
subject user or rights holder
object scope
permitted operations
purpose
model or project scope where applicable
start time
expiration time
revocation state
policy version
recording interface
Hash216_identity
Hash72 receipt
```

Absence of consent is not consent.

# 33. Rights and licensing

Every training-eligible object MUST have a resolved rights classification.

Required classifications include:

```text
USER_OWNED
USER_LICENSED
PUBLIC_DOMAIN
OPEN_LICENSED
INTERNAL_AUTHORIZED
UNKNOWN_RIGHTS
RESTRICTED
EXCLUDED
```

Dataset release MUST fail when required rights are unknown, incompatible, expired, revoked, or outside the declared training purpose.

License metadata MUST retain source evidence and version.

# 34. Sensitive-data classification

Pass 194 MUST support policy-controlled classification for sensitive content, including personally identifying, confidential, regulated, security-sensitive, or user-designated private material.

Classification MAY be user-supplied, deterministic, or model-assisted, but origin MUST remain explicit.

Sensitive classification MUST affect:

```text
access
search disclosure
vector indexing
external model use
training eligibility
export
retention
deletion urgency
logging and preview policy
```

Raw private content MUST NOT be written to ordinary application logs.

# 35. Dataset release authority

A dataset is a governed projection of one immutable snapshot.

```harmonicode
DatasetRelease(
  sourceSnapshot = Snapshot(...),
  selection = VersionedQuery(...),
  transforms = RegisteredOnly,
  exclusions = PolicyClosure,
  splits = Deterministic,
  rights = Validate,
  consent = Validate,
  identity = Hash216,
  receipt = Hash72
)
```

A dataset release MUST NOT query mutable live storage after its identity is frozen.

# 36. Dataset record

Every dataset release MUST contain:

```text
dataset_id
source_snapshot_id
selection query identity
included member identities
excluded member identities and reasons
transform graph
chunk and label policy
deduplication policy
train-validation-test split identity
rights closure
consent closure
sensitive-data closure
quality report
dataset card
known limitations
Hash216 identity
Hash72 release receipt
supersedes dataset id
```

# 37. Deterministic dataset splits

Dataset splits MUST be reproducible from declared identities and policy.

Split assignment MUST avoid leakage across configured related groups, such as:

```text
versions of the same file
chunks from the same source
near duplicates
same user or project when configured
paired modalities
translated variants
frames from the same video
samples from the same session
```

The split strategy and grouping key MUST be recorded.

# 38. Label provenance

Every label MUST identify its origin:

```text
USER_LABEL
EXPERT_LABEL
DETERMINISTIC_LABEL
IMPORTED_LABEL
MODEL_PSEUDO_LABEL
MODEL_GENERATED_LABEL
INFERRED_RELATION
```

Model-generated labels MUST NOT be presented as human labels.

Label corrections MUST create new versions and preserve superseded history.

# 39. Training-plan authority

Training and fine-tuning begin with an immutable plan.

A training plan MUST bind:

```text
plan_id
base model identity
model architecture identity
dataset release identity
snapshot identity
operation registry version
training code revision
container or environment identity
hyperparameters
optimizer and scheduler policy
random-seed policy
hardware profile
precision policy
checkpoint schedule
evaluation suite
safety constraints
resource budget
cancellation policy
output policy
Hash216 identity
created receipt
```

# 40. Training lifecycle

Every training or fine-tuning run MUST use a finite-state lifecycle:

```text
PLANNED
→ DATASET_VALIDATED
→ AUTHORIZED
→ QUEUED
→ PROVISIONING
→ RUNNING
→ CHECKPOINTING
→ EVALUATING
→ ACCEPTED | REJECTED | CANCELLED | FAILED
→ ARCHIVED
```

A run MUST support bounded status, cancellation, failure reason, retry policy, and recovery checkpoints.

# 41. Authorization revalidation

Consent, permissions, rights, exclusions, and legal holds MUST be checked:

1. when a snapshot is created;
2. when a dataset is released;
3. immediately before a training run starts;
4. before resuming a paused run when policy may have changed;
5. before model publication or export.

A revoked or newly restricted member MUST block a not-yet-started run.

# 42. Training-run record

Every run MUST retain:

```text
run_id
plan_id
dataset_id
snapshot_id
base model identity
code identity
environment identity
hardware identity
start and end times
state transitions
resource usage
checkpoint identities
metrics
failure records
policy revalidation receipts
output model identities
Hash72 receipt chain
replay classification
```

# 43. Fine-tuning-cycle authority

Fine-tuning MUST be distinguished from base training, retrieval-only indexing, prompt adaptation, and evaluation.

Required cycle classes include:

```text
PRETRAINING
CONTINUED_PRETRAINING
SUPERVISED_FINE_TUNING
PREFERENCE_TUNING
REWARD_MODELING
ADAPTER_TUNING
DISTILLATION
EMBEDDING_TUNING
MULTIMODAL_ALIGNMENT
EVALUATION_ONLY
RETRIEVAL_INDEX_ONLY
```

Every cycle class MUST declare its data requirements, output semantics, and authorization scope.

# 44. Checkpoint lineage

Every model checkpoint MUST contain or reference:

```text
checkpoint_id
parent checkpoint id
base model id
training run id
step or epoch
model weights artifact identity
optimizer state identity
scheduler state identity
random state identity
metric summary
safety evaluation state
serialization format
Hash216 identity
Hash72 receipt
```

A checkpoint without dataset and run lineage is non-conforming.

# 45. Model identity

Model identity MUST bind:

```text
architecture
base checkpoint
training plan
dataset release
snapshot
code revision
configuration
output weight bytes
adapter bytes where applicable
tokenizer or processor identity
license and usage policy
```

Two byte-identical model artifacts with different asserted lineage MUST trigger an identity reconciliation check.

# 46. Evaluation authority

Evaluation datasets MUST be versioned and snapshot-bound like training datasets.

The system MUST distinguish:

```text
training metrics
validation metrics
held-out test metrics
safety evaluations
regression evaluations
human review
calibration evidence
```

Training data MUST NOT silently enter a held-out evaluation set.

# 47. Retrieval versus training

Pass 194 MUST preserve the distinction:

```text
RETRIEVAL CONTEXT
!= PARAMETER TRAINING
```

A file authorized for assistant retrieval is not automatically authorized for model training.

A file authorized for training is not automatically authorized for public model release or dataset sharing.

# 48. Deletion request lifecycle

Deletion MUST be a tracked lifecycle:

```text
REQUESTED
→ AUTHORIZED
→ IMPACT_ANALYZED
→ SOURCE_REMOVED_OR_CRYPTO_ERASED
→ DERIVATIVES_REMOVED
→ VECTOR_ENTRIES_REMOVED
→ DATASETS_INVALIDATED_OR_SUPERSEDED
→ RECEIPT_WRITTEN
→ COMPLETED
```

Failure and legal-hold states MUST be explicit.

# 49. Deletion propagation

A source deletion or consent revocation MUST be evaluated across:

```text
source file versions
blobs
folder manifests
chunks
derived artifacts
metadata
relationships
embeddings
vector indexes
snapshot memberships
dataset memberships
pending training plans
queued runs
cached exports
```

Past immutable receipts MAY retain a tombstoned identity and non-sensitive audit metadata. They MUST NOT retain deleted plaintext solely to preserve a receipt chain.

# 50. Model unlearning classification

When data has already influenced a trained model, the system MUST classify the response rather than assume deletion from storage removes model influence.

Allowed classifications include:

```text
PROSPECTIVE_EXCLUSION_ONLY
RETRAIN_REQUIRED
UNLEARNING_REQUIRED
ADAPTER_REMOVAL_SUFFICIENT
MODEL_WITHDRAWAL_REQUIRED
NO_MODEL_IMPACT_DEMONSTRATED
UNRESOLVED_REVIEW_REQUIRED
```

The classification, evidence, and decision authority MUST be recorded.

# 51. Retention and legal hold

Retention policies MUST be explicit by object class and workspace.

Legal hold MUST prevent destructive deletion while restricting ordinary use according to policy.

Expired retention MUST not delete an object that remains required by a stricter legal hold, but the conflict MUST be visible and auditable.

# 52. Quarantine

Objects MUST be quarantined when they have unresolved integrity, malware, format, rights, consent, policy, identity, or encryption failures.

Quarantined objects MUST NOT enter retrieval, dataset, training, fine-tuning, evaluation, export, or publication unless an explicit repair and readmission succeeds.

# 53. Security boundary

Pass 194 MUST implement least privilege for:

```text
upload
read
preview
derive
embed
search
snapshot
dataset release
train
fine-tune
evaluate
export
delete
administer keys
```

High-risk parsers and converters MUST run in bounded sandboxes.

Archive extraction MUST prevent path traversal, decompression bombs, device files, and unauthorized symbolic-link escape.

# 54. Encryption and key management

Private source, metadata, vectors, snapshots, datasets, and checkpoints SHOULD be encrypted at rest according to workspace policy.

Authenticated encryption is REQUIRED for fields or payloads designated confidential.

Keys MUST NOT be stored in ordinary source control or plaintext application logs.

Key rotation MUST preserve object identity while recording the encryption-envelope version change.

Crypto-erasure MAY satisfy deletion only when the encryption boundary and key exclusivity are verified.

# 55. Backup and restore

Backups MUST preserve:

```text
blob identities
SQL transaction consistency
vector-space versions
snapshot manifests
encryption envelopes
schema versions
receipt continuity
```

Restore MUST verify integrity before reactivating data.

A restored database MUST not silently point to missing or mismatched blobs.

# 56. Canonical HARMONICODE constructors

The Pass 190 operation registry MUST include operations equivalent to:

```harmonicode
StorageRoot.Create
UploadSession.Create
Storage.UploadFile
Storage.UploadFolder
Blob.Admit
File.Create
File.CreateVersion
Folder.Create
Folder.CreateVersion
Folder.Hydrate
Modality.Classify
Adapter.Run
Chunk.Create
Metadata.Attach
Relation.Attach
Embedding.Generate
VectorSpace.Create
Snapshot.Create
Snapshot.Diff
Snapshot.Replay
Dataset.Release
Dataset.Validate
Training.Plan
Training.Authorize
Training.Run
Training.Cancel
Training.Resume
Checkpoint.Create
Evaluation.Run
Consent.Grant
Consent.Revoke
Storage.Delete
Quarantine.Admit
Quarantine.Release
```

# 57. CLI surface

Minimum shell commands are:

```bash
hhs storage upload file <path>
hhs storage upload folder <path>
hhs storage status <job-id>
hhs storage cancel <job-id>
hhs storage retry <job-id>
hhs storage inspect <object-id>
hhs storage tree <folder-id>
hhs storage search <query>
hhs storage metadata set <object-id> <key> <value>
hhs storage permissions show <object-id>
hhs storage permissions set <object-id> --training deny
hhs storage consent grant <object-id> --purpose <purpose>
hhs storage consent revoke <consent-id>
hhs storage snapshot create --root <object-id>
hhs storage snapshot diff <snapshot-a> <snapshot-b>
hhs storage snapshot replay <snapshot-id>
hhs dataset create --snapshot <snapshot-id>
hhs dataset validate <dataset-id>
hhs train plan --dataset <dataset-id> --base-model <model-id>
hhs train run <plan-id>
hhs train status <run-id>
hhs train cancel <run-id>
hhs train resume <run-id>
hhs model checkpoint inspect <checkpoint-id>
hhs storage delete <object-id>
```

Human-readable output is the default. `--json` MUST provide stable machine-readable output.

# 58. OpenAPI surface

Minimum API families are:

```text
POST   /v1/storage/uploads
GET    /v1/storage/uploads/{id}
POST   /v1/storage/uploads/{id}/cancel
POST   /v1/storage/uploads/{id}/retry
GET    /v1/storage/objects/{id}
GET    /v1/storage/folders/{id}/tree
POST   /v1/storage/search
POST   /v1/storage/objects/{id}/metadata
GET    /v1/storage/objects/{id}/permissions
PUT    /v1/storage/objects/{id}/permissions
POST   /v1/storage/objects/{id}/consents
DELETE /v1/storage/consents/{id}
POST   /v1/storage/snapshots
GET    /v1/storage/snapshots/{id}
POST   /v1/storage/snapshots/diff
POST   /v1/storage/snapshots/{id}/replay
POST   /v1/datasets
GET    /v1/datasets/{id}
POST   /v1/datasets/{id}/validate
POST   /v1/training/plans
POST   /v1/training/runs
GET    /v1/training/runs/{id}
POST   /v1/training/runs/{id}/cancel
POST   /v1/training/runs/{id}/resume
GET    /v1/models/checkpoints/{id}
DELETE /v1/storage/objects/{id}
```

All routes MUST resolve to the same canonical operations and VM81 authority used by CLI, SDK, automation, assistant, and Visual IDE surfaces.

# 59. SDK requirements

Generated SDKs MUST expose typed asynchronous upload, status, cancellation, snapshot, search, dataset, consent, training, checkpoint, and deletion operations.

Large file upload SHOULD support resumable bounded chunks with end-to-end final-byte verification.

SDKs MUST NOT hide training consent changes behind generic upload calls.

# 60. Visual IDE requirements

The Visual IDE MUST provide a human-readable storage and training workspace with:

```text
folder tree
file preview
version history
metadata inspector
relationship inspector
permissions and consent controls
quarantine state
snapshot browser
snapshot diff
dataset builder
training plan editor
job status
cancel and retry
checkpoint browser
receipt and lineage view
deletion impact preview
```

Raw JSON MAY be available as an advanced view but MUST NOT be the only usable interface.

# 61. Assistant integration

The assistant MAY search and retrieve only within the user's authorized context.

Every assistant retrieval MUST be attributable to source objects and snapshot or live-context policy.

The assistant MUST distinguish:

```text
private retrieval context
training-authorized data
public data
model inference
user-provided fact
```

The assistant SHALL NOT silently change consent, release datasets, or begin training.

# 62. Operation receipts

Every admitted mutation MUST produce a receipt containing:

```text
operation id
actor
workspace
prior state identity
candidate state identity
decision
policy closure
input object identities
output object identities
Hash216 result identity
Hash72 receipt
replay information
failure or rejection reason
```

Read-only search MAY use compact query receipts according to privacy and audit policy.

# 63. Snapshot and dataset identity

Snapshot and dataset Hash216 identities MUST bind canonical serialization of all member identities, policies, schemas, adapters, transformations, and lineage.

Ordering MUST be deterministic.

A change in any training-relevant member, policy, transform, split, label, or adapter MUST create a new identity.

# 64. Bounded materialization

Folder traversal, archive expansion, chunking, embedding, search, snapshot closure, dataset construction, and training MUST enforce finite bounds.

Required configurable limits include:

```text
maximum upload bytes
maximum file count
maximum folder depth
maximum archive expansion ratio
maximum chunk count
maximum derived artifacts
maximum vector dimension
maximum query results
maximum snapshot members
maximum training tokens or samples
maximum runtime
maximum retries
```

An unbounded request MUST be rejected or converted to an explicitly bounded lazy job.

# 65. Idempotency

Upload finalization, blob admission, file-version creation, snapshot creation, dataset release, and training-run creation MUST support idempotency keys.

Retrying an accepted request with the same idempotency key and same canonical inputs MUST return the same admitted identity rather than duplicate objects.

A key reused with different canonical inputs MUST be rejected.

# 66. Concurrency

Concurrent mutations MUST use explicit transaction and expected-state controls.

Snapshot creation MUST observe one consistent committed SQL state.

Training authorization MUST fail if expected consent, rights, permission, dataset, or snapshot identities have changed.

# 67. Data-quality reports

Before dataset release, the system MUST produce a data-quality report covering applicable dimensions such as:

```text
missing or corrupt blobs
unsupported formats
chunk failures
metadata completeness
duplicate and near-duplicate rates
label provenance
class or modality balance
rights and consent completeness
sensitive-data findings
split leakage risk
vector coverage
quarantined members
```

The report MUST distinguish measured facts from model-inferred estimates.

# 68. Negative conformance cases

The conformance suite MUST reject at least:

1. training without explicit authorization;
2. fine-tuning under retrieval-only permission;
3. snapshot creation with an unresolved missing blob;
4. vector comparison across incompatible spaces without a bridge;
5. model-generated metadata presented as user-supplied;
6. live-directory mutation after dataset identity freeze;
7. archive path traversal;
8. duplicate idempotency key with different input;
9. non-finite embedding values;
10. unauthorized local path escape;
11. file deletion that leaves active embeddings undeclared;
12. dataset release with unknown rights;
13. consent revocation ignored by a queued run;
14. training checkpoint without dataset lineage;
15. silent fallback to a different parser or encoder version;
16. source overwrite by OCR or transcription output;
17. infinite or unbounded folder traversal;
18. plaintext secret or encryption key committed to source control;
19. raw private content emitted to ordinary logs;
20. smooth success status after a quarantined or failed admission.

# 69. Positive conformance cases

The suite MUST verify at least:

1. deterministic file fingerprinting;
2. duplicate-byte deduplication with distinct file contexts;
3. folder hierarchy preservation;
4. file move without unnecessary blob duplication;
5. new file version on byte mutation;
6. deterministic chunks for the same adapter policy;
7. metadata provenance preservation;
8. AES-GCM or equivalent authenticated vector persistence;
9. restart recovery;
10. atomic snapshot creation;
11. deterministic snapshot diff;
12. explicit consent grant and revocation;
13. deterministic dataset split;
14. no cross-split leakage for configured relation groups;
15. training-plan identity stability;
16. checkpoint lineage;
17. deletion impact analysis;
18. vector removal or quarantine after source-policy change;
19. CLI/API/SDK operation parity;
20. Hash72 and Hash216 replay continuity.

# 70. Performance and scale tests

Performance evidence MUST include representative workloads for:

```text
many small files
large single files
deep folder trees
large archives
long audio and video
large PDFs
high-resolution images
3D scenes
application repositories
incremental snapshots
mixed-modality search
vector reindexing
training dataset materialization
```

Performance optimization MUST NOT weaken identity, permission, consent, integrity, or receipt guarantees.

# 71. Migration requirements

Implementation MUST provide repository-visible migration for existing upload and vector records.

Migration evidence MUST include:

```text
source schema identity
target schema identity
object counts
migrated counts
quarantined counts
unresolved counts
identity mapping
receipt root
rollback or recovery plan
```

A migration MUST be restartable from repository-visible state and persistent checkpoints.

# 72. Reference implementation layout

A conforming implementation SHOULD provide an organization equivalent to:

```text
native_projects/hhs_pass194_multimodal_storage/
  contracts/
  schema/
  migrations/
  src/
  api/
  cli/
  sdk/
  tests/
  evidence/
  examples/
```

Expected schema assets include:

```text
SQL migrations
JSON Schemas
HARMONICODE type declarations
OpenAPI schema
vector-space registry schema
snapshot manifest schema
dataset manifest schema
training-plan schema
checkpoint schema
receipt schema
```

# 73. Restartability record

Before every long-running migration, ingestion, embedding, snapshot, dataset, or training operation, the system MUST externalize:

```text
authoritative base identity
active operation id
input identities
completed stages
remaining stages
checkpoint identities
validation results
resource state
next action
blockers
```

Recovery MUST NOT depend solely on chat memory, local scratch state, or one live process.

# 74. Completion evidence

Pass 194 runtime completion requires repository-visible evidence for:

```text
implemented source
schema migrations
migration reports
unit tests
integration tests
negative tests
security tests
restart tests
snapshot replay tests
dataset reproducibility tests
training lifecycle tests
delete and revocation tests
CLI/API/SDK parity tests
Visual IDE acceptance
Hash72 receipts
Hash216 manifests
performance profiles
operational documentation
```

# 75. Completion gates

Pass 194 SHALL NOT be classified runtime complete until all applicable gates pass:

```text
G1  original bytes preserved
G2  folder topology versioned
G3  SQL constraints active
G4  legacy records migrated or classified
G5  encrypted vectors restart safely
G6  compatible vector spaces enforced
G7  snapshots atomic and replayable
G8  private-by-default policy verified
G9  explicit training consent verified
G10 dataset rights and consent closure verified
G11 deterministic splits and leakage controls verified
G12 training lifecycle finite and cancellable
G13 checkpoint lineage complete
G14 deletion and revocation propagation verified
G15 CLI/API/SDK/UI parity verified
G16 receipts and replay verified
G17 authoritative main closure verified
```

# 76. Governing invariants

```text
USER MULTIMODAL SOURCE
⇒ ORIGINAL SOURCE PRESERVED
∧ VERSIONED FILE/FOLDER IDENTITY
∧ SQL CONTEXT GRAPH
∧ ENCRYPTED DERIVED STORAGE
∧ VERSIONED VECTOR SPACE
∧ IMMUTABLE SNAPSHOT CLOSURE
∧ EXPLICIT TRAINING AUTHORIZATION
∧ DATASET LINEAGE
∧ MODEL CHECKPOINT LINEAGE
∧ HASH216 IDENTITY
∧ HASH72 RECEIPT
∧ DETERMINISTIC REPLAY
```

```text
UPLOAD
!= TRAINING CONSENT
```

```text
RETRIEVAL AUTHORIZATION
!= FINE-TUNING AUTHORIZATION
```

```text
VECTOR INDEX
!= SOURCE OF TRUTH
```

```text
SNAPSHOT IDENTITY
⇒ EXACT MEMBER CLOSURE
∧ EXACT POLICY CLOSURE
∧ EXACT ADAPTER CLOSURE
∧ EXACT VECTOR-SPACE CLOSURE
```

```text
TRAINING RUN
⇒ AUTHORIZED DATASET RELEASE
∧ IMMUTABLE PLAN
∧ FINITE LIFECYCLE
∧ CHECKPOINT LINEAGE
∧ RECEIPT CONTINUITY
```

```text
DELETE OR REVOKE
⇒ IMPACT ANALYSIS
∧ DERIVATIVE PROPAGATION
∧ FUTURE TRAINING EXCLUSION
∧ AUDITABLE TOMBSTONE
```

# 77. Required initial classification

The authoritative state after committing this contract is:

```text
HHS PASS 194 CONTRACT AUTHORIZED
FULL IMPLEMENTATION REQUIRED
NO RUNTIME COMPLETION CLAIM
```

# 78. Final law

```text
ONE USER-CONTROLLED MULTIMODAL CORPUS
→ ONE IMMUTABLE SOURCE-BYTE GRAPH
→ ONE VERSIONED FILE/FOLDER CONTEXT GRAPH
→ ONE CANONICAL SQL AUTHORITY
→ MANY VERSIONED ENCRYPTED VECTOR PROJECTIONS
→ IMMUTABLE AUTHORIZED HYDRATION SNAPSHOTS
→ REPRODUCIBLE DATASET RELEASES
→ GOVERNED TRAINING AND FINE-TUNING CYCLES
→ COMPLETE MODEL CHECKPOINT LINEAGE
→ REVOCABLE PERMISSION AND DELETION CONTROL
→ ONE VM81 ADMISSION PATH
→ ONE HASH72 RECEIPT CHAIN
→ ONE HASH216 IDENTITY TOPOLOGY
```

Pass 194 establishes the durable, private-by-default, versioned, contextual, reproducible, and user-governed data substrate required for AGI retrieval, training, fine-tuning, evaluation, and model evolution over uploaded multimodal files without losing source identity, folder context, rights, consent, lineage, or deterministic replay.
