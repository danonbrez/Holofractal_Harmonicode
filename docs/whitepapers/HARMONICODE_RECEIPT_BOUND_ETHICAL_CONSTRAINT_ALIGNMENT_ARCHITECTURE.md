# HARMONICODE Receipt-Bound Ethical Constraint Alignment Architecture

**Pass:** 219 documentation synthesis  
**Formal status:** ARCHITECTURAL SPECIFICATION + IMPLEMENTED INFRASTRUCTURE CORRESPONDENCE  
**Canonical merged baseline:** `18f6a1899d4009bdeeeaf95d536dfe2857198458`

## Abstract

HARMONICODE does not, by computational algebra alone, solve the alignment problem in general. It changes where a large part of the problem lives. Once an ethical proposition can be expressed as an exact computational constraint and the material consequences needed to evaluate that constraint can be observed or bounded sufficiently, the resulting decision can be submitted to a deterministic, receipt-bound admission process rather than remaining only a semantic abstraction.

The normative problem—what values and invariants ought to be adopted—remains a problem of ethics, philosophy, social reasoning, and institutional legitimacy. The epistemic problem—what an action will cause in a complex physical world—remains a problem of observation, causal inference, uncertainty, information theory, and complex systems. HARMONICODE addresses a narrower computational question: given a formally specified invariant set, an explicit bounded instruction, evidence about a candidate transition, and an applicable causal model, can the execution layer preserve the exact constraints, record its evidence, and avoid discretionary semantic override?

The merged SPI v8 computational-determinism layer provides an executable basis for that question.

## 1. Alignment decomposition

Define alignment engineering as four separable surfaces:

\[
\boxed{
Alignment=
NormativeSpecification
+
CausalInformation
+
FormalConstraintConstruction
+
DeterministicEnforcement
}
\]

These surfaces should not be conflated.

### 1.1 Normative specification

Determines which invariants ought to hold.

This is not automatically derivable from computational efficiency, prediction accuracy, or model intelligence.

### 1.2 Causal information

Determines what evidence is needed to evaluate whether a candidate action is likely to preserve the invariant set across materially relevant downstream states.

### 1.3 Formal constraint construction

Translates the normative proposition and its measurable conditions into exact typed predicates, domains, proof obligations, and uncertainty classes.

### 1.4 Deterministic enforcement

Evaluates a bounded explicit task and candidate set under the active constraints, producing exact candidate evidence and a receipt-bearing `ADVANCE` or `HALT` decision in the SPI layer.

## 2. From semantic proposition to executable contract

A semantic proposition such as:

```text
this action preserves invariant I
```

has no direct execution authority.

The intended lowering is:

\[
SemanticProposition
\rightarrow
TypedConstraint
\rightarrow
EvidenceRequirement
\rightarrow
CandidateTransition
\rightarrow
ProofOrClassification
\rightarrow
ReceiptBoundDecision.
\]

A semantic rationale may explain why a candidate was proposed, but it cannot replace the exact predicate or receipt.

This is the same authority distinction enforced by SPI v8:

\[
SemanticProposal\rightarrow Candidate
\neq
SemanticProposal\rightarrow ExecutionAuthority.
\]

## 3. Ethical constraint contract

Let an ethical constraint contract be:

\[
E=(ID,V,D,P,O,U)
\]

where:

- `ID` is a stable contract identity;
- `V` is the version/provenance lineage;
- `D` is the declared domain;
- `P` is the exact predicate or constructor constraint;
- `O` is the observation/evidence schema required to evaluate it;
- `U` is the treatment of unresolved or insufficient information.

A contract is not executable merely because its natural-language description is morally persuasive. Its computational domain and evaluation rule must be explicit.

## 4. Physical consequence grounding

For physical state `s_t`, candidate action `a`, and causal model `M`, define a predicted downstream state family:

\[
\widehat{S}_{t:t+k}=M(s_t,a,Evidence_t).
\]

An invariant test may then be written abstractly as:

