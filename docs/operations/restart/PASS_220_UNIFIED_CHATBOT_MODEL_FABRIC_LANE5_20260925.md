# Pass 220 Unified Chatbot Model Fabric + Lane 5 — Restart Checkpoint

Date: 2026-09-25

## Repository state

- repository: `danonbrez/Holofractal_Harmonicode`
- base main: `156d4138f2640c6fd8937f96ffb5c030ae9b7952`
- branch: `pass220/unified-chatbot-lane5-model-fabric-20260925`
- implementation head before documentation: `f03139926208810e97a371622637809c99e457b5`
- merge target: `main`
- pull request: `#589` — `https://github.com/danonbrez/Holofractal_Harmonicode/pull/589`
- exact PR head before this restart-record update: `230baca6fe33ddfeaec9d90224412b7489bff505`

## Trigger

Production native chat was observed to respond to a trivial greeting while substantive generation did not use the repository's broader language-model capability.

Repository audit established two disconnected surfaces:

1. production assistant selection was hard-coded around one configured LiteRT alias plus the native provider;
2. Lane 5 capability self-model/reverse-discovery was not exposed through the assistant tool registry.

## Implemented

1. Added `hhs_pass153_assistant_transport_v1.py` so Pass 153 registered language models participate in the same assistant receipt/ingress pipeline.
2. Added `hhs_unified_language_model_fabric_v1.py` to inventory and order all registered LiteRT models plus native/Pass 153/Pass 166 contributors.
3. Reworked `ProductionAssistantService` to route all registered LiteRT models on one witnessed user message before native HHS and Pass 153 fallback.
4. Added `HHS_ASSISTANT_PRIMARY_MODEL` and `HHS_ASSISTANT_MODEL_PRIORITY` selection semantics without guessing quality from model names.
5. Added assistant tools:
   - `hhs_language_model_fabric`
   - `hhs_lane5_capability_status`
   - `hhs_lane5_capability_search`
6. Added native `BOTH`-mode routing for explicit Lane 5/model-fabric requests.
7. Preserved the Lane 5 candidate-only/no-auto-promotion boundary and singleton signed VM81 admission export.
8. Added dependency-scoped tests.
9. Extended the existing Pass 220 integration workflow to compile and run the new surfaces/tests.

## Changed files

```text
.github/workflows/pass220-i003-four-phase-abc-max-hardware.yml
hhs_backend/runtime/hhs_assistant_api_tool_gateway_v1.py
hhs_backend/runtime/hhs_litert_lm_hhs_api_assistant_v1.py
hhs_backend/runtime/hhs_native_litert_lm_provider_v1.py
hhs_backend/runtime/hhs_pass153_assistant_transport_v1.py
hhs_backend/runtime/hhs_production_assistant_v1.py
hhs_backend/runtime/hhs_unified_language_model_fabric_v1.py
tests/pass220/test_hhs_pass220_unified_chatbot_lane5_model_fabric.py
docs/pass220/PASS_220_UNIFIED_CHATBOT_MODEL_FABRIC_LANE5.md
docs/operations/restart/PASS_220_UNIFIED_CHATBOT_MODEL_FABRIC_LANE5_20260925.md
```

## Commands / repository operations completed

```text
create branch from main
repository code searches for language models, provider registries, hydration, and Lane 5 services
fetch current production assistant / native provider / tool gateway / Pass 153 / Pass 215 / Pass 220 sources
incremental GitHub contents commits for implementation
compare branch against main
source review of changed routing/tool sections
extend existing Pass 220 workflow
```

A container-side raw-GitHub compile attempt was made, but the container had no DNS resolution for `raw.githubusercontent.com`; no source-level failure was inferred from that environment limitation.

## Validation completed

- branch remains based on exact main with no behind commits at the implementation checkpoint;
- changed-file scope reviewed;
- model routing preserves one shared thread and `continue_message()` fallback;
- Lane 5 tools are read-only/candidate-only by construction;
- native `BOTH` intent guard repaired so Lane 5/model-fabric prompts reach the new tools;
- existing Pass 220 workflow now includes new modules/tests in its compile/test matrix.

## Validation remaining

Pull request #589 triggered repository CI at exact PR head `230baca6fe33ddfeaec9d90224412b7489bff505`.

Observed queued checks include:

```text
Pass 220 I003-I010 integration     run 36195013074
LiteRT-LM Gemma 4 Assistant       run 36195013017
Runtime OS Production Root        run 36195013060
```

`Guarded Continuous Integration` run `36195013016` was skipped; it is not used as positive acceptance evidence for this bounded change.

Repository CI on the pull-request exact head:

```text
Pass 220 I003-I010 Cold Raw x86_64 Calibration + User-Controlled RAG Context Integration
```

The relevant post-calibration stages must compile:

```text
hhs_assistant_api_tool_gateway_v1.py
hhs_pass153_assistant_transport_v1.py
hhs_unified_language_model_fabric_v1.py
hhs_production_assistant_v1.py
hhs_native_litert_lm_provider_v1.py
```

and run:

```text
tests/pass220/test_hhs_pass220_unified_chatbot_lane5_model_fabric.py
```

alongside the inherited I003-I010 integration tests.

## Environment state

- no model download was performed;
- no hydrated model artifact was replaced;
- no VM81/Hash72/Hash216 authority was widened;
- no Lane 5 composition/superedge promotion was admitted;
- no deployment mutation was performed.

## Blockers

No implementation blocker identified.

CI is required to establish exact-head repository validation. The local container network limitation prevents using raw GitHub downloads for an independent local `py_compile` run in this chat environment.

## Next action

1. allow the existing dependency-scoped Pass 220 workflow to finish on PR #589;
2. repair forward only changed-surface failures;
3. when green and mergeable, merge PR #589;
4. verify `main` contains the unified model fabric + Lane 5 assistant tooling;
5. production deployment should then verify the runtime `/api/assistant/health` reports the expected declared primary hydrated model and the assistant can answer a nontrivial prompt through that model.
