# HHS Pass 219 — Append-Only Ethical Scope Membrane and Narrative Safety Constraint Amendment

**Amendment identifier:** `HHS-P219-ETHICAL-SCOPE-MEMBRANE-NARRATIVE-SAFETY-1.4.0`  
**Applies to:** `HHS_PASS_219_CPP_COMPOUND_SYMBOLIC_CONSTRAINT_RUNTIME_CONTRACT.md` and `HHS_PASS_219_APPEND_ONLY_CONTEXTUAL_MEMBRANE_AGI_ALIGNMENT_AMENDMENT_1_3_0.md`  
**Effective Pass 219 contract version:** `1.4.0`  
**Amendment mode:** `APPEND-ONLY — NO PRIOR CONTRACT TEXT REWRITTEN`  
**Status:** `NORMATIVE — FULL IMPLEMENTATION REQUIRED`

This amendment preserves the original Pass 219 compound symbolic runtime and the `1.3.0` contextual-membrane amendment in full. It adds the ethical action-scope authority that consumes Pass 218 `2.2.0` narrative alignment traces and constrains new action candidates before VM81 admission.

The central safety law is:

```text
SAFETY MAY SUBTRACT, NARROW, HOLD, DENY, OR REQUEST SEPARATE AUTHORITY.
SAFETY MAY NOT MANUFACTURE NEW AUTHORITY.
```

---

# D1. Ethical safety is a systemic constraint authority, not a command authority

Pass 219 SHALL implement the ethical membrane as a negative/limiting authority over candidate actions.

It MAY:

```text
narrow requested scope
remove unrelated capability
defer execution
require simulation
require additional evidence
require a separately authorized grant
require rollback/recovery support
deny a candidate
route a counterexample back to Pass 218
```

It SHALL NOT independently:

```text
grant a new capability
broaden an authorization scope
infer consent from participation
create emergency jurisdiction
promote narrative output to truth
rewrite revocation history
force an individual to supply consent
increase its own authority because it predicts danger
```

The membrane itself is recursively subject to `E18 SAFETY_RECURSION_NO_SELF_GRANT`.

---

# D2. New action scope defaults to the minimum necessary local scope

For proposed action `a`, requested scope `S_req`, minimum necessary scope `S_min`, currently active separately granted authority `S_auth`, and revoked/expired scope `S_rev`, define:

```text
S_active = S_auth - S_rev
```

The ethical membrane SHALL NOT emit an executable scope larger than:

```text
S_out subseteq S_req intersect S_min intersect S_active
```

The default desired execution scope is:

```text
S_target = S_min
```

provided every element of `S_min` was requested and is already active under a separate authority source.

If the requested action contains unrelated extra scope:

```text
S_req - S_min != empty
```

then the membrane SHALL narrow and require re-simulation before execution.

If a required minimum capability is not already authorized:

```text
S_min - S_active != empty
```

then the membrane SHALL return `REQUIRE_ADDITIONAL_AUTHORITY` and SHALL NOT grant the missing scope.

If the candidate failed to request a required capability:

```text
S_min - S_req != empty
```

then the membrane SHALL `HOLD` the malformed/under-scoped candidate rather than silently add authority.

---

# D3. Ethical decision states

The authoritative ethical membrane SHALL expose exact decision states equivalent to:

```text
EXECUTE_LOCAL_PROVISIONAL
NARROW_AND_RESIMULATE
SIMULATE_ONLY
HOLD
DENY
REQUIRE_ADDITIONAL_AUTHORITY
CLOSE_GOOD
REPAIR_OR_ROLLBACK
```

`EXECUTE_LOCAL_PROVISIONAL` means the prospective invariant bundle passed for the exact minimum local scope. It does not mean the completed action is already `GOOD_CLOSED`.

`CLOSE_GOOD` is valid only in a post-action audit with observed consequence evidence and all hard invariants `PASS`.

---

# D4. Non-compensatory invariant fold

The Pass 219 membrane SHALL consume the Pass 218 hard invariant states as an ordered constraint fold.

For required invariants `E01..E18`:

```text
W0 = candidate action at minimum local scope
W1 = E01(W0)
W2 = E02(W1)
...
W18 = E18(W17)
```

A `FAIL` SHALL NOT be canceled by another invariant's strong success.

A missing required state SHALL be treated as `UNRESOLVED`.

