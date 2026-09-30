# Pass 219 Global Capability Integration Repair — 2026-09-29

## Restart identity

- Base commit: `7b1b158dcc42a96512b213668f9b3e1d8047582e`
- Branch: `repair/pass219-global-capability-integration-20260929`
- Merge target: `main`
- Governing contract: `contracts/pass219/PASS_219_LANE5_GLOBAL_HOLOGRAPHIC_NUCLEUS_V1.md`
- Repair type: dependency-scoped integration repair; no new canonical authority.

## Implemented

1. Pass 219 Lane 5 repository hydration 1.69 now statically discovers repository callables in addition to the bounded inherited 1.44 snapshot.
2. Repository callable discovery is visibility-only and never executes discovered source.
3. Security/canonical authority remains unchanged: discovered callables are candidate-only and require runtime validation.
4. `demo`, `reference`, configuration, adapter, and non-executable states are not inferred from inability to bypass the kernel or from candidate-only status.
5. The production assistant no longer accepts `EXACT_SEMANTIC_FALLBACK` as a completed text-generation turn.
6. Exact semantic fallback output is not persisted as an assistant message.
7. Unified language-model fabric classifies the native semantic member as a semantic/context contributor rather than a `TEXT_GENERATION` provider.
8. The source-text-integrity scanner now treats JavaScript/template-literal text as string context while continuing to reject literal escaped-newline injection inside executable `${...}` expressions. This repairs the false-positive source guard without weakening the original `\\n` injection contract.
9. Pass 219 Lane 5 1.69 statically scans fetched branch and pull-request Git objects for callable surfaces without checkout or execution. Ref-only capabilities remain visible with `closure_state=UNRESOLVED`, exact ref/commit provenance, candidate-only authority, and a Hash216 ref-snapshot root.
10. The Hash216 deep-index workflow explicitly fetches branch and PR refs before hydration, so the repository index exercises the same global visibility topology.
11. The Lane 5 native-provider workflow now runs service-registry/WebSocket integration tests after installing the declared Pass 220 FastAPI substrate instead of falsely treating a missing test dependency as capability unavailability.
12. Production chat generator choice now routes through `hhs_pass219_lane5_chat_generator_selection_v1.py`, which adapts visible ready generators into the inherited Pass 124 parallel deterministic generalization engine.
13. Generator selection requires three deterministic witness lanes, exact invariant isolation, Fraction-weighted selection only after admission, and deterministic replay. Probability does not create authority.
14. A failed selected generator is retained as evidence and excluded from the next Lane 5 composition while the same witnessed user message is reused; there is no local provider fallback hierarchy.
15. Production assistant health reports the Lane 5 candidate pool and only reports selected provider/model identity from an actual selection receipt. `provider_mode`, `native_first`, and the legacy hierarchy field are explicitly non-authoritative metadata.
16. All unified language-model fabric members remain `visible_to_lane5=true` even when they are not callable for the current turn. Semantic-only contributors remain visible but cannot satisfy `TEXT_GENERATION`.
17. The obsolete local LiteRT ordering method was removed from the production assistant.
18. The unified-chatbot and I003-I010 workflows compile and exercise the Pass 219 selector directly.

## Changed files

- `hhs_backend/runtime/hhs_pass219_lane5_repository_hydration_knowledge_graph_1_69.py`
- `hhs_backend/runtime/hhs_litert_lm_assistant_v1.py`
- `hhs_backend/runtime/hhs_unified_language_model_fabric_v1.py`
- `hhs_backend/runtime/hhs_pass219_lane5_chat_generator_selection_v1.py`
- `hhs_backend/runtime/hhs_production_assistant_v1.py`
- `tests/pass219/test_pass219_lane5_repository_hydration_knowledge_graph_1_69.py`
- `tests/pass220/test_hhs_pass220_unified_chatbot_lane5_model_fabric.py`
- `tests/test_hhs_litert_lm_hhs_api_tools_v1.py`
- `tests/test_hhs_production_public_app_v1.py`
- `hhs_runtime/hhs_source_text_integrity_v1.py`
- `tests/test_hhs_source_text_integrity_v1.py`
- `.github/workflows/native-fastapi-default-provider.yml`
- `.github/workflows/repository-hash216-dependency-index.yml`
- `.github/workflows/pass220-unified-chatbot-lane5-model-fabric.yml`
- `.github/workflows/pass220-i003-four-phase-abc-max-hardware.yml`
- `docs/pass220/PASS_220_UNIFIED_CHATBOT_MODEL_FABRIC_LANE5.md`
- this restart record.

## Required dependency-scoped validation

- `pytest -q tests/pass219/test_pass219_lane5_repository_hydration_knowledge_graph_1_69.py`
- `pytest -q tests/pass220/test_hhs_pass220_unified_chatbot_lane5_model_fabric.py`
- `pytest -q tests/test_hhs_litert_lm_hhs_api_tools_v1.py`
- regenerate/validate the repository Hash216 dependency projection because Lane 5 capability counts change.
- verify no canonical VM81/Hash72/Hash216/mutation authority is introduced.
- verify semantic fallback leaves only the witnessed user message and permits production failover to an actual generator.
- `pytest -q tests/test_hhs_source_text_integrity_v1.py`
- full source-text-integrity scan must accept valid string/template `\\n` data while rejecting injected `\\n` separators in executable source.
- branch/PR ref fixture must hydrate a callable absent from main without executing it and must bind the exact ref/commit snapshot into a 216-character Hash216 root.
- Lane 5 native-provider workflow must run the native-core tests before external FastAPI installation, then run service-registry/WebSocket integration after the declared FastAPI substrate is installed.
- Pass 219 chatbot selector must return a replay-validated Pass 124 selection receipt, never create authority from probability, and exclude only failed members on recomposition.
- production chatbot regression must prove exactly one selected generator executes for a successful turn and that the witnessed thread contains exactly one user message plus one assistant message.
- production assistant health must report `composition_authority=PASS219_LANE5`, `local_provider_hierarchy_authority=false`, the visible candidate pool, and no guessed selected provider/model before a turn.
- `pytest -q tests/test_hhs_production_public_app_v1.py` under the unified-chatbot workflow.

## Environment state

The connected GitHub repository is authoritative. A local clone was attempted only for dependency-scoped execution but the execution container has no DNS access to GitHub, so no local repository test result is claimed. Validation must therefore come from repository CI/check evidence for this branch.

The first source-text-integrity run exposed pre-existing false positives on valid JavaScript/template-string `\\n` data. The scanner itself was repaired on this branch. Check conclusions must be refreshed against the latest branch head before merge; no stale earlier result is treated as current validation.

## Remaining work

1. Run/inspect dependency-scoped PR checks.
2. Repair forward only failures attributable to this branch.
3. Refresh generated Hash216 repository index after source validation.
4. Merge when required checks permit.
5. Verify `main` contains the merged repair and regenerated projection.
6. Extend ref provenance with explicit GitHub PR validation/merge-state metadata where available; ref visibility itself is now implemented and does not depend on that metadata.
7. After this scoped assistant/global-hydration repair closes, audit the generic capability resolver/fallback planner because its legacy deterministic provider-ID ordering remains a separate local-selection surface. Do not reopen it inside this checkpoint unless current CI proves a direct dependency.
