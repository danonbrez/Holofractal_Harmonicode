# Pass 219 — Lane 5 Executable Capability Self-Model 1.43

Status: **ADDITIVE / EXACT / CANDIDATE-ONLY / REPOSITORY-DISCOVERED / SINGLE-CANONICAL-BOUNDARY PRESERVING**

## 1. Purpose

This cycle turns the previously declared Lane 5 API/capability visibility requirement into an executable self-model rather than a boolean assertion.

The model SHALL discover and reconcile two authoritative repository-visible callable surfaces at runtime:

1. the inherited Pass 147 public capability registry built from the real CLI/API parser topology; and
2. the complete transitive `HHS_EXACT_API` export surface reachable from `hhs_runtime/include/hhs_runtime_exact_abi.h`.

The result is one deterministic typed graph that Lane 5 can inspect before candidate planning. This cycle is intentionally a **bounded first closure** of the self-model. It proves complete coverage of those two source surfaces only; it does not falsely claim that every historical pass-local helper, test-only primitive, private implementation function, or unregistered service has already been promoted into the global capability graph.

## 2. Governing relation

```text
Pass147 public capability registry
        +
transitive exact-ABI export graph
        ↓
normalized typed capability nodes
        ↓
exact authority classification
        ↓
dependency / origin topology
        ↓
deterministic model root
        ↓
native C validation receipt
        ↓
Lane 5 candidate-safe self knowledge
```

The self-model is evidence and routing metadata. It SHALL NOT become a second execution authority.

## 3. Required source closure

### 3.1 Pass 147 public surface

The model MUST call the inherited `PublicSurfaceRegistry.build_catalog()` implementation and preserve for every record where present:

```text
capability_id
surface_type
argv or method/path
classification
capabilities
reversibility_class
mutating
capability_hash72
```

No synthetic replacement registry is authorized.

### 3.2 Native exact ABI surface

Starting from:

```text
hhs_runtime/include/hhs_runtime_exact_abi.h
```

the model MUST recursively follow repository-local quoted header includes under `hhs_runtime/include/`, detect every exported symbol declared with `HHS_EXACT_API`, preserve the declaring header, and deduplicate by exact export name.

The discovered native surface is therefore derived from the same aggregate header used to build the cumulative exact runtime.

## 4. Typed authority classes

Every self-model node SHALL retain one of the following self-model classifications:

```text
OBSERVATION                 = 1
GOVERNED_TRANSFORM          = 2
CANONICAL_ADMISSION_BOUNDARY= 3
RESTRICTED_OR_UNAVAILABLE   = 4
```

These are routing/self-model classes, not new runtime authority levels.

The inherited singleton canonical mutation seam MUST be identified exactly as:

```text
hhs_exact_pass219_vm81_environment_admit_signed
```

Exactly one discovered native node may carry `CANONICAL_ADMISSION_BOUNDARY` in this cycle.

Every other native export remains observation/governed-transform metadata from the self-model perspective. The self-model does not reinterpret internal implementation semantics merely from a symbol name.

Public operations that are explicitly restricted, platform-inapplicable, or observed failing remain visible but are classified `RESTRICTED_OR_UNAVAILABLE`; they are not silently erased from the topology.

## 5. Deterministic identity

The Python layer SHALL normalize nodes and dependency/origin edges with canonical JSON (`sort_keys=True`, compact separators) and derive deterministic SHA-256-backed 64-bit signatures for native validation.

The C membrane SHALL receive an ordered, unique signature vector and source/authority class vectors. It MUST reject:

```text
zero entry signatures
unordered or duplicate entry signatures
unknown source kinds
unknown authority classes
source-count mismatches
a missing or duplicate canonical admission boundary
boundary-signature mismatch
zero public/native/model/dependency roots
attempted canonical authority on the self-model itself
missing signed-environmental-admission requirement
```

The native receipt MUST reproduce the validated counts and exact model/boundary roots.

## 6. Source kinds

```text
PUBLIC_REGISTRY = 1
NATIVE_EXACT_ABI = 2
```

