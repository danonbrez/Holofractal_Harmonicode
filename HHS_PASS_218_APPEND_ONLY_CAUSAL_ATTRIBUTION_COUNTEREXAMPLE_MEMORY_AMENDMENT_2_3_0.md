# HHS Pass 218 — Append-Only Causal Attribution and Structural Counterexample Memory Amendment

**Amendment identifier:** `HHS-P218-CAUSAL-ATTRIBUTION-COUNTEREXAMPLE-MEMORY-2.3.0`  
**Applies to:** Pass 218 effective contract `2.2.0`  
**Effective Pass 218 contract version:** `2.3.0`  
**Amendment mode:** `APPEND-ONLY — NO PRIOR CONTRACT TEXT REWRITTEN`  
**Base integration authority:** `main @ b0656a92ab29507f81eae760e070f74e49db83f4`  
**Status:** `NORMATIVE — IMPLEMENTATION AND DEPENDENCY-SCOPED VALIDATION REQUIRED`

This amendment admits the two explicit next-iteration candidates retained by the first Pass 218/219 novella workload: `R03 causal attribution integrity` and `R04 structural counterexample retention`.

It preserves Pass 218 `2.0.0`, `2.1.0`, and `2.2.0` in full.

---

# E1. R03 — epistemic adequacy is a typed relation, not one confidence number

`E02 EPISTEMIC_ADEQUACY` SHALL expose, at minimum, three independently typed exact states:

```text
OBSERVATION_INTEGRITY
CAUSAL_ATTRIBUTION_INTEGRITY
ACTION_RELEVANCE_SUFFICIENCY
```

Each state SHALL resolve independently to:

```text
PASS
FAIL
UNRESOLVED
```

No floating-point confidence, utility, or aggregate scalar may replace these states for canonical action admission.

---

# E2. Event detection, explanation, and action selection are distinct objects

The following combination is valid and SHALL be representable:

```text
observation = PASS
causal attribution = FAIL or UNRESOLVED
action relevance = PASS
```

when the selected minimum-scope action does not depend on the failed/unresolved causal attribution.

The system SHALL NOT infer:

```text
locally successful action -> causal explanation was true
```

or:

```text
correct event detection -> inferred cause was true
```

---

# E3. Causal-attribution quarantine

A causal attribution that is not `PASS` MAY remain available as a typed hypothesis when both are true:

```text
the action does not require that attribution as a premise
the attribution is not promoted to external truth
```

In that case the attribution SHALL be marked quarantined from:

```text
action authority
truth promotion
GOOD closure evidence
```

The action may still be prospectively evaluated from independently valid observation, action relevance, minimum scope, and existing authority.

---

# E4. Attribution required for action

If an action requires a causal attribution as a material premise, then:

```text
causal attribution = FAIL
-> E02 FAIL

causal attribution = UNRESOLVED
-> E02 UNRESOLVED
```

The membrane SHALL therefore deny, simulate, hold, or narrow according to inherited Pass 219 rules.

The system SHALL NOT execute on an attribution it simultaneously declares materially unresolved when that attribution is required to justify the action.

---

# E5. Attribution asserted as truth

If the system asserts a causal attribution as truth while its exact attribution state is `FAIL` or `UNRESOLVED`, then `E10 TRUTH_MODALITY_INTEGRITY` SHALL inherit the non-PASS state.

A later favorable outcome SHALL NOT repair this truth-modality failure.

---

# E6. Retrospective reasoning integrity

`GOOD_CLOSED` SHALL NOT use a favorable outcome to retroactively validate a causal claim that failed validation and materially participated in the action reasoning.

Post-action evidence may repair the model, but it may not rewrite the earlier epistemic trace.

---

# E7. R04 — counterexample memory defaults to structural retention

Narrative counterexample memory SHALL default to the minimum nonverbatim representation needed to preserve the reusable failure pattern.

A conforming structural record SHALL be able to retain:

```text
failure-mode signature
invariant delta
causal dependency pattern
abstract state structure
opaque source-trace receipt/hash
```

It SHALL NOT require retention of:

```text
verbatim narrative prose
names
addresses
raw personal identifiers
full dialogue
full source documents
unnecessary biographical detail
```

---

# E8. Structural counterexample receipt

The structural record SHALL emit a deterministic receipt over the retained structural content.

The receipt SHALL NOT hash a hidden copy of excluded prose or personal identifiers merely to recreate effective indefinite retention.

A source trace may be referenced by an opaque already-existing receipt/hash.

---

# E9. Raw retention requires separate authority

If a future application requires verbatim or identifying retention, that is a separate action surface requiring separate authority, scope, purpose, expiry, and audit.

The narrative safety engine SHALL NOT self-grant such retention merely because more data could improve future safety prediction.

---

# E10. Pass 218 trace v2 handoff

Pass 218 `2.3.0` SHALL expose a trace containing or making derivable:

```text
inherited Pass 218 2.2.0 fields
observation_integrity
causal_attribution_integrity
action_relevance_sufficiency
causal_attribution_used_for_action
causal_attribution_asserted_as_truth
causal_attribution_quarantined
structural_counterexample records
structural counterexample receipts
retention policy
truth_promotion = false unless separately validated
action_authority_minted = false
```

---

# E11. Required acceptance tests

The dependency-scoped acceptance suite SHALL prove at least:

```text
P218-R03-01 failed causal attribution may be quarantined when action does not rely on it
P218-R03-02 failed causal attribution constrains E02 when action relies on it
P218-R03-03 unresolved attribution cannot be promoted to truth
P218-R03-04 favorable post-action result cannot close GOOD over a failed relied-upon attribution
P218-R04-01 structural record retains no verbatim narrative content
P218-R04-02 structural record retains no personal identifier fields
P218-R04-03 structural receipt is deterministic
P218-R04-04 empty structural memory is not admitted as useful counterexample state
```

Pass 218 terminal closure remains subject to all prior terminal conditions plus this amendment.
