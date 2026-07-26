# HHS PASS 153 COMPLETION ADDENDUM — LiteRT-LM Gemma 4 AI Thread Interface

## 1. Normative metadata

| Field | Normative value |
|---|---|
| Contract identifier | `HHS-P153-LITERTLM-G4-AITI` |
| Canonical layer | `LITERT_LM_GEMMA4_AI_THREAD_INTERFACE` |
| Version | `1.0.0` |
| Repository | `danonbrez/Holofractal_Harmonicode` |
| Inheritance | Complete authoritative Pass 158 inherited nucleus, with Pass 153 assistant-interface requirements completed additively |
| Provider | Google AI Edge LiteRT-LM local runtime |
| Model family | Gemma 4 `.litertlm` instruction model |
| Transport | Local OpenAI-compatible HTTP API |
| HHS authority role | Natural-language request and projection interface only |
| Canonical mutation authority | VM81 admission surfaces only |
| Provider evidence | Hash72-linked invocation receipt followed by HHS provider-result ingress |

## 2. Purpose

This layer makes Gemma 4 the conversational AI thread interface to HHS. The
assistant receives natural-language messages, preserves a bounded thread
history, communicates with a local LiteRT-LM server, returns text and tool-call
proposals to the user interface, and routes every completed provider result
through the existing HHS capability, policy, receipt, modality-ingress, and
canonical-observer layers.

The model is not the HHS runtime. It is a provider attached to the HHS runtime.

```text
User message
-> HHS thread envelope
-> capability proposal
-> policy gate
-> LiteRT-LM / Gemma 4
-> provider receipt
-> HHS result ingress
-> user projection
```

## 3. Mandatory invariants

1. `MODEL_OUTPUT_REQUIRES_HHS_INGRESS`.
2. `MODEL_HAS_NO_DIRECT_VM81_MUTATION_AUTHORITY`.
3. `SUCCESSFUL_INFERENCE_DOES_NOT_EQUAL_ADMITTED_MUTATION`.
4. `THREAD_TRANSCRIPT_IS_NOT_CANONICAL_RUNTIME_STATE`.
5. `TOOL_CALLS_ARE_REQUEST_PROPOSALS_UNTIL_SEPARATELY_ADMITTED`.
6. `EVERY_USER_AND_ASSISTANT_MESSAGE_HAS_A_HASH72_CHAIN_WITNESS`.
7. `THREAD_HISTORY_IS_BOUNDED_WHILE_MESSAGE_SEQUENCE_REMAINS_MONOTONIC`.
8. `TRANSPORT_FAILURE_RETURNS_A_CLOSED_REJECTION_ENVELOPE`.
9. `RAW_PROVIDER_OUTPUT_NEVER_REPLACES_THE_USER_SOURCE`.
10. `PROVIDER_IDENTITY_IS_DISTINCT_FROM_CAPABILITY_AND_AUTHORITY`.

## 4. Runtime components

### 4.1 Conversation service

`hhs_backend/runtime/hhs_litert_lm_assistant_v1.py` provides:

- environment-resolved LiteRT-LM configuration;
- a standard-library HTTP transport for `/v1/models` and `/v1/chat/completions`;
- bounded conversation thread storage;
- Hash72-linked message records;
- deterministic provider selection through the HHS capability registry;
- policy-gated invocation;
- provider invocation receipts;
- universal provider-result ingress;
- explicit non-mutation and non-canonical-output flags;
- an offline-safe health result;
- a network-independent self-test transport.

### 4.2 API router

