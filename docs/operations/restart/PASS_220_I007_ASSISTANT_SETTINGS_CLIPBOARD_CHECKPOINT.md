# Pass 220 I007 restart checkpoint — assistant settings, clipboard UX, conversational egress

Status: **RESTARTABLE IMPLEMENTATION CHECKPOINT — CI PENDING**

## Lineage

- branch: `pass220-lo-shu-normalization-checkpoint-1`
- predecessor I006 head: `47f7cf9c8b9f0ee067ab12e96498f18e57c7396e`
- I007 preimplementation checkpoint: `88f49027852b47ba12c7c4df07bb3defc9c9c6c8`
- merge target: `main`
- PR: #491

## Implemented user-facing result

The production mobile assistant now provides:

- a `Settings` panel;
- a persistent browser-local `System instructions` textarea;
- bounded 8192-character custom instructions sent on every assistant turn;
- touch-friendly Copy controls on messages;
- touch-friendly Paste control in the composer;
- clear conversational natural-language provider defaults;
- assistant responses rendered as prose instead of raw turn JSON;
- vector readback summarized first with `Inspect technical JSON` disclosure;
- acquisition/replay results summarized first with `Inspect technical JSON` disclosure.

## System-instruction authority

User custom instructions are additive to the inherited governed HHS system instruction. They never replace HHS runtime authority constraints.

Backend propagation:

```text
REST/WebSocket assistant request
→ ProductionAssistantService
→ Gemma/LiteRT-LM primary or native HHS fallback
→ HHSAssistantService model-message composition
```

The raw custom instruction is not echoed in returned governed turn evidence. Instead the turn records:

```text
custom_system_instruction_applied
custom_system_instruction_root_hash72
```

## Data boundary retained

File/vector ingress remains user-triggered and separate from assistant prompt attachment.

```text
vector_payload_auto_attached_to_prompt = false
```

continues to be sent by the mobile assistant.

## Added files

- `tests/pass220/test_hhs_pass220_i007_custom_system_instruction.py`
- `tests/pass220/test_hhs_pass220_i007_assistant_settings_clipboard_ui.py`
- `docs/pass220/PASS_220_I007_ASSISTANT_SETTINGS_CLIPBOARD_CONVERSATIONAL_EGRESS.md`

## Modified files

- `hhs_backend/runtime/hhs_litert_lm_assistant_v1.py`
- `hhs_backend/runtime/hhs_litert_lm_hhs_api_assistant_v1.py`
- `hhs_backend/runtime/hhs_production_assistant_v1.py`
- `hhs_backend/api/litert_lm_assistant_routes.py`
- `hhs_gui/runtime_os/workspace/ProductionAssistantChat.tsx`
- `hhs_gui/runtime_os/workspace/ProductionMobileControlCenter.tsx`
- `hhs_gui/runtime_os/workspace/OpenSourceAcquisitionPanel.tsx`
- `hhs_gui/scripts/workspace-source-verify.mjs`
- `.github/workflows/pass220-i003-four-phase-abc-max-hardware.yml`
- `.github/workflows/digitalocean-mobile-control-ingress.yml`

## Implementation commits

- preimplementation checkpoint: `88f49027852b47ba12c7c4df07bb3defc9c9c6c8`
- assistant-core custom instruction composition: `a3d2a92d9136ac943879607801c1fd0791c5e58e`
- governed tool assistant propagation: `ab9d886a33a9acfca229162e4e050f40e7df647a`
- production provider propagation: `8b833ccd1e1965bcd16637a78380d17de8bd8b91`
- native-fallback propagation repair: `e711eec90f9de7e5db4859d8a015988c249619ae`
- assistant API field: `c62a04904da44c339add0732531a45de4a2fcfe8`
- Settings/Copy/Paste frontend: `c2fd27d3d6f7580be7b96b190898874dbcdd5455`
- vector JSON progressive disclosure: `83ccad08251c099140aa4d75d4b4e017432b03fe`
- backend I007 tests: `35f30cfcb41720248f48fc286f09818e19de0703`
- registered-provider test repair: `c8613d8f1d87c6e3900a40da1d7577b1696b46a0`
- workspace verifier: `f989b706338f3c1ce7d9584294cc84eaba9fa50c`
- UI/source tests: `be60d3ca89d7e2f6cfd7c21950eee33593432433`
- Copy-label test repair: `ab5c69671e75f04e873890aa6c60e272ce558fef`
- cumulative I003-I007 workflow: `b53f79a17747de6b803282c2030988c81ee63adf`
- assistant capability/status advertisement: `60df991b21f52170732009eee832a417db693f05`
- formal I007 document: `d9ac9498926c69a1eb5f38c4a12bcfd9d3869287`
- DigitalOcean mobile gate extension: `8d8722439acaf041f38b9a42a8f8c7588d731cb5`
- acquisition summary-first UI: `cc77524ec8f4fbdbaa8a7d59dde9b3f04898d066`
- acquisition source-verifier enforcement: `bd24de92e79ff9dcf3fb7e4c2a44575d0bd9bdb6`
- acquisition UI regression test: `5e1f19cd8f9830644f283e06f6712fbc027e6a65`
- cumulative trigger completion: `fda95b14983db29592481999664f52ba2253d4bd`

## Validation surfaces

The impacted validation set is now:

1. Pass 220 cumulative I003-I007 workflow;
2. Runtime OS production-root typecheck/source-verifier/build workflow;
3. DigitalOcean Mobile Control and Vector Ingress workflow;
4. exact-main DigitalOcean production workflow only after merge.

No queued external CI is required before preserving this restartable checkpoint.

## Next action

Inspect only the impacted workflows on the checkpoint head. Repair forward any I007-specific TypeScript, route, custom-instruction, source-verifier, or bundle-contract failure. If green, close PR #491 for merge readiness; after exact-main merge, verify the deployed mobile assistant in the public DigitalOcean Runtime OS with:

- Settings persistence;
- one custom-instruction turn;
- Copy/Paste interaction;
- one normal conversational answer;
- one file/vector ingress;
- technical JSON hidden until Inspect is opened.
