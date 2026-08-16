# VM81 Exact ABI Repair — restart record

Status: IMPLEMENTATION IN PROGRESS

Repository: `danonbrez/Holofractal_Harmonicode`

Parent kernel-repair commit: `e38510b2157ffa20af5732197aae18b59965ca90`

Branch: `agent/vm81-kernel-exact-phase-hash72-repair`

Merge target: `main`

Draft PR: `#254`

## Authorized scope

Repair the ABI after the exact VM81 kernel repair while preserving backwards compatibility for existing callers and exact x86_64 bytecode ingress/egress.

The existing ABI v1 structure layouts and exported symbol names are compatibility surfaces and MUST NOT be resized, reordered, or silently retyped. Historical floating-point fields may remain only inside that legacy compatibility shell; they are not authoritative exact-computation state.

The new authoritative ABI extension must use integer, modular, or exact-rational representations only and must expose the repaired `81 × 64 = 5,184`-bit VM81 carrier, ordered `(x,y,z,w,xy,yx,zw,wz)` phase identity, Hash72 positional coordinates, and byte-preserving x86_64 ingress/egress.

Pass 186's validated System V AMD64 mapping and register probe are inherited rather than reimplemented with a competing register convention.

## Planned changed files

- `hhs_runtime/include/hhs_runtime_exact_abi.h` — new exact additive ABI extension
- `hhs_runtime/c/hhs_runtime_exact_abi.c` — exact implementation
- `hhs_runtime/include/HARMONICODE_VM_RUNTIME.h` — additive inclusion/documentation only; legacy v1 layout preserved
- `hhs_runtime/c/hhs_runtime_abi.h` — additive inclusion/documentation only; legacy v1 layout preserved
- `Makefile` — link exact ABI and inherited Pass 186 x86_64 ABI into `libhhs_runtime.so`
- `hhs_python/runtime/hhs_ctypes_bridge.py` — additive exact ctypes bindings while retaining legacy classes
- dependency-scoped tests for ABI layout, exact phase/address/frame behavior, and x86_64 byte round-trip
- `scripts/run_pass214_vm81_ir_adapter_validation.sh` only if needed to replace its obsolete literal kernel-blob pin with an authorized exact-kernel lineage check

## Validation plan

1. Strict C11 compile of the exact ABI with warnings as errors.
2. Verify the new exact header/source contain no `float`, `double`, or host transcendental arithmetic.
3. Exhaustive `72 × 72 = 5,184` Hash72 positional round-trip.
4. Exhaustive `81 × 8 × 8 = 5,184` VM81 ordered phase-address round-trip.
5. Exact 648-byte little-endian VM81 frame ingress/egress round-trip.
6. x86_64 instruction bytes round-trip exactly, including legacy-prefix, REX, relative-control, and unsupported/feature-retained forms.
7. Existing Pass 175 exact x86_64 decoder retains byte-for-byte `reencode()` identity.
8. Existing ABI v1 ctypes/C structure sizes remain unchanged.
9. Pass 186 System V AMD64 map/register tests remain green.
10. Dependency-scoped inherited runtime tests remain green.

Deployment state: no production deployment authorized or attempted.

Next action: implement the additive exact ABI extension and compile/link it with the existing validated x86_64 surfaces.
