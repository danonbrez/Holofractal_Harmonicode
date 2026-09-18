# Pass 220 I006 preimplementation checkpoint — mobile dark LLM control surface + multimodal ingress

Status: **RESTARTABLE PREIMPLEMENTATION CHECKPOINT**

## Lineage

- branch: `pass220-lo-shu-normalization-checkpoint-1`
- predecessor head: `8709728d441edfb8f35e1f0ac6236ca435f26503`
- merge target: `main`
- PR: #491
- production deployment authority: `.github/workflows/digitalocean-production-main.yml` after exact-main merge

## Authorized product result

The DigitalOcean production Runtime OS control surface SHALL look and behave like a normal modern LLM application on phone and desktop while keeping HHS authority separation intact.

The default mobile control page shall combine:

1. a dark-theme natural-language assistant conversation surface;
2. normal multi-turn `/api/assistant/chat` interaction;
3. assistant health/readiness;
4. one-tap new conversation;
5. mobile composer and file-ingress shortcut;
6. the existing user-controlled multimodal file reader/preview;
7. governed Pass 174 multimodal ingress;
8. persistent Hash216 vector-store hydration/readback;
9. application/workspace/authority navigation.

## Authority and privacy constraints

- Uploading a file does **not** automatically attach its contents to a model prompt.
- Assistant chat and vector ingress remain separately user-triggered surfaces.
- A hydrated vector identity may be displayed as current workspace/thread metadata, but shall not be represented as model context unless an explicit retrieval path actually supplies it.
- Browser UI has no VM81/Hash72/Hash216 mutation authority.
- Existing Pass 174 ingress remains the persistent vector-store authority.
- Existing `/api/assistant/chat` remains the production assistant route.
- No mock chat responses, raw JSON-first UX, or static placeholder controls qualify.

## Planned files

- new `hhs_gui/runtime_os/workspace/ProductionAssistantChat.tsx`
- integrate it into `ProductionMobileControlCenter.tsx`
- extend `hhs_gui/scripts/workspace-source-verify.mjs`
- add Pass 220 I006 dependency-scoped source tests
- formal I006 product/UI document
- cumulative I003-I006 workflow wiring
- restart checkpoint

## Deployment boundary

This cycle changes the canonical `hhs_gui` Runtime OS source that the DigitalOcean production-root workflow builds.  The branch itself will not be deployed as production; exact-main deployment remains the governed next boundary after merge and validation.
