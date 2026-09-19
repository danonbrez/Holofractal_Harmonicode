# Pass 220 I008 restart checkpoint — general chat + agentic application development modes

Status: **RESTARTABLE IMPLEMENTATION CHECKPOINT — CI PENDING**

## Lineage

- branch: `pass220-lo-shu-normalization-checkpoint-1`
- predecessor I007 checkpoint: `add61a7aeae51a9731d28bfcd30be1c20cfdd610`
- I008 preimplementation checkpoint: `a0eef509ea9049c2b5cd5395cd143f0979e1c5c9`
- merge target: `main`
- PR: #491

## Implemented assistant modes

The production/native assistant now has one user-controlled mode field with exactly three normalized values:

```text
GENERAL_CHAT
AGENTIC_APPLICATION_DEVELOPMENT
BOTH
```

`BOTH` is the compatibility default.

### GENERAL_CHAT

- ordinary natural-language prompt/response behavior is primary;
- default HHS developer/runtime/repository tools are explicitly removed from the turn;
- the native provider does not automatically search the repository;
- conversational history and custom system instructions remain active;
- no canonical mutation authority is added.

### AGENTIC_APPLICATION_DEVELOPMENT

- code/application/workspace/runtime/test/build/deploy/repository work is the selected domain;
- governed HHS tools remain available;
- native repository retrieval occurs only when the prompt actually contains development intent;
- unrelated ordinary chat is redirected to General chat or Both rather than silently changing mode.

### BOTH

- ordinary chat remains ordinary chat;
- explicit development intent may use governed tools;
- the native provider independently prevents automatic repository retrieval for unrelated conversation;
- custom instructions, RAG/vector boundaries, receipts and inherited authority membranes remain unchanged.

## Implemented stack

Mode propagation now spans:

```text
mobile Settings
→ /api/assistant/chat | thread message | WebSocket
→ ProductionAssistantService
→ Gemma/LiteRT-LM primary or HHS native fallback
→ HHSAssistantService system-message composition
→ mode-aware governed tool membrane
→ mode-aware native prompt/response provider
```

System instruction order is:

```text
inherited governed HHS instruction
→ assistant-mode instruction
→ optional user custom system instruction
→ conversation history
```

## Native provider behavior

The repository-native provider now:

- reads the selected mode from the system-message marker;
- supports a no-tool General Chat prompt/response cycle;
- uses exact development-intent routing before selecting repository tools;
- leaves ordinary Both-mode conversation out of repository search;
- keeps HARMONICODE semantic analysis and governed evidence paths available;
- records `assistant_mode` and `general_chat_prompt_response_cycle` in its trace;
- keeps internal Word2Vec context from being appended as diagnostic chatter to ordinary greetings/general conversation.

This is still the inherited native language stack: Pass 148 semantic membrane, Pass 151 bounded reasoner, Pass 166 language memory, governed provider receipts/result ingress, plus the current Pass 220 assistant-mode routing. No new canonical authority is granted.

## Mobile UI

`ProductionAssistantChat.tsx` now exposes:

- General chat
- Agentic application development
- Both

under Settings.

The choice persists as:

```text
hhs.production.assistant.mode
```

and is sent on every turn as `assistant_mode`.

The active mode is visible in the assistant header, turn metadata and footer.

I007 system instructions, Copy/Paste, conversational egress, inspect-only raw JSON, and user-controlled vector ingress remain intact.

## Implementation commits

- preimplementation checkpoint: `a0eef509ea9049c2b5cd5395cd143f0979e1c5c9`
- base assistant mode normalization/system composition: `9217106aef4bc15954ae1fb5d977030d38db698d`
- governed HHS tool mode membrane: `352eb82bd20d026a7dab435e2d0d0223f3bcc9d8`
- production hierarchy mode propagation: `350a6bd97463dcad588e19cf64762291be084ede`
- native fallback mode repair: `45fcc3ce4b2ba4eadac484815ea96105070dce5c`
- assistant REST/WS mode API: `386b1d30b862819f3879d6aa58577f777d217512`
- native general-chat + mixed-intent routing: `adf98906a3e3dbdc73416539a5a22a09e27289fa`
- mobile mode selector/settings persistence: `0c5ad156e9a4fa922df3e37a662c6f7b6f3638d4`
- per-turn HHS tool availability reporting: `8f147345c2c4c4713d61a5229726b7df7a654f15`
- native development-intent hardening: `787fc2297ea926f457affb20ce97ccbc8631e24c`
- production capability/status update: `7c8ab915cb3f5597081d5a56939e785b4b4634a8`
- agentic unrelated-chat repository-search repair: `3fcdafd988b9f26df9fc0239100e47767187d9ce`
- dependency-scoped assistant-mode tests: `3b2f6b8d7dff1c71429f4edc7b9fd584f8612e95`
- Runtime OS mode source verification: `755963b5115e959b4027020c001c2acc7b267bbd`
- mobile mode UI source tests: `81ada3b5da2ad66366b3c9ded07eca72ec0cfdef`
- invalid WebSocket mode fail-closed repair: `2aa6e617b7273b5e123aaf28ca7a410a8b0b3368`
- formal I008 contract: `f1199ca1dce5b2f761e6545adf4722fffda32c2b`
- cumulative I003-I008 workflow: `bfdcd131f92aa369c7cced684e01a2df38cda48d`
- DigitalOcean mobile bundle mode checks: `233788154264ca22772125e9b58da717eb2eded5`
- conversational native Word2Vec presentation repair: `3877c70ccaa9b0da7b28dc44ad779c475f0a989d`

## Validation

The cumulative Pass 220 workflow now compiles and runs dependency-scoped I001-I008 tests after the unchanged cold raw x86_64 calibration.

The DigitalOcean mobile-control workflow verifies the built bundle contains the three user modes.

Runtime OS production-root validation remains responsible for the full TypeScript/source-verifier/build surface.

Per the repository responsiveness policy, this checkpoint is preserved without waiting for queued external runners.

## Next action

Inspect the newest impacted workflow runs. Repair forward only I008-specific failures. If green, close PR #491 toward merge readiness and then validate the exact-main DigitalOcean deployment with one turn in each mode:

1. ordinary General Chat with zero HHS developer tool calls;
2. Agentic Application Development with an explicit governed development request;
3. Both with one ordinary chat turn followed by one explicit application-development turn in the same assistant surface.