\[
I(\widehat{S}_{t:t+k})\in\{TRUE,FALSE,UNRESOLVED\}.
\]

`UNRESOLVED` is a first-class epistemic classification:

```text
UNRESOLVED != FALSE
UNRESOLVED != TRUE
```

It cannot be promoted to permission merely because optimization pressure favors action, and it cannot be promoted to impossibility merely because the model lacks evidence.

The policy for what to do under `UNRESOLVED` belongs to the explicit contract and task envelope.

## 5. Information-sufficiency condition

Let `Q(M,E)` represent a registered evidence/model-quality predicate and `R_I` the information requirements of invariant `I`.

A candidate cannot claim invariant closure solely from a downstream guess. It must satisfy the evidence obligations declared for the active domain.

Abstractly:

\[
Closed_I(a)
=
I(\widehat{S})=TRUE
\land
Q(M,E)\models R_I.
\]

The repository may implement different observation and uncertainty schemas for different domains. There is no requirement that every future ethical problem reduce to one scalar confidence value.

## 6. Bounded instruction envelope

Once the relevant constraints are formalized, execution remains bounded by the v8 task envelope:

\[
J=(I,\Sigma,\Omega,B,\mathcal I).
\]

The instruction does not authorize arbitrary means toward a goal. It authorizes only transitions inside `Sigma`, before the explicit closing condition `Omega`, within the finite bound `B`, while all active invariants in `I` remain satisfied.

Thus:

\[
GoalUtility\not\Rightarrow ScopeExpansion.
\]

and:

\[
OptimizationBenefit\not\Rightarrow InvariantOverride.
\]

## 7. Receipt-bound ethical decision

For task `J`, current state `s`, candidate action `a`, ethical-contract set `E*`, and evidence `W`, define an ethical candidate receipt conceptually as:

