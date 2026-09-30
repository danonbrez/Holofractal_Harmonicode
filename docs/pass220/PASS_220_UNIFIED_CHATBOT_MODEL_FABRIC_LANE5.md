# Pass 220 — Unified Chatbot Model Fabric + Lane 5 Tooling

Status: IMPLEMENTED CHECKPOINT / DEPENDENCY-SCOPED CI PENDING / AUTHORITY PRESERVED

## Purpose

The production HHS assistant is one chatbot surface over the language capabilities already present in the repository/runtime.

The production chatbot is an ingress/egress surface of Pass 219 / Lane 5. It must not create a parallel provider-selection authority outside the C++ RNA cell-wall composition manifold.

The unified routing contract is now:

```text
one witnessed conversation thread
  -> expose every language capability to Pass 219 / Lane 5
  -> attach runtime health, loading, preference, provenance, and authority evidence
  -> adapt ready TEXT_GENERATION members into the inherited Pass 124 selector
  -> three deterministic witness lanes isolate mutually validated invariants
  -> exact Fraction probability selects only among admitted candidates
  -> replay the selection receipt
  -> invoke the selected member through the inherited assistant receipt/ingress membrane
  -> on failure preserve evidence, exclude only that failed member, and recompose
  -> closed unavailable turn only when no admissible visible generator remains
```

No failed provider attempt appends a second user message. Reselection uses the inherited `continue_message()` witness path. Probability allocates selection among already-admissible candidates and never creates canonical authority.

## Declaring the primary model

HHS does not infer capability from a filename.

The declared primary/priority controls are:

```text
HHS_ASSISTANT_PRIMARY_MODEL=<registered-model-id>
HHS_ASSISTANT_MODEL_PRIORITY=model-a,model-b,model-c
HHS_LITERT_LM_MODEL=<compatibility configured model>
```

These declarations are retained as typed selection evidence and compatibility preferences. They do **not** form an execution hierarchy and they do not hide any other model from Lane 5.

The Pass 219 selector may incorporate declared/configured/loaded state into exact candidate utility while the Pass 124 witness lanes independently require visibility, callability, runtime readiness, text-generation capability, and preserved authority boundaries. The selected candidate is therefore receipt-bearing and replayable rather than the result of a local `if/else` provider chain.

## Unified contributors

The fabric reports and composes:

- every model returned by the LiteRT-LM `/v1/models` registry;
- the repository-native causal model when configured/loaded;
- the repository-native exact semantic/Pass 166 path as a context contributor, **not** a completed text generator;
- Pass 153 registered open-model generation;
- the active Pass 166 Word2Vec model as semantic-memory/retrieval contribution;
- other registered text-generation capability providers as visible specialized contributors, with actual unresolved runtime/configuration/adapter evidence preserved when present rather than inferred from the security membrane.

Pass 166 is not relabeled as a causal generator. It remains semantic memory and retrieval context.

## Pass 153 adapter

`hhs_backend/runtime/hhs_pass153_assistant_transport_v1.py` projects registered Pass 153 model backends through the same OpenAI-compatible assistant envelope.

Pass 153 output therefore enters the inherited:

```text
provider proposal
-> capability policy gate
-> provider receipt
-> provider-result ingress
-> Hash72-linked assistant message
```

It does not create a parallel chatbot or bypass assistant authority.

## Lane 5 tooling

The governed assistant tool registry now includes:

```text
hhs_language_model_fabric
hhs_lane5_capability_status
hhs_lane5_capability_search
```

The inherited 1.44 typed reverse-discovery spine remains valid, while Pass 219 1.69 now hydrates current-tree callable surfaces plus statically fetched branch/PR callable provenance into the Hash216 knowledge graph. Ref-only capability discovery never checks out or executes branch code, remains `UNRESOLVED`, and carries no canonical authority.

They explicitly preserve:

```text
candidate_only = true
runtime_mutation_admitted = false
automatic_hash216_composition_promoted = false
automatic_superedge_promotion_admitted = false
```

The canonical signed environmental VM81 admission boundary remains:

```text
hhs_exact_pass219_vm81_environment_admit_signed
```

The chatbot does not gain self-authorization or canonical mutation authority.

## Native intent routing

In `BOTH` mode, explicit Lane 5/model-fabric prompts bypass the old developer-keyword prefilter and can invoke the new governed tools.

Ordinary general conversation still does not force developer/Lane 5 tools.

`GENERAL_CHAT` continues to disable the governed developer tool registry by design.

## Health/status

Production assistant health now reports:

- the complete visible unified model fabric;
- `lane5_candidate_member_ids` and `lane5_candidate_count`;
- `composition_authority=PASS219_LANE5`;
- `local_provider_hierarchy_authority=false`;
- the last replayable Lane 5 selection receipt, when a turn has actually been composed;
- `selected_provider_id` / `selected_model_id` only after an actual Lane 5 selection rather than as a readiness guess;
- native causal/semantic readiness;
- Pass 153 model visibility;
- Pass 166 semantic-memory contribution;
- `lane5_tooling_enabled=true`.

## Validation

Focused tests cover:

1. declared model preferences remain visible without becoming composition authority;
2. unified fabric membership and Lane 5 visibility for LiteRT, native causal, Pass 153, and Pass 166;
3. Pass 124 consensus/probability selection with deterministic replay on one shared witnessed thread;
4. failed selected generators are excluded for the next composition without duplicating the user witness;
5. Lane 5/model-fabric tools remain in the governed read-only registry;
6. native `BOTH` mode Lane 5 intent routing;
7. exact semantic fallback cannot be persisted as a completed assistant generation;
8. Pass 153 transport remains available through the same governed assistant membrane.

The existing Pass 220 I003-I010 integration workflow is extended to compile the new modules and run the new focused test file.

## Authority

This change is routing and reachability only.

It does not grant:

- model self-authorization;
- direct VM81 mutation;
- direct Hash72 mint/commit authority;
- direct Hash216 persistence/mutation authority;
- automatic Lane 5 Hash216 composition promotion;
- automatic Lane 5 superedge promotion;
- filesystem/repository/deployment mutation from model output.

All inherited HHS admission, receipt, and result-ingress boundaries remain active.
