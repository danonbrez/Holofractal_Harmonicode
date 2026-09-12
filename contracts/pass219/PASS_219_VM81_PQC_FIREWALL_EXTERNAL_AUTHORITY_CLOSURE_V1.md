# PASS 219 — VM81 PQC Firewall and External Runtime Authority Closure v1

## 1. Purpose

This contract closes the remaining externally reachable runtime-authority paths while preserving the Pass 220+ development model established by the Post-219 Compositional Development ABI.

It adds a mandatory pre-execution provenance firewall between Pass 219 RNA C++ cell-wall lowering and canonical VM81 admission.

The permanent execution path is:

```text
Pass 220+ high-level operation
        ↓
Pass 219 subject-blind composition
        ↓
Pass 219 RNA C++ cell wall
        ↓
VALID parent Hash216 array reference
        ↓
VM81 PQC provenance firewall
        ↓
Pass 219 RNA composed admission
        ↓
singleton VM81 canonical authority
        ↓
VALID child Hash216 array + canonical receipt
```

The firewall does not become a second transition authority. It is a mandatory fail-closed admission precondition.

---

## 2. Authority law

For every externally reachable API, ABI, service, plugin, cache, distributed node, optimizer, or Pass 220+ caller `E`:

```text
ExternalInvocation(E) = allowed
CanonicalAuthority(E) = false
```

Canonical execution is permitted only after the instruction has traversed the Pass 219 cell wall and the firewall proves its provenance.

Therefore:

```text
external invocation != external authority
valid payload        != valid execution path
valid path           != canonical commit
firewall acceptance  != canonical authority
```

The inherited RNA/VM81 authority remains the only component permitted to create canonical committed state and canonical Hash72/Hash216 lineage.

---

## 3. Firewall halt predicate

Let an instruction envelope be `I`, its exact VM81 candidate be `W`, its parent Hash216 transition array be `H_parent`, and its Pass 219 RNA cell-wall path evidence be `R`.

VM81 may proceed only when:

```text
FIREWALL(I,W,H_parent,R) = TRUE
```

with:

```text
FIREWALL :=
    Post219Pass(I.pass)
∧   ValidHash216Reference(H_parent)
∧   RNACellWallRouted(R)
∧   CandidateHashMatches(I,W)
∧   PathHashMatches(I,R,H_parent)
∧   PQCAuthenticatorValid(I,W,H_parent)
∧   NoAuthorityEscalation(I)
```

If any term is false:

```text
VM81_EXECUTION = HALTED
CANONICAL_ADMISSION_INVOKED = FALSE
COMMITTED_FRAME = ZERO
```

The halt is latched for that firewall instance. Recovery requires explicit reconstruction/reinitialization of the trusted firewall context; an untrusted instruction cannot clear its own halt.

---

## 4. Valid Hash216 array reference

A Hash216 reference is not valid merely because it contains 216 characters.

A referenced parent transition MUST satisfy all of the following:

1. its three Hash72 lanes are structurally valid;
2. `transition_word216 == previous_hash72 || change_hash72 || receipt_hash72` in the required lane order;
3. its transition identity is present and exact;
4. it contains exactly 216 positional occurrence records;
5. every occurrence has the expected absolute position, lane role, lane-local position, and glyph;
6. all 216 SHA-256 index records are marked present;
7. `resolved_index_count == 216`;
8. every SHA-256 index record revalidates through the authoritative Hash216 index resolver.

Thus:

```text
ValidHash216Reference(H) :=
    StructuralClosure(H)
∧   PositionalClosure216(H)
∧   AuthoritativeIndexReplay216(H)
```

A caller cannot satisfy this requirement by setting completion flags or copying a syntactically valid 216-character string.

---

## 5. Hash lineage law

An admitted instruction must reference its parent lineage explicitly.

For the current UQCEL/RNA canonical path:

```text
uqcel_input.previous_hash72 == H_parent.receipt_hash72
```

If the equality does not hold, the firewall halts before RNA canonical admission.

After canonical RNA admission succeeds, the generated child transition must independently satisfy `ValidHash216Reference(H_child)` before the firewall returns COMMITTED.

Therefore canonical execution is bracketed by valid Hash216 arrays on both sides:

```text
Valid(H_parent)
    → firewalled instruction
    → RNA canonical admission
    → Valid(H_child)
```

---

## 6. RNA C++ cell-wall path law

A caller-supplied boolean claiming that an instruction used the cell wall is not sufficient.

The reference firewall creates a provenance envelope only after executing through:

```text
CoreHolographicRNACellWall::route_parallel(...)
```

and only if the resulting prepared/decision records preserve:

- exact integer semantics;
- candidate-only authority;
- Hash216-driven routing identity;
- no VM81 mutation authority;
- no canonical Hash72 authority;
- no canonical Hash216 authority;
- no persistence authority;
- source transition identity equality with the referenced parent Hash216 array.

The firewall path hash binds the candidate Hash72, parent transition identity, pass number, instruction sequence, graph signature, tensor signature, decision signature, and selected lane.

An instruction constructed outside this path has no valid sealed provenance envelope and must halt.

---

## 7. PQC authentication profile v1

The first firewall cryptographic profile is:

```text
HMAC-SHA-512
kernel-held symmetric key size = 512 bits
firewall tag size               = 512 bits
```

This is a **post-quantum symmetric authentication profile**, not a claim that HMAC is a public-key post-quantum signature scheme. Its purpose is to ensure that externally supplied instructions cannot manufacture a valid cell-wall provenance token without possession of the kernel-held secret.

The authenticated material binds:

