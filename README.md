# Holofractal Harmonicode (HHS)

Deterministic VM81 execution, HARMONICODE source semantics, Hash72 receipt authority, Hash216 historical identity, governed multimodal tooling, a repository-native LiteRT-LM natural-language development interface, and VM81-governed creative-artifact generation.

## Current main interface

The default page at `/` is the **HHS LiteRT-LM Visual Development Assistant** implemented through the Pass 161 Holofractal Harmonizer.

It provides:

- bounded conversation threads backed by the repository-native LiteRT-LM provider;
- the `gemma4-12b` model as the default registered inference model;
- governed read-only HHS API tools for runtime, service, invariant, conformance, and closure inspection;
- registered-object navigation, nested inspectors, object-workspace cards, spatial projection, and API-controller views;
- provider health, tool-count, thread, model, backend, receipt, and authority diagnostics;
- degraded-mode startup when the model provider is unavailable, unless strict startup is enabled.

The former JSON root response is preserved at `/api/system/status`.

### Pass 162 creative-writing runtime

`main` also contains the additive Pass 162 VM81 creative-novel runtime.

Its sole external generation surface is:

```text
POST /api/runtime/creative/novel
```

The runtime accepts a bounded novel contract, authorizes the operation through VM81, invokes the configured language-model provider through the HHS proposal/policy/receipt/ingress path, assembles Hash72-rooted chapters, and persists admitted Markdown artifacts beneath `creative_writing/novels/` through the HHS persistence guard.

External callers must not call LiteRT-LM `/v1/chat/completions` directly for this workflow and cannot choose an arbitrary output directory.

The current repository exposes the visual assistant and creative-writing API through separate server compositions:

- `bash start.sh` launches `hhs_backend.visual_server:app`, the default visual development environment;
- `python -m uvicorn hhs_backend.pass162_server:app ...` launches the specialized Pass 162 creative runtime surface.

The committed reference manuscript `creative_writing/novels/THE_NINTH_ARCHIVE.md` is explicitly classified as a seed artifact with `runtime_execution_receipt: null`. Live Pass 162 execution verification requires a reachable provider and an admitted VM81 response; no receipt is fabricated when that evidence is unavailable.

## Authority model

The language model is a capability provider and projection layer. It does not own canonical HHS state.

```text
Human request
    ↓
Pass 161 visual assistant
    ↓
/api/assistant
    ↓
Provider execution proposal
    ↓
Capability policy gate
    ↓
LiteRT-LM / Gemma 4 completion
    ↓
Provider invocation receipt
    ↓
HHS provider-result ingress
    ↓
Bounded assistant-thread projection
```

The following rules remain binding:

- VM81 and the HHS runtime remain the execution authority.
- Model output is not canonical merely because inference completed.
- Model-generated mutations are proposals only.
- No assistant route permits direct VM81 mutation.
- Read-only assistant tools return governed HHS evidence.
- State transitions require admission, audit, and receipt closure.
- Hash72, Hash216, ordered products, exact rational authority, and inherited pass invariants may not be silently replaced by alternate truth paths.

See [`AGENTS.md`](AGENTS.md) for the repository navigation and invariant contract.

## Architecture

```text
Browser
└── applications/holofractal_harmonizer/
    ├── Default LiteRT-LM assistant
    ├── Registered-object workspace
    ├── Nested object inspector
    ├── Spatial object projection
    └── Governed API controller
            ↓
hhs_backend/visual_server.py
├── mounts the Pass 161 application at /
├── composes /api/assistant
└── preserves canonical API-route precedence
            ↓
hhs_backend/server.py
├── FastAPI lifecycle
├── VM81/runtime initialization
├── graph and replay services
├── WebSocket orchestration
└── runtime/workspace/capability/document routes
            ↓
hhs_backend/runtime/hhs_litert_lm_hhs_api_assistant_v1.py
├── bounded thread store
├── per-thread request serialization
├── allowlisted read-only HHS tool loop
├── provider proposal and policy gate
├── invocation receipt
└── provider-result ingress
            ↓
LiteRT-LM service on port 9379
└── registered model: gemma4-12b
            ↓
VM81 + HARMONICODE + Hash72 + Hash216 + persistence/replay

Optional Pass 162 composition
hhs_backend/pass162_server.py
└── /api/runtime/creative/novel
    ├── VM81 authorized tick
    ├── bounded creative provider transport
    ├── Hash72 outline/chapter/manuscript roots
    └── guarded creative_writing/novels persistence
```

## Quick start

### Prerequisites

