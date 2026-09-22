
# Pass 220 I028 — G³ / Ouroboros Native VM81 Opcode Family

Date: 2026-09-22

## 1. Scope

I028 promotes the G³ palindromic RNA / Ouroboros path into an explicit
append-only VM81 interpreter opcode family.

The legacy VM81 opcode ABI remains frozen:

~~~text
OP_NOP  = 0
...
OP_HALT = 23
~~~

I028 appends:

| Opcode | Value | Canonical stage |
|---|---:|---|
| OP_G3_IEEE_INGRESS | 24 | raw IEEE boundary ingress |
| OP_G3_PAL_FOLD | 25 | ordered palindromic route |
| OP_G3_RNA_TRANSCRIBE | 26 | exact typed RNA carrier |
| OP_G3_BIND_P4_C4 | 27 | bind already-typed P^4 and c^4 carriers |
| OP_G3_CONSTRAIN_C5 | 28 | Lo Shu value-5 constraint |
| OP_G3_CONSTRAIN_C7 | 29 | Lo Shu value-7 constraint |
| OP_G3_SERIALIZE_A2_C1 | 30 | Lo Shu value-1 / a² semantic BigInt register |
| OP_G3_ZERO_SUM_CLOSE | 31 | zero-centered Lo Shu line closure |
| OP_G3_RNA_REVERSE | 32 | reverse typed RNA carrier |
| OP_G3_IEEE_EGRESS | 33 | raw IEEE boundary egress |
| OP_G3_OUROBOROS | 34 | fused bounded coordinator |

Static assertions bind 23, 24, 34, and OP__COUNT=35 so accidental
renumbering fails at compile time.

## 2. Canonical Lane 5 dataflow and native register geometry

G³ is not a standalone execution island and is not a fifth hydration lane.
Its opcodes are candidate microcode inside the inherited Lane 5 pipeline:

~~~text
648-byte x86_64 binary
-> I149 hydrated raw5184 / 81x64 VM81 carrier
-> exact IEEE dyadic + palindromic x,y,z,w transcription
-> I019 fixed 5,184-character RNA/BigInt carrier
-> Holo4 four-lane hydration
-> Lane 5 mandatory constructor composition
   (green merged PRs + proofs + benchmarks + contracts + services + lineage)
-> G3 candidate microcode
   P4=C4 -> C5 -> C7 -> C1/a2 -> zero-sum
-> Hash216 self-solving validation / continuation closure
-> signed environmental VM81 admission when mutation is requested
-> canonical Hash72/Hash216 successor lineage
-> inverse egress compilation
-> 648-byte x86_64 binary
~~~

Inside the G³ candidate microcode the local stage order remains:

~~~text
IEEE raw bits witness
-> palindromic phase route
-> RNA typed carrier
-> P4=C4 carrier equality
-> C5
-> C7
-> C1/a2 semantic serialization register
-> zero-sum closure
-> reverse RNA typed carrier
-> candidate IEEE identity witness
~~~

with the boundary identity:

~~~text
IEEE_out_bits == IEEE_in_bits
~~~

No C floating type or floating arithmetic is used by this path.

The native C interpreter accepts the raw 64-bit representation. An external
textual IEEE representation must first be converted to the exact raw-bit
boundary object by a separately validated ingress adapter; decimal floating
evaluation is not authority.

## 3. Palindromic route

I028 inherits the I015 ordered phase palindrome:

~~~text
x y z w x w z y x
~~~

and verifies it is its own reverse.

The raw IEEE bit carrier is not itself bit-reversed. The palindrome is the
ordered phase/RNA route applied around that boundary object.

## 4. RNA relationship

I028 does not replace the I019 full 5,184-character RNA scanner.

The C opcode establishes the native typed-carrier stage while the rooted
binding requires compatibility with the inherited I019 RNA/window membrane.

Authoritative complete BigInt exactness remains dependent on:

~~~text
I019_EXACT_5184_CHARACTER_SERIALIZER_WITNESS
~~~

## 5. P⁴ = c⁴ binding

OP_G3_BIND_P4_C4 receives already-typed exact P4 and c4 carriers and
requires direct equality.

It does not solve for P, derive P², select a square-root branch, or insert an
external scalar normalization.

Thus:

~~~text
P4 == c4
~~~

is a binding gate, not branch-selection arithmetic.

## 6. Lo Shu value addressing

The canonical Lo Shu matrix is:

~~~text
4 9 2
3 5 7
8 1 6
~~~