A later cycle MAY add independently typed source kinds for pass-local service registries, model services, graphics engines, deployment/runtime adapters, or reverse-pass-discovered capabilities. Such additions MUST be versioned and may not rewrite 1.43 evidence retroactively.

## 7. Self-model graph

The Python result SHALL include at minimum:

```text
schema
version
base/source roots
public capability count
native exact-ABI export count
restricted count
canonical boundary export
normalized nodes
origin/dependency edges
native validation receipt
authority descriptor
scope statement
```

Public dependency edges SHALL preserve declared boundary capability requirements. Native dependency edges SHALL preserve the declaring-header origin of each exact ABI export.

## 8. Deterministic replay

Two independent builds against byte-identical repository state MUST produce the same:

```text
public catalog root
native export root
dependency topology root
model root
native descriptor signature
native receipt signature
```

No wall clock, random value, process ID, host path, filesystem traversal order, Python object hash, or floating-point value may participate in these roots.

## 9. Authority boundary

The executable self-model has:

```text
global_capability_discovery = TRUE
public_registry_snapshot = TRUE
native_exact_abi_snapshot = TRUE
ordered_identity = TRUE
dependency_topology = TRUE
authority_classification = TRUE
deterministic_replay = TRUE
canonical_boundary_singleton = TRUE
candidate_only = TRUE
exact_integer_only = TRUE

canonical_vm81_mutation_authority = FALSE
canonical_hash72_authority = FALSE
canonical_hash216_authority = FALSE
canonical_persistence_authority = FALSE
pqc_key_authority = FALSE
receipt_clock_authority = FALSE
floating_point_canonical_authority = FALSE

requires_signed_environmental_vm81_admission = TRUE
```

The self-model may inform Lane 5 routing and reverse-pass planning. It may not itself execute a canonical mutation, mint Hash72/Hash216, persist canonical state, or bypass the environmental signed admission seam.

## 10. Relationship to 1.34 and 1.42

1.34 declared `api_registry_visible = TRUE`; 1.43 supplies the first repository-discovered executable evidence for that declaration.

1.42 supplies exact candidate route optimization and automatic superedge learning. 1.43 does not modify those route semantics. Instead, it supplies a typed capability topology that later cycles may translate into candidate route edges only after each edge's input/output and authority contract is proven.

No public capability is automatically promoted into a Hash216 superedge merely because it appears in the self-model.

## 11. Reverse-pass use

The self-model SHALL make missing integration visible instead of masking it. A capability may be present in one discovered source and absent from another. Such asymmetry is evidence for reverse-pass work, not an error by itself.

This supports the repair-forward loop:

```text
discover existing capability
-> classify authority and dependencies
-> identify unbound/underexposed surfaces
-> repair or expose through a typed candidate-safe adapter
-> validate
-> add the proven edge to Lane 5 composition topology
```

## 12. Required positive tests

Acceptance MUST prove at least:

```text
Pass147 real catalog contributes nonzero nodes
transitive exact ABI discovery contributes nonzero nodes
all public node identities are unique
all native export identities are unique
signed environmental VM81 admission is present exactly once
native receipt accepts the deterministic sorted signature vector
self-model itself has zero canonical mutation/mint/persistence authority
two builds from the same repository state replay to identical roots
```

## 13. Required negative tests

Acceptance MUST reject at least:

```text
zero entry signature
duplicate/unordered signature vector
wrong source count
unknown source kind
unknown authority class
zero model root
zero dependency root
missing canonical admission boundary
duplicate canonical admission boundary
boundary signature mismatch
self-model canonical mutation escalation
self-model canonical persistence escalation
missing signed-environmental admission requirement
```

## 14. Scope-completeness statement

A green 1.43 result means:

```text
Pass147 public registry coverage = COMPLETE for the repository state under test
cumulative exact ABI export coverage = COMPLETE for the repository state under test
repository-total historical capability coverage = NOT YET CLAIMED
```

The next reverse-pass cycles may extend this nucleus to pass-local capability services and other validated subsystems without changing the singleton canonical authority law.