| Requirement | Purpose |
|---|---|
| Python 3.11 or newer | HHS backend, tests, and bootstrap tooling |
| GCC or Clang | Native runtime and VM81 build |
| GNU Make | Canonical C build and verification targets |
| Node.js 22 or newer | Pass 161 tests, browser audit, finalization, and packaging |
| GPU driver and accelerator access | Required for the default production `gpu` inference profile |
| Vulkan loader/device access on Linux or Windows | Required by the default local GPU profile |
| Metal-capable host on macOS | Native macOS GPU execution path |

### Start the integrated environment

```bash
git clone https://github.com/danonbrez/Holofractal_Harmonicode.git
cd Holofractal_Harmonicode

python -m pip install -r requirements.txt
bash start.sh
```

Open:

```text
http://localhost:8080/
```

`start.sh` performs the integrated startup sequence:

1. validates Python compatibility;
2. resolves or installs the repository-local LiteRT-LM CLI;
3. stages and verifies the Vulkan loader when the GPU profile requires it;
4. imports the configured Gemma 4 `.litertlm` model when it is not already registered;
5. starts or reuses the LiteRT-LM provider on port `9379`;
6. verifies the requested model through `/v1/models`;
7. builds and verifies the native HHS C surfaces;
8. launches `hhs_backend.visual_server:app` on port `8080`.

Model weights are runtime assets and are not committed to Git. A first local startup may download and import the configured model.

### Start the Pass 162 creative runtime

With the LiteRT-LM provider available:

```bash
python -m uvicorn hhs_backend.pass162_server:app \
  --host 0.0.0.0 \
  --port 8080 \
  --ws websockets
```

Generate a novel only through the VM81 client:

```bash
python tools/vm81_generate_novel.py \
  --runtime-url http://127.0.0.1:8080 \
  --title "The Ninth Archive" \
  --chapters 9 \
  --target-words 9000 \
  --filename THE_NINTH_ARCHIVE.md
```

The response includes VM81 authorization, runtime I/O records, provider evidence, outline and chapter roots, manuscript and result roots, persistence evidence, word count, elapsed time, and optimization metadata.

## LiteRT-LM configuration

| Variable | Default | Meaning |
|---|---|---|
| `HHS_LITERT_LM_PROVIDER_MODE` | `auto` | Reuse a reachable provider or start a validated local provider |
| `HHS_LITERT_LM_BASE_URL` | `http://127.0.0.1:9379/v1` | OpenAI-compatible LiteRT-LM endpoint |
| `HHS_LITERT_LM_MODEL` | `gemma4-12b` | HHS model registry ID |
| `HHS_LITERT_LM_BACKEND` | `gpu` | Requested LiteRT-LM execution backend |
| `HHS_LITERT_LM_AUTO_BOOTSTRAP` | `1` | Install the repository-local LiteRT-LM CLI when absent |
| `HHS_LITERT_LM_AUTO_IMPORT` | `1` | Import the configured model when absent |
| `HHS_LITERT_LM_STRICT_STARTUP` | `0` | Permit assistant-degraded HHS startup when the provider is unavailable |
| `HHS_START_LITERT_LM` | `1` | Enable provider supervision |
| `HHS_VULKAN_AUTO_INSTALL` | `1` | Stage the repository-owned Vulkan loader when required |
| `HHS_SKIP_C_BUILD` | `0` | Skip native build only when explicitly requested |
| `PORT` | `8080` | HHS API and visual-interface port |

Supported provider modes:

| Mode | Behavior |
|---|---|
| `auto` | Reuse a reachable provider; otherwise start locally only for a loopback endpoint after accelerator validation |
| `local` | Require or start a local provider |
| `external` | Use only the configured external provider |
| `disabled` | Start the HHS API and visual environment without provider supervision |

### Local GPU provider

```bash
HHS_LITERT_LM_PROVIDER_MODE=local \
HHS_LITERT_LM_BACKEND=gpu \
bash start.sh
```

### External GPU provider

On the GPU host:

```bash
python -m pip install -r requirements-litert-lm.txt
bash tools/import_hhs_gemma4_model.sh
litert-lm serve --host 0.0.0.0 --port 9379
```

On the HHS API/UI host:

```bash
HHS_LITERT_LM_PROVIDER_MODE=external \
HHS_LITERT_LM_BASE_URL=http://GPU_HOST:9379/v1 \
HHS_LITERT_LM_MODEL=gemma4-12b \
HHS_LITERT_LM_BACKEND=gpu \
bash start.sh
```

Do not expose an unauthenticated LiteRT-LM endpoint directly to the public internet. Use a private network, authenticated reverse proxy, VPN, or service mesh.

### CPU diagnostic profile

```bash
HHS_LITERT_LM_PROVIDER_MODE=local \
HHS_LITERT_LM_BACKEND=cpu \
bash start.sh
```

CPU execution is a diagnostic or compatibility profile, not the default HHS production profile.