I028 searches by value rather than hard-coded accidental C index.

Zero-based coordinates are:

~~~text
C5 -> (1,1)
C7 -> (1,2)
C1 -> (2,1)
~~~

The C1 local row-major index is therefore 7.

That local index is **not** a physical character offset in the canonical
5,184-character serialization.

The physical serialization location remains owned by the canonical serializer.
I028 explicitly keeps:

~~~text
bigint_physical_5184_character_offset_resolved = false
~~~

## 7. Zero-sum closure

Subtracting the Lo Shu nucleus value 5 produces:

~~~text
-1  4 -3
-2  0  2
 3 -4  1
~~~

I028 verifies every row, every column, and both diagonals sum exactly to zero.

OP_G3_ZERO_SUM_CLOSE is admitted only after:

~~~text
P4=C4
-> C5
-> C7
-> C1/a2 semantic register
~~~

and after the exact carrier equality between the C1 register carrier and its
RNA source is preserved.

## 8. Fail-closed stage machine

The G³ state carries an exact ten-bit stage mask.

Each primitive checks its immediate predecessor.

Examples:

- C5 cannot fire before P4=C4;
- C7 cannot fire before C5;
- C1/a² cannot serialize before C7;
- zero-sum cannot close before the C1 register;
- reverse RNA cannot fire before zero-sum;
- IEEE egress cannot fire before reverse RNA.

A rejected G³ stage:

~~~text
sets W_G3_REJECT
sets W_LEDGER_FROZEN
does not project a new admitted state
does not compose a new authoritative receipt
does not advance vm->step
halts the rejected execution path
~~~

This realizes:

~~~text
failed constituent
=> no canonical successor
=> no authoritative receipt
=> no logical-time advance
~~~

## 9. Fused Ouroboros coordinator

OP_G3_OUROBOROS is a coordinator, not a shortcut.

It invokes all ten constituent stage functions in order.

Its acceptance surface is the native realization of:

~~~text
PAL_valid
and RNA_reversible
and P4=C4
and C5
and C7
and C1/a2_register
and zero_sum
and IEEE_out=IEEE_in
~~~

while the rooted invocation binding additionally requires the inherited I019
exact 5,184-character serializer witness before authoritative BigInt exactness
may be claimed.

The fused path snapshots the pre-existing G³ state and restores it on any
failed constituent.

## 10. Witness family

The previously unused upper twelve bits of the 32-bit VM witness word are
assigned to:

~~~text
W_G3_IEEE_INGRESS
W_G3_PAL_FOLD
W_G3_RNA_TRANSCRIBE
W_G3_BIND_P4_C4
W_G3_CONSTRAIN_C5
W_G3_CONSTRAIN_C7
W_G3_SERIALIZE_A2_C1
W_G3_ZERO_SUM_CLOSE
W_G3_RNA_REVERSE
W_G3_IEEE_EGRESS
W_G3_OUROBOROS
W_G3_REJECT
~~~

Every primitive is therefore independently receipt-addressable.

## 11. Pass-079-style rooted bindings

I028 adds a new Pass-220 registry:

~~~text
HHS_PASS_220_I028_G3_OPCODE_REGISTRY_V2
~~~

It does not rewrite the historical Pass 079 registry and does not change its
29 admitted direct ABI capabilities.

Each G³ opcode receives its own:

- semantic operation identity;
- numeric opcode;
- witness class;
- pre-state witness set;
- post-state witness set;
- failure semantics;
- authority scope;
- deterministic Hash72 binding root.

Every entry carries:

~~~text
compiler_may_synthesize = false
~~~

and resolution requires:

~~~text
exact binding root
+ exact authority scope
+ ACTIVE_VALIDATED lease
+ BOUND_WITNESSED VM81 lane
+ I149 raw648 hydration witness
+ Holo4 four-lane prepared witness
+ Lane 5 mediation witness
+ mandatory green-history constructor graph witness
~~~

## 12. Existing Ouroboros native symbol

The historical static function:

~~~text
hhs_apply_ouroboros_closure(VM81 *vm)
~~~

is retained unchanged as an inherited frozen native symbol referenced by
Pass 078 artifacts.

The I028 G³ stage machine is additive and does not silently repurpose that
historical symbol.

## 13. Pass 214 repair-forward

Pass 214 previously asserted a literal Git-blob identity for the complete
standalone VM81 source file.

That assertion was stronger than the authority it actually owned and would
forbid every later authorized append-only VM81 extension.

