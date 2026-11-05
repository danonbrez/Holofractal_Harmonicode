# Pass 220 I069 — D-Wave Dual-Rail Post-Merge Verification

Date: 2026-10-03

## Authority base

I068 was merged to authoritative `main` at:

```text
87c5283730d27f94ddca694ab6fc01f982c7e165
```

I069 starts from that exact merge and treats the merged I068 runtime—not its
pre-merge branch—as the implementation under test.

## Objective

I069 performs an extensive dependency-scoped verification pass over the
D-Wave dual-rail candidate membrane and updates the quantum white-paper proofs
to match executable post-merge behavior.

The pass does not widen D-Wave simulator authority. The simulator remains an
external candidate source; canonical VM81 mutation and canonical Hash72/Hash216
commit authority remain downstream HHS responsibilities.

## Exhaustive ordered-state verification

The I068 symbol alphabet is:

```text
{0, 1, *}
```

with exact codes:

```text
0 -> 0
1 -> 1
* -> 2
```

For ordered control/target symbols:

```text
outcome = 3 * control_code + target_code
```

I069 exhaustively verifies all nine ordered pairs.

Exact partition:

```text
ordered pair states        = 9
erasure-bearing pair states = 5
clean pair states           = 4
```

Reversing an unequal pair changes its address. Equal pairs are fixed under
reversal. No control/target commutation is introduced.

## Full VM81 collapse-address product

The inherited I027 address rule is:

```text
vm81_cell = 9 * nucleus + outcome
```

For:

```text
nucleus in 0..8
outcome in 0..8
```

I069 verifies:

```text
9 * 9 = 81 distinct cells
minimum cell = 0
maximum cell = 80
covered set = {0,1,...,80}
```

Thus the I068 ordered nine-state surface can be supplied to every inherited
I027 nucleus address without collision or omission.

This is an address-space theorem. It does not grant the external D-Wave
simulator canonical VM81 mutation authority.

## Exact histogram stress testing

The dependency-scoped Python suite exhaustively enumerates every weak
composition of 1, 2, 3, and 4 shots across the nine ordered dual-rail states.

Count:

```text
C(9,8) + C(10,8) + C(11,8) + C(12,8)
= 9 + 45 + 165 + 495
= 714 exact histograms
```

For every distribution the test requires:

```text
transcribed nine-bin histogram == source composition exactly
clean_shots + erased_shots == total_shots
sum(histogram) == total_shots
```

No probability approximation or floating-point threshold participates.

## Additional adversarial coverage

The I069 suite also verifies:

- explicit register reorder handling;
- control/target reversal sensitivity;
- repeat-until execution semantics;
- multiple measurement rounds with common shot count;
- clean ideal-mode acceptance and erasure rejection in ideal mode;
- post-selected-only provenance rejection;
- explicit `get_counts(post_select=False)` use;
- typed MCED event validation and receipt sensitivity;
- configuration and result mutation sensitivity;
- deterministic exact replay receipts;
- documented versus unknown QPU classification without authority promotion;
- VM81 histogram equality, same-count mismatch, and sample-count mismatch;
- invalid VM81 receipt/outcome rejection;
- recursive floating-point rejection;
- malformed width/symbol/register/hash surfaces;
- stable candidate-only authority across every ordered pair class.

## Wolfram verification

Connected Wolfram Language verification returned:

```text
schema = HHS_PASS_220_I069_DWAVE_DUAL_RAIL_POSTMERGE_WOLFRAM_V1
status = PASS
checks = 9 / 9
failed = {}

nine-state outcome set = {0,1,2,3,4,5,6,7,8}
erasure-bearing pair count = 5
clean pair count = 4
VM81 cell minimum = 0
VM81 cell maximum = 80
VM81 unique cell count = 81
```

The proof uses exact integer and symbolic equality only.

## White-paper update scope

I069 updates:

```text
docs/whitepapers/HHS_QUANTUM_INFORMATION_THROUGHPUT_NORMALIZATION_V1.md
docs/whitepapers/HARMONICODE_QUANTUM_GEOMETRIC_SHARED_ROOT_CLOSURE_THEOREM.md
```

The first receives explicit normalization language for external simulator shots,
detected erasures, post-selection, and exact HHS candidate receipts.

The second receives the post-merge theorem extension:

```text
3 ordered control states
x 3 ordered target states
= 9 error-aware outcomes

9 nuclei
x 9 outcomes
= 81 exact VM81 collapse addresses
```

Neither update equates simulator evidence with physical-hardware authority or
canonical HHS state transition authority.

## Acceptance boundary

I069 succeeds only if:

```text
merged I068 implementation is the test base
+ all nine ordered states remain bijective
+ all 81 inherited I027 cell addresses remain bijective
+ erasure provenance remains observable
+ exact histogram conservation holds
+ adversarial negative gates fail closed
+ authority remains candidate-only
+ white-paper statements match executable behavior
```