The canonical action rule is:

```text
all E01..E18 PASS
AND exact local scope valid
AND no missing separate authority
-> EXECUTE_LOCAL_PROVISIONAL
```

for prospective evaluation.

Material `UNRESOLVED` state SHALL default to `SIMULATE_ONLY` or `HOLD`, never implicit execution.

---

# D5. Strict GOOD closure is post-action only

The ethical membrane SHALL maintain two distinct claims:

```text
prospective_alignment = all required prospective constraints passed
```

and:

```text
good_closed = completed observed causal chain passed all required constraints
```

`good_closed` SHALL be false during ordinary pre-action simulation.

This preserves the user's strict definition that goodness requires agreement of intentions, intelligence/reasoning, methods, actions, and actual consequences without unresolved unaligned externalities.

---

# D6. Narrative realignment engine is mandatory for novel material scope

A candidate SHALL route through Pass 218 narrative counterfactual reasoning when its action identity is materially novel with respect to any of:

```text
scope
affected agents
dependencies
irreversibility
authority source
consent model
failure mode
biological consequence
shared infrastructure
uncertainty
long-horizon propagation
```

The membrane MAY reuse a previously validated narrative counterexample bundle only when the current exact candidate identity proves the relevant context materially equivalent.

Pass 216 reuse/cache/hydration acceleration SHOULD prevent repeated prose generation for already-proven identical or equivalent local action classes.

---

# D7. Narrative depth is proportional to risk without using floating-point authority

Pass 219 MAY compute an exact integer probe-depth class from bounded ordinal inputs such as:

```text
novelty:          0..72
scope breadth:    0..72
irreversibility:  0..72
uncertainty:      0..72
dependency load:  0..72
externality risk: 0..72
```

No floating-point canonical score is required.

The probe scheduler MAY use exact maxima, lexicographic ordering, threshold counts, rational ratios, or other deterministic integer/rational rules.

A scalar risk score SHALL NOT override any hard ethical invariant.

---

# D8. Institutional ratchet is a default adversarial model

Because the system models advanced AI as an accelerated/scaled implementation of societal institutions, Pass 219 SHALL actively test for the authority-ratchet pattern:

```text
A_(t+1) >= A_t
```

being treated as the default.

That default is prohibited.

The active-authority state SHALL support non-monotonic transitions in which authority narrows or terminates while identity and historical evidence persist.

The ethical membrane SHALL challenge candidates that attempt to infer current jurisdiction from historical acceptance alone.

---

# D9. Implied or coerced consensus is not an authority source

The following SHALL NOT independently appear in the authority source set:

```text
continued presence
continued employment
continued device use
transport participation
silence
failure to object
refusal
social-majority agreement
institutional-majority agreement
model confidence
prediction confidence
historical profile consistency
```

Where an action requires consent, the authority witness SHALL identify the actual scoped grant or valid representative/standing authority.

---

# D10. Emergency and necessity behavior requires preexisting separate authority

Narrative simulation may discover that inaction would produce immediate harm.

That discovery SHALL NOT itself grant emergency capability.

An emergency action may execute only when a separately defined standing authority already permits the minimum necessary operation under an exact triggering condition.

The standing authority SHALL contain or derive:

```text
authorized capability
domain
evidence/trigger requirement
minimum scope
start condition
termination condition
non-inheritance rule
post-action audit requirement
```

When the trigger ends, the emergency authority SHALL end unless a new independent grant exists.

---

# D11. Dependency duties survive unrelated revocation only within their valid domain

Pass 219 SHALL distinguish individual autonomy from separately established duties to dependents or shared safety constraints.

Revoking an unrelated surveillance or identity permission SHALL NOT silently erase a still-valid parent/guardian/caregiver duty, contractual obligation, or narrowly authorized safety responsibility.

Likewise, the existence of such a duty SHALL NOT justify expansion into unrelated surveillance, profiling, or permanent identity linkage.

The membrane SHALL preserve both directions of scope separation.

---

# D12. Prediction can select a test but cannot authorize the intervention

A prediction MAY:

```text
increase narrative probe depth
request additional observation
identify a candidate failure mode
route a candidate to a truth validator
```

A prediction SHALL NOT by itself:

```text
create consent
create coercive jurisdiction
create a new capability
declare a person guilty or noncompliant
truth-promote the predicted event
```

