# Pass 220 — Unified Chatbot Model Fabric + Lane 5 Tooling

Status: IMPLEMENTED CHECKPOINT / DEPENDENCY-SCOPED CI PENDING / AUTHORITY PRESERVED

## Purpose

The production HHS assistant is one chatbot surface over the language capabilities already present in the repository/runtime.

The previous production selector treated one configured LiteRT alias and the native semantic provider as separate alternatives. That allowed a registered/hydrated model to exist without being considered by the chatbot when its ID was not the configured alias.

The unified routing contract is now:

```text
one conversation thread
  -> discover all LiteRT-LM registered model IDs
  -> apply declared model priority
  -> try each registered LiteRT generator on the same witnessed user message
  -> native HHS causal/semantic provider
  -> Pass 153 registered open-model fallback
  -> closed unavailable turn only if every callable member fails
```

No failed provider attempt appends a second user message. Fallback uses the inherited `continue_message()` witness path.

## Declaring the primary model

HHS does not infer capability from a filename.

The declared primary/priority controls are:

```text
HHS_ASSISTANT_PRIMARY_MODEL=<registered-model-id>
HHS_ASSISTANT_MODEL_PRIORITY=model-a,model-b,model-c
HHS_LITERT_LM_MODEL=<compatibility configured model>
```

Ordering is:

1. explicit primary if registered;
2. explicit priority list entries if registered;
3. the configured `HHS_LITERT_LM_MODEL` if registered;
4. all remaining registered LiteRT models in deterministic order.

This lets the most capable hydrated/imported model be designated without disconnecting the other registered models from the chatbot.

## Unified contributors

The fabric reports and composes:

- every model returned by the LiteRT-LM `/v1/models` registry;
- the repository-native causal model when configured/loaded;
- the repository-native exact semantic fallback;
- Pass 153 registered open-model generation;
- the active Pass 166 Word2Vec model as semantic-memory/retrieval contribution;
- other registered text-generation capability providers as specialized registered contributors pending their own runtime-health/adapter requirements.

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

Lane 5 tools use the validated 1.44 repository capability reverse-discovery surface and return bounded evidence only.

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

- `selected_provider_id`;
- `selected_model_id`;
- `unified_model_fabric`;
- registered LiteRT model IDs and route order;
- native causal/semantic readiness;
- Pass 153 fallback models;
- Pass 166 semantic-memory contribution;
- `lane5_tooling_enabled=true`.

## Validation

Focused tests cover:

1. explicit primary/priority ordering across all registered LiteRT models;
2. unified fabric membership for LiteRT, native causal, Pass 153, and Pass 166;
3. routing to the declared primary model on one shared witnessed thread;
4. Lane 5/model-fabric tools present in the governed read-only registry;
5. native `BOTH` mode Lane 5 intent routing;
6. Pass 153 transport availability as an assistant fallback.

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
