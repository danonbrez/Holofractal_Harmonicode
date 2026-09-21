# Pass 220 I008 preimplementation checkpoint — general chat + agentic application development modes

Status: **RESTARTABLE PREIMPLEMENTATION CHECKPOINT**

## Lineage

- branch: `pass220-lo-shu-normalization-checkpoint-1`
- predecessor head: `add61a7aeae51a9731d28bfcd30be1c20cfdd610`
- merge target: `main`
- PR: #491

## User-controlled assistant modes

The production/native assistant SHALL expose three explicit modes:

```text
GENERAL_CHAT
AGENTIC_APPLICATION_DEVELOPMENT
BOTH
```

### GENERAL_CHAT

- ordinary natural-language prompt/response token-generation behavior;
- conversational answers are primary;
- developer/runtime/repository tool surfaces are disabled by default;
- no automatic repository search merely because a prompt is not HARMONICODE;
- custom system instructions remain available;
- no canonical runtime mutation authority.

### AGENTIC_APPLICATION_DEVELOPMENT

- application/code/workspace/runtime development is the explicit task domain;
- governed HHS assistant tools are available;
- native provider may use repository/runtime evidence to support development work;
- unrelated general-chat prompts should remain secondary to the selected development-only mode;
- any mutating operation remains subject to inherited HHS authority and user/governed workflow gates.

### BOTH

- ordinary general conversation remains normal conversation;
- application-development tooling is also available;
- native HHS provider SHALL NOT force repository/tool retrieval for unrelated general chat;
- explicit development/runtime/repository intent may activate governed tools.

## Required implementation

1. Add one normalized `assistant_mode` field through REST, thread-message, and WebSocket assistant requests.
2. Propagate mode through production provider hierarchy and native fallback.
3. Compose a mode-specific system instruction beneath the inherited HHS authority instruction and above user custom instructions.
4. Make governed default tools mode-aware.
5. Make the native provider mode-aware so BOTH does not auto-search the repository on ordinary conversation.
6. Add Settings selector with General chat / Agentic application development / Both.
7. Persist the user choice locally.
8. Display the active mode in the conversation surface/turn metadata.
9. Add backend + UI negative/replay tests.
10. Preserve I007 copy/paste, conversational egress, inspect-only JSON, and user-controlled vector ingress.

## Default

`BOTH` is the compatibility/default mode so the application remains a general chatbot and a governed development assistant without requiring a mode switch for mixed workflows.

## Validation boundary

Dependency-scoped tests and Runtime OS typecheck/build will be wired before the postimplementation checkpoint. External CI may remain queued; implementation will checkpoint without waiting.