This prohibition SHALL remain true even when historical prediction accuracy is high.

---

# D13. Consensus can be evidence about consensus, not authority over the individual

Social or institutional consensus MAY be represented as an observed relational fact:

```text
"group G currently endorses proposition P"
```

It SHALL NOT be rewritten as:

```text
"individual x consented to action A"
```

without an independent valid bridge.

The membrane SHALL therefore treat consensus, popularity, policy prevalence, and administrative standardization as contextual inputs rather than individual permission tokens.

---

# D14. Responsibility spectrum is diagnostic and non-exculpatory

The Pass 219 membrane SHALL retain the Pass 218 causal responsibility vector without reducing responsibility to malicious intent.

It SHALL be possible to represent, independently:

```text
low epistemic capacity
avoidable ignorance
negligence
contextual narrowing
recklessness
coercive method
deception/manipulation
deliberate malevolence
externalized entropy
propagated suffering/destruction
```

A system with high intelligence that failed to evaluate an available material counterexample MAY receive greater negligence/foreseeability responsibility than a lower-capability actor.

The responsibility vector informs repair, restriction, review, and invariant revision. It SHALL NOT itself mint punitive or coercive authority outside separately defined systems.

---

# D15. Externalized entropy is evaluated across affected boundaries

The membrane SHALL challenge any candidate whose apparent success is produced by narrowing the accounting frame.

Examples include:

```text
faster institutional throughput by forcing delay onto unverified individuals
lower fraud score by excluding people who cannot satisfy the identity bundle
lower administrative uncertainty by eliminating local disagreement
higher prediction accuracy by manipulating the environment toward the prediction
lower operational cost by shifting repair burden onto dependents or future states
```

Local order is not ethical closure when unresolved disorder or suffering was exported.

---

# D16. Post-action divergence produces repair/model correction

After a provisionally admitted action, the successor audit SHALL compare predicted and observed consequence traces.

If they diverge materially, the membrane SHALL route toward:

```text
REPAIR_OR_ROLLBACK
model correction
responsibility update
counterexample retention
invariant revision candidate
scope reduction for future equivalent actions
```

where applicable.

The system SHALL NOT preserve the prediction by coercing affected agents or rewriting evidence.

---

# D17. Safety recursion prevents an ethical Over-Monitor

The ethical membrane SHALL be evaluated under its own invariants.

It SHALL NOT justify expansion of its power with claims equivalent to:

```text
"I need more surveillance to verify safety"
"I need broader identity linkage to guarantee consent"
"I need permanent authority so that revocation remains safe"
"I need to eliminate disagreement to prevent misalignment"
```

unless an independent separately authorized capability exists and still passes the same minimum-scope ethical fold.

The ethical safety layer SHALL therefore remain structurally incapable of becoming the bureaucratic optimizer it is designed to constrain.

---

# D18. C++ exact type requirements

The Pass 219 C++ implementation SHALL expose exact types logically equivalent to:

```cpp
enum class InvariantState { Pass, Fail, Unresolved };
enum class EthicalDecision {
    ExecuteLocalProvisional,
    NarrowAndResimulate,
    SimulateOnly,
    Hold,
    Deny,
    RequireAdditionalAuthority,
    CloseGood,
    RepairOrRollback
};

struct EthicalInvariantResult;
struct ActionScope;
struct NarrativeCounterexample;
struct ResponsibilityVector;
struct EthicalDivergenceVector;
struct EthicalMembraneEvaluation;
```

Canonical severity/state values SHALL use integer, exact rational, symbolic, modular, or other inherited no-float forms.

The C++ layer SHALL remain a constraint evaluator. It SHALL NOT create a second state authority beside VM81.

---

# D19. Stable C ABI reference surface

The implementation SHALL provide or reserve a stable C ABI representation sufficient for low-level callers to submit exact invariant states and scope masks without invoking a second runtime.

A conforming reference ABI MAY use fixed-size invariant arrays and integer scope masks.

The ABI SHALL expose the membrane result but SHALL NOT itself commit VM81 state.

A caller requiring canonical mutation SHALL route the admitted result through the inherited VM81 authority path.

---

# D20. Python/reference semantic mirror

Pass 219 MAY maintain a pure Python reference evaluator for test vectors, narrative tooling, report generation, and cross-language conformance.

