# Pass 220 I007 — Assistant Settings, Clipboard UX, Conversational Egress

Status: IMPLEMENTED CHECKPOINT / DEPENDENCY-SCOPED CI PENDING / NO AUTHORITY WIDENING

## 1. Product requirement

The production mobile assistant now behaves like a conventional LLM chat application while preserving HHS governance beneath the conversation surface.

The user-facing default is:

```text
conversation
→ natural-language response
→ optional copy
→ optional paste
→ optional settings
→ optional technical inspection
```

Raw API objects and JSON are not the primary interaction surface.

## 2. Custom system instructions

The mobile assistant exposes a `Settings` panel containing a bounded, user-editable `System instructions` field.

The browser stores the field under:

```text
hhs.production.assistant.custom_system_instruction
```

The setting is local to the user’s browser and is included with each assistant turn as:

```text
custom_system_instruction
```

Maximum length:

```text
8192 characters
```

An empty field means no user customization is applied.

## 3. System-instruction composition

User customization is additive.

The provider input is constructed as:

```text
inherited governed HHS system instruction
+
user-configured system instructions
+
thread conversation
```

The user field therefore customizes language-model response style and task behavior without replacing inherited HHS runtime-authority constraints.

The implementation validates the user instruction, then records a Hash72 root of the instruction in provider proposal/turn evidence. The raw instruction text is not copied into the returned governed turn object.

Turn evidence reports:

```text
custom_system_instruction_applied
custom_system_instruction_root_hash72
```

## 4. Conversational natural-language default

The inherited assistant system instruction is strengthened to require:

- clear conversational natural language;
- concise explanation of technical evidence;
- summarization of tool/runtime results;
- no raw JSON dump unless the user explicitly asks to inspect it.

The governed HHS tool assistant carries the same natural-language rule.

This changes presentation, not runtime authority.

## 5. Mobile clipboard controls

Every visible chat message now has a touch-friendly `Copy` action.

Copy behavior uses:

```text
navigator.clipboard.writeText
```

when available, with a browser fallback for copy-only environments.

The composer exposes a touch-friendly `Paste` button using:

```text
navigator.clipboard.readText
```

when browser permission is available.

If clipboard read is unavailable, the UI reports that the user can use the device-native Paste command.

The existing keyboard behavior remains:

```text
Enter       → send
Shift+Enter → newline
```

## 6. Raw JSON progressive disclosure

The primary assistant surface renders only the assistant message content and compact human-readable receipt/mode metadata.

It does not render the complete assistant turn JSON.

Persisted vector readback is now shown first as a natural-language state:

```text
Persisted vector retrieved
status …
operation …
mutation authority …
```

The exact object is placed behind a closed:

```text
Inspect technical JSON
```

control.

Other advanced Runtime OS areas may expose technical evidence when the user explicitly navigates to or opens an inspection surface.

## 7. User-controlled file/vector boundary

I007 preserves I006’s separation:

```text
file/vector ingress != assistant prompt attachment
```

Uploading or hydrating a file does not silently attach its payload to the language model.

The assistant metadata continues to state:

```text
vector_payload_auto_attached_to_prompt = false
```

Explicit RAG retrieval remains a separate operation.

## 8. Backend propagation

The bounded user instruction is propagated through:

```text
/api/assistant/chat
/api/assistant/threads/{thread_id}/messages
/api/assistant/ws/{thread_id}
→ ProductionAssistantService
→ primary Gemma/LiteRT-LM provider
→ native HHS fallback provider
→ HHSAssistantService model-message construction
```

Primary-to-native fallback therefore preserves the same user customization.

## 9. Authority

System-instruction customization cannot grant:

```text
VM81 mutation authority
Hash72 mint/commit authority
Hash216 mutation authority
filesystem authority
repository authority
automatic vector-to-prompt disclosure
```

The existing provider proposal, policy, receipt, ingress, tool allowlist, and runtime authority membranes remain in force.

## 10. Validation

I007 adds dependency-scoped validation for:

1. additive system-instruction composition;
2. base system instruction remaining first;
3. custom instruction Hash72 witnessing;
4. raw custom instruction not echoed in governed turn evidence;
5. 8192-character bound;
6. REST request support and oversized rejection;
7. Settings/localStorage source contract;
8. mobile Copy/Paste controls;
9. natural-language provider defaults;
10. assistant UI not rendering raw turn JSON;
11. vector JSON hidden behind explicit inspection;
12. workspace source verifier enforcement.

The cumulative Pass 220 workflow now includes I003-I007 while retaining the cold x86_64 calibration as the first executable workload.
