# VM81 Exact ABI Repair — restart record

Status: IMPLEMENTED AND DEPENDENCY-SCOPED VALIDATION GREEN

Repository: `danonbrez/Holofractal_Harmonicode`

Kernel-repair parent: `e38510b2157ffa20af5732197aae18b59965ca90`

Exact ABI validated code head: `3235f9066219bf2e665503d9f94aa11701d4c20e`

Branch: `agent/vm81-kernel-exact-phase-hash72-repair`

Merge target: `main`

Draft PR: `#254`

Merge status: OPEN / DRAFT / MERGEABLE / UNMERGED

Deployment state: no production deployment authorized or attempted.

## Authorized scope

Repair the ABI after the exact VM81 kernel repair while preserving backwards compatibility for existing callers and exact x86_64 bytecode ingress/egress.

The existing ABI v1 structure layouts and exported symbol names remain compatibility surfaces and were not resized, reordered, or silently retyped. Historical approximate fields remain only inside that legacy compatibility shell and are not authoritative exact-computation state.

The authoritative additive ABI extension uses integer/modular representations and exposes the repaired `81 × 64 = 5,184`-bit VM81 carrier, ordered `(x,y,z,w,xy,yx,zw,wz)` phase identity, Hash72 positional coordinates, and byte-preserving x86_64 ingress/egress.

Pass 175 remains the exact architectural x86_64 decoder/re-encoder authority. Pass 186 remains the validated System V AMD64 register/quantization ABI authority. Neither convention was replaced or silently reinterpreted.

## Changed files

- `hhs_runtime/HARMONICODE_VM_RUNTIME.c` — exact integer/modular VM81 kernel repair
- `hhs_runtime/include/hhs_runtime_exact_abi.h` — additive exact ABI v1.1 extension
- `hhs_runtime/c/hhs_runtime_exact_abi.c` — exact ABI implementation
- `hhs_runtime/c/hhs_runtime_abi.c` — legacy ABI retained and exact extension linked into the same shared library
- `hhs_python/runtime/hhs_exact_ctypes_bridge.py` — additive exact ctypes bridge; legacy bridge remains intact
- `tests/test_hhs_exact_runtime_abi_v1.py` — exact ABI and x86_64 compatibility validation
- `tests/test_hhs_pass214_vm81_ir_adapter_v1.py` — repair-forward exact-kernel blob freeze
- `scripts/run_pass214_vm81_ir_adapter_validation.sh` — repair-forward exact-kernel blob freeze
- `.github/workflows/vm81-exact-abi-repair.yml` — bounded exact ABI validation workflow
- this restart/freeze record

No Pass 218/219 contract, Python hydration implementation, Pass 175 decoder, Pass 186 mapping implementation, deployment surface, or production service was changed.

## Exact ABI boundary

The additive exact ABI freezes:

```text
Hash72 alphabet             = 72 symbols
Hash72 ordered positions    = 72
Hash72 positional plane     = 72 × 72 = 5,184
VM81 cells                  = 81
VM81 word width             = 64 bits
VM81 raw frame              = 5,184 bits = 648 bytes
ordered phase basis         = 8
ordered phase pairs/cell    = 8 × 8 = 64
VM81 ordered address plane  = 81 × 64 = 5,184
x86_64 instruction envelope = 1..15 exact bytes
```

Ordered phase identity preserves the inherited relations:

```text
xy -> phase 0   tag 0x5859
yx -> phase 36  tag 0x5958
zw -> phase 0   tag 0x5A57
wz -> phase 36  tag 0x575A
```

The exact header/source contain no `float`, `double`, `<math.h>`, or host transcendental arithmetic.

## x86_64 backwards compatibility

The ABI repair is additive, not a translation rewrite.

### Raw byte ingress/egress

`hhs_x86_64_ingress_exact()` retains every encoded byte of one architectural instruction without normalization.

`hhs_x86_64_egress_exact()` returns those bytes unchanged.

`hhs_x86_64_bytecode_copy_exact()` provides arbitrary-length byte-preserving transport for x86_64 bytecode streams.

### Pass 175 inheritance

The compatibility tests retain Pass 175's existing `ExactX86Decoder` and prove `reencode() == ingress bytes` for representative:

- single-byte instruction;
- legacy-prefix + REX arithmetic;
- REX register form;
- syscall form;
- VEX-retained feature form;
- relative-control form;
- address-size + REX + ModRM/SIB/displacement form.

Unsupported/feature-gated forms remain byte-retained and fail closed according to the inherited Pass 175 policy rather than being rewritten.

### Pass 186 inheritance

The existing Pass 186 System V AMD64 authority remains unchanged:

```text
RDI = x
RSI = y
RDX = z
RCX = w
R8  = quantization pointer
R9  = result pointer
```

Its established canonical ordered lanes and VM81/Q144/G243 mapping tests remain the register-level interoperability authority.

## Legacy v1 binary-layout freeze

The exact-head gate verifies the existing SysV AMD64 ABI v1 structure sizes remain:

```text
HHSRuntimeState = 992 bytes
HHSReceipt      = 192 bytes
HHSTensorState  = 40 bytes
HHSGraphNode    = 112 bytes
HHSGraphEdge    = 24 bytes
```

No existing field was resized or reordered. Existing ctypes/cffi/native callers can therefore retain their v1 binary layouts while new authoritative callers opt into the exact v1.1 surface.

## Pass 214 repair-forward freeze

Pass 214 continues to forbid its Python governed IR adapter from directly entering `apply_instruction()` or `vm81_step()` below the governed runtime boundary.

The only freeze-authority change is the kernel Git-blob identity:

```text
superseded v7.2 blob: 362cd6e892ae66024333b111aec83f12023fdce3
authorized exact blob: 81d9699b2d28d5d6a09ea4763653f3ba9eda9e15
```

Both the validation script and Python test now bind the exact authorized blob.

## Validation evidence

Dedicated exact-head workflow:

```text
VM81 Exact ABI Repair
run: 31941882432
job: 95152163266
head: 3235f9066219bf2e665503d9f94aa11701d4c20e
result: SUCCESS
```

All stages passed:

1. exact ABI strict C11 compile with `-Wall -Wextra -Werror`;
2. exact-source prohibition scan for approximate numeric authority;
3. legacy-compatible `libhhs_runtime.so` build;
4. exact symbol export verification;
5. exhaustive `72 × 72 = 5,184` Hash72 coordinate round-trip;
6. exhaustive `81 × 8 × 8 = 5,184` VM81 address round-trip;
7. ordered phase identity checks;
8. exact 648-byte VM81 frame round-trip;
9. exact x86_64 ingress/egress and Pass 175 re-encode identity tests;
10. repaired VM81 kernel `--verify`;
11. repaired Pass 214 governed adapter boundary;
12. inherited Pass 186 SysV AMD64 native ABI tests.

Separate Pass 214 VM81 IR Adapter run on the same repaired head is terminal green:

```text
run: 31941882461
job: 95152163335
result: SUCCESS
```

The first exact-ABI workflow attempt exposed two validation-harness defects only: the workflow omitted `cryptography`, which is required to import the inherited Pass 175 package, and the Pass 214 Python test still contained the superseded kernel blob literal. Both were repaired forward without changing computational semantics.

## Closure

Implementation and dependency-scoped validation are complete. PR #254 remains draft and unmerged because no merge or production-deployment authorization was given.

The next action, if separately authorized, is review/promotion of PR #254; no additional ABI semantic repair is currently required by the completed validation surface.
