# Pass 220 I007 preimplementation checkpoint — assistant settings, clipboard UX, conversational egress

Status: **RESTARTABLE PREIMPLEMENTATION CHECKPOINT**

## Lineage

- branch: `pass220-lo-shu-normalization-checkpoint-1`
- predecessor head: `47f7cf9c8b9f0ee067ab12e96498f18e57c7396e`
- merge target: `main`
- PR: #491
- predecessor I006 workflows were queued at checkpoint time

## Authorized product result

The production mobile assistant SHALL behave like a normal consumer LLM application:

1. Settings exposes a user-editable system-instructions field.
2. The user instruction is applied to generation as an additive user-configured system instruction while inherited HHS authority constraints remain enforced.
3. System instructions persist locally in the browser and may be changed between turns.
4. Mobile-friendly Copy controls are available on conversational messages.
5. A Paste control reads from the browser clipboard into the composer when permission is available.
6. Assistant responses are conversational natural language by default.
7. Tool/runtime evidence is summarized for the user; raw JSON is not shown in the primary UI unless the user explicitly opens an Inspect control.
8. Vector ingress remains user-controlled and does not auto-attach uploaded payloads to prompts.

## Backend changes required

- Add bounded `custom_system_instruction` support to assistant API requests.
- Propagate it through production primary/fallback providers.
- Compose it with, never replace, the inherited provider system instruction.
- Record only the fact/hash of the customization in governed turn evidence where appropriate.
- Preserve no-direct-mutation authority.

## Frontend changes required

- Add Settings toggle + system instruction textarea.
- Persist setting under a namespaced localStorage key.
- Send `custom_system_instruction` on every assistant turn.
- Add Copy buttons to messages.
- Add Paste button to the composer.
- Convert persisted-vector raw JSON from default-visible output into a natural-language summary with closed `Inspect technical JSON` details.

## Validation

- backend unit tests for custom instruction composition and fallback propagation;
- route request-shape test;
- I007 source/UI regression tests;
- Runtime OS typecheck/source verification/build;
- cumulative Pass 220 workflow.

## Deployment boundary

No feature-branch production promotion. DigitalOcean remains exact-main after validation and merge.
