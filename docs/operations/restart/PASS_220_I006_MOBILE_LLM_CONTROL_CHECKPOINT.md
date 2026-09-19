# Pass 220 I006 restart checkpoint — mobile dark LLM control + multimodal vector ingress

Status: **RESTARTABLE IMPLEMENTATION CHECKPOINT — CI PENDING**

## Lineage

- branch: `pass220-lo-shu-normalization-checkpoint-1`
- predecessor I005 head: `8709728d441edfb8f35e1f0ac6236ca435f26503`
- I006 preimplementation checkpoint: `f27f1b288299a14e72ad697d3d25a13b20e31c27`
- merge target: `main`
- PR: #491

## Implemented product result

The canonical Runtime OS default production control surface is now assistant-first.

The page combines:

- mobile/desktop dark-theme HHS Assistant chat;
- multi-turn `/api/assistant/chat`;
- assistant health;
- one-tap new chat;
- Enter-send / Shift+Enter newline behavior;
- mobile file shortcut;
- existing local multimodal file reader/preview;
- Pass 174 governed ingress;
- persistent Hash216 vector hydration/readback;
- Visual Program / Workspace / Authority navigation.

## User-controlled data boundary

Uploaded file/vector payloads are **not** automatically attached to assistant prompts.

The chat and ingress paths remain separate user actions.  The UI may display a hydrated vector identity as workspace/thread metadata, but I006 does not claim that the model retrieved or consumed that vector payload.

## Files

Added:
- `hhs_gui/runtime_os/workspace/ProductionAssistantChat.tsx`
- `tests/pass220/test_hhs_pass220_i006_mobile_llm_control_surface.py`
- `docs/pass220/PASS_220_I006_MOBILE_DARK_LLM_VECTOR_INGRESS_CONTROL_SURFACE.md`

Modified:
- `hhs_gui/runtime_os/workspace/ProductionMobileControlCenter.tsx`
- `hhs_gui/scripts/workspace-source-verify.mjs`
- `.github/workflows/pass220-i003-four-phase-abc-max-hardware.yml`

## Commit sequence

- preimplementation checkpoint: `f27f1b288299a14e72ad697d3d25a13b20e31c27`
- mobile assistant component: `5310bb144d50ff742ee2aced28c3bc9a6cc455b7`
- control-center integration: `2ff7ca6005e274e1e2da05745f2565cd8fee97ae`
- TypeScript expression repair: `a24a3c16f833a98294f0840f02f5e774b38af2a6`
- workspace source verifier: `ad2b562904fb684581676a47d53c446a335ce1a7`
- I006 dependency-scoped source tests: `f635f7f9a20a3a647e9f98c89a78ad158d8fa5af`
- formal I006 document: `76b6e79caab28c0336bde57463d1b7b1497ac751`
- cumulative I003-I006 workflow: `de29b5a84497d2ad2433bb17a2d4f43e573b89e8`

## Validation plan

Two CI paths should now cover this change:

1. Pass 220 cumulative I003-I006 workflow:
   - cold raw x86_64 calibration first;
   - dependency-scoped I001-I006 tests under pipefail.

2. Runtime OS production-root workflow:
   - TypeScript typecheck;
   - workspace source verifier;
   - Runtime OS build;
   - production-root route/mount validation.

Per repository responsiveness policy, this checkpoint is committed without waiting on queued external CI.

## DigitalOcean deployment boundary

The feature branch is not deployed directly.

After validation and exact-main merge, the governed DigitalOcean production workflow remains the promotion boundary.  The deployed interface will therefore be built from exact `main`, not from this draft branch.

## Next action

Inspect only the new/impacted CI runs. Repair forward any I006-specific TypeScript/source-verifier/test failure. Once green, merge-ready closure can proceed and DigitalOcean exact-main deployment/browser verification becomes the next production task.
