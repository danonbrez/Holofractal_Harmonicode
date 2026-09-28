# Pass 219 Lane 5 — Unified VM5184 / Hash216 Training API 1.72

Status: IMPLEMENTED RESTARTABLE CHECKPOINT / NATIVE VALIDATION WORKFLOW ADDED / CANDIDATE-ONLY

## Purpose

Pass 219 Lane 5 1.72 makes training an explicit native capability without replacing the repository existing specialized executors.

The canonical class is hhs::lane5::VM5184Hash216TrainingAPI.

It registers 18 existing training families and accepts them through one typed specimen surface. Every accepted specimen is routed through the inherited C++ RNA VM5184 cell wall (81 x 64 = 5184 bits) before a candidate Hash216 training witness is derived.

## Invariants

The class SHALL:
1. expose one compile-time registry for all registered training modes;
2. require exact mode, temporal-class, and learning-target compatibility;
3. bind source and oracle/evidence identities as 216-character Hash216-form identities;
4. require deterministic replay evidence for every training method;
5. require negative-control evidence for every training method;
6. preserve the ingress/egress compatibility membrane;
7. delegate VM5184 execution to hhs_exact_pass219_rna_vm5184_route;
8. derive only candidate Hash216 training witnesses;
9. expose no VM81 mutation, canonical Hash72, canonical Hash216, persistence, or floating-point canonical authority;
10. classify LINGUISTIC_OPERATOR and ETHICAL_TEXT as native natural-language training modes;
11. require every natural-language TrainingSpecimen, regardless of training mode, to bind a verified Pass 219 ethical-text supervisor Hash216 identity and nonzero supervisor signature before VM5184 routing;
12. reject natural-language training that attempts to bypass the ethical-text supervisory membrane.

## Registered modes

REALTIME_HASH216
WOLFRAM_FORMALIZATION
EXTERNAL_LIBRARY_RECONSTRUCTION
PALINDROMIC_ROUND_TRIP
PULL_REQUEST_HYDRATION
MULTIMODAL_INGRESS
LINGUISTIC_OPERATOR
ETHICAL_TEXT
RNA_CELL_WALL_ALIGNMENT
CURRICULUM
CALLABLE_CORPUS
CANONICAL_CORPUS
WORKLOAD_CALIBRATION
ANTI_FORGETTING_REPLAY
AB_HYDRATION_CALIBRATION
PROJECTION_CORPUS
INVERSE_RENDER_HYDRATION
REPOSITORY_HYDRATION

## Relationship to existing implementations

1.72 is a unification membrane, not a replacement runtime. Existing formalizers, corpus runners, repository hydration, multimodal ingestion, alignment training, calibration workloads, palindromic codecs, and external-library reconstruction remain responsible for producing their native evidence.

They hand their normalized evidence to the common TrainingSpecimen, after which the execution authority path is shared.

## Native validation

tests/pass219/test_pass219_lane5_vm5184_hash216_training_1_72.cpp verifies:
- all 18 modes are registered exactly once;
- the registry count remains greater than ten;
- every mode is VM5184-routed, candidate-Hash216-producing, candidate-only, replay-bound, negative-control-bound, and ingress/egress preserving;
- all 18 modes execute through the inherited RNA VM5184 route;
- mode-separated specimens produce distinct deterministic candidate Hash216 witnesses;
- raw 648-byte ingress and typed VM81 frame ingress produce identical receipts;
- temporal drift, target drift, missing negative controls, missing replay, codec-membrane bypass, malformed identities, unknown modes, and malformed raw lengths fail closed;
- oracle-required methods reject missing oracle verification;
- intrinsic natural-language modes cannot bypass natural-language classification;
- missing ethical-text supervisor identity, signature, or verification rejects natural-language training;
- a general multimodal method carrying natural-language training is also supervised;
- ethical-text training itself remains executable as a supervised training method;
- supervisor lineage is bound into the candidate Hash216 witness;
- no canonical mutation authority is granted.

## Build integration

GNUmakefile links the 1.72 C++ object into libhhs_runtime.so. The dedicated GitHub workflow builds the inherited exact ABI, compiles the native test, and executes it.

## Ethical-text supervisory membrane

PASS_219_ETHICAL_TEXT_TRAINING_CYCLE_V1 is a peer training method and a supervisor over the natural-language subset of the unified training surface.

The existing executable ethical-text cycle remains the upstream producer of supervision evidence. The 1.72 C++ API does not reimplement the Python/text compiler. Instead, a normalized natural-language TrainingSpecimen carries its verified ethical supervisor lineage into the common native membrane.

Required natural-language fields:
- natural_language_training = true;
- ethical_text_supervisor_identity216 = valid Hash216-form identity;
- ethical_text_supervisor_signature64 != 0;
- ethical_text_supervision_verified = true.

Native language modes cannot clear natural_language_training. Mixed/general modes may set it when the specimen contains natural-language training data, at which point the same requirements apply.

The supervisor evidence is included in the candidate Hash216 training-witness material, so changing or removing the supervisor lineage changes or invalidates the candidate.
