# Pass 077 — Compiler and Artifact-Lineage Pipeline

Pass 077 implements compilation as verified semantic projection plus lineage-preserving packaging.

> Compilation may change representation, layout, optimization, and deployment form. It may not change admitted program meaning, authority scope, or provenance identity.

## Core chain

```text
committed Harmonicode source
→ HHS_TYPED_IR_V1
→ HHS_EXECUTABLE_IR_V1
→ interpreter reference execution
→ HHS_COMPILATION_PLAN_V1
→ HHS_TARGET_IR_V1
→ HHS_PORTABLE_BYTECODE_V1
→ target execution
→ exact canonical semantic comparison
→ HHS_ARTIFACT_LINEAGE_CERTIFICATE_V1
→ deterministic evidence package
→ independent verifier
→ admitted artifact registry entry
```

The artifact is evidence-bearing, not self-authorizing. The external verifier uses package contents only and reexecutes both the reference executable IR and portable bytecode path.