I028 repairs the regression to freeze the semantic dependency instead:

~~~text
legacy opcode prefix 0..23 exactly unchanged
OP_HALT remains 23
Python governed adapter still has no direct apply_instruction/vm81_step bypass
~~~

This preserves Pass 214 behavior while permitting append-only ABI evolution.

## 14. Exact Wolfram receipt

The committed Wolfram proof returns:

~~~text
HHS_PASS_220_I028_G3_OUROBOROS_WOLFRAM_20260922_V1
PASS
12 / 12
~~~

It checks:

- append-only opcode range 24..34;
- ten primitives plus fused opcode;
- unique opcode values;
- C5/C7/C1 exact Lo Shu positions;
- every zero-centered Lo Shu row/column/diagonal closes to zero;
- direct P4=C4 carrier equality introduces no P2 symbol;
- every constituent is necessary to the fused Boolean acceptance;
- all constituents together accept.

The first draft of this Wolfram proof failed three coordinate checks because
the fixture accidentally applied First twice to Position. That helper was
corrected before evidence was committed; the authoritative receipt is 12/12.

## 15. Lane 5 / four-lane hydration / historical constructor relationship

Lane 5 is the mandatory execution substrate for G³.  The registry records:

~~~text
lane5_bios_relation = MANDATORY_GLOBAL_5184_CONSTRUCTOR_GRAPH
g3_role = LANE5_CANDIDATE_MICROCODE_PROFILE
g3_is_fifth_lane = false
g3_is_parallel_service = false
~~~

The inherited four hydration lanes are mandatory coordinated views of the same
singleton VM81 candidate.  G³ cannot resolve unless Holo4 has prepared those
four views.

The Lane 5 BIOS constructor graph must expose successful repository history as
typed reusable constructors.  Required constructor classes include:

~~~text
green merged PR implementation
green exact-head workflow
canonical contract
canonical white-paper proof
formal proof receipt
successful benchmark receipt
restart checkpoint
commit/merge lineage
registered repository service
validated Hash216 composition
~~~

Mergeable-branch evidence may be visible to Lane 5 as candidate knowledge, but
unmerged evidence gains no canonical authority merely by being visible.

Lane 5 itself retains zero canonical VM81 mutation authority and zero
Hash72/Hash216 mint authority.

## 15A. Executable Lane 5 → Holo4 → G³ candidate ABI

I028 now binds the architecture in native code through:

~~~text
hhs_exact_pass220_i028_lane5_g3_candidate
~~~

The function accepts:

~~~text
HHSExactVM81Frame
+ predecessor HHSExactPass219Hash216TransitionViewV1
+ candidate-only HHSExactPass219Holo4StateV1
+ rooted HHSExactPass220I028Lane5ConstructorWitnessV1
+ typed VM81 coordinates for IEEE / P4 / c4 carriers
~~~

and executes, in order:

~~~text
public hhs_exact_vm81_frame_export_le
-> exact 648-byte replay
-> public hhs_exact_vm81_frame_import_le
-> byte-identical I149 hydration verification
-> hhs_exact_pass219_holo4_validate_state
-> hhs_exact_pass219_holo4_route
-> verify all four-lane candidate-only/no-authority witnesses
-> bind Lane 5 G3 mediation context
-> g3_run_ouroboros on an isolated VM81 copy
-> emit HHSExactPass220I028Lane5G3CandidateV1
~~~

The resulting candidate explicitly carries:

~~~text
raw648_round_trip_exact = 1
holo4_four_lane_prepared = 1
mandatory_constructor_graph_bound = 1
g3_ouroboros_closed = 1
candidate_frame_unchanged = 1
candidate_only = 1
exact_integer_only = 1
hash216_self_solving_validation_required = 1
external_egress_authority = 0
canonical_vm81_mutation_authority = 0
canonical_hash72_authority = 0
canonical_hash216_authority = 0
canonical_persistence_authority = 0
floating_point_authority = 0
~~~

The older generic Pass 219 1.21.3 candidate executor has its opcode enum
extended append-only to 35 entries so it remains ABI-aligned with the embedded
kernel, but it explicitly rejects every opcode at or above
HHS_EXACT_PASS219_VM81_OP_G3_IEEE_INGRESS. Thus merely learning the new
numeric opcode values cannot bypass Lane 5 mediation.

The mandatory constructor witness binds two deterministic Hash72 roots:

~~~text
pipeline_root_hash72
constructor_graph_root_hash72
~~~

