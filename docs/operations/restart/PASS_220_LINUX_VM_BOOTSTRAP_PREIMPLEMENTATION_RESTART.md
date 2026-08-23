# Pass 220 Linux VM Bootstrap — Non-Promotional Restart Record

## Status

`NON_PROMOTIONAL_PREIMPLEMENTATION`

This record is intentionally not named Pass 220 Iteration 1 because the governing Pass 220 contract requires terminal Pass 219 merge and exact-head verification on authoritative `main` before implementation admission.

## Repository boundary

- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative main observed at task start: `ff66e376a44c8b928a9a42c2e6d8aa1846785fc2`
- Main identity: `Merge Pass 219B I6 inherited runtime equation conformance`
- Validated stacked parent: Pass 219B I7 head `6df75bc39fd7c58108b8cf7aee3758341fe345a5`
- Parent PR: `#319`, ready for review and unmerged at bootstrap start
- Development branch: `agent/pass220-linux-vm-bootstrap-preimplementation`
- Intended immediate review base while the gate remains closed: `agent/pass219b-i7-exact-selective-projection-optimization`
- Terminal merge to `main`: forbidden by the Pass 220 gate until Pass 219 terminal closure is established

## Governing contract

`HHS_PASS_220_HARMONICODE_UNIVERSAL_POLYGLOT_NATIVE_LINUX_VISUAL_IDE_PORTABLE_VM_COMPILER_CONTRACT.md`

Relevant inherited law:

```text
terminal Pass 219 merge + exact-head verification
-> Pass 220 implementation admission may begin
```

Before that gate, Pass 220 work may only be non-promotional/experimental/reference/prototype/standards-research work.

## Task purpose

Begin the Linux VM substrate and deprecate the browser frontend as a primary product surface without deleting inherited compatibility or creating an alternate authority path.

## Changed/new surfaces

- `native_projects/hhs_pass220_linux_vm/__init__.py`
- `native_projects/hhs_pass220_linux_vm/hhs_linux_vm.py`
- `native_projects/hhs_pass220_linux_vm/config/hhs-vm.default.json`
- `hhs_backend/api_server.py`
- `hhs_backend/visual_server.py`
- `start_api.sh`
- `start_vm.sh`
- `start_web_compat.sh`
- `tests/pass220/test_hhs_linux_vm_bootstrap.py`
- `tests/pass220/test_pass220_interface_migration.py`
- `docs/pass220/PASS_220_LINUX_VM_BOOTSTRAP_PREIMPLEMENTATION.md`
- `.github/workflows/pass220-linux-vm-bootstrap-preimplementation.yml` when added
- `README.md` / architecture-flow documentation if reconciled in this branch
- this restart record

## Implemented boundary

- deterministic exact JSON VM configuration and SHA-256 config identity;
- QEMU x86_64 host probing;
- `/dev/kvm` capability probing;
- deterministic `auto -> kvm|tcg` acceleration selection;
- deterministic QEMU argv construction;
- virtio disk/RNG/balloon/network and GTK/headless display choices;
- QEMU user-network guest access to host HHS API at `10.0.2.2:8080` by default;
- no bridge/tap network by default;
- API-only FastAPI compositor preserving accumulated API routes while removing three legacy static product mounts;
- explicit browser status `DEPRECATED_COMPATIBILITY_ONLY`;
- primary API launcher and preferred VM bootstrap launcher;
- explicit web-compatibility launcher;
- zero guest/launcher canonical mutation, persistence, and Hash72 authority.

## Validation completed before CI

Repository inspection established:

- Pass 220 contract already exists and explicitly makes native Linux GUI/CLI/API primary and web secondary;
- no prior Pass 220 implementation branch was found;
- `hhs_backend.visual_server` composes accumulated APIs in addition to static UI, so bypassing it directly would drop API surface;
- the new `hhs_backend.api_server` therefore inherits the accumulated composition and strips only named static UI mounts as a transitional adapter.

No local repository checkout/compiler environment is assumed persistent. GitHub Actions is the repository validation environment for this checkpoint.

## Validation remaining

The dedicated workflow must prove:

1. validated I7 ancestry;
2. Python compile for VM and interface modules;
3. VM bootstrap unit tests;
4. interface migration unit tests;
5. deterministic manifest/plan generation;
6. shell syntax for `start_api.sh`, `start_vm.sh`, and `start_web_compat.sh`;
7. zero `float`/`double` tokens in VM planning authority;
8. Pass 220 implementation-gate text remains present;
9. web frontend is deprecated but not deleted;
10. API-only compositor names the inherited singleton authority and creates none of its own.

## Environment state

No QEMU process, KVM device, Linux guest image, graphical session, or live guest-to-host API connection has been claimed by this checkpoint. CI is intentionally hardware-independent.

## Blocker

The blocker to promotion is contractual and repository-visible: authoritative `main` has not yet established terminal Pass 219 closure required by Pass 220.

## Next action

Open a non-promotional stacked PR against the validated Pass 219B I7 branch, run exact-head and synthetic validation, repair forward if needed, and freeze the resulting bootstrap checkpoint. Do not merge this work to `main` as Pass 220 until the governing admission gate is satisfied.
