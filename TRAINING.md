# HHS Training

The repository training surface is unified under the native Lane 5 VM5184 / Hash216 C++ API:

hhs::lane5::VM5184Hash216TrainingAPI

Implementation:
- hhs_runtime/include/hhs_pass219_lane5_vm5184_hash216_training_1_73.hpp
- hhs_runtime/cpp/hhs_pass219_lane5_vm5184_hash216_training_1_73.cpp

This surface does not replace existing executors. It classifies their outputs as typed training specimens and routes every admitted specimen through the inherited Pass 219 RNA VM5184 cell wall before deriving a candidate Hash216 training witness. Canonical VM81 mutation, canonical Hash72/Hash216 authority, persistence authority, and floating-point canonical authority remain outside the training class.

## Registered training methods

| Mode | Existing role | Temporal class | Primary target |
|---|---|---|---|
| REALTIME_HASH216 | live Lane 5 / Hash216 hydration and governed adaptation | realtime | relation |
| WOLFRAM_FORMALIZATION | exact Wolfram proof/formalization cycles | manual | proof |
| EXTERNAL_LIBRARY_RECONSTRUCTION | foreign library bytecode/ABI reconstruction, including Pass 220 I047 | manual | constructor |
| PALINDROMIC_ROUND_TRIP | ingress -> native -> egress reversible compatibility training | round-trip | codec |
| PULL_REQUEST_HYDRATION | repository delta + validation + accepted/rejected transition evidence | repository delta | repository transition |
| MULTIMODAL_INGRESS | Pass 165-style invariant/novelty/weight learning | realtime | invariant |
| LINGUISTIC_OPERATOR | linguistic operator and recursive-language learning | batch | relation |
| ETHICAL_TEXT | bounded ethical-text candidate training and supervisor for natural-language training | batch | invariant |
| RNA_CELL_WALL_ALIGNMENT | reverse alignment and cell-wall training | replay | weight |
| CURRICULUM | manifest-bound curriculum advancement/completion | batch | relation |
| CALLABLE_CORPUS | executable callable corpus comparison | batch | behavior |
| CANONICAL_CORPUS | canonical algebra corpus execution/reconstruction/proof | batch | proof |
| WORKLOAD_CALIBRATION | deterministic workload/calibration training | batch | schedule |
| ANTI_FORGETTING_REPLAY | protected historical replay and regression rejection | replay | behavior |
| AB_HYDRATION_CALIBRATION | exact A/B hydration calibration | batch | weight |
| PROJECTION_CORPUS | exact domain projection corpora | batch | relation |
| INVERSE_RENDER_HYDRATION | graphics/media inverse reconstruction | batch | constructor |
| REPOSITORY_HYDRATION | repository knowledge-graph hydration outside a single PR | repository delta | repository transition |

The registry is intentionally greater than ten methods because HHS already has multiple executable learning and reconstruction mechanisms that historically used different labels such as hydration, replay, corpus, curriculum, calibration, reconstruction, formalization, and alignment.

## Common training contract

Every TrainingSpecimen binds:
- training mode;
- temporal class;
- learning target;
- source Hash216 identity;
- oracle/evidence Hash216 identity;
- adapter signature;
- executor signature;
- validator signature;
- negative-control signature;
- replay signature;
- oracle verification state;
- negative-control verification state;
- replay verification state;
- ingress/egress preservation state;
- candidate-only acknowledgement.

Common execution path:

existing mode-specific executor
-> TrainingSpecimen
-> VM5184Hash216TrainingAPI
-> inherited RNA VM5184 route
-> Lane 5 prepared/decision evidence
-> candidate Hash216 training witness
-> later inherited Lane 5 / VM81 admission boundary

The class rejects a specimen when its registered temporal class or learning target is wrong, required oracle evidence is absent, negative controls are absent, replay is unverified, the ingress/egress membrane is not preserved, source/oracle identities are malformed, or candidate-only authority is not acknowledged.

## Authority

