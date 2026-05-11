# HHS Import Normalization Policy
## Canonical Runtime Import Governance Specification

Version: v1  
Status: ACTIVE  
Repository: Holofractal_Harmonicode  
Purpose: Canonical import governance and authority-safe runtime routing policy.

---

# PURPOSE

This document defines:

- canonical runtime import topology,
- authority-safe import routing,
- compatibility shim import rules,
- prohibited import patterns,
- bootstrap import ordering,
- replay-safe migration imports,
- namespace governance,
- future cleanup rules.

This document exists to prevent:

- authority drift,
- replay ambiguity,
- duplicate runtime routing,
- compatibility sprawl,
- topology fragmentation,
- bootstrap nondeterminism.

---

# CORE PRINCIPLE

The repository is now a:

```text
deterministic replay-governed runtime operating environment
```

At this scale:

```text
imports
=
runtime topology
```

Import routing directly affects:

- authority ownership,
- replay continuity,
- bootstrap determinism,
- transport routing,
- workspace restoration,
- runtime execution surfaces.

---

# IMPORT GOVERNANCE RULE

Imports MUST route through canonical runtime authorities.

Imports may NEVER create:

- parallel runtime authorities,
- duplicate execution surfaces,
- replay divergence,
- topology ambiguity.

---

# CANONICAL IMPORT SURFACES

| Import Surface | Status |
|---|---|
| Package Imports | CANONICAL |
| Root Imports | COMPATIBILITY ONLY |
| cwd-relative Imports | DEPRECATED |
| sys.path Mutation | COMPATIBILITY ONLY |
| Duplicate Authority Imports | PROHIBITED |
| Parallel Runtime Imports | PROHIBITED |

---

# CANONICAL IMPORT PATHS

## Runtime Substrate

```python
from hhs_runtime...
```

---

## Backend Runtime Bridge

```python
from hhs_backend...
```

---

## Runtime-Native Objects

```python
from hhs_python.runtime...
```

---

## Runtime Workspace Topology

```python
from hhs_gui.runtime...
```

---

# CANONICAL AUTHORITY IMPORTS

| Runtime Responsibility | Canonical Import Surface |
|---|---|
| Runtime Execution | `hhs_runtime.core_sandbox...` |
| Replay Verification | `hhs_receipt_replay_verifier_v1` |
| Runtime Registry | `hhs_python.runtime.runtime_object_registry` |
| Runtime Transport | `hhs_backend.runtime.runtime_transport_protocol` |
| Runtime Workspace | `hhs_gui.runtime.runtime_workspace_objects` |
| Runtime State | `hhs_python.runtime.hhs_runtime_state` |
| Backend Bootstrap | `hhs_backend.server` |

---

# PROHIBITED IMPORT PATTERNS

The following patterns are prohibited unless explicitly compatibility-scoped.

---

## cwd-relative Runtime Imports

Avoid:

```python
import runtime_layer_v1
import ../runtime_layer
```

Reason:

```text
cwd-relative imports break deterministic runtime topology
```

---

## Manual sys.path Mutation

Avoid:

```python
sys.path.append(...)
sys.path.insert(...)
```

unless explicitly compatibility-only.

Reason:

```text
manual path mutation bypasses authority normalization
```

---

## Duplicate Authority Imports

Prohibited:

```python
from old_runtime import ...
from new_runtime import ...
```

simultaneously for identical authority domains.

Reason:

```text
duplicate authorities create replay ambiguity
```

---

## Parallel Runtime Imports

Prohibited:

```python
multiple runtime controllers
multiple replay engines
multiple transport authorities
```

inside one execution chain.

Reason:

```text
parallel runtime imports fracture deterministic topology
```

---

# COMPATIBILITY SHIM IMPORT RULES

The repository contains migration-era compatibility surfaces.

These are:

```text
topology-preserving migration bridges
```

NOT canonical runtime authorities.

---

# SHIM IMPORT TYPES

| Shim Type | Import Scope |
|---|---|
| Compatibility Shim | explicit migration bridge |
| Replay Shim | replay continuity only |
| Bootstrap Shim | temporary initialization bridge |
| Historical Shim | historical continuity only |

---

# SHIM IMPORT RULE

Compatibility imports MUST terminate into canonical runtime authorities.

Example:

```text
compatibility shim
→ canonical package authority
```

NOT:

```text
compatibility shim
→ another compatibility shim
```

---

# AUTHORITY RESOLUTION RULE

Imports may NEVER bypass canonical authority routing.

Examples:

