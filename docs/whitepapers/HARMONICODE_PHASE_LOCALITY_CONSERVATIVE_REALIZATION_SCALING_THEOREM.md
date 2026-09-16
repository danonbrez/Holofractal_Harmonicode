# HARMONICODE Phase-Locality Conservative Realization and Scaling Theorem

**Document class:** formal-system white paper  
**Theorem status:** canonical invariant + derived restriction theorem + exact finite-work theorem + empirical boundary  
**Scope:** all HHS phase-quantized candidate, lookup, cache, hydration, and accelerator realization paths possessing exact pre-expansion selectors  
**Depends on:** the Noncommutative Tensor Hydration Foundations Theorem and the Full Hydration Bijection and Reconstruction Theorem

## Abstract

The canonical Pass 219B Universal Phase-Locality Invariant requires exact local realization whenever an exact selector is available before expansion and the selected phase volume is smaller than the potential phase volume. This paper proves the mathematical content beneath that invariant.

For phase dimensions `l=1..d`, let:

```text
q_l = potential cardinality of dimension l
s_l = exactly selected cardinality of dimension l
1 <= s_l <= q_l.
```

Define:

```text
Q = product(q_l)
M = product(s_l).
```

The first theorem proves the exact combinatorial work ratio `Q/M` for uniform per-combination base work. The second theorem proves **conservative local realization**: if the local path preserves original dense identity and returns exactly the same selected result as the dense reference, then replacing dense enumeration by exact restriction does not change any selected result. The third theorem proves that the finite full manifold is exactly recoverable as the union of all such local restrictions.

The paper then separates this exact mathematics from hardware performance. A runtime model such as `T(M)=a+bM` is empirical. It may be strongly supported by measurements, but it is not used as a premise of the canonical invariant.

---

## 1. Canonical invariant

The repository canonical contract states:

```text
Q = product(q_l)
M = product(s_l)
1 <= s_l <= q_l.
```

When an exact selector exists before expansion and `M<Q`:

```text
LOCAL realization is mandatory.
```

Dense realization is forbidden except for an explicit audit/ablation route.

The local route additionally requires:

```text
original dense identity preserved
exact selected-result equality preserved
zero independent VM81 mutation authority
zero independent persistence authority
zero independent Hash72 authority.
```

The requirement to choose the local route is a **canonical policy invariant**. The theorems below establish why that route is mathematically conservative when its proof obligations hold.

## 2. Product phase domain

### Definition 2.1 — potential domain

For each dimension `l`, let `D_l` be a finite typed phase domain with:

```text
|D_l| = q_l.
```

Define the full potential domain:

```text
D = D_1 × D_2 × ... × D_d.
```

### Definition 2.2 — selected domain

Let:

```text
S_l subseteq D_l
|S_l| = s_l.
```

Define:

```text
S = S_1 × S_2 × ... × S_d.
```

### Lemma 2.3 — potential volume

```text
|D| = Q = product(q_l).
```

#### Proof

Repeated application of finite Cartesian-product cardinality. QED.

### Lemma 2.4 — selected volume

```text
|S| = M = product(s_l).
```

#### Proof

Identical finite-product reasoning on the selected subsets. QED.

### Corollary 2.5

Because `S_l subseteq D_l` for every `l`:

```text
M <= Q.
```

Equality holds iff all dimensions are fully selected.

## 3. Exact work-reduction theorem

### Definition 3.1 — uniform base work

Let one realized phase combination require exactly `B` logical base units under the chosen reference accounting, where:

```text
B > 0.
```

Examples include a fixed number of candidate branches, lane dispatches, descriptor constructions, or exact comparison units per combination.

### Lemma 3.2 — dense work

Full dense realization requires:

```text
W_dense = B*Q.
```

### Lemma 3.3 — selected work

Exact local realization requires:

```text
W_local = B*M.
```

### Theorem 3.4 — exact deterministic reduction

The exact work ratio is:

```text
R_work = W_dense / W_local
       = (B*Q)/(B*M)
       = Q/M.
```

#### Proof

Since `B>0`, cancel the common base factor from numerator and denominator. QED.

