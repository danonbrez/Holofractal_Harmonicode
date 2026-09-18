# Pass 220 I010 preimplementation checkpoint — explicit user-approved vector context in chat

Status: **RESTARTABLE PREIMPLEMENTATION CHECKPOINT**

## Lineage

- branch: `pass220-lo-shu-normalization-checkpoint-1`
- predecessor repair checkpoint: `d61007b1b2545a2975c9778fea8cbe7c888ab3c1`
- merge target: `main`
- PR: #491

## Objective

Close the remaining product gap between multimodal vector-store ingress and RAG chat while preserving the user-controlled disclosure boundary.

The production path SHALL be explicit:

```text
choose file
→ local preview
→ Hydrate vector store
→ Read persisted vector
→ Use in chat
→ assistant request carries bounded user-approved context
→ language model sees that context as evidence/data
```

Nothing is attached merely because a file was uploaded or hydrated.

## Context contract

A chat context attachment SHALL contain bounded metadata plus context text:

```text
explicit_user_attachment = true
source_name
modality
source_identity_sha256
operation_key
lifecycle_hash216
text
```

The backend SHALL:

- reject context without the explicit user-attachment flag;
- validate 64-hex source/operation identities when supplied;
- bound attached text to 32,768 characters;
- bind the normalized attachment into Hash72 turn/proposal evidence;
- insert it below inherited HHS authority + mode + user custom instructions;
- mark it as untrusted/evidence data rather than executable system instruction;
- avoid echoing the raw attachment text in the returned governed turn object.

## Multimodal behavior

- text/source/JSON/YAML/CSV/HARMONICODE files may attach their local decoded text after persisted vector readback;
- image/audio/video/PDF/binary files may attach only bounded file/vector metadata in I010 unless a separately implemented modality decoder has produced authorized natural-language content;
- I010 MUST NOT pretend that binary/vector ciphertext is natural-language context.

## UI

The mobile file surface SHALL add:

- `Use in chat` after persisted-vector readback;
- `Remove from chat` for the active context;
- a visible context chip in the assistant composer;
- context clearing when a new file selection replaces the source.

The existing `vector_payload_auto_attached_to_prompt = false` invariant remains true because attachment is explicit, not automatic.

## Validation

Dependency-scoped tests SHALL prove explicit opt-in, bounded context, no raw-context echo in governed turn evidence, actual provider prompt injection as evidence context, UI attach/remove controls, and no automatic attachment.