- firewall interface version;
- Pass number;
- instruction sequence;
- exact candidate Hash72;
- exact 648-byte VM81 canonical little-endian frame;
- cell-wall path Hash216;
- referenced parent transition word216;
- referenced parent transition identity216;
- all 216 positional SHA-256 index records;
- graph/tensor/decision signatures;
- selected lane;
- cryptographic profile identifier.

The profile is versioned. A future NIST public-key PQ profile such as ML-DSA MAY be added as a successor without changing the authority law.

The cryptographic algorithm is therefore replaceable; the fail-closed provenance requirement is not.

---

## 8. Canonical admission law

The firewall MUST NOT call the lower-level raw UQCEL commit primitive.

The v1 firewalled canonical path delegates to:

```text
hhs_exact_pass219_rna_admit_composed
```

That inherited function already performs the composed UQCEL/Pass-192 admission and does not copy its staged frame into the committed output until the newly generated Hash216 transition has all 216 positional indexes resolved and complete.

The firewall then revalidates that child Hash216 reference through the same authoritative index resolver before returning COMMITTED.

The final condition is:

```text
COMMIT_ALLOWED :=
    FirewallAccepted
∧   ProfilePrecheckAccepted
∧   ParentHash216ReferenceVerified
∧   ParentReceiptLineageMatched
∧   RNAAdmissionStatusOK
∧   ChildFrameEqualsCandidate
∧   ChildHash216ReferenceVerified
```

---

## 9. Semantic rejection versus security halt

The firewall distinguishes normal mathematical/constraint rejection from provenance failure.

A validly authenticated, correctly routed instruction that fails UQCEL or another canonical mathematical constraint returns:

```text
CANONICAL_REJECTED
COMMITTED_FRAME = ZERO
FIREWALL_HALTED = FALSE
```

An instruction with an invalid path, hash reference, lineage, authenticator, or authority claim returns:

```text
HALTED
COMMITTED_FRAME = ZERO
CANONICAL_ADMISSION_INVOKED = FALSE
```

This prevents security failures from being confused with ordinary mathematical rejection.

---

## 10. Legacy low-level ABI closure

`hhs_exact_vm81_admit_uqcel` is an inherited internal composition primitive used beneath the composed Pass 219 authority.

It MUST NOT remain a production-public dynamic ABI symbol.

The closure requirement is:

```text
internal source linkage = allowed
public dynamic symbol   = forbidden
external ctypes binding = forbidden
```

Existing internal C implementation paths may continue to call it inside `libhhs_runtime.so`. External callers must use the composed/RNA/cell-wall request surfaces.

The historical Python `HHSUQCELRuntimeBridge.admit_vm81` compatibility method MAY remain as a source-level convenience, but it must delegate to the composed Pass 219 bridge rather than bind the hidden raw symbol.

---

## 11. Detached receipt-commit closure

A public client must not be able to create a second state transition authority by splitting execution and receipt mutation into unrelated calls.

The runtime law is:

```text
production transition = atomic authorized tick + receipt lineage
```

A compatibility receipt endpoint MAY remain for clients that expect the route, but it must not independently mutate runtime state or create a second receipt for an arbitrary detached state.

Public receipt access is observation/retrieval of already-authorized lineage, not receipt authority.

---

## 12. Pass 220+ preservation

Nothing in this firewall limits future Pass-system development.

For every `P_n`, `n >= 220`:

```text
Define(P_n)              = allowed
Compose(P_n)             = allowed
LowerThroughRNA219(P_n)  = allowed
Optimize(P_n)            = allowed
ExposeAPI(P_n)           = allowed
ExposeABI(P_n)           = allowed
RequestCanonical(P_n)    = allowed
DirectCanonicalCommit(P_n) = forbidden
BypassFirewall(P_n)        = forbidden
```

The stable recursive path becomes:

```text
P_(n+1)
  = Compose(P_<=n, NewStructure_n)
  → Lower_RNA219
  → Route_RNA_CellWall
  → Seal_PQC_Provenance
  → Verify_Parent_Hash216
  → Request_RNA_Canonical_Admission
  → Verify_Child_Hash216
  → Commit or Reject
```

---

## 13. Required conformance tests

The reference implementation must prove at least:

1. a valid post-219 candidate routed through the RNA cell wall can be sealed and committed;
2. the old direct post-219 canonical handoff is disabled;
3. an instruction envelope constructed outside the cell wall halts before canonical delegation;
4. a modified PQC authenticator halts before canonical delegation;
5. an incomplete Hash216 positional array halts;
6. a forged SHA-256 positional record halts;
7. a parent-receipt lineage mismatch halts;
8. a security halt returns a zero committed frame;
9. a normal canonical constraint rejection returns zero committed state without misclassifying the event as a provenance attack;
10. the child transition contains and revalidates all 216 positional SHA-256 records;
11. `hhs_exact_vm81_admit_uqcel` is absent from the public dynamic symbol table;
12. the Python compatibility bridge contains no direct raw-symbol binding;
13. Pass 220+ composition and RNA lowering remain operational.

---

## 14. Terminal invariant

After this closure:

```text
ExternalCapability
    ⊆ Define + Compose + Lower + Request + Observe
```

and:

```text
CanonicalVM81Execution
    ⇒ ValidRNA219CellWallPath
    ∧ ValidParentHash216Array
    ∧ ValidPQCProvenance
    ∧ ValidHashLineage
    ∧ InheritedCanonicalRevalidation
    ∧ ValidChildHash216Array
```

while:

```text
invalid path
∨ invalid parent Hash216 reference
∨ invalid lineage
∨ invalid cryptographic authenticator
∨ authority escalation
    ⇒ VM81 HALT
    ⇒ no canonical admission
    ⇒ zero committed frame
```

This closes external runtime-kernel authority by construction while preserving open-ended Pass 220+ compositional development through the Pass 219 RNA C++ cell wall.