# HHS Pass 220 Linux VM Bootstrap

Status: **NON_PROMOTIONAL_PREIMPLEMENTATION**

This directory starts the native Linux VM substrate authorized by the Pass 220 contract. It is intentionally not Pass 220 Iteration 1 until terminal Pass 219 closure is present on authoritative `main`.

## Boundary

```text
Linux guest
  -> HHS host API
  -> inherited runtime/controller
  -> singleton VM81/kernel
  -> Hash72 / Hash216
```

QEMU/KVM, the guest kernel, guest processes, and guest-local files do not become canonical HHS authority.

## Requirements

For planning/tests:

- Python 3.11+

For an actual guest launch:

- Linux host
- `qemu-system-x86_64`
- a bootable x86_64 Linux disk image
- `/dev/kvm` access for hardware acceleration, or TCG fallback
- GTK QEMU display support unless headless mode is selected

## Host probe

```bash
python -m native_projects.hhs_pass220_linux_vm.hhs_linux_vm probe
```

## Deterministic launch plan

```bash
python -m native_projects.hhs_pass220_linux_vm.hhs_linux_vm plan
```

Force software emulation for a hardware-independent plan:

```bash
python -m native_projects.hhs_pass220_linux_vm.hhs_linux_vm plan --acceleration tcg
```

## Configure the guest

Default config:

`config/hhs-vm.default.json`

The default disk path is:

`.hhs/vm/hhs-linux.qcow2`

A blank qcow2 image can be created with the host QEMU toolchain:

```bash
mkdir -p .hhs/vm
qemu-img create -f qcow2 .hhs/vm/hhs-linux.qcow2 64G
```

A blank disk is not bootable. Provision a Linux guest using a pinned distribution installer or image whose source/version/checksum is recorded by the deployment workflow. This bootstrap deliberately does not download or silently select an operating-system image.

## Start API + guest

```bash
bash start_vm.sh
```

Override the disk without editing the canonical config template:

```bash
HHS_VM_DISK=/path/to/guest.qcow2 bash start_vm.sh
```

Dry-run the composed startup path without executing QEMU:

```bash
HHS_VM_DRY_RUN=1 HHS_SKIP_C_BUILD=1 bash start_vm.sh
```

The default QEMU user network exposes the host to the guest at `10.0.2.2`; the HHS API endpoint is therefore `http://10.0.2.2:8080` unless the config is changed.

## Start API only

```bash
bash start_api.sh
```

This serves `hhs_backend.api_server:app`, which preserves the accumulated backend/API composition and removes legacy static product-UI mounts.

## Legacy browser compatibility

```bash
bash start_web_compat.sh
```

The browser frontend remains available for compatibility, remote access, administration, and migration comparison. It is no longer the target primary local interface for Pass 220.

## Security/authority notes

- Default VM networking is QEMU user-mode networking; no bridge/tap is created.
- The launcher constructs argv directly and does not invoke QEMU through a shell.
- KVM is selected only when `/dev/kvm` is present and accessible.
- Requiring `--acceleration kvm` fails closed when KVM is unavailable.
- `--network none` disables guest networking.
- The launch plan carries no mutation, persistence, or Hash72 authority.
- Guest actions that need HHS state changes must use existing governed API/runtime paths.

## Not yet claimed

This bootstrap does not yet provide the Pass 220 native GUI, a guest image builder, an image provenance registry, vsock/virtio-serial transport, GPU passthrough, native desktop packaging, or end-to-end graphical VM acceptance evidence. Those are later bounded implementation steps after the Pass 220 admission gate opens.
