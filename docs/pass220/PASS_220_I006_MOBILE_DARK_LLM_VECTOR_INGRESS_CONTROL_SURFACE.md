# Pass 220 I006 — Mobile Dark LLM Control Surface + User-Controlled Multimodal Vector Ingress

Status: IMPLEMENTED CHECKPOINT / DEPENDENCY-SCOPED CI PENDING / DIGITALOCEAN DEPLOYMENT AFTER EXACT-MAIN MERGE

## 1. Product boundary

The canonical Runtime OS production control surface now presents the HHS application server like a normal modern LLM application while retaining the existing click-through Runtime OS controls.

The default production surface is:

```text
mobile/desktop browser
→ HHS Assistant conversation
→ user-controlled Files action
→ local preview
→ governed multimodal ingress
→ persistent Hash216 vector hydration/readback
→ Visual Program / Workspace / Authority controls
```

The assistant is the primary interaction surface.  Runtime internals and authority controls remain accessible but are not forced into the user’s main conversation view.

## 2. Mobile dark-theme assistant

`hhs_gui/runtime_os/workspace/ProductionAssistantChat.tsx` implements an ordinary LLM-style conversation UI:

- dark neutral/cyan production theme;
- responsive phone/desktop layout;
- bounded scrollable message history;
- distinct user and assistant message bubbles;
- large natural-language composer;
- Enter to send;
- Shift+Enter for a newline;
- visible assistant/model readiness;
- one-tap `New chat`;
- quick natural-language prompts;
- progress state while a response is being generated;
- receipt/mode/tool metadata below assistant turns;
- direct `Files` shortcut into the user-controlled ingress surface.

Production chat uses the inherited endpoints:

```text
GET  /api/assistant/health
POST /api/assistant/chat
```

No fake assistant answer is generated in the browser.

## 3. User-controlled multimodal vector ingress

The existing `ProductionMobileControlCenter` remains the ingress authority surface and continues to provide:

- multiple file selection;
- local text/source/JSON/YAML/CSV reader;
- PDF preview;
- image preview;
- audio playback;
- video playback;
- exact binary ingress even when no browser preview is available;
- Pass 174 governed SDLC/hydration;
- persistent Hash216 vector-store continuation;
- explicit persisted-vector readback.

Ingress routes remain:

```text
POST /api/v1/pass174/sdlc/run
POST /api/v1/pass174/hash216/query
```

The browser does not become canonical VM81, Hash72, or Hash216 authority.

## 4. No automatic file-to-model disclosure

Chat and file/vector ingestion are intentionally separate user actions.

The assistant surface explicitly states:

```text
File/vector ingress is user-controlled;
uploaded payloads are not automatically attached to assistant prompts.
```

A hydrated vector identity may be visible as current workspace/thread metadata, but I006 does not claim that the assistant has retrieved or consumed that payload merely because the file exists in the vector store.

This preserves the boundary required for the later explicit RAG retrieval integration.

## 5. Thread behavior

The mobile assistant submits ordinary production chat turns:

```text
thread_id
project_id
title
metadata
content
```

A returned thread ID is retained for later turns.

`New chat` clears the local thread ID and visible conversation without fabricating backend deletion or changing canonical runtime state.

Thread metadata records:

```text
workspace_surface = production_mobile_control
vector_identity_visible_to_user = <identity or null>
vector_payload_auto_attached_to_prompt = false
```

This metadata is descriptive; it is not a claim of RAG retrieval.

## 6. Application-server composition

`HHSProductWorkspace` already defaults to:

```text
surface = control
```

and mounts `ProductionMobileControlCenter`.

I006 makes that control center assistant-first by mounting `ProductionAssistantChat` immediately below production health, ahead of advanced application launch cards and vector-store controls.

The existing secondary surfaces remain:

- Visual Program;
- Workspace;
- Authority;
- open-source acquisition/replay;
- multimodal ingress/vector store.

## 7. DigitalOcean production path

I006 modifies the canonical `hhs_gui` Runtime OS source consumed by the production-root build.

The repository’s DigitalOcean deployment boundary remains exact-main:

```text
feature branch / PR
→ validation
→ merge to main
→ Runtime OS build
→ digitalocean-production-main.yml
→ governed production host
```

The feature branch is not directly promoted to the production droplet.

## 8. Validation

I006 adds:

`tests/pass220/test_hhs_pass220_i006_mobile_llm_control_surface.py`

which verifies:

1. the mobile control mounts the assistant;
2. normal assistant health/chat endpoints are used;
3. the user controls file selection and hydration;
4. Pass 174 vector ingress/readback remains present;
5. chat code does not directly upload file bytes;
6. the mobile assistant reserves a usable touch viewport;
7. dark-theme surface classes are present;
8. the canonical product still defaults to the mobile control surface;
9. workspace source verification enforces the new UI;
10. DigitalOcean exact-main deployment remains the governed deployment boundary.

The existing `hhs_gui/scripts/workspace-source-verify.mjs` is also extended so the normal Runtime OS production build fails if the assistant or vector-ingress controls disappear.

## 9. Authority

I006 is a user-interface/application composition pass.

It does not add:

```text
VM81 mutation authority
Hash72 mint/commit authority
Hash216 mutation authority
automatic model access to uploaded file payloads
browser-local runtime truth
```

It connects implemented production services into the user-facing control surface without weakening their inherited boundaries.
