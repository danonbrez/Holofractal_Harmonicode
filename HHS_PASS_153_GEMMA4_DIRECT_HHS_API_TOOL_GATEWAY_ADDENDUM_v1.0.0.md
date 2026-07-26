# HHS PASS 153 ADDENDUM — Gemma 4 Direct HHS API Tool Gateway

## Normative metadata

| Field | Normative value |
|---|---|
| Contract identifier | `HHS-P153-G4-DIRECT-API-TOOLS` |
| Version | `1.0.0` |
| Parent | `HHS-P153-LITERTLM-G4-AITI` |
| Provider | `provider:hhs.litert_lm.gemma4` |
| Default model alias | `gemma4-12b` |
| Tool authority | Read-only canonical HHS API projection |
| Mutation authority | Prohibited for model-generated tool calls |
| Maximum automatic tool rounds | `4` |

## Purpose

Gemma 4 shall communicate with HHS through explicit governed API tools rather
than relying only on prompt context or unverified model recollection. The
assistant transport supplies a default HHS tool registry to LiteRT-LM, receives
OpenAI-compatible function calls, executes only allowlisted read-only HHS API
surfaces, returns Hash72-witnessed tool receipts to the model, and requests a
final natural-language answer grounded in those results.

```text
User message
-> Gemma 4
-> proposed HHS API tool call
-> read-only tool registry gate
-> canonical HHS API function
-> guarded API response + HHS I/O evidence
-> Hash72 tool receipt
-> Gemma 4 final answer
-> provider receipt
-> HHS result ingress
-> AI thread projection
```

## Default tools

| Tool | Canonical HHS surface | Authority |
|---|---|---|
| `hhs_runtime_state` | `GET /api/runtime/state` | Read-only |
| `hhs_runtime_services` | `GET /api/runtime/services` | Read-only |
| `hhs_runtime_service_status` | `GET /api/runtime/services/status` | Read-only |
| `hhs_kernel_invariants` | `GET /api/runtime/conformance/invariants` | Read-only |
| `hhs_kernel_conformance_status` | `GET /api/runtime/conformance/status` | Read-only |
| `hhs_pass152_status` | `GET /api/runtime/pass152/status` | Read-only |
| `hhs_pass152_capabilities` | `GET /api/runtime/pass152/capabilities` | Read-only |

The registry is exposed to clients at:

```text
GET /api/assistant/tools
```

## Mandatory invariants

1. `MODEL_TOOL_CALL_IS_NOT_SELF_AUTHORIZATION`.
2. `ONLY_REGISTERED_READ_ONLY_HHS_API_TOOLS_EXECUTE_AUTOMATICALLY`.
3. `MUTATING_MODEL_TOOL_EXECUTION_ALLOWED = FALSE`.
4. `EVERY_EXECUTED_TOOL_RESULT_HAS_A_HASH72_TOOL_RECEIPT`.
5. `THE_CANONICAL_HHS_API_RESPONSE_REMAINS_INSIDE_THE_TOOL_RECEIPT`.
6. `THE_MODEL_RECEIVES_TOOL_EVIDENCE_BEFORE_GENERATING_THE_FINAL_ANSWER`.
7. `UNKNOWN_OR_MUTATING_TOOL_NAMES_CLOSE_AS_REJECTIONS`.
8. `TOOL_REJECTION_NEVER_FABRICATES_RUNTIME_MUTATION`.
9. `AUTOMATIC_TOOL_RECURSION_IS_BOUNDED`.
10. `THE_FINAL_MODEL_RESULT_STILL_REQUIRES_PROVIDER_RECEIPT_AND_HHS_INGRESS`.

## Runtime implementation

### Tool gateway

`hhs_backend/runtime/hhs_assistant_api_tool_gateway_v1.py` provides:

- the default OpenAI-compatible function-tool definitions;
- a deterministic allowlist of read-only HHS API executors;
- canonical route-function invocation;
- closed rejection for unknown or mutating tool names;
- Hash72-witnessed tool receipts;
- an inspectable tool registry root;
- a self-test covering admitted status access and rejected halt access.

### Tool-loop transport

`hhs_backend/runtime/hhs_litert_lm_hhs_api_assistant_v1.py` provides:

- default HHS tools on every assistant inference request;
- parsing of LiteRT-LM OpenAI-compatible `tool_calls`;
- bounded execution of read-only HHS tools;
- canonical `tool` role messages returned to Gemma 4;
- final-answer inference after tool evidence is available;
- a complete `hhs_api_tool_trace` attached to the HHS assistant turn;
- explicit `mutating_model_tool_execution_allowed = false`;
- recomputed Hash72 turn root after the tool trace is attached.

## Rejection semantics

The following model request shall not execute:

```json
{
  "name": "hhs_runtime_halt",
  "arguments": {}
}
```

It shall produce:

```text
REJECT_HHS_ASSISTANT_API_TOOL_CALL
runtime_mutation_admitted = false
model_self_authorized = false
```

Mutating HHS actions may be added only through a separate contract containing:

- an explicit user-authorized operation;
- target and capability validation;
- zero-bypass interposition;
- a distinct execution proposal;
- VM81 admission;
- Hash72 receipt closure;
- negative tests for model self-authorization.

## Acceptance requirements

1. The tool registry contains all seven default read-only tools.
2. `hhs_runtime_halt` is absent from the registry.
3. A two-inference fake LiteRT-LM workload performs one tool call and one final answer.
4. The tool result includes the canonical Pass 152 API response.
5. The tool receipt has a non-empty Hash72 root.
6. The assistant turn includes the complete tool trace.
7. The assistant turn reports zero admitted runtime mutations.
8. Unknown and mutating tool calls close as deterministic rejections.
9. Python compilation and dependency-scoped tests pass against current `main`.
10. A live `gemma4-12b` workload must be recorded before terminal live-model classification.

## Classification

Before live Gemma 4 execution evidence:

```text
HHS_PASS_153_GEMMA4_DIRECT_HHS_API_TOOL_GATEWAY_IMPLEMENTED_PENDING_LIVE_MODEL
```

After a live tool-call workload records model, backend, latency, context,
provider receipt, tool receipt, and HHS ingress roots:

```text
HHS_PASS_153_GEMMA4_DIRECT_HHS_API_TOOL_GATEWAY_LIVE_VERIFIED
```
