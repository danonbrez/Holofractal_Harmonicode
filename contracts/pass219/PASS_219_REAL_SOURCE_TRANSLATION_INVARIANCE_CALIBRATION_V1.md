# Pass 219 — Real-Source Translation-Invariance Calibration v1

## 1. Purpose

This contract adds a deterministic calibration layer above the merged Pass 219 translation-invariant multimodal ingress.

The calibration consumes **frozen empirical observations from immutable, permissively licensed upstream revisions** and measures whether translation/cross-modal candidate correspondence closes at the intended semantic scope without collapsing source identity or promoting unsupported detail.

It does not modify canonical admission logic.

## 2. Inherited authority

The following remain inherited and unchanged:

```text
raw source bytes / SHA256 identity        -> Pass 165
semantic projection                       -> candidate evidence only
translation/cross-modal family grouping   -> Pass 219 candidate layer
I29 or equivalent validation              -> required before canonical Hash216 routing
Lane 5                                    -> candidate search/optimization only
VM81                                      -> singleton canonical mutation/admission authority
```

Calibration SHALL NOT mint truth, VM81 authority, canonical Hash72, canonical Hash216, action authority, or permanent prune authority.

## 3. Real-source evidence rule

Every calibration observation SHALL carry:

- provider;
- repository;
- immutable hexadecimal revision;
- evidence path;
- normalized open-source license;
- metric family;
- semantic scope;
- subject/candidate identities;
- exact rational capture of the displayed upstream score;
- expected positive/negative classification;
- semantic family;
- optional model repository and immutable model revision.

Mutable references such as `main`, `latest`, branch aliases, or unpinned model identifiers are insufficient for calibration admission.

## 4. License rule

Production calibration evidence SHALL use the same permissive-license allowlist as the translation-invariant ingress layer.

Non-commercial licenses are not equivalent to open-source production admission and SHALL fail closed.

## 5. Semantic-scope separation

Translation invariance SHALL be evaluated independently at:

```text
FAMILY
SCENE_DETAIL
IDENTITY
```

A correspondence may close at `FAMILY` while remaining unresolved or false at `SCENE_DETAIL` or `IDENTITY`.

Therefore:

```text
FamilyMatch(x,y) = 1
-/->
SceneDetailMatch(x,y) = 1

FamilyMatch(x,y) = 1
-/->
IdentityMatch(x,y) = 1
```

This prevents coarse semantic similarity from laundering unsupported modifiers or identity claims.

## 6. Exact score handling

Displayed upstream decimal/percentage scores SHALL be serialized as exact rational observations.

They are empirical diagnostics, not theorem proof:

```text
ObservedScore = p/q
```

No binary floating-point value is authoritative in calibration output.

## 7. Threshold calibration

For a metric family and semantic scope, define exact counts:

```text
TP, FP, TN, FN in N
```

and:

```text
precision = TP / (TP + FP)
recall    = TP / (TP + FN)
FPR       = FP / (FP + TN)
```

When both positive and negative examples exist, the sample-only separability interval is:

```text
max(negative_scores) < threshold <= min(positive_scores)
```

when the strict inequality holds.

The interval is diagnostic only. A calibration result SHALL NOT silently rewrite the production ingress threshold.

## 8. Frozen upstream evidence used by v1

The v1 manifest binds to:

```text
GitHub repository:
  huggingface/sentence-transformers
revision:
  2236e4f6ec18191ef73b91dbd17f60fbbfd97bc6
license:
  Apache-2.0
```

The text calibration uses the repository README's recorded similarity matrix for a weather/sunny paraphrase and stadium negative controls.

The cross-modal calibration uses the pinned multilingual image-classification notebook observations for:

- Eiffel Tower day -> Russian `Paris` family correspondence;
- Eiffel Tower night -> Chinese `Paris at night` scene-detail correspondence;
- Eiffel Tower day -> Chinese `Paris at night` negative scene-detail control;
- dogs in snow -> German `dog` family correspondence;
- dog image -> Spanish `cat` negative control;
- cat image -> Spanish `cat` family correspondence;
- cat image -> German `dog` negative control.

The multilingual CLIP reference is revision-pinned in the manifest.

## 9. Current-threshold interpretation

The production ingress threshold remains `3/4`.

The calibration is allowed to show that a real positive observation falls below that threshold. Such a result is a **false-negative diagnostic**, not authorization to lower the threshold.

Likewise, a high-confidence family correspondence cannot override an explicit modifier conflict.

## 10. Warm-hydration bridge

Only `FAMILY` observations that are expected positive and meet the current diagnostic threshold may be emitted as warm-hydration **candidates**.

Every such candidate SHALL carry:

```text
candidate_only = true
requires_i29_or_equivalent_validation = true
canonical_hash216 = null
```

Calibration cannot synthesize the 216-symbol canonical Hash216 carrier.

## 11. Network boundary

The canonical calibration runtime performs no network fetching.

Network/model execution belongs to a later external acquisition/replay surface. That surface must freeze retrieved source/model revisions and then feed immutable evidence into this deterministic calibration kernel.

## 12. Required negative controls

Conformance requires tests proving at least:

1. mutable revision rejection;
2. non-permissive/non-commercial license rejection;
3. deterministic calibration receipt;
4. false-match controls remain separated;
5. semantic-family closure does not promote scene-detail claims;
6. threshold overrides remain diagnostic only;
7. no canonical authority is minted; and
8. warm-hydration candidates still require I29/equivalent validation.

## 13. Closure

This layer closes when the exact frozen manifest compiles, all bounded tests pass, and the report preserves source/model provenance, exact rational metrics, semantic-scope separation, and zero canonical authority drift.