See [`docs/HHS_LITERT_LM_GPU_DEPLOYMENT.md`](docs/HHS_LITERT_LM_GPU_DEPLOYMENT.md) for deployment details.

## Default routes

| Route | Purpose |
|---|---|
| `/` | LiteRT-LM visual development assistant and Pass 161 object environment |
| `/api/system/status` | Preserved machine-readable HARMONICODE system status |
| `/api/assistant/status` | Assistant configuration and authority projection |
| `/api/assistant/health` | Live LiteRT-LM provider and model health |
| `/api/assistant/tools` | Governed assistant-tool registry |
| `/api/assistant/threads` | List or create bounded assistant threads |
| `/api/assistant/threads/{thread_id}` | Read a bounded thread projection |
| `/api/assistant/threads/{thread_id}/messages` | Execute a governed assistant turn |
| `/api/assistant/chat` | Create or continue a thread and execute one turn |
| `/api/assistant/ws/{thread_id}` | Assistant WebSocket transport |
| `/health` | Integrated HHS runtime, graph, emulator, and WebSocket health |
| `/docs` | FastAPI interactive API documentation |
| `/api/runtime/*` | Canonical runtime, graph, conformance, workspace, capability, and document surfaces |
| `/api/runtime/creative/novel/status` | Pass 162 creative runtime status; available through `hhs_backend.pass162_server:app` |
| `/api/runtime/creative/novel` | VM81-governed novel generation; available through `hhs_backend.pass162_server:app` |

## Visual development environment

The Pass 161 home interface contains two coordinated work modes.

### Assistant home

The assistant home is loaded by default and exposes:

- model and backend identity;
- provider online/degraded state;
- thread identity and bounded message count;
- governed HHS tool availability;
- user, assistant, error, and tool-trace message projections;
- provider receipt and ingress metadata;
- new-thread and quick-prompt controls;
- direct access to object space and the API controller.

### Registered-object workspace

The object workspace preserves the Pass 161 unified object-control environment:

- typed registered-object navigation;
- search across object metadata;
- nested inspector lineage;
- capability, relationship, authority, receipt, visual-face, diagnostic, and raw-schema panels;
- equivalent 2D and spatial object identities;
- responsive mobile navigation;
- shader and sprite fallbacks;
- bounded panel recursion and deterministic receipt tracking.

The LiteRT-LM model, assistant agent, and assistant API are registered as first-class Pass 161 objects rather than being embedded as an untracked external overlay.

## Assistant execution contract

A completed assistant turn follows this sequence:

1. create or resolve a bounded conversation thread;
2. append a Hash72-linked user message;
3. build and validate a provider execution proposal;
4. evaluate the capability policy gate;
5. invoke LiteRT-LM through the configured accelerated transport;
6. resolve allowlisted read-only HHS tool calls within a bounded tool loop;
7. create a provider invocation receipt;
8. pass the result through universal provider-result ingress;
9. append the assistant projection with receipt and ingress references.

Default bounds include:

- 128 in-memory threads;
- 64 retained messages per thread;
- four governed tool rounds;
- per-thread request serialization;
- no mutating model-tool execution.

These are projection-store bounds, not canonical VM81-state limits.

## Repository topology

```text
applications/holofractal_harmonizer/
├── index.html                         Default visual assistant and workspace shell
├── src/browser.mjs                   Assistant, thread, registry, inspector, and API UI
├── src/core.mjs                      Pass 161 object-control runtime
├── src/styles.css                    Responsive dark visual system
├── src/finalization.mjs              Browser, repository, native, replay, and package gates
├── tests/                            Pass 161 JavaScript tests
└── tools/                            Audit, finalization, verification, and package tools

hhs_backend/
├── visual_server.py                  Default visual assistant HTTP entrypoint
├── pass162_server.py                 Specialized VM81 creative-writing composition
├── server.py                         Canonical FastAPI runtime authority
├── api/litert_lm_assistant_routes.py Assistant REST and WebSocket routes
├── api/vm81_creative_writing_routes.py
└── runtime/
    ├── hhs_litert_lm_assistant_v1.py
    ├── hhs_litert_lm_hhs_api_assistant_v1.py
    ├── hhs_litert_lm_accelerated_transport_v1.py
    ├── hhs_assistant_api_tool_gateway_v1.py
    ├── hhs_provider_execution_proposal_v1.py
    ├── hhs_capability_policy_gate_v1.py
    ├── hhs_provider_invocation_receipt_v1.py
    ├── hhs_provider_result_ingress_v1.py
    └── hhs_vm81_creative_novel_v1.py

creative_writing/
├── README.md
└── novels/THE_NINTH_ARCHIVE.md       Seed/reference manuscript; no fabricated live receipt

tools/
├── bootstrap_litert_lm.sh
├── import_hhs_gemma4_model.sh
├── probe_litert_lm_accelerator.py
├── install_vulkan_loader.sh
└── vm81_generate_novel.py

requirements-litert-lm.txt             Pinned LiteRT-LM CLI/runtime dependency
start.sh                               Integrated provider, native runtime, API, and UI launcher
native_projects/                       Versioned native pass implementations and evidence
tests/                                 Python regression and integration tests
docs/                                  Deployment and implementation documentation
```

