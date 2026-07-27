# HHS runtime graphics Vulkan loader

The HHS native graphics substrate uses the Khronos Vulkan loader as the dispatch
boundary between native applications and host-installed Vulkan ICD drivers.
The loader is projection infrastructure only. It does not receive VM81 authority
and it does not replace a GPU vendor driver.

## Runtime layout

Repository initialization and local LiteRT-LM GPU startup stage the loader under:

```text
.hhs/runtime/graphics/vulkan/
├── lib/libvulkan.so.1
├── env.sh
└── vulkan-loader-receipt.json
```

The staged library is normally an absolute symlink to the distribution-provided
`libvulkan.so.1`. When symlinks are unavailable, the installer copies the loader.
The generated directory is runtime state and is excluded from Git.

## Install

```bash
bash tools/install_vulkan_loader.sh
```

The installer is idempotent and supports these Linux package families:

| Distribution family | Loader package | Diagnostic package |
|---|---|---|
| Debian/Ubuntu | `libvulkan1` | `vulkan-tools` |
| Fedora/RHEL | `vulkan-loader` | `vulkan-tools` |
| Arch | `vulkan-icd-loader` | `vulkan-tools` |
| Alpine | `vulkan-loader` | `vulkan-tools` |
| openSUSE | `libvulkan1` | `vulkan-tools` |

Verification without package installation:

```bash
bash tools/install_vulkan_loader.sh --verify-only
```

The installer may require root or `sudo` when the distribution loader is absent.
It never installs proprietary GPU drivers and cannot grant container GPU-device
access.

## Runtime verification

```bash
python -m hhs_backend.runtime.hhs_vulkan_loader_runtime_v1 \
  --require-loader
```

The service verifies:

- a loadable versioned Vulkan loader (`libvulkan.so.1`);
- required Vulkan application entry points;
- the loader API version when `vkEnumerateInstanceVersion` is available;
- discoverable ICD manifests;
- the repository-local staged loader path;
- a Hash72 diagnostic receipt.

The LiteRT-LM accelerator probe adds separate checks for render/NVIDIA/WSL
device exposure and optional `vulkaninfo --summary` enumeration.

## API

The canonical HHS backend exposes:

```text
GET /api/runtime/graphics/status
GET /api/runtime/graphics/vulkan
GET /api/runtime/graphics/capabilities
```

These routes report native graphics capability and evidence. They do not mutate
canonical runtime state.

## Startup controls

| Variable | Default | Meaning |
|---|---:|---|
| `HHS_VULKAN_AUTO_INSTALL` | `1` | Install/stage the loader before local GPU startup |
| `HHS_VULKAN_RUNTIME_ROOT` | `.hhs/runtime/graphics/vulkan` | Runtime staging root |
| `HHS_VULKAN_LOADER_PATH` | staged `libvulkan.so.1` | Explicit loader path |
| `HHS_INSTALL_VULKAN_LOADER` | `1` | Provision during `init.sh` |
| `HHS_VULKAN_INSTALL_TOOLS` | `1` | Install `vulkaninfo` diagnostics |

For a CPU-only HHS web host using an external GPU provider, the local loader is
not required. Configure `HHS_LITERT_LM_PROVIDER_MODE=external` and point
`HHS_LITERT_LM_BASE_URL` at the protected GPU host.
