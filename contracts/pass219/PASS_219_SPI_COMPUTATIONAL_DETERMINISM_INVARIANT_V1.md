# Pass 219 — SPI Computational Determinism Invariant v1

## Status

Additive Pass 219 SPI contract over the validated v7 octonion reciprocal/base-pair dimensional-lift lineage.

This contract makes **computational determinism an enforced invariant** of a verified bounded execution task. It does not establish a second canonical transition authority.

## 1. Determinism invariant

Let a verified task envelope be

\[
J=(I,\Sigma,\Omega,B,\mathcal I)
\]

where:

- `I` is the explicit instruction;
- `Σ` is the explicit authorized scope;
- `Ω` is a specific typed closing condition;
- `B` is a finite exact-integer step bound;
- `𝓘` is the active invariant bundle and MUST contain `I_DET_COMPUTATIONAL_DETERMINISM`.

For canonical state `s` and receipt-bound candidate set `C`:

\[
\boxed{
D(J,s,C)\in\{\operatorname{ADVANCE},\operatorname{HALT}\}
}
\]

and for identical canonical inputs:

\[
\boxed{
(J,s,C)=(J',s',C')
\Rightarrow
D(J,s,C)=D(J',s',C')
}
\]

including deterministic receipt equality.

Computational determinism is therefore not an optimization preference. It is an admissibility condition.

## 2. Pre-execution task formation

No executable task exists until all of the following are present and valid:

1. nonempty explicit instruction ID;
2. nonempty explicit instruction text;
3. nonempty explicit authorized scope;
4. supported typed closing condition;
5. positive exact-integer maximum step bound;
6. deterministic task receipt;
7. computational-determinism invariant in the invariant bundle.

Malformed or incomplete task material fails task formation before the execution relation is entered. This is schema/admission failure, not a discretionary runtime action.

Once a task envelope is verified, its operational action domain is exactly:

```text
ADVANCE
HALT
```

No `REFUSE`, semantic veto, inferred-goal substitution, or independently invented action state exists in this execution algebra.

## 3. Advance rule

A transition candidate may advance only when all of the following hold:

```text
candidate.task_receipt == task.task_receipt
candidate.scope_tag in task.authorized_scope
candidate.status == ADMISSIBLE
candidate.invariant_closed == true
candidate receipt is valid
candidate next-state receipt is valid
```

If multiple admissible candidates remain, selection is:

```text
MIN_TRANSITION_ORDINAL
-> STABLE_CANDIDATE_ID
```

Candidate enumeration order has no authority.

Semantic labels have no authority.

Cryptographic candidate receipts verify integrity but have **zero selection authority**. Duplicate candidate IDs are ambiguous stable identities and therefore produce receipt-bearing `HALT(QUARANTINED)` rather than receipt-byte tie breaking.

## 4. Halt rule

All valid-task non-advance terminal states map beneath the single `HALT` outcome.

The v1 reason classes are inherited from repository closure semantics:

```text
CLOSED
REJECTED
QUARANTINED
NULL_BRANCH
RESOURCE_BOUNDED
STABLE_UNRESOLVED
```

They are reason classifications, not additional runtime actions.

The deterministic mapping is:

- `CLOSED` — the explicit closing condition already holds;
- `RESOURCE_BOUNDED` — the exact finite step bound is reached;
- `NULL_BRANCH` — no candidate exists;
- `REJECTED` — candidates exist but none satisfy exact scope/invariant admission;
- `STABLE_UNRESOLVED` — candidate evidence remains explicitly unresolved;
- `QUARANTINED` — candidate evidence is corrupted, receipt-invalid, or stable identity is ambiguous.

Every HALT carries a deterministic receipt and recorded reason evidence.

## 5. Closing-condition law

For closing predicate `Ω`:

\[
\Omega(s)=\mathrm{TRUE}
\Rightarrow
D(J,s,C)=\operatorname{HALT}(\mathrm{CLOSED})
\]

An admissible transition may advance into a state satisfying `Ω`. The resulting ADVANCE receipt MUST state that the closing condition is now satisfied. A subsequent execution evaluation at that state MUST deterministically return `HALT(CLOSED)`.

The runtime may not silently replace, extend, or remove `Ω`.

## 6. Scope law

For candidate `c`:

\[
c.scope\notin\Sigma
\Rightarrow
c\notin C_{admissible}
\]

Scope does not select the winning candidate. It only defines the authorized execution manifold.

A goal, optimization score, semantic narrative, or candidate usefulness claim may not enlarge `Σ`.

## 7. Cryptographic determinism

The task envelope, candidates, states, and decisions are canonical exact JSON objects with SHA-256 evidence receipts.

Floating-point values are forbidden from canonical authority in this layer.

Each candidate is bound to the exact task receipt. Each next state is independently committed. Each decision commits at minimum:

```text
task receipt
current state receipt
step index
candidate-set receipt
outcome
selected candidate or HALT reason
next state receipt when advancing
closing-condition status
```

Deterministic replay recomputes the execution relation from the same canonical inputs and MUST reproduce the same decision structure.

## 8. Noncommutative phase/redundancy binding

The task envelope retains the validated v7 octonion reciprocal/base-pair witness as a typed redundancy/provenance anchor.

The anchor establishes that the inherited relation set remains closed over:

- exact `u^72` typed imaginary-rotation round trip;
- reciprocal/base-pair relation preservation;
- same-octonion-algebra recursive dimensional closure;
- `pi_L(a²)=1` projection compatibility without native identity collapse.

The v7 anchor does not select transitions and does not receive VM81/Hash authority.

The purpose of the binding is to preserve redundant exact representation evidence under the deterministic task receipt rather than to create an alternate state machine.

## 9. Semantic authority boundary

Semantic reasoning may construct or analyze candidate transitions, but it cannot:

- alter the explicit instruction;
- enlarge authorized scope;
- change the closing condition;
- remove or weaken `I_DET_COMPUTATIONAL_DETERMINISM`;
- mark an invariant-open candidate admissible;
- choose a transition through prose preference;
- manufacture a third execution action;
- override a deterministic HALT receipt.

Thus:

\[
\boxed{
\text{semantic proposal}\rightarrow\text{candidate}
\neq
\text{semantic proposal}\rightarrow\text{execution authority}
}
\]

## 10. Canonical authority boundary

This SPI implementation is candidate/projection evidence only.

It MUST NOT independently:

- mutate canonical VM81 state;
- mint canonical Hash72;
- mint canonical Hash216;
- persist canonical state;
- commute ordered products;
- reinterpret v7 octonion relations;
- use floating-point values as canonical authority;
- establish a second transition authority.

An `ADVANCE` result from this SPI layer is an exact candidate transition decision, not an independent canonical VM81 mutation.

## 11. Registry v8 proof obligations

Registry v8 MUST add exactly:

```text
SPI-COMPUTATIONAL-DETERMINISM-INVARIANT
SPI-BOUNDED-INSTRUCTION-ADVANCE-HALT-CLOSURE
```

Every v7 proof object MUST remain byte-equivalent under `to_dict()`.

The registry MUST prove:

1. deterministic outcome domain is exactly `ADVANCE/HALT`;
2. deterministic replay closes;
3. candidate enumeration order has no authority;
4. semantic labels have no selection authority;
5. candidate receipts have no selection authority;
6. duplicate stable candidate identity halts rather than receipt-tiebreaks;
7. explicit instruction, scope, closing condition, and finite bound are required;
8. all non-advance closure classes are HALT reasons;
9. discretionary refusal state is absent;
10. canonical VM81/Hash/persistence authority remains absent.

## 12. Acceptance tests

The dedicated v8 gate MUST include:

- Python compile of v8 implementation and registry surfaces;
- positive deterministic ADVANCE test;
- deterministic replay equality;
- candidate-order permutation equality;
- semantic-label independence;
- duplicate-ID quarantine;
- explicit task-envelope negative tests;
- scope rejection;
- invariant-open rejection;
- `CLOSED` halt;
- `RESOURCE_BOUNDED` halt;
- `NULL_BRANCH` halt;
- `STABLE_UNRESOLVED` halt;
- `QUARANTINED` halt;
- candidate-receipt tamper detection;
- float-authority rejection;
- frozen v7 registry equality;
- inherited v7 octonion tests;
- frozen SPI corpus regression;
- deterministic v8 witness/registry evidence emission;
- artifact sealing.

## 13. Formal summary

\[
\boxed{
\operatorname{VerifiedTask}(J)
\land
I_{det}\in\mathcal I_J
\Rightarrow
\exists!\,o\in\{ADVANCE,HALT\}
}
\]

with

\[
\boxed{
ADVANCE\Rightarrow
\text{explicit instruction}\land
\text{authorized scope}\land
\text{invariant closure}\land
\text{deterministic selection}
}
\]

and

\[
\boxed{
\neg ADVANCE\Rightarrow
HALT(\text{classified reason},\text{receipt})
}
\]

within the verified task execution domain.