### Corollary 3.5 — repeated 81-way phase quantization

If:

```text
q_l = 81
```

for every layer `l=1..d`, then:

```text
Q = 81^d.
```

If exactly one origin is selected in every layer:

```text
s_l = 1
M = 1
R_work = 81^d.
```

This is an exact combinatorial work-count theorem. It is not a claim of `81^d` wall-clock acceleration.

### Corollary 3.6 — bounded neighborhoods

If each repeated 81-way layer selects exactly `r` origins:

```text
R_work = (81/r)^d
```

whenever `r` divides the exact work accounting as expressed by the rational ratio `81^d/r^d`.

No floating-point approximation is needed to represent the ratio.

## 4. Dense reference and local restriction

### Definition 4.1 — dense reference function

Let the exact reference computation be a deterministic function:

```text
F : D -> Y
```

where `Y` is a typed exact result space.

For every potential original identity `i in D`, `F(i)` is the exact reference result associated with that identity.

### Definition 4.2 — local realization function

Let:

```text
L : S -> Y
```

be an optimized local realization defined only on the selected set.

### Definition 4.3 — stable identity embedding

Let:

```text
j : S -> D
```

be the original dense identity map. In the canonical case, `S` is literally a subset of `D`, so `j` is the inclusion map.

Stable identity requires that local ordinal position is not substituted for `j(s)`.

## 5. Conservative realization theorem

### Axiom/verification condition V-EQ

For every selected identity `s in S`:

```text
L(s) =_Y F(j(s)).
```

This is the exact selected-result equality obligation.

### Axiom/verification condition V-ID

For every `s in S`, the local result retains the same original dense identity `j(s)` used by the reference namespace.

### Theorem 5.1 — conservative exact restriction

Under `V-EQ` and `V-ID`, local realization is exactly the restriction of the dense reference to `S`:

```text
L = F|_S
```

under the identity embedding `j`.

#### Proof

Function equality on domain `S` requires equality at every element of `S`. `V-EQ` states precisely that for each selected element, while `V-ID` ensures that the element compared is the same original dense identity rather than a rebased local ordinal. Therefore `L` and the restriction of `F` agree pointwise on the full local domain. QED.

### Corollary 5.2 — selected semantic equivalence

Any downstream pure computation `G` whose inputs are exactly the selected results and their stable identities receives the same input sequence/set from `L` as from dense reference restriction.

Thus:

```text
G(L(S)) = G(F|_S(S))
```

provided `G` is invoked with the same ordering/identity convention.

### Corollary 5.3 — what is not proven

Theorem 5.1 does not assert values for `D\S`. It proves exact equality on the selected domain only.

Therefore a selector is valid only when the requested computation genuinely requires `S` and not an unselected dependency.

## 6. Selector sufficiency and dependency closure

### Definition 6.1 — dependency-closed selector

For requested computation `C`, call selector `S` dependency-closed iff every phase identity required to compute or validate `C` belongs to `S`, or is supplied by an authenticated inherited predecessor/reference that the active contract permits to reuse.

### Theorem 6.2 — safe omission criterion

If `S` is dependency-closed and Theorem 5.1 holds, then omitting `D\S` from materialization does not change the exact result of `C`.

#### Proof

By dependency closure, `C` does not require a newly realized value from `D\S`. Every newly required value lies in `S`, where local and dense reference results agree by Theorem 5.1. Reused authenticated predecessors are unchanged by hypothesis. Therefore all inputs affecting `C` are equal under both execution paths, so deterministic `C` yields the same result. QED.

### Corollary 6.3

An exact pre-expansion phase selector is not merely a performance hint. It is a proof object describing which portion of the full domain is dependency-relevant for the requested local realization.

## 7. Full reconstruction from local restrictions

### Definition 7.1 — selector partition

Let `{S_alpha}` be a family of pairwise-disjoint exact selector sets satisfying:

```text
union_alpha S_alpha = D.
```

### Theorem 7.2 — dense function reconstruction

If each local realization `L_alpha` satisfies:

```text
L_alpha = F|_{S_alpha},
```

