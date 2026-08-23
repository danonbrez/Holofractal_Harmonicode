# Pass 220 Linux VM Bootstrap — Non-Promotional Restart Record

## Status

`NON_PROMOTIONAL_PREIMPLEMENTATION`

This record is intentionally not named Pass 220 Iteration 1 because the governing Pass 220 contract requires terminal Pass 219 merge and exact-head verification on authoritative `main` before implementation admission.

## Repository boundary

- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative main observed at task start: `ff66e376a44c8b928a9a42c2e6d8aa1846785fc2`
- Main identity: `Merge Pass 219B I6 inherited runtime equation conformance`
- Validated stacked parent: Pass 219B I7 head `6df75bc39fd7c58108b8cf7aee3758341fe345a5`
- Development branch: `agent/pass220-linux-vm-bootstrap-preimplementation`
- Draft PR: `#320`
- Intended immediate review base while the gate remains closed: `agent/pass219b-i7-exact-selective-projection-optimization`
- Terminal merge to `main`: forbidden by the Pass 220 gate until Pass 219 terminal closure is established
- Deployment-objective implementation checkpoint: `e6e8703cee014067c339bb4d9a826b979864743e`
- Later branch movement after that checkpoint has been observed from hosted evidence writers; such evidence-only commits must be distinguished from the implementation checkpoint before promotion.

## Governing contracts

Primary Pass 220 contract:

`HHS_PASS_220_HARMONICODE_UNIVERSAL_POLYGLOT_NATIVE_LINUX_VISUAL_IDE_PORTABLE_VM_COMPILER_CONTRACT.md`

Pass 219 cumulative deployment end-state objective:

`docs/pass219/PASS_219_CUMULATIVE_DEPLOYMENT_END_STATE.md`

Relevant inherited law:

```text
terminal Pass 219 merge + exact-head verification
-> Pass 220 implementation admission may begin
```

Before that gate, Pass 220 work may only be non-promotional/experimental/reference/prototype/standards-research work.

The deployment end-state is binding downstream but is **not** a Pass 219 terminal-closure claim.

## Binding cumulative deployment end state

The final deployable HHS product must simultaneously support:

```text
FULL CLOUD SERVER API
+ NATIVE HARMONICODE LINUX VMs
+ DOWNLOADABLE STANDALONE APPLICATIONS AND CREATIVE CONTENT
+ SECURE DATABASE FUNCTIONS
```

This requirement SHALL survive later implementation choices. HHS must not be narrowed into a browser-only, cloud-only, desktop-only, or VM-only product.

The cloud/API, VM, secure-data, artifact/content, and presentation planes remain separate from the singleton inherited HHS semantic authority. Database/object/vector/cache persistence and cloud infrastructure do not independently become canonical mutation authority.

## Task purpose

Begin the Linux VM substrate and deprecate the browser frontend as a primary product surface without deleting inherited compatibility or creating an alternate authority path, while preserving the larger final deployment target above.

## Changed/new surfaces

- `docs/pass219/PASS_219_CUMULATIVE_DEPLOYMENT_END_STATE.md`
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
- `.github/workflows/pass220-linux-vm-bootstrap-preimplementation.yml`
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
- zero guest/launcher canonical mutation, persistence, and Hash72 authority;
- cumulative deployment contract defining cloud API, native HHS Linux VMs, downloadable standalone apps/content, and secure database functions;
- acceptance requirements for authenticated cloud access, native VM execution, standalone downloads, creative-content integrity, secure DB operations, denial tests, backup/restore, and local/cloud identity continuity.

## Validation completed

Dedicated workflow run `32657253528` completed green on both exact and synthetic jobs for implementation checkpoint `e6e8703cee014067c339bb4d9a826b979864743e`.

It proved:

1. validated Pass 219B I7 ancestry;
2. Pass 220 implementation admission gate remains present;
3. cumulative deployment end-state contains all four required product forms;
4. deployment end-state remains explicitly non-terminal for Pass 219;
5. singleton inherited VM81/kernel authority remains named;
6. no `float`/`double` token in VM planning authority;
7. Python migration surfaces compile;
8. VM bootstrap conformance passes;
9. interface migration conformance passes;
10. deterministic VM manifest/plan generation passes;
11. launcher shell syntax passes;
12. web deprecation preserves compatibility rather than deleting the inherited frontend;
13. default VM config parses.

## Environment state

No QEMU process, KVM device, Linux guest image, graphical session, cloud production deployment, production database service, standalone release artifact, or live guest-to-host API connection has been claimed by this checkpoint. CI is intentionally hardware-independent.

## Blocker

The blocker to Pass 220 promotion is contractual and repository-visible: authoritative `main` has not yet established terminal Pass 219 closure required by Pass 220.

The cumulative deployment objective is not itself a blocker to Pass 219 closure unless a separate accepted Pass 219 contract explicitly promotes one of its downstream dependencies into Pass 219 closure criteria.

## Next action

Continue Pass 219 to terminal closure. Preserve this deployment contract and the non-promotional VM/API bootstrap. After terminal Pass 219 merge and exact-head verification, reconcile the bootstrap against authoritative `main`, perform the required Pass 220 Iteration 1 inventory/ADR, and then begin promotional implementation of the native Linux, packaging, cloud, secure-data, and distribution surfaces in dependency-scoped stages.
