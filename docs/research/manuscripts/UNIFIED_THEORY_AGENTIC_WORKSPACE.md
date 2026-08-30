# Unified Theory Manuscript — Agentic Repository Workspace

## Repository identity

- Repository: `danonbrez/Holofractal_Harmonicode`
- Branch: `agent/unified-human-social-science-manuscript`
- Base main commit: `a1532df2cbcc02d30728055f3a1dfd55a0c1f387`
- Canonical manuscript: `docs/research/manuscripts/UNIFIED_THEORY_OF_HUMAN_SOCIAL_SCIENCE.md`
- Branch policy: manuscript development only; do not merge to `main` without explicit authorization.

## Purpose

This branch is a persistent agentic workspace for developing, expanding, auditing, and reconciling the manuscript against the native HHS codebase. Future manuscript work should use repository-visible state as the restart authority rather than relying on private thread state.

The repository is not passive storage. Native HHS indexing, content-generation proposal, exact execution preflight, and receipt-bearing surfaces may be used as development inputs when applicable.

## Native surfaces available from the inherited repository

### Pass 195 Kimi K3 content engine

Path:

`hhs_backend/runtime/hhs_kimi_k3_content_engine_v2.py`

Primary surface:

`KimiK3ContentEngine`

Relevant behavior observed at the branch base:

- bounded request normalization;
- constraint hashing through Hash72;
- strict provider-plan schema validation;
- provider invocation through proposal and receipt layers;
- provider result ingress;
- native handoff fields including `story_text`;
- provider remains proposal-only rather than receiving canonical mutation authority.

Use this surface for bounded generative proposals, alternative prose expansions, style-conditioned drafts, or multimodal reference analysis when a later task wires or invokes the runtime.

### Pass 191 repository hydration

Path:

`hhs_runtime/pass191/repository_hydration.py`

The inherited operation registry exposes:

- `P191.Hydrate.Repository`
- `P191.Hydrate.Genesis`
- `P191.Hydrate.Pass`
- `P191.Hydrate.Object`
- `P191.Hydrate.Function`
- `P191.Hydrate.Surface`
- `P191.Hydrate.ChangedSince`
- `P191.Hydrate.Resume`
- `P191.Hydrate.Verify`
- `P191.Hydrate.Replay`
- `P191.Hydrate.Report`
- `P191.Registry.Resolve`
- `P191.Symmetry.Validate`
- `P191.Reciprocal.Verify`
- `P191.Receipt.Get`

Use these repository-native surfaces to recover source-preserving historical context, dependency relations, function/surface metadata, exact symmetry witnesses, and receipt-bearing repository state before synthesizing manuscript claims that depend on HHS implementation details.

### Pass 219 execution composer

Path:

`hhs_runtime/hhs_pass219_execution_composer_registration_v1.py`

Primary surfaces:

- `pass219_execution_surface_declaration()`
- `pass219_execution_registration_manifest()`
- `preflight_pass219_execution_composer()`
- C ABI execution symbol `hhs_exact_pass219_rna_execution_compose`
- C ABI preparation symbol `hhs_exact_pass219_rna_execution_prepare_candidate`

Use the preflight surface to verify that a proposed execution path remains compatible with inherited exact execution, mandatory Genesis scaling, authenticated predecessor state, the dependency frontier, and the single inherited C VM81 mutation authority.

## Manuscript development loop

Each substantial manuscript iteration should follow:

```text
READ CURRENT BRANCH MANUSCRIPT
→ HYDRATE/SEARCH RELEVANT REPOSITORY STATE
→ CALL OR INSPECT NATIVE HHS SURFACES WHEN MATERIAL
→ GENERATE/COMPARE CANDIDATE TEXT
→ PRESERVE FORMAL / EMPIRICAL / INTERPRETIVE TYPE BOUNDARIES
→ EDIT CANONICAL MANUSCRIPT
→ DEPENDENCY-SCOPED VALIDATION
→ COMMIT
→ UPDATE RESTART RECORD
→ RETURN CONTROL TO USER
```

## Authority and evidence rules

1. Repository source and receipts are authoritative for claims about what HHS implements.
2. External content engines are proposal generators only.
3. The manuscript may contain system-internal axioms, but must distinguish them from external empirical claims whenever the manuscript itself makes that distinction.
4. Do not invent a repository API, pass surface, receipt, or validation result.
5. Preserve exact equations and formal identities when editing; do not silently normalize them.
6. Large revisions should be committed in restartable increments.
7. Queued external CI must not hold the interactive thread open once a repository-visible restartable checkpoint exists.

## Current manuscript state

The branch contains the Introduction, Volume I, and Volume II through Chapter 32, including:

- Genesis identity kernel;
- Root Metadata and ERS-native phase transport;
- HHS execution-layer mapping;
- Reich/Jung/Adler/Taoist synthesis;
- coupled-agent relational model;
- typed relational ledger;
- trust calibration;
- disclosure relevance;
- partner-specific dynamic entry tensor (mathbf{M}_{i\rightarrow j}(t));
- tensor-driven Asymmetry Index;
- adaptive persona switching;
- pair-bond multivariable model;
- boundary membrane and repair protocol.

## Next intended development frontier

Primary next prose frontier:

`VOLUME IV — MYTHOPOETICS AS EMPIRICAL RECORD`

Before expanding it, inspect relevant HHS compression, checksum/ECC, provenance, corpus/style, narrative/content, hydration-index, and receipt surfaces so symbolic-memory correspondences are derived from repository state rather than memory alone.

## External research policy

Web and literature research may be used as a Class-B evidentiary layer for anthropology, psychology, history, network science, biology, and comparative data. External sources may support, falsify, parameterize, or contextualize a manuscript proposition, but they do not become canonical HHS authority merely by publication or consensus. Any claim that an external result changes a native HHS proposition requires an explicit repository-grounded derivation showing the formal relationship. Conflicts remain visible rather than being silently normalized.

A later implementation may add a dedicated manuscript orchestration adapter that composes Pass 191 hydration, Pass 195 proposal generation, and Pass 219 exact preflight. That adapter should be added only when its execution contract and tests are specified.