then:

```text
F = union_alpha L_alpha
```

as a function over `D`.

#### Proof

Every `i in D` belongs to exactly one selector set because the family is a partition. On that set, `L_alpha(i)=F(i)`. Therefore the union function is defined for every `i in D` and equals `F` everywhere. QED.

### Corollary 7.3 — phase-slice reconstruction

For the one-layer 81-origin hydration manifold, the 81 fixed-origin slices form such a partition. Therefore exhaustive union of all exact phase-local slices reconstructs the full phase-projected hydration function exactly.

## 8. Mixed-radix stable identity theorem

The full-hydration white paper establishes a bijective mixed-radix index `I` over the typed hydration coordinate tuple.

### Theorem 8.1

Let local selection return coordinates `h_1,...,h_n` from the full phase domain. Preserving `I(h_k)` for every selected coordinate preserves the same original dense coordinate identity namespace because `I` is injective.

#### Proof

If two selected coordinates had the same preserved `I`, injectivity would imply they were the same coordinate tuple. Therefore no selected coordinate can be aliased to a different full-domain identity under the preserved index. QED.

### Corollary 8.2

A local implementation must not replace `I(h)` with local enumeration `0..n-1` when downstream identity semantics require the original dense namespace.

## 9. Phase factorization theorem

### Theorem 9.1 — exact work count depends on product volume

Under the uniform-base-work model of Section 3, two selector factorizations:

```text
(s_1,...,s_d)
(r_1,...,r_d)
```

with:

```text
product(s_l) = product(r_l) = M
```

have identical logical base work:

```text
B*M.
```

#### Proof

By Lemma 3.3 local work depends only on `B` and `M`. QED.

### Important boundary

Theorem 9.1 is a logical work-count theorem. It does **not** prove identical wall-clock hardware time for different factorizations, because memory access, dispatch topology, workgroup layout, cache behavior, and fixed overhead may depend on factorization.

Near-equality of hardware time across factorizations is therefore empirical evidence supporting a hardware implementation, not a premise of this theorem.

## 10. Hydration specialization

For the canonical one-layer Pass 219B phase extension:

```text
q_1 = 81.
```

Selecting `O` exact origins gives:

```text
Q = 81
M = O
R_work = 81/O.
```

For one 5,184 parent surface:

```text
B = 5,184
W_dense = 5,184*81 = 419,904
W_local = 5,184*O.
```

For the entire inherited parent manifold:

```text
B = 51,648,192
W_dense = 51,648,192*81 = 4,183,503,552
W_local = 51,648,192*O
```

if the entire parent manifold is otherwise required. More commonly, both parent and phase selectors reduce `B` and `M` simultaneously.

## 11. Nested phase locality

### Definition 11.1 — depth-d phase tuple

For repeated exact phase dimensions:

```text
p = (p_1,...,p_d)
```

with `p_l in D_l`.

### Theorem 11.2 — multiplicative potential/selective law

The exact potential and selected phase volumes are:

```text
Q_d = product(q_l)
M_d = product(s_l).
```

The deterministic base-work reduction is:

```text
R_d = Q_d/M_d.
```

This is Theorem 3.4 applied at arbitrary finite depth.

### Corollary 11.3 — repeated VM81 origin dimensions

For `q_l=81`:

```text
Q_d = 81^d.
```

Single-origin selection at every layer gives:

```text
M_d=1
R_d=81^d.
```

The theorem remains conditional on exact dependency-closed selectors being available before the avoided expansion.

## 12. Canonical authority theorem

### Theorem 12.1 — local equality does not grant mutation authority

Suppose local realization satisfies all mathematical equality and identity conditions. It still does not thereby acquire VM81 canonical mutation, Hash72 emission, or persistence authority.

#### Proof

Authority is a separate typed capability in the inherited HHS execution model. Equality of candidate values establishes result equivalence, not possession of an admission/commit capability. The canonical contract explicitly sets these phase-local authority fields to zero. Therefore authority cannot be inferred from correctness. QED.

### Corollary 12.2

The correct execution boundary remains:

