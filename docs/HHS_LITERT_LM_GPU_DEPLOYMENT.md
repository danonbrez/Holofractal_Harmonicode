# HHS LiteRT-LM GPU deployment

The HHS conversational API and the LiteRT-LM inference provider are separate
runtime services. The HHS API/UI can run on a CPU-only web host. Gemma 4
inference should run on a GPU-capable host and is addressed through the
OpenAI-compatible LiteRT-LM endpoint.

## Required execution substrate

The HHS production default is:

```text
model registry ID: gemma4-12b
execution backend: gpu
request model ID:  gemma4-12b,gpu
provider API:      /v1/models and /v1/chat/completions
provider port:     9379
```

For Linux and Windows GPU execution, the host requires:

- a supported physical GPU;
- the vendor GPU driver;
- a Vulkan-compatible driver and Vulkan loader;
- GPU device access inside the process or container;
- sufficient RAM/VRAM for the imported `.litertlm` model and cache.

macOS GPU execution uses Metal rather than Vulkan.

The Python package installs the LiteRT-LM CLI and runtime bindings. It cannot
install GPU hardware, host kernel drivers, or grant container device access.

## Verify a local GPU host

```bash
python tools/probe_litert_lm_accelerator.py --backend gpu --require
```

On Linux the probe requires a loadable Vulkan loader and an exposed render,
NVIDIA, or WSL GPU device. When `vulkaninfo` is installed, its device summary is
also checked.

## Local provider topology

Use this only when the HHS backend host itself has the accelerator substrate:

```bash
python -m pip install -r requirements.txt
bash tools/import_hhs_gemma4_model.sh
HHS_LITERT_LM_PROVIDER_MODE=local \
HHS_LITERT_LM_BACKEND=gpu \
bash start.sh
```

`start.sh` performs the accelerator probe before launching `litert-lm serve`.
The server is started on port `9379`; each HHS chat request selects the GPU
backend through the current LiteRT-LM model-parameter form
`gemma4-12b,gpu`.

## Split web-host and GPU-host topology

This is the recommended deployment when the public HHS page is hosted on a
CPU-only platform.

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

Use a private network, authenticated reverse proxy, VPN, or service mesh. Do not
expose an unauthenticated LiteRT-LM endpoint directly to the public internet.

## Startup behavior

`HHS_LITERT_LM_PROVIDER_MODE` supports:

- `auto`: reuse a reachable provider; otherwise start locally only for a
  loopback URL and only after accelerator validation;
- `local`: require or start a local provider;
- `external`: use only the configured external provider;
- `disabled`: start the HHS API/UI without provider supervision.

The HHS API/UI starts in a clearly degraded assistant state when the provider is
unavailable. Set `HHS_LITERT_LM_STRICT_STARTUP=1` to make provider failure block
HHS startup.

CPU is an upstream-supported LiteRT-LM backend, but it is not the default HHS
Gemma 4 production profile. It can be selected explicitly for diagnostics:

```bash
HHS_LITERT_LM_BACKEND=cpu HHS_LITERT_LM_PROVIDER_MODE=local bash start.sh
```
