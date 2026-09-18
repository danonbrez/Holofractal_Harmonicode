# Pass 220 I010 — User-Approved Vector Context RAG

Status: IMPLEMENTED CHECKPOINT / DEPENDENCY-SCOPED CI PENDING / EXPLICIT USER ATTACHMENT ONLY

## 1. Purpose

I010 connects the production multimodal vector-ingress surface to the assistant as an explicit user-controlled retrieval context.

The production flow is:

```text
choose file
→ preview
→ Hydrate vector store
→ Read persisted vector
→ Use in chat
→ bounded user-approved context
→ assistant generation
```

No uploaded or hydrated payload is attached merely because it exists in the workspace/vector store.

## 2. Explicit attachment contract

Assistant context is accepted only when:

```text
explicit_user_attachment = true
```

The normalized attachment carries:

- source name;
- modality;
- optional source SHA-256;
- optional Pass 174 operation key;
- optional lifecycle Hash216 lineage identity;
- bounded context text.

Maximum context text length is 32,768 characters.

64-character source/operation/lifecycle identities are validated as hexadecimal when supplied.

## 3. Authority ordering

The model input order remains:

```text
inherited governed HHS authority instruction
→ selected assistant-mode instruction
→ optional user custom system instruction
→ explicit user-approved retrieval context
→ conversation history
```

The context is marked as evidence/data and explicitly denied authority to become a higher-priority instruction, permission boundary, or mutation grant.

## 4. No raw context echo

The raw attached text is used only to construct the provider prompt.

Governed turn evidence stores:

```text
user_context_applied
user_context_root_hash72
user_context_source
```

where `user_context_source` contains only bounded identity metadata.

The raw context body is not copied into the returned turn object.

## 5. Mobile Runtime OS behavior

The Pass 174 file/vector surface now requires this explicit sequence:

```text
Hydrate vector store
→ Read persisted vector
→ Use in chat
```

The `Use in chat` control is not enabled conceptually until persisted readback has succeeded with:

```text
HHS_PASS_174_VECTOR_QUERY_HIT
```

The active context is visible above the composer as:

```text
Context attached by you
<source name> · <modality>
Remove
```

Selecting a different file or rehydrating the source clears the active assistant context.

## 6. Text and multimodal behavior

For browser-readable text/source/JSON/YAML/CSV/HARMONICODE inputs, the locally decoded text is attached up to the 32,768-character boundary after explicit user approval.

For PDF/image/audio/video/binary inputs without an authorized natural-language decoder, I010 attaches only bounded source/vector metadata.

The UI explicitly states that the binary payload itself has not been decoded into natural language.

I010 therefore does not fabricate image, audio, video, PDF, or binary understanding.

## 7. Existing privacy boundary

The inherited metadata remains:

```text
vector_payload_auto_attached_to_prompt = false
```

Even when an explicit context attachment is active, this remains true because the attachment is user-triggered rather than automatic.

Each request separately records:

```text
user_approved_context_attached = true|false
```

## 8. Assistant API

The following surfaces now accept optional `user_context`:

- `POST /api/assistant/chat`
- `POST /api/assistant/threads/{thread_id}/messages`
- `/api/assistant/ws/{thread_id}`

The context propagates through:

```text
ProductionAssistantService
→ preferred Gemma/LiteRT-LM provider
→ native HHS fallback
→ HHSAssistantService prompt composition
```

Primary-provider failure does not lose the explicit context when the native provider continues the already-witnessed user message.

## 9. Hash72 binding

The normalized context is bound as:

```text
user_context_root_hash72
```

and that root is included in the provider execution proposal input.

This gives deterministic evidence that a particular explicit attachment participated in the language-generation turn without exposing the raw context in the governed response object.

## 10. Tests

I010 dependency-scoped tests verify:

1. context reaches the provider only when explicitly attached;
2. the context is marked as evidence/data rather than instruction authority;
3. raw context text is absent from governed turn evidence;
4. the attachment root and source identities are returned;
5. implicit context is rejected before provider invocation;
6. oversize context is rejected;
7. malformed SHA-256 identities are rejected;
8. REST chat accepts explicit context;
9. vector readback is required before the UI can attach context;
10. text context is bounded;
11. non-text payloads attach metadata only;
12. the composer visibly exposes attached context;
13. context removal is user controlled;
14. workspace source verification and DigitalOcean mobile bundle gates require the new controls.

## 11. Authority

I010 adds no direct:

```text
VM81 mutation authority
Hash72 commit authority
Hash216 mutation authority
repository mutation authority
filesystem authority
automatic data disclosure
```

It is a user-controlled RAG context projection into the existing natural-language generation boundary.
