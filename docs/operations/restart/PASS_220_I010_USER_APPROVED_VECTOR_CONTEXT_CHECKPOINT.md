# Pass 220 I010 restart checkpoint — explicit user-approved vector context RAG

Status: **RESTARTABLE IMPLEMENTATION CHECKPOINT — CI PENDING**

## Lineage

- branch: `pass220-lo-shu-normalization-checkpoint-1`
- predecessor I009 checkpoint: `39ae1222becadcf935553df7163e73d3d829a2c4`
- I009 repair-forward checkpoint: `d61007b1b2545a2975c9778fea8cbe7c888ab3c1`
- I010 preimplementation checkpoint: `7354cd23db236d46f1beed26d4b706d3d9f0c590`
- merge target: `main`
- PR: #491

## I009 repair-forward completed before I010

Observed CI defects were repaired rather than ignored:

- Pass 220 pytest collection now installs FastAPI/TestClient dependencies after the untouched cold raw calibration;
- the cold calibration Markdown report no longer executes backtick text as shell command substitution;
- the legacy LiteRT mobile console pins React 19.2.0 with react-three/fiber 9.7.0 to close the React 19.3 peer conflict;
- Full Application IDE browser acceptance now navigates from the intentional Mobile Control default to Visual Program before checking the lazily mounted registry programmer;
- main's verified Lane 5 self-enforcement proof regression/checkpoint have been incorporated into the branch content.

## I010 implemented result

The production assistant now has an explicit user-controlled vector-to-chat context boundary:

```text
Choose file
→ Hydrate vector store
→ Read persisted vector
→ Use in chat
→ bounded user-approved context
→ assistant turn
```

No file/vector payload is automatically attached.

### Backend

`HHSAssistantService` now accepts optional `user_context` with:

- `explicit_user_attachment=true` required;
- 32,768-character text bound;
- optional source SHA-256, operation key, lifecycle Hash216 identity validation;
- Hash72 context root binding;
- context projected below inherited authority/mode/custom instructions;
- explicit evidence/data semantics rather than instruction authority;
- raw context omitted from returned governed turn evidence.

Propagation spans:

```text
REST / thread-message / WebSocket
→ ProductionAssistantService
→ preferred Gemma/LiteRT provider
→ native HHS fallback
→ provider prompt
```

### Mobile Runtime OS

The file/vector surface now adds:

- `Use in chat` only after persisted vector readback;
- `Remove from chat`;
- composer-visible `Context attached by you` chip;
- automatic context clearing when the selected source changes or is rehydrated;
- text/source context bounded to 32,768 characters;
- metadata-only attachment for non-text modalities without an authorized decoder.

The request preserves:

```text
vector_payload_auto_attached_to_prompt = false
user_approved_context_attached = true|false
```

## Files added

- `tests/pass220/test_hhs_pass220_i010_user_approved_context.py`
- `tests/pass220/test_hhs_pass220_i010_user_approved_context_ui.py`
- `docs/pass220/PASS_220_I010_USER_APPROVED_VECTOR_CONTEXT_RAG.md`

## Major files modified

- `hhs_backend/runtime/hhs_litert_lm_assistant_v1.py`
- `hhs_backend/runtime/hhs_litert_lm_hhs_api_assistant_v1.py`
- `hhs_backend/runtime/hhs_production_assistant_v1.py`
- `hhs_backend/api/litert_lm_assistant_routes.py`
- `hhs_gui/runtime_os/workspace/ProductionAssistantChat.tsx`
- `hhs_gui/runtime_os/workspace/ProductionMobileControlCenter.tsx`
- `hhs_gui/scripts/workspace-source-verify.mjs`
- `.github/workflows/pass220-i003-four-phase-abc-max-hardware.yml`
- `.github/workflows/litert-lm-assistant.yml`
- `.github/workflows/digitalocean-mobile-control-ingress.yml`

## Implementation commits

I009 repair-forward:
- `006a852ca6f4caacaa21fd27330c059defb4004d` cold report shell-literal repair
- `6d93b8829af43439f62250055a40e1c69974238a` post-calibration assistant-test dependencies
- `8c7445a411f1feebdd6a669f0c4663e88aebf504` compatible legacy mobile React pins
- `bc18cc1aa7c2b1abf0ff7a81389d44741f62687e` Full IDE Visual Program navigation repair
- `c827fe0ea6d80dc9b65a35d5eb1803b07005557c` main Lane 5 proof regression sync
- `7c8169ab1b4a3371c7e9ceff903142a332923041` main Lane 5 proof checkpoint sync
- `d61007b1b2545a2975c9778fea8cbe7c888ab3c1` repair checkpoint

I010:
- `7354cd23db236d46f1beed26d4b706d3d9f0c590` preimplementation checkpoint
- `bcc54a45ba986b124c75bf9d0b0ff4f388bc4399` assistant-core context contract
- `9dae754e5a6acd23c0cfb26e89fa83489009fc37` governed assistant propagation
- `d277183787a1e8c0d1130664005e3c337c33e385` production provider hierarchy propagation
- `9e5d1ad46fe8d48f2192749eecf24fc18460ff17` REST/WebSocket request field
- `e3150424a0f4d225b9c16bc569a80471e3a20b08` assistant attached-context UI
- `f7e9491b6933964b64f6b8e75eac768f0088b0ac` persisted-vector Use in chat control
- `496f6e2e69fcea8fe9354dd31f202533be3a4915` Runtime OS source verifier
- `c0bef4035c551ab0fbfbebf69fd5789dd2756333` backend context tests
- `5aaad08f381bcd739b660cca29b0f89c7a166c12` UI/source tests
- `2993077116d60993765eca8c595bf2da850885a8` Pass 220 I003-I010 workflow
- `eb556030bb213cd0fc4207e4ce2ae3d449c63866` LiteRT assistant validation
- `a38444b89339c97c590865ad3c94858aad044991` DigitalOcean mobile bundle gate
- `91597029a86b8f43849c6089faec128209c1da1d` formal I010 contract

## Validation pending

Impacted validation includes:

1. Pass 220 I003-I010 cumulative cold-calibration/integration workflow;
2. LiteRT-LM assistant backend/interface workflow;
3. Runtime OS production-root/full application IDE validation;
4. DigitalOcean mobile control/vector ingress bundle validation.

Per the forward-progress policy, this repository-visible checkpoint is sealed without waiting for queued external CI.

## Next action

Inspect only the new impacted runs. Repair forward any dependency-scoped failure. After green validation, the next production closure is to make PR #491 merge-ready, merge against current main, verify main, and then exercise the exact-main DigitalOcean interface with:

1. one text file hydration/readback;
2. explicit `Use in chat`;
3. one General Chat response grounded in that context;
4. explicit `Remove`;
5. a second turn proving the removed context is no longer supplied;
6. one non-text file proving metadata-only attachment rather than fabricated multimodal decoding.
