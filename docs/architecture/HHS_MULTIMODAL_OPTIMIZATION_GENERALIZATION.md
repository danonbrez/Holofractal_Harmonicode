# HHS multimodal optimization generalization invariant

## Universal rule

All successful optimizations are multimodal by default.

A performance improvement first demonstrated in one modality, object, benchmark, workload, or localized scenario is a candidate canonical improvement for every compatible modality and object that can safely realize the same benefit. Local-only is never the default classification.

```text
SUCCESSFUL_OPTIMIZATION
  -> DISCOVER_COMPATIBLE_TARGETS
  -> VALIDATE_UNRESOLVED_TARGETS
  -> GENERALIZE_SAFE_BENEFICIAL_TARGETS
```

## Compatibility substrate

Compatibility is derived from canonical metadata and object semantics, not from modality labels alone. The current primary descriptor substrate is `HHS_PASS_187_OBJECT_DESCRIPTOR_V1`.

Relevant fields include:

- object_class
- modality_set
- state_schema
- input and output port types
- operations
- dependencies
- compatible egress targets
- runtime_authority

Two different modalities may therefore be compatible when they share the same descriptor format and optimization-relevant semantics.

## Mandatory classifications

```text
incompatible target
  -> NOT_APPLICABLE

compatible + not yet validated
  -> VALIDATION_REQUIRED

compatible + validated safe + validated beneficial
  -> GENERALIZE_REQUIRED

compatible + explicit bounded exception + evidence
  -> LOCAL_EXCEPTION_ALLOWED
```

A compatible target never becomes local-only merely because the original optimization was discovered in another modality.

## Bounded exceptions

Locality is allowed only when global application is unsafe, demonstrably non-beneficial, context-specific, metadata/object incompatible, interface-only, ingress-only, egress-only, or an explicitly contracted one-off.

Unsafe and no-benefit exceptions require executed validation. Context-specific and one-off exceptions require an explicit bounded contract. Every exception requires repository-visible evidence.

Absence of testing produces `VALIDATION_REQUIRED`, not an exception.

## Automatic recognition

Pass 219 tooling must identify optimization-bearing code changes, require a generalization manifest, discover compatible descriptor targets, and fail CI when a compatible target is silently omitted.

The system does not require a new user instruction for each compatible modality. Generalization follows automatically from the canonical invariant once compatibility, safety, and benefit are established.

## Interaction with global canonical defaults

This invariant refines `HHS-P219-GLOBAL-CANONICAL-DEFAULTS`.

A canonical optimization is not only inherited across pass versions. It is also propagated horizontally across compatible modalities and objects. Compatible older objects that have not been evaluated are repair-forward validation debt; compatible objects that reproduce the improvement are repair-forward implementation debt until the optimization is generalized.

## Governing rule

```text
ALL OPTIMIZATIONS ARE MULTIMODAL BY DEFAULT.
LOCALITY IS AN EVIDENCED BOUNDED EXCEPTION.
COMPATIBLE UNTESTED TARGETS REQUIRE VALIDATION.
COMPATIBLE SAFE BENEFICIAL TARGETS REQUIRE GENERALIZATION.
NO NEW USER DIRECTIVE IS REQUIRED FOR EACH COMPATIBLE MODALITY.
```