```text
exact selector
→ phase-local candidate/retrieval/hydration
→ exact selected equality / identity proof
→ inherited VM81 admission
→ canonical Hash72 receipt
→ inherited Hash216 lineage.
```

## 13. Empirical timing boundary

### Definition 13.1 — observational affine model

A device/kernel may empirically fit:

```text
T(M) = a + b*M.
```

When `b>0`, define the overhead-equivalent selected volume:

```text
c = a/b.
```

Then the corresponding empirical speedup model is:

```text
S_emp(M) = (Q+c)/(M+c).
```

### Theorem 13.2 — algebraic derivation of model ratio

If the empirical affine model holds for both dense `Q` and selected `M`, then the ratio above follows by substitution:

```text
T(Q)/T(M)
= (a+bQ)/(a+bM)
= (Q+a/b)/(M+a/b).
```

QED.

### Boundary 13.3

The statement that a particular device actually follows the affine model is an `EMPIRICAL_CLAIM`, not a derived theorem.

The Samsung Galaxy Z Fold7 measurements preserved in the repository are evidence for the tested WebGPU kernel. They do not convert `a`, `b`, or `c` into universal HHS constants.

## 14. Main Phase-Locality Theorem

### Theorem 14.1 — exact conservative local realization

Assume:

1. a finite typed potential phase domain `D` with volume `Q`;
2. an exact pre-expansion selector producing dependency-closed `S subset D` with volume `M<Q`;
3. a deterministic exact dense reference `F`;
4. a local realization `L` preserving original dense identity;
5. exact selected equality `L=F|_S`;
6. inherited canonical authority remains outside `L`.

Then:

```text
(a) local logical base work is reduced exactly from BQ to BM;
(b) exact deterministic work reduction is Q/M;
(c) every selected result is identical to the dense reference result for the same original identity;
(d) any deterministic downstream computation whose dependency frontier is closed by S receives the same exact required inputs;
(e) the omitted complement D\S need not be materialized for that computation;
(f) exhaustive union of a partition of exact local realizations reconstructs the dense reference over D;
(g) local correctness does not transfer canonical mutation or receipt authority.
```

#### Proof

(a)–(b): Theorem 3.4.  
(c): Theorem 5.1.  
(d)–(e): Theorem 6.2.  
(f): Theorem 7.2.  
(g): Theorem 12.1. QED.

## 15. Falsification conditions

The theorem or a claimed implementation instance fails if any of the following occurs:

```text
SELECTOR_NOT_EXACT
SELECTOR_DISCOVERED_ONLY_AFTER_FULL_EXPANSION
SELECTOR_NOT_DEPENDENCY_CLOSED
SELECTED_VOLUME_OUT_OF_RANGE
POTENTIAL_VOLUME_OVERFLOW_UNHANDLED
ORIGINAL_DENSE_IDENTITY_REBASED
EXACT_SELECTED_EQUALITY_FAILURE
LOCAL_RESULT_DEPENDS_ON_OMITTED_UNVERIFIED_STATE
DENSE_REALIZATION_USED_WITH_EXACT_SELECTOR_WITHOUT_AUDIT_AUTHORIZATION
LOCAL_PATH_GAINS_CANONICAL_AUTHORITY
WORK_REDUCTION_MISSTATED_AS_WALLCLOCK_THEOREM
EMPIRICAL_MODEL_MISSTATED_AS_UNIVERSAL_CONSTANT
```

## 16. Conclusion

The canonical phase-locality invariant has a precise mathematical basis:

```text
full finite phase domain D
        ↓ exact selector
selected dependency-closed restriction S
        ↓
L = F|_S with original identity preserved
        ↓
exact work BQ -> BM
        ↓
R_work = Q/M
        ↓
inherited canonical VM81 admission remains unchanged.
```

The result is stronger than a cache optimization and narrower than a claim of universal hardware acceleration. It is an exact conservative-restriction theorem over a finite typed hydration manifold. Whenever exact pre-expansion selectors and equality witnesses exist, HHS can compute the required realized phase volume rather than the full potential phase volume without changing selected semantics.