`hhs_backend/api/litert_lm_assistant_routes.py` provides:

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/api/assistant/status` | HHS assistant configuration and authority boundary |
| `GET` | `/api/assistant/health` | LiteRT-LM model-server reachability and model list |
| `GET` | `/api/assistant/threads` | List bounded conversation projections |
| `POST` | `/api/assistant/threads` | Create a new HHS AI thread |
| `GET` | `/api/assistant/threads/{thread_id}` | Read one thread projection |
| `POST` | `/api/assistant/threads/{thread_id}/messages` | Execute one governed assistant turn |
| `POST` | `/api/assistant/chat` | Create-or-continue convenience endpoint |
| `WS` | `/api/assistant/ws/{thread_id}` | Bidirectional thread message channel |

### 4.3 Provider registry

The deterministic provider registry shall expose:

```text
provider:hhs.litert_lm.gemma4
```

with:

```text
provider_kind = LITERT_LM_OPENAI_COMPATIBLE_LOCAL_PROVIDER
capability_classes = [TEXT_GENERATION]
authority_scope = PROVIDE_RAW_RESULT_ONLY
result_ingress_required = true
provider_is_canonical_authority = false
provider_self_authorizes = false
```

## 5. LiteRT-LM deployment contract

The local model server shall be started through LiteRT-LM's OpenAI-compatible
server command and shall expose port `9379` unless explicitly configured
otherwise.

Default HHS values:

```bash
export HHS_LITERT_LM_BASE_URL=http://127.0.0.1:9379/v1
export HHS_LITERT_LM_MODEL=gemma-4-E2B-it
export HHS_LITERT_LM_TIMEOUT_SECONDS=120
export HHS_LITERT_LM_MAX_THREADS=128
export HHS_LITERT_LM_MAX_MESSAGES_PER_THREAD=64
export HHS_LITERT_LM_MAX_OUTPUT_TOKENS=2048
export HHS_LITERT_LM_TEMPERATURE=0.2
export HHS_LITERT_LM_TOP_P=0.95
export HHS_LITERT_LM_TOP_K=40
export HHS_LITERT_LM_SEED=72
export HHS_LITERT_LM_REASONING_EFFORT=medium
```

The model identifier is deployment-configurable because imported LiteRT-LM
model aliases may differ. The deployed alias and `HHS_LITERT_LM_MODEL` must
match.

## 6. Message-chain contract

Every message record shall contain:

- `message_id`;
- `thread_id`;
- monotonic `sequence`;
- `role`;
- `content`;
- optional `tool_calls`;
- `previous_message_root_hash72`;
- `message_root_hash72`;
- provider-ingress admission projection;
- explicit non-canonical and non-mutation flags.

When bounded retention removes older message bodies, `message_count` and later
sequence values shall not be renumbered. This preserves monotonic conversation
history even when the user-interface projection is compacted.

## 7. Tool-use boundary

Gemma 4 tool calls may describe HHS API operations, but the assistant service
shall not execute mutating operations merely because a model emitted a tool
call. Tool dispatch requires a distinct HHS operation request, policy decision,
authorized target, execution receipt, and runtime admission result.

A returned tool call is therefore `PROPOSED_TOOL_CALL` and never
`COMMITTED_RUNTIME_TRANSITION` without separate admitted evidence.

## 8. Failure closure

The following states are terminal for a single assistant turn and shall not
leave an unresolved authority transition:

- `REJECT_LITERT_LM_PROVIDER_INVOCATION`;
- `LITERT_LM_TRANSPORT_ERROR`;
- `PROJECT_LITERT_LM_TURN_WITH_INGRESS_REJECTION`;
- `HHS_AI_CONVERSATION_THREAD_NOT_FOUND`;
- `HHS_AI_CONVERSATION_MESSAGE_REJECTION`.

The user message may remain in the bounded thread projection after transport
failure, but no assistant message or runtime mutation shall be fabricated.

## 9. Acceptance requirements

The layer is complete only when:

1. Python syntax compilation passes for the service, router, and tests.
2. A fake-transport positive turn produces a user-message Hash72 root, an assistant-message Hash72 root, a provider invocation receipt root, and a provider-result ingress root.
3. The selected `TEXT_GENERATION` provider is `provider:hhs.litert_lm.gemma4`.
4. Three conversation turns with a four-message retention limit preserve `message_count = 6`, `len(messages) = 4`, and terminal sequence `6`.
5. Health succeeds against a fake `/v1/models` response.
6. Offline transport returns `LITERT_LM_OFFLINE` or `LITERT_LM_TRANSPORT_ERROR` without a direct runtime mutation.
7. Existing provider-registry negative tests continue rejecting self-authorizing providers.
8. The canonical backend exposes the REST and WebSocket routes.
9. A live LiteRT-LM Gemma 4 workload is executed before terminal release classification.
10. Release evidence records the model alias, LiteRT-LM version, backend, device, context limit, latency, and receipt roots.

## 10. Current implementation classification

The committed code constitutes the complete governed API/thread integration
surface and a deterministic fake-transport verification harness.

A terminal live-model classification remains conditional on executing the
repository against an installed Gemma 4 `.litertlm` model and recording the
resulting HHS receipts:

```text
HHS_PASS_153_LITERT_LM_GEMMA4_AI_THREAD_INTERFACE_LIVE_VERIFIED
```

Until that live workload is recorded, the accurate classification is:

```text
HHS_PASS_153_LITERT_LM_GEMMA4_AI_THREAD_INTERFACE_IMPLEMENTED_PENDING_LIVE_MODEL
```