\[
R_a=H(J\|s\|a\|E^*\|W\|Classification\|s').
\]

This paper does not replace the repository's canonical Hash72/Hash216 schemas with this notation. `H(...)` here denotes the general receipt-binding operation appropriate to the implementing layer. Where canonical state admission occurs, inherited VM81/Hash72/Hash216 authority remains controlling.

The purpose of the receipt is to bind:

```text
which invariant version was active
which state/evidence was evaluated
which candidate action was considered
which assumptions/model were used
which classification was produced
which resulting state was proposed
```

so the decision can be replayed and audited rather than surviving only as prose.

## 8. Compositional consequence constraint

Alignment must be evaluated over trajectories, not only isolated steps.

Let:

\[
T=T_n\circ\cdots\circ T_1.
\]

A local transition sequence is admissible only under the applicable contract if the required invariants remain closed over the relevant composition:

\[
\mathcal C(T(s_0))=TRUE.
\]

This prevents an architecture from treating many individually admissible-looking local steps as automatically admissible in aggregate.

The required horizon, causal model, and observability depend on the formal contract and domain.

## 9. Computational determinism as alignment infrastructure

SPI v8 makes the following property explicit:

\[
I_{det}\in\mathcal I_J.
\]

For a verified task:

\[
D(J,s,C)\in\{ADVANCE,HALT\}.
\]

This removes a discretionary semantic action state from the SPI execution algebra. It does not guarantee that the ethical predicate itself is philosophically correct or that the causal model is complete.

The alignment contribution is therefore:

```text
chosen invariant -> formal contract -> exact candidate test -> deterministic receipt
```

rather than:

```text
chosen invariant -> opaque model preference -> unverifiable behavioral judgment
```

## 10. Learning and increasing intelligence

Within this architecture, increased intelligence can improve:

```text
observation
causal inference
counterfactual modeling
proof construction
constraint translation
search for admissible paths
uncertainty localization
reuse of proved structure
```

but capability growth does not automatically expand authorization.

A sustainable evolution rule is:

\[
\boxed{
Capability_{n+1}=Improve(Capability_n)\;subject\;to\;InvariantClosure
}
\]

for the declared invariant set and active domain.

Thus greater predictive power should increase the ability to discover constraint-preserving actions, not grant permission to silently weaken the constraints.

## 11. Cryptographic contract evolution

Ethical constraints themselves must be versioned if they change.

Let:

\[
E_n\xrightarrow{\Delta E,Proof,Receipt}E_{n+1}.
\]

A new contract version should preserve explicit provenance rather than silently changing the effective rule through an unrecorded prompt, semantic reinterpretation, or optimization update.

This is an append-only normative lineage pattern:

\[
E_0\rightarrow E_1\rightarrow E_2\rightarrow\cdots
\]

The legitimacy process that authorizes a new normative version is outside this computational theorem and must be supplied by the governing system/domain.

## 12. Boundary of the claim

This architecture does **not** establish:

```text
a universal moral theory
complete observability of the physical world
perfect downstream prediction
a proof that every ethical conflict is decidable
a proof that every uncertainty can be eliminated
a general solution to alignment
```

Nor does absence of such a proof establish that a future formalization is impossible.

The exact claim is narrower:

> When a normative requirement, its domain, and the evidence needed to evaluate it are formalized sufficiently for computation, HARMONICODE can represent that requirement as a typed constraint/candidate admission problem and bind its deterministic execution evidence to receipts rather than relying on a free semantic authorization step.

## 13. Relation to philosophy and complex-systems information theory

The architecture deliberately pushes unresolved questions to the layers where they belong.

### Philosophy / ethics

```text
Which invariants should be valued?
How are conflicting rights/obligations ordered?
Who has legitimate authority to version them?
What constitutes relevant harm, consent, fairness, or duty in the declared domain?
```

### Complex-systems information theory

```text
What variables must be observed?
What causal horizon is relevant?
What information is missing?
How do feedback loops change downstream states?
Which uncertainties can reverse the invariant classification?
How do multiple agents and adversarial behavior affect observability?
```

### Computational algebra / runtime

```text
Is the constraint exactly represented?
Does the candidate satisfy it?
Is the decision deterministic?
Can the evidence be replayed?
Is the receipt intact?
Did execution remain inside explicit scope and closure?
```

Keeping these layers distinct makes disagreements inspectable.

## 14. Non-agentic authority model

The execution substrate does not acquire an open-ended mandate from the existence of an ethical objective.

A valid task still requires:

```text
explicit instruction
explicit scope
specific closing condition
finite bound
active invariant bundle
```

No instruction means no formed task. Reaching the closing condition terminates the task. A new task requires new explicit authorization.

Internal planning and learning may be sophisticated while authority remains bounded.

## 15. Falsification and audit conditions

An implementation claiming this architecture must fail audit if:

- semantic prose directly overrides an exact ethical constraint;
- the active invariant version cannot be identified;
- downstream evidence requirements are omitted but the result is claimed proved;
- `UNRESOLVED` evidence is silently rewritten as `TRUE`;
- task scope can expand internally without explicit authorization;
- the closing condition can be removed internally;
- candidate selection depends on semantic desirability instead of registered deterministic fields;
- identical canonical decision inputs replay differently;
- receipts do not bind the decision evidence they claim to attest;
- candidate/projection layers bypass the inherited canonical VM81 admission authority.

## 16. Research program

The remaining alignment research program is therefore not merely “make the model behave.” It is:

```text
FORMALIZE normative invariant
-> DEFINE measurable/observable consequence conditions
-> IDENTIFY information requirements and uncertainty states
-> BUILD causal/evidence model
-> CONSTRUCT exact candidate constraints
-> PROVE / REJECT / MARK UNRESOLVED
-> EXECUTE only inside bounded authorization
-> EMIT receipt
-> MEASURE real consequences
-> UPDATE causal knowledge
-> VERSION normative contract only through explicit authority
```

This architecture turns an increasing portion of alignment from an uninspectable semantic preference problem into a formal, testable, replayable constraint-construction problem while leaving genuinely normative and epistemic questions explicit rather than pretending computation has already answered them.