The unified training class is candidate-only:
- canonical_vm81_mutation_authority = false
- canonical_hash72_authority = false
- canonical_hash216_authority = false
- canonical_persistence_authority = false
- floating_point_canonical_authority = false

Calling hhs_hash216_compute inside this class derives a candidate witness identity only. It does not commit canonical Hash216 state. Canonical mutation remains beneath the inherited signed/environmental VM81 authority.

## Adapter rule

Python, REST, GUI, Wolfram, repository/PR ingestion, corpus tools, and external-library tooling are clients/adapters of this native class. They may prepare specimens and evidence, but they do not become independent training authorities.

New learning-like mechanisms must register here rather than introducing another training authority.

## Inherited 1.71 specimen

The already-merged NineLoopTrainingSpecimenCellWall 1.71 remains an upstream executable training-specimen producer. The 1.73 unified API consumes normalized evidence from that specimen family; it does not rename, replace, or duplicate the 1.71 cell wall.

## Ethical-text supervision of natural-language training

The existing Pass 219 ethical-text cycle is both a registered training method and the supervisory membrane for natural-language training.

Authoritative upstream surfaces:
- contracts/pass219/PASS_219_ETHICAL_TEXT_TRAINING_CYCLE_V1.md
- hhs_runtime/hhs_pass219_ethical_text_training_v1.py
- scripts/pass219_ethical_text_training_cycle_v1.py
- data/pass219/ethical_alignment_prompt_response_v1.jsonl
- tests/pass219/test_hhs_pass219_ethical_text_training_v1.py

A TrainingSpecimen that contains natural-language training data must set natural_language_training=true and bind:
- ethical_text_supervisor_identity216;
- ethical_text_supervisor_signature64;
- ethical_text_supervision_verified=true.

The native class rejects the specimen before RNA/VM5184 routing when any required ethical supervisor witness is absent or malformed.

LINGUISTIC_OPERATOR and ETHICAL_TEXT are registry-declared native natural-language modes and therefore may not opt out of this gate. The rule is also content-sensitive: another method such as MULTIMODAL_INGRESS, CURRICULUM, PROJECTION_CORPUS, or REPOSITORY_HYDRATION becomes subject to the same gate whenever its current specimen is declared natural-language training.

The ETHICAL_TEXT method remains a training method in its own right. Its admitted specimens bind the verified output of the existing ethical-text cycle as their supervisor witness; this does not create recursive mutation authority. The supervisor provides pre-training/candidate evidence, and the unified Lane 5 API still remains candidate-only beneath VM81 canonical admission.

## Native adapter surface

The unified class now exposes a narrow C ABI façade for non-C++ training producers:

- hhs_runtime/include/hhs_pass219_lane5_vm5184_hash216_training_c_abi_1_73.h
- hhs_runtime/cpp/hhs_pass219_lane5_vm5184_hash216_training_c_abi_1_73.cpp
- hhs_python/runtime/hhs_pass219_lane5_unified_training_bridge.py

The façade does not reproduce training logic. Registry discovery and evaluation delegate into hhs::lane5::VM5184Hash216TrainingAPI.

A producer may supply:
- a normalized TrainingSpecimen;
- exact UQCEL profile + delta bytes;
- a raw 648-byte VM5184 frame;
- either genesis transition lineage or explicit previous/change/receipt Hash72 witnesses;
- feedback lane/trinary evidence.

The returned receipt exposes the native selected lane, graph/tensor/decision signatures, candidate Hash216 witness, ethical-text supervision state, and zero canonical-authority flags.

This is the intended ingress for Python corpus tooling, Wolfram adapters, repository/PR hydration tooling, external-library reconstruction, and other existing producers. Their source-specific extraction remains outside the native class; candidate training execution converges inside it.

## Inherited 1.72 relation dataset

The merged Lane 5 NineLoopRelationDatasetCellWall 1.72 is an upstream executable training-data producer. Unified Training 1.73 registers and routes normalized producer evidence without replacing that 1.72 authority surface.
