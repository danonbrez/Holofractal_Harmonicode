# Pass 220 — Native Linux VM Bootstrap Preimplementation

## Status

`NON_PROMOTIONAL_PREIMPLEMENTATION`

This document does **not** claim Pass 220 Iteration 1 admission, Pass 220 implementation completion, native-GUI completion, virtual-machine deployment acceptance, or terminal Pass 220 authority.

The governing contract remains:

`HHS_PASS_220_HARMONICODE_UNIVERSAL_POLYGLOT_NATIVE_LINUX_VISUAL_IDE_PORTABLE_VM_COMPILER_CONTRACT.md`

That contract requires exact authoritative `main` after terminal Pass 219 merge and exact-head verification before Pass 220 implementation admission. At this checkpoint authoritative `main` remains Pass 219B I6 `ff66e376a44c8b928a9a42c2e6d8aa1846785fc2`; this work is intentionally stacked on the separately validated Pass 219B I7 head `6df75bc39fd7c58108b8cf7aee3758341fe345a5`.

## Purpose

Begin the Linux virtual-machine substrate and interface migration now that the accumulated HHS API surface is sufficiently broad to serve as the machine-facing boundary.

The migration direction is:

```text
native Linux guest / future native IDE
              |
              | API / CLI / governed action proposals
              v
primary HHS API-only backend
              |
              v
inherited runtime/controller/security mesh
              |
              v
singleton VM81/kernel admission
              |
              v
Hash72 receipt -> Hash216 archival/indexing
```

The virtual machine is an execution, containment, compatibility, and human-interface environment. It is **not** a second HHS runtime authority.

## Binding cumulative deployment end state

This bootstrap inherits the Pass 219 carry-forward deployment objective defined in:

`docs/pass219/PASS_219_CUMULATIVE_DEPLOYMENT_END_STATE.md`

The final deployable HHS product SHALL simultaneously support:

```text
FULL CLOUD SERVER API
+ NATIVE HARMONICODE LINUX VMs
+ DOWNLOADABLE STANDALONE APPLICATIONS AND CREATIVE CONTENT
+ SECURE DATABASE FUNCTIONS
```

These are cumulative product requirements, not mutually exclusive alternatives. The native Linux VM work in this branch is one deployment plane inside that larger system; it SHALL NOT narrow HHS into a VM-only or desktop-only product. Likewise, later cloud work SHALL NOT narrow HHS into a browser-only or API-only service.

Pass 219 remains responsible for closing its exact reusable runtime/ABI obligations. The cloud service, production VM fleet, standalone release pipeline, creative-content distribution path, and hardened database service are downstream implementation/acceptance work unless an accepted Pass 219 contract explicitly promotes a particular dependency into Pass 219 closure.

## Interface disposition

Pass 220 already defines native Linux GUI, CLI/Bash, and machine API as the primary interaction surfaces. The browser becomes secondary compatibility, remote-access, administration, and projection only.

This bootstrap therefore establishes:

| Surface | Preimplementation disposition |
|---|---|
| `hhs_backend.api_server:app` | primary API-only composition candidate |
| `bash start_api.sh` | primary host API launcher candidate |
| `bash start_vm.sh` | preferred local VM bootstrap candidate |
| `hhs_backend.visual_server:app` | deprecated compatibility/remote browser projection |
| `bash start.sh` | inherited compatibility launcher; retained to avoid breaking existing deployment/user flows |
| `bash start_web_compat.sh` | explicit deprecated browser compatibility entrypoint |

No web files are deleted in this checkpoint. Removal would be a separate compatibility migration requiring inventory, callers, deployment references, tests, and replacement coverage.

## API-only compositor

`hhs_backend/api_server.py` inherits the accumulated router/API composition currently assembled by `hhs_backend.visual_server` and removes only these legacy static product mounts:

- `hhs-storybook-reel-studio`
- `hhs-probability-hydration-studio`
- `hhs-visual-home`

This transitional dependency is deliberate. Rebuilding the router list independently before Pass 220 Iteration 1 inventory would risk dropping accumulated API capability or creating divergent composition. After terminal Pass 219 closure, the common API composition should be factored into a shared backend module and both native/remote projections should consume it.

The API-only composition exposes:

`GET /api/interface/status`

with migration and authority metadata.

