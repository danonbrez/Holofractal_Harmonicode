# HHS-DQVM-001 — Lane 5 reciprocal dyadic virtual-register extension

**Status:** Candidate-only source extension. Does not establish native admission, Hash72 mutation, Hash216 persistence, complete master-equation closure, or production deployment.

## Inherited ownership

Follow `AGENTS.md`, `REPOSITORY_INDEX.md`, `ARCHITECTURE.md` and `docs/architecture/HHS_FROZEN_LAYER_PRESERVATION_CONTRACT.md`. This extension inherits Pass 191 hydration, the Pass 219 Lane 5 knowledge graph, and Pass 220 I065 read-only 72×72 hydration. It creates no parallel VM81, Hash72, or Hash216 authority.

## Native quantization contract

- Primitive reciprocal dyadic structure: `Delta = {2^n | n in Z}`; `1` is the zero-exponent identity element, not the whole structure.
- Exact reciprocal counterpart: `2^n * 2^(-n) = 1`.
- Finite symmetric shell: `-N..N` has `2N+1` addressed exponent positions. Its inversion closure is distinct from unbounded multiplication closure.
- Exact virtual manifold address: 72 ordered base-72 digits representing `[0,72**72)`. A full index is arbitrary precision, not one uint64.
- Existing fixed hydration geometry: `72*72=5184=81*64`. Linear projection `72*i+j` is an address witness and does not replace native I065 hydration.
- Register identity must retain ordered address, signed exponent, phase, type, constructor and provenance.
- Rational projection: `p=P-d; q=P+d; P**2-p*q=d**2=2**n`. Odd-exponent irrational displacements retain symbolic identity; do not approximate them or certify admission.
- Prime-centered unit-defect case: `p=P-1; q=P+1; P**2-p*q=1`. It is a specialization, not a restriction of irrational/real-centered constructors.
- Master-equation obligations include `AB=P^4`, distinct typed `A,B` and `p,q`, `sqrt(AB)=P²=a²+b²=c²/Delta`, and `b=a²`. This addition does not claim their full native execution.

## Enforcement and follow-on integration

The Python module `hhs_runtime/pass220/lane5_dyadic_virtual_register.py` offers exact **read-only candidate** and address functions. Host-side arithmetic checks are projection witnesses, NOT replacement interpretations of constitutive `==` / `OP_11 DIRAC_PASS`. It neither registers new mutation operations nor produces authoritative receipts.

Completion requires tracing existing Lane 5 native service registration, full typed ingress/egress, exact irrational symbolic branches, HNAN guards, C++ cell-wall integration, singleton VM81 signed admission, Hash72-before-Hash216 receipt lineage, replay, source-integrity CI and production runtime evidence. Retain inherited services, tests, equations and frozen foundations.

Focused test: `python -m unittest discover -s tests -p 'test_lane5_dyadic_virtual_register.py'`.


## Continuation: exact symbolic reciprocal pair and typed ingress proposal

The extension also exposes `symbolic_reciprocal_pair(n)`, which retains the *ordered*
symbolic branches `P=positive_sqrt(1+2^n)`, `d=positive_sqrt(2^n)`,
`p=P-d`, `q=P+d`. Its exact difference-of-squares projection gives
`pq=1` for each signed integer `n`; no binary float, surrogate scalar
gate, or branch truncation is involved. The expression remains a typed,
unadmitted candidate awaiting the canonical native constructor interpretation.

`prepare_lane5_hydration_candidate(VirtualRegister)` binds that symbolic
candidate to the immutable ordered 72-digit address, phase, cell type,
constructor and source provenance, and reads the existing Pass148
`HHS_GATE_EQ` operator registry declaration. The function explicitly
rejects mismatched exponent witnesses and any witness claiming canonical
admission. It neither calls VM81 nor writes receipts or persistence.

Additional regressions verify negative and positive exponent witnesses, the
`P=sqrt(2)` and `P=sqrt(3)` examples, source identity, inherited typed gate,
and fail-closed candidate-only boundaries.

**Still open:** actual source-to-VMIR and C++ cell-wall admission binding,
Lean/Wolfram proof identity linkage, HNAN denominator guards, Hash72/Hash216
receipt continuity, source-integrity checks, and exact-main production replay.
Do not interpret these read-only proposal objects as native admitted proof.

## Pass159 typed candidate/source lineage handoff

`bind_existing_pass159_provenance` consumes an exact `VirtualRegister` and an
already-produced Pass159 source-to-VMIR provenance packet. It invokes the
inherited Pass219 I157 `verify_frozen_source_identity` against repository bytes
and `normalize_pass159_provenance` for schema, provenance stage identifiers,
source SHA and authority-boundary flags. It requires the register's provenance
reference to equal the normalized `provenance_binding_sha256` value.

The resulting proposal is read-only and **not** a verified VM81 admission,
Hash72 receipt or Hash216 knowledge commit. The producer deliberately does not
construct, fabricate, or guess a source/VMIR provenance packet. Neither source
metadata validation nor symmetric candidate identities substitute for full
master-equation execution.

Symbolic reciprocal witnesses now receive complete field, type and value
comparison against the deterministic exact candidate before they enter the
proposal. Unknown fields, altered `pq`, altered difference-of-squares, float
payloads, changed operator semantics and forged authority labels fail closed.
The tests exercise these negative cases and the source-lineage mismatch boundary.

Pending native work remains Pass159 compiler ingress, typed P219 I157 graph
composition, actual C++ cell-wall forwarding, signed VM81 admission and
receipt/replay verification. Frozen source files and runtime registrations
have not been changed.

## Continuation: inherited Pass219 I157 typed graph attachment

`attach_existing_i157_typed_graph` accepts a previously validated dyadic
Pass159 binding and an existing I157 typed graph. It checks the graph schema,
recomputes the inherited exact diagnostic root using I157's own serializer,
requires identical source identity and Pass159 source-to-VMIR lineage,
retains the 5184 hydration scope, and rejects any graph carrying claimed
VM81 execution, Hash72 mint, Hash216 persistence or replay verification.

**Critical type boundary:** I157 snapshot `P` is an integer-local hydration
parameter, while the new dyadic pair's `P=sqrt(1+2^n)` may be irrational.
The attachment explicitly retains both fields with their separate identities
and does not coerce the irrational center into I157's integer snapshot,
overwrite its fifteen frozen source terms, or assert that the attached graph
has executed the dyadic full master equation.

This is a read-only, lineage-checked composition object, not a canonical
receipt. Native cell-wall forwarding, Pass159 compiler execution for the new
source, and singleton VM81 signed admission remain separate obligations.