| Layer | Canonical Authority |
|---|---|
| Transport | transport protocol |
| Replay | replay verifier |
| Registry | runtime object registry |
| Workspace | workspace objects |
| Persistence | database integration |
| Backend | backend bootstrap |

---

# SINGLE AUTHORITY RULE

Exactly ONE canonical authority per runtime responsibility.

Allowed:

```text
canonical authority
+ compatibility bridge
```

Prohibited:

```text
multiple active authorities
```

---

# BOOTSTRAP IMPORT ORDERING

Canonical runtime bootstrap import ordering:

```text
environment normalization
→ kernel resolution
→ runtime authority imports
→ replay imports
→ registry imports
→ transport imports
→ graph imports
→ persistence imports
→ backend imports
→ workspace imports
```

Import ordering is part of runtime determinism.

---

# REPLAY PRESERVATION IMPORT RULES

Migration imports MUST preserve:

- historical replay reconstruction,
- receipt continuity,
- registry restoration,
- workspace restoration,
- graph replay continuity.

---

# REPLAY SAFETY RULE

Import normalization may NEVER invalidate:

- historical replay traces,
- receipt lineage,
- replay certification,
- compatibility replay restoration.

---

# TEST HARNESS IMPORT POLICY

Critical runtime validation surfaces:

| Validation Surface | Policy |
|---|---|
| smoke tests | canonical imports only |
| regression suite | canonical imports only |
| stress suite | canonical imports only |
| bundle runner | canonical imports only |

---

# TEST IMPORT RULE

Test harnesses may NOT:

- bypass runtime authority,
- bypass replay authority,
- bypass transport authority,
- import duplicate runtime surfaces.

---

# ROOT FILE IMPORT POLICY

Root-level files may exist for:

- migration continuity,
- replay preservation,
- CI compatibility,
- historical execution support.

Root files are NOT automatically canonical authorities.

---

# ROOT IMPORT RULE

Allowed:

```text
root wrapper
→ canonical authority
```

Avoid:

```text
root wrapper
→ root wrapper
```

---

# NAMESPACE GOVERNANCE

## Runtime Substrate

```text
hhs_runtime
```

Scope:

- runtime execution,
- kernel routing,
- replay substrate.

---

## Backend Runtime Bridge

```text
hhs_backend
```

Scope:

- API bridge,
- websocket bridge,
- runtime transport exposure.

---

## Runtime-Native Objects

```text
hhs_python.runtime
```

Scope:

- runtime objects,
- registry,
- runtime state,
- replay-aware entities.

---

## GUI Runtime Topology

```text
hhs_gui.runtime
```

Scope:

- workspace topology,
- panel topology,
- viewport topology,
- multimodal surfaces.

---

# IMPORT NORMALIZATION PHASES

| Phase | Meaning |
|---|---|
| Legacy | root imports dominant |
| Migration | mixed topology |
| Consolidation | canonical package imports dominant |
| Runtime OS | fully normalized runtime topology |

---

# CURRENT PHASE

Current repository state:

```text
Consolidation / Runtime OS Transition
```

Meaning:

- canonical package authorities exist,
- compatibility shims remain active,
- root wrappers remain transitional,
- import normalization remains ongoing.

---

# ACTIVE ENTROPY SOURCES

Remaining import topology risks:

| Risk | Status |
|---|---|
| duplicate imports | active |
| root-wrapper imports | transitional |
| sys.path mutation | partial |
| compatibility sprawl | partial |
| stale import assumptions | active |

---

# FUTURE CLEANUP RULES

Compatibility imports become removable ONLY when:

- replay continuity preserved,
- canonical authorities stabilized,
- certification topology passes,
- migration ledger updated,
- bootstrap normalization complete.

---

# FUTURE NORMALIZATION TARGETS

Remaining likely normalization targets:

- root runtime imports,
- root replay imports,
- manual path mutation,
- duplicate transport imports,
- duplicate registry imports,
- legacy bootstrap imports.

---

# IMPORT AUDIT REQUIREMENT

Before adding new runtime infrastructure:

1. inspect canonical authority map,
2. inspect migration ledger,
3. inspect import topology,
4. verify canonical authority absence,
5. preserve replay continuity,
6. normalize imports first.

---

# FINAL RULE

When uncertain:

DO NOT create new runtime imports first.

Instead:

1. locate canonical authority,
2. normalize routing,
3. preserve replay continuity,
4. preserve bootstrap determinism,
5. extend existing runtime topology.

Import normalization is now a runtime invariant.