## Validation

Run dependency-scoped checks for the surfaces changed.

### Native runtime

```bash
make verify-c
```

### LiteRT-LM assistant and default home

```bash
python -m pytest -q \
  tests/test_hhs_litert_lm_visual_home_v1.py \
  tests/test_hhs_litert_lm_assistant_v1.py \
  tests/test_hhs_litert_lm_gpu_runtime_v1.py \
  tests/test_hhs_litert_lm_hhs_api_tools_v1.py \
  tests/test_hhs_litert_lm_repo_bootstrap_v1.py
```

### Pass 162 creative runtime

```bash
python -m pytest -q tests/test_hhs_vm81_creative_novel_v1.py
```

### Static launcher and interface checks

```bash
python -m py_compile hhs_backend/visual_server.py
bash -n start.sh
node --check applications/holofractal_harmonizer/src/browser.mjs
```

### Pass 161 application gates

```bash
cd applications/holofractal_harmonizer
npm test
npm run audit:browser
HHS_PASS160_CLI=../../native_projects/hhs_pass160_validated_transition_runtime/dist/hhs-pass160 npm run finalize
npm run package
```

Terminal Pass 161 classification is emitted only through the cross-architecture closure workflow. Local checks produce validation evidence but do not independently redefine terminal authority.

Relevant CI workflows:

- `.github/workflows/litert-lm-assistant.yml`
- `.github/workflows/pass161-harmonizer.yml`
- `.github/workflows/hhs-ledger-latency-repairs.yml`

## Development and repository policy

- Commit only new and modified files relevant to the active pass or repair.
- Do not recommit the inherited legacy package as a duplicate monolithic archive.
- Preserve previously verified evidence unless affected code or dependencies changed.
- Prefer dependency-scoped regression, targeted integration, calibration workloads, and one bounded final replay.
- Follow repair-forward operation if later breakage is discovered.
- Do not weaken authority, replay, or receipt checks to make path or environment failures disappear.
- Preserve source text and HARMONICODE operand order.
- Additive adapters must not create alternate canonical state paths.

## Documentation index

- [`HHS_PASS_153_LITERT_LM_GEMMA4_AI_THREAD_INTERFACE_CONTRACT_v1.0.0.md`](HHS_PASS_153_LITERT_LM_GEMMA4_AI_THREAD_INTERFACE_CONTRACT_v1.0.0.md)
- [`docs/HHS_LITERT_LM_GPU_DEPLOYMENT.md`](docs/HHS_LITERT_LM_GPU_DEPLOYMENT.md)
- [`applications/holofractal_harmonizer/README.md`](applications/holofractal_harmonizer/README.md)
- [`HHS_PASS_161_INHERITANCE_AMENDMENT_V1_1.md`](HHS_PASS_161_INHERITANCE_AMENDMENT_V1_1.md)
- [`HHS_PASS_161_AUTHORITY_BINDING.json`](HHS_PASS_161_AUTHORITY_BINDING.json)
- [`HHS_PASS_162_VM81_CREATIVE_NOVEL_LANGUAGE_MODEL_OPTIMIZATION.md`](HHS_PASS_162_VM81_CREATIVE_NOVEL_LANGUAGE_MODEL_OPTIMIZATION.md)
- [`docs/HHS_VM81_CREATIVE_WRITING_RUNTIME.md`](docs/HHS_VM81_CREATIVE_WRITING_RUNTIME.md)
- [`creative_writing/README.md`](creative_writing/README.md)
- [`AGENTS.md`](AGENTS.md)

## Current integrated status

The `main` branch uses the governed repository-native LiteRT-LM Gemma 4 assistant as the default visual development interface while preserving the canonical HHS server, VM81 authority, existing API routes, WebSocket surfaces, deterministic receipts, and Pass 161 object environment.

Pass 162 is merged as an additive VM81 creative-novel runtime with targeted tests, operator documentation, a CLI client, guarded creative-artifact persistence, and a complete reference manuscript. Its implementation classification does not substitute for live execution verification: terminal live-provider status requires an admitted runtime result and persistence receipt from a reachable LiteRT-LM provider.

The previous README was a Replit-specific integration and latency investigation. That material described an earlier launch path and interface arrangement and is superseded by this operational guide.