## VM host substrate

The current bootstrap lives under:

`native_projects/hhs_pass220_linux_vm/`

### Implemented

- deterministic JSON VM configuration;
- canonical SHA-256 identity of the exact VM launch configuration;
- Linux host and `qemu-system-x86_64` probe;
- `/dev/kvm` usability probe;
- `auto` acceleration resolving to KVM when available and TCG otherwise;
- explicit `kvm` and `tcg` modes;
- `q35` machine profile;
- integer vCPU and memory configuration;
- virtio disk, RNG, balloon, graphics, and network devices;
- GTK display or headless mode;
- user-mode networking or no-network mode;
- guest-to-host API endpoint default `http://10.0.2.2:8080` under QEMU user networking;
- direct argv construction with no shell interpolation;
- dry-run launch plans and host manifests;
- fail-closed launch when the host, QEMU binary, KVM requirement, or guest disk is unavailable.

### Explicitly not implemented yet

- no bootable Linux guest image is claimed;
- no distribution/rootfs installer is claimed;
- no native GTK/Qt/other GUI application is claimed;
- no GUI framework decision is frozen before the required Iteration 1 inventory/ADR;
- no virtio-serial/vsock HHS protocol is claimed;
- no PCI/GPU passthrough is claimed;
- no bridged/tap networking is enabled by default;
- no guest-side mutation authority exists;
- no QEMU process becomes a VM81, Hash72, Hash216, persistence, or receipt authority;
- no VM boot or graphical acceptance is claimed by CI.

## Authority boundary

The bootstrap publishes and tests these constants:

```text
canonical_mutation_authority    = false
canonical_persistence_authority = false
canonical_hash72_authority      = false
guest_is_canonical_authority    = false
```

The only authority path represented by the launcher is:

```text
INHERITED_HHS_API_TO_SINGLETON_VM81_KERNEL
```

A guest action may call HHS APIs, but an HTTP success, guest-local state, QEMU device state, filesystem change, graphical state, or guest process result does not independently become canonical HHS state.

## Networking boundary

Default networking is QEMU user-mode networking. It is chosen for the bootstrap because it does not require a host bridge, tap device, root network reconfiguration, or a second distributed state layer.

The default guest API host is `10.0.2.2`. The host API listener remains configurable. Production isolation, authentication, transport security, vsock/virtio-serial, and firewall policy belong to later validated iterations.

## Web deprecation law

`DEPRECATED_COMPATIBILITY_ONLY` means:

1. browser UI code remains available for existing users, remote access, diagnostics, and migration comparison;
2. no new primary product workflow should depend exclusively on the browser frontend;
3. API/runtime capability remains the source of functionality;
4. native Linux surfaces must invoke the same governed backend capability rather than duplicate business logic;
5. static browser removal is deferred until replacement coverage is proven.

Deprecation is therefore an ownership transition, not deletion of evidence or inherited compatibility.

## Validation boundary

The preimplementation CI must validate, without requiring QEMU/KVM hardware:

- Python syntax for the VM launcher and API-only compositor;
- deterministic config identity;
- KVM/TCG resolution rules;
- deterministic QEMU argv generation;
- explicit no-network/headless paths;
- invalid-config rejection;
- zero canonical authority constants;
- web/API/native-interface migration metadata;
- shell syntax of the new entrypoints;
- no approximate-arithmetic tokens in the VM planning module;
- ancestry from validated Pass 219B I7;
- Pass 220 contract remains present and retains its implementation gate;
- the cumulative deployment end-state keeps all four required product forms and remains non-terminal for Pass 219.

Actual QEMU boot, guest image construction, native desktop rendering, and end-to-end guest-to-HHS action execution require later environment-backed evidence.

## Promotion gate

This branch cannot be promoted as Pass 220 Iteration 1 while terminal Pass 219 closure is absent from authoritative `main`.

When that prerequisite is satisfied, the next valid step is:

```text
terminal Pass 219 main + exact-head verification
-> rebase/reconcile this bootstrap
-> Pass 220 Iteration 1 authoritative inventory and standards freeze
-> validate API/GUI/CLI/language/toolchain/deployment/architecture inventory
-> freeze native GUI framework ADR and VM transport/profile decisions
```

Until then, this work is reusable preimplementation only.
