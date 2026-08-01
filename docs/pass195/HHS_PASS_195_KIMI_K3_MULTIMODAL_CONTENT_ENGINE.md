# HHS PASS 195 — KIMI K3 MULTIMODAL CONTENT ENGINE

## Governed storyboard, sprite-map, shader-plan, and native MP4 training-manifest generation for the HARMONICODE graphics and game engine

## 1. Normative metadata

| Field | Value |
|---|---|
| Contract | `HHS-P195-KIMI-K3-MCE-SPR-SHD-SB-MP4-H72-H216` |
| Pass | 195 additive implementation |
| Provider | Moonshot AI Kimi K3 through its OpenAI-compatible API |
| Provider ID | `provider:hhs.moonshot.kimi_k3` |
| Default model | `kimi-k3` |
| Production host | Existing DigitalOcean Ubuntu deployment |
| Canonical execution authority | HHS VM81, native sprite/shader/game/storybook runtimes, Hash72/Hash216 admission |
| Provider authority | Non-mutating proposal and visual-analysis capability only |
| Vercel | Excluded from implementation and acceptance |

## 2. Purpose

Pass 195 installs Kimi K3 as the external content-planning engine used to develop:

- scene-by-scene storyboards;
- sprite-atlas layouts and animation ranges;
- shader channels, uniforms, passes, and phase rules;
- x/y/z/w reciprocal palette and phase-plane assignments;
- native HHS MP4 render plans;
- reproducible animation training examples and acceptance tests;
- native Storybook Reel Studio handoffs.

Kimi K3 does not become a second renderer, game engine, state authority, or MP4 pipeline. It returns a structured proposal. The existing HHS native surfaces rasterize sprite maps, execute shader logic, advance game state, render ordered frames, encode H.264/AAC transport, and issue the authoritative receipts.

## 3. Deployment architecture

The DigitalOcean host is intentionally an API client. It does not attempt to load the complete Kimi K3 weights into the 4 GB application droplet.

```text
Storybook Studio / HHS IDE
        ↓
/api/runtime/content-engine/kimi-k3/plan
        ↓
HHS provider execution proposal
        ↓
Capability policy gate
        ↓
Moonshot OpenAI-compatible /v1/chat/completions
        ↓
Strict JSON content plan
        ↓
Provider invocation receipt
        ↓
Universal result ingress + Hash72 witness
        ↓
HHS native handoff
        ↓
Sprite/shader/game/storybook execution
        ↓
Native ordered frames + FFmpeg codec transport
        ↓
MP4 + source package + receipts
```

## 4. Provider configuration

The runtime reads:

| Variable | Default | Meaning |
|---|---|---|
| `HHS_KIMI_K3_ENABLED` | `1` | Enables the provider adapter |
| `HHS_KIMI_K3_BASE_URL` | `https://api.moonshot.ai/v1` | Moonshot OpenAI-compatible endpoint |
| `HHS_KIMI_K3_MODEL` | `kimi-k3` | Model registry ID |
| `HHS_KIMI_K3_API_KEY` | unset | Preferred protected API key |
| `MOONSHOT_API_KEY` | unset | Compatible fallback key |
| `HHS_KIMI_K3_REASONING_EFFORT` | `max` | `low`, `high`, or `max` |
| `HHS_KIMI_K3_MAX_COMPLETION_TOKENS` | `8192` | Bounded plan output budget |
| `HHS_KIMI_K3_TIMEOUT_SECONDS` | `300` | Provider timeout |
| `HHS_KIMI_K3_MAX_REFERENCE_IMAGES` | `4` | Maximum images per plan request |
| `HHS_KIMI_K3_MAX_REFERENCE_IMAGE_BYTES` | `8388608` | Maximum decoded bytes per reference image |

A template is committed at:

```text
deploy/digitalocean/hhs-kimi-k3.env.example
```

The real key must be supplied through the protected systemd environment file or deployment secret manager. It must not be committed to Git.