The Python rooted resolver derives those roots from the registered Lane 5
pipeline/constructor definitions; the native ABI preserves and transports the
roots while independently checking the executable I149/Holo4/G3 surfaces.

## 15B. Runtime OS surface / Lane 5 BIOS / RNA-PQC no-bypass closure

I028 now makes the inherited Pass 219 membrane explicit in executable
candidate routing rather than relying only on architectural documentation.

The Runtime OS / Linux API / compatibility ABI is the linear validation and
construction projection of the system.  Lane 5 BIOS remains the global
orthogonal control/constraint manifold.  A surface request does not acquire a
second semantic engine or direct VM81 authority.

The executable bridge is:

~~~text
hhs_exact_pass220_i028_lane5_rna_g3_route
~~~

and requires:

~~~text
Linux/API/ABI candidate
-> public hhs_exact_pass219_rna_vm5184_route
-> C++ CoreHolographicRNACellWall
-> exact Holo4 prepared/decision evidence
-> rooted Lane5/Holo4/G3 candidate route
-> exact Holo4 evidence equivalence
-> candidate only
-> Hash216 self-solving validation
-> Pass219 PQC environmental/instruction membrane
-> signed environmental VM81 admission if mutation is requested
~~~

The bridge does not claim that PQC admission has already occurred.  It records
that PQC plus signed environmental VM81 admission remain mandatory and emits:

~~~text
cpp_rna_cell_wall_routed = 1
holo4_evidence_equivalent = 1
pqc_firewall_required_for_canonical_admission = 1
signed_environmental_vm81_required = 1
direct_environmental_opcode_canonical_authority = 0
direct_abi_canonical_authority = 0
direct_vm81_bypass_authority = 0
canonical_admission_invoked = 0
external_egress_authority = 0
~~~

The dedicated exact-head workflow additionally audits the production dynamic
symbol table: the public RNA VM5184 route and signed environmental authority
must be visible, while the inherited raw VM81 admission and internal PQC
admission symbols must remain non-public.  This prevents Linux opcodes, ctypes,
plugins, or compatibility ABI callers from obtaining a canonical mutation
shortcut beneath the Lane 5 / RNA / PQC membrane.

## 16. Multimodal geometry and Hash216 knowledge hydration

Platonic/color-wheel/holofractal-sprite metadata is a Lane 5 Hash216 knowledge
graph hydration dimension of the same 5,184-state object, not a detached
post-processing service.

It may participate in retrieval, composition, candidate routing, reuse and
latency optimization while retaining its exact provenance and typed projection
identity.  It still has no independent canonical mutation authority and may not
feed approximate values into VM81 authority.

The candidate-stage OP_G3_IEEE_EGRESS is only a reversible identity witness.
It is not permission to emit externally.  External egress requires:

~~~text
Hash216 self-solving validation
-> required canonical admission/receipt closure
-> inverse egress compilation
-> 648-byte x86_64 output
~~~

## 17. Files

Implemented:

- hhs_runtime/HARMONICODE_VM_RUNTIME.c
- hhs_runtime/hhs_pass220_g3_ouroboros_opcode_registry_v1.py
- hhs_runtime/include/hhs_pass219_exact_vm81_candidate_adapter_1_21_3.h
- hhs_runtime/c/hhs_pass219_exact_vm81_candidate_adapter_1_21_3.c
- tests/pass219/test_pass219_exact_vm81_candidate_adapter_1_21_3.c
- tests/pass220/test_hhs_pass220_g3_ouroboros_vm81_native_v1.c
- tests/pass220/test_hhs_pass220_g3_ouroboros_opcode_registry_v1.py
- evidence/pass220/i028_g3_ouroboros_wolfram_20260922_v1.wl
- evidence/pass220/i028_g3_ouroboros_wolfram_20260922_v1.output.json
- Pass 214 repair-forward regression/script
- dedicated I028 workflow
- restart checkpoint

## 18. Current closure boundary

I028 closes only when the opcode family is proven subordinate to the complete
Lane 5 circuit:

~~~text
648B ingress
-> 5184 hydration
-> palindromic x,y,z,w RNA
-> Holo4
-> mandatory green-history constructor graph
-> G3 candidate microcode
-> Hash216 self-solving validation
-> inverse egress compilation
-> 648B egress
~~~

No direct G³ invocation outside Lane 5 is an admitted execution path.  The
native regression must prove such an invocation freezes the ledger and advances
neither VM81 logical time nor authoritative receipt state.