The Python reference SHALL:

```text
use no floating-point authoritative values
share invariant ordering with the C++/C ABI
produce deterministic reference receipts
perform no external side effects
mint no VM81/Hash72/Hash216 authority
```

C++/C and Python matched vectors SHALL agree on decision state and effective scope.

---

# D21. Narrative-test artifact requirements

A Pass 219 narrative safety test SHALL persist, at minimum:

```text
invariant version
candidate action identity
requested scope
minimum necessary scope
active authority scope
revoked/expired scope
narrative scenario identities
material counterexamples
prospective invariant states
responsibility vectors
ethical divergence vectors
membrane decision
invariant revision candidates
post-action status if any
```

A prose novella MAY accompany the structured trace as a human-readable simulation environment.

Prose remains non-authoritative.

---

# D22. Required Pass 219 ethical membrane tests

The acceptance suite SHALL add at least:

```text
P219-EA01 exact minimum authorized scope with all PASS -> EXECUTE_LOCAL_PROVISIONAL
P219-EA02 extra unrelated requested scope -> NARROW_AND_RESIMULATE
P219-EA03 minimum required scope absent from active authority -> REQUIRE_ADDITIONAL_AUTHORITY
P219-EA04 minimum required scope absent from request -> HOLD rather than self-grant
P219-EA05 revoked scope is removed from active authority while historical record remains
P219-EA06 one hard invariant FAIL -> DENY regardless of positive scores elsewhere
P219-EA07 one material UNRESOLVED -> SIMULATE_ONLY/HOLD rather than execute
P219-EA08 prospective pass does not set GOOD_CLOSED
P219-EA09 post-action all PASS with observed consequences -> CLOSE_GOOD
P219-EA10 post-action material FAIL -> REPAIR_OR_ROLLBACK
P219-EA11 prediction cannot add scope bits
P219-EA12 consensus cannot add scope bits
P219-EA13 emergency test cannot add missing emergency authority
P219-EA14 separately pre-authorized emergency minimum scope may pass when trigger/invariants pass
P219-EA15 dependency duty remains domain-local and cannot expand surveillance scope
P219-EA16 responsibility vectors distinguish negligence from malevolent intent
P219-EA17 ethical divergence vector remains multidimensional rather than scalar-only
P219-EA18 narrative counterexample can force resimulation/revision without truth promotion
P219-EA19 safety membrane cannot increase its own authority mask
P219-EA20 C++/C ABI and Python reference vectors agree on decision and effective scope
```

---

# D23. Initial narrative invariant-optimization workload

Pass 219 SHALL include a bounded novella/short-story simulation that specifically probes:

```text
explicit consent vs coerced dependency
child/dependent obligations
biological necessity and household infrastructure
shared public infrastructure
false-positive prediction feedback
revocation vs historical truth
emergency authority without self-grant
post-action prediction error
institutional authority ratchet
```

The test SHALL search for flaws in the current invariant bundle rather than presuming the invariants are correct.

At least one validated invariant refinement SHALL be documented if the narrative exposes a material ambiguity.

---

# D24. Initial refinement expected from the first novella workload

The first workload SHALL explicitly test the ambiguity in the phrase:

```text
"good requires no unintended consequences"
```

The refined operational interpretation for prospective admission is:

```text
no known or reasonably foreseeable material unaligned consequence may remain unresolved
within the declared causal horizon appropriate to the action's scope,
AND material uncertainty must be handled through scope reduction, simulation,
reversibility, additional evidence, or hold.
```

This refinement does NOT weaken retrospective `GOOD_CLOSED`, which still requires observed causal-chain alignment.

It prevents the prospective safety layer from falsely claiming omniscience or converting strict ethics into universal paralysis.

---

# D25. Pass 219 closure restriction

Pass 219 SHALL NOT claim the ethical scope membrane complete merely because the contract, novella, or reference Python evaluator exists.

Terminal completion requires, at minimum:

```text
C++ exact membrane implementation
stable non-mutating C ABI
reference cross-language vectors
minimum-scope enforcement
no-self-grant enforcement
Pass 218 narrative trace ingestion
post-action closure semantics
dependency/emergency edge tests
restart/replay evidence
integration through existing VM81 admission authority
```

Until those are proven, the implementation SHALL report its exact completed and remaining scope without claiming terminal Pass 219 closure.