## 5. API

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/api/runtime/content-engine/kimi-k3/status` | Local configuration and authority status without a network request |
| `GET` | `/api/runtime/content-engine/kimi-k3/health` | Authenticated provider/model probe |
| `POST` | `/api/runtime/content-engine/kimi-k3/plan` | Generate and admit a governed multimodal content plan |

Supported operations:

```text
sprite_map
storyboard
native_mp4_training
complete_pipeline
```

The request supports story or design text, art direction, exact duration/fps/dimensions, constraints, and up to four base64 image references. Public image URLs are rejected so the adapter follows Kimi K3's supported inline visual-input boundary and avoids remote URL ambiguity.

## 6. Strict plan schema

The provider must return a strict JSON object containing:

1. project intent and art direction;
2. integer-frame storyboard scenes;
3. sprite-atlas geometry, anchors, animation ranges, collision notes, and shader channels;
4. shader language, uniforms, ordered passes, phase rules, and invariants;
5. native MP4 duration, rate, geometry, frame count, codec, pixel format, audio strategy, and render steps;
6. training objective, examples, validations, and acceptance tests;
7. a Storybook Studio native handoff with title, story text, template, and bounded style controls.

After provider return, HHS overwrites the transport-critical fields with the authorized request values:

```text
frame_count = duration_seconds × fps
codec = h264
pixel_format = yuv420p
external_model_is_proposal = true
hhs_native_renderer_is_authority = true
direct_vm81_mutation_allowed = false
```

The normalized plan receives a Hash72 identity before it is exposed to the native handoff surface.

## 7. Visual interface

The Storybook Reel Studio receives an additive Kimi K3 panel. It provides:

- generation-scope selection;
- target geometry selection;
- art-direction editing;
- provider configuration status;
- governed plan generation;
- plan summary and Hash72 display;
- JSON plan download;
- one-click application of the native Storybook handoff.

Applying a handoff updates only editable Storybook Studio fields. It does not silently start native generation, upload narration, mutate VM81, or claim that an MP4 exists.

## 8. Image and video boundary

Kimi K3 is used for visual understanding and structured planning. Pass 195 supports inline base64 reference images. The first implementation does not create a hidden duplicate pixel-generation path and does not upload arbitrary user videos to a third party automatically.

Native MP4 training manifests describe how HHS should build and validate examples. Existing HHS ingestion, frame rendering, Hash72/Hash216 receipt chains, and MP4 inspection remain the authoritative training-data pipeline.

A later additive pass may introduce explicit user-authorized Kimi file uploads for reference-video analysis. Such a pass must include lifecycle deletion, size limits, privacy disclosure, and receipt evidence.

## 9. Security and cost controls

- API keys are never returned by status or health routes.
- The key is sent only in the Authorization header to the configured Moonshot base URL.
- Output is bounded by `HHS_KIMI_K3_MAX_COMPLETION_TOKENS`.
- Reference image count and decoded size are bounded.
- Provider reasoning content is not treated as the content plan.
- Provider output cannot directly mutate VM81 or repository state.
- Native rendering does not begin automatically after plan generation.
- The integration fails closed when the key, provider, model, strict JSON, receipt, or ingress evidence is unavailable.

## 10. DigitalOcean activation

After deployment of the merged repository version:

```bash
sudo install -d -m 0750 /etc/hhs
sudoedit /etc/hhs/hhs.env
```

Add the protected values shown in `deploy/digitalocean/hhs-kimi-k3.env.example`, including a real key:

```text
HHS_KIMI_K3_ENABLED=1
HHS_KIMI_K3_API_KEY=<secret>
HHS_KIMI_K3_MODEL=kimi-k3
```

Ensure the existing HHS systemd service reads `/etc/hhs/hhs.env`, then restart and verify:

```bash
sudo systemctl daemon-reload
sudo systemctl restart hhs
curl -fsS http://127.0.0.1:8080/api/runtime/content-engine/kimi-k3/status
curl -fsS http://127.0.0.1:8080/api/runtime/content-engine/kimi-k3/health
```

The status route is expected to remain available without a provider call. The health route becomes ready only after a valid Moonshot account, key, and model access are present.

## 11. Validation

The Pass 195 workflow validates:

- Python bytecode compilation;
- provider secret non-disclosure;
- dedicated and fallback environment-key resolution;
- Kimi K3 completion controls without unsupported sampling overrides;
- base64-only image-reference enforcement;
- strict JSON schema request construction;
- provider proposal, policy, receipt, and ingress path;
- forced HHS native authority flags;
- exact `duration × fps` frame count;
- H.264/yuv420p native handoff;
- Storybook Studio JavaScript syntax.

No live provider call is required in public CI. Live acceptance requires the protected production key and is recorded separately from repository conformance.

## 12. Acceptance classification

The repository implementation is accepted when:

```text
HHS_PASS_195_KIMI_K3_CONTENT_ENGINE_IMPLEMENTED
```

Live production classification requires successful authenticated `/health` and one admitted `/plan` response:

```text
HHS_PASS_195_KIMI_K3_CONTENT_ENGINE_LIVE_VERIFIED
```

The second classification must not be claimed until a real provider response has passed HHS receipt and ingress admission on the DigitalOcean host.
