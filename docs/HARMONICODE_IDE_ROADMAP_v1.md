# HARMONICODE IDE Roadmap v1

## Purpose

Define the staged path from the current HHS runtime into a full HARMONICODE programming language platform:

- interpreter
- compiler
- IDE
- AI assistant
- scientific calculator
- DAW / harmonic audio workstation
- Python / C / assembly compatibility
- receipt-verified execution
- recursive global closure benchmarking

The core rule is unchanged:

```text
Input -> Symbolic/Macro Expansion -> State Patch -> Kernel Audit -> Receipt Commit -> Replay Verification
```

No language feature, IDE feature, AI feature, calculator feature, or DAW feature may bypass the kernel authority path.

---

## Architectural Invariants

Every layer must preserve:

```text
Δe = 0
Ψ = 0
Θ15 = true
Ω = true
```

Hard constraints:

1. Kernel numerics remain exact / rational / finite-field safe.
2. Floating point is allowed only in outer UX/DSP approximation layers with explicit boundary receipts.
3. Ordered products remain ordered: `xy != yx` unless a specific projection authorizes collapse.
4. State mutation requires shell gate + receipt + replay validation.
5. AI-generated changes are suggestions until compiled, audited, approved, and committed.
6. Audio, HARMONICODE, XYZW, and Hash72 are high-priority modality witnesses for realtime state transitions.

---

## Phase 0 — Specification Lock

### Goal
Create the canonical language and platform contract.

### Deliverables

- `docs/HARMONICODE_SPEC_v1.md`
- `docs/HARMONICODE_IR_v1.md`
- `docs/HARMONICODE_EFFECT_MODEL_v1.md`
- `docs/HARMONICODE_FFI_BOUNDARY_v1.md`
- `docs/HARMONICODE_AUDIO_DAW_SPEC_v1.md`
- `docs/HARMONICODE_CALCULATOR_SPEC_v1.md`

### Acceptance Criteria

- Grammar sketch exists.
- Core AST node families are defined.
- IR transition format is defined.
- Kernel-audited vs UX-only operations are separated.
- No-bypass rule is explicit.
- Backwards compatibility strategy is scoped.

---

## Phase 1 — Language Core

### Goal
Build a deterministic interpreter and compiler-ready IR.

### Deliverables

- Lexer
- Parser
- AST
- Macro expansion engine
- Symbol table
- Type/effect checker
- IR emitter
- REPL
- Interpreter receipts

### Acceptance Criteria

- HARMONICODE source can parse into AST.
- AST can lower into IR.
- IR can execute through audited state patches.
- Every stateful execution emits receipt chain.
- Replay mismatch fails closed.

---

## Phase 2 — Compiler Backends

### Goal
Compile HARMONICODE into compatible host targets.

### Backends

1. Python backend
2. C backend
3. Assembly / LLVM-compatible backend

### Acceptance Criteria

- Host code generation is deterministic.
- Host side effects use capability wrappers.
- FFI calls emit boundary receipts.
- Non-deterministic host behavior is quarantined unless explicitly wrapped.

---

## Phase 3 — IDE Core

### Goal
Create a programming environment around HARMONICODE.

### Deliverables

- Editor
- LSP server
- syntax highlighting
- diagnostics
- go-to-definition
- build graph
- package manifest
- receipt timeline viewer
- replay debugger
- phase visualization panel

### Acceptance Criteria

- IDE can edit, parse, compile, run, and replay HARMONICODE modules.
- Diagnostics are produced from parser/type/effect/receipt layers.
- Time-travel debugging follows receipt chain, not runtime guesswork.

---

## Phase 4 — AI Assistant Interface

### Goal
Add an AI copilot that works inside the audit model.

### Modes

- Explain
- Patch
- Refactor
- Prove
- Optimize
- DAW Assist
- Calculator Assist

### Acceptance Criteria

- AI suggestions are staged, never silently applied.
- Suggested patches compile before approval.
- Approved patches pass kernel audit and replay verification.
- Assistant receives AST/IR/receipt context instead of raw unbounded text only.

---

## Phase 5 — Scientific Calculator

### Goal
Build a Casio-style scientific calculator that compiles calculator expressions to HARMONICODE IR.

### Features

- algebraic mode
- RPN mode
- symbolic mode
- exact rational mode
- matrices
- complex numbers
- memory registers
- programmable scripts
- expression history

### Acceptance Criteria

- Calculator expressions parse through shared language frontend where possible.
- Exact mode avoids floating-point drift.
- Approximation mode marks numeric boundary receipts.
- Calculator scripts can emit IR and replay receipts.

---

## Phase 6 — DAW / Harmonic Audio Workstation

### Goal
Build digital audio workstation functionality using HARMONICODE as the control/programming layer.

### Features

- audio graph engine
- waveform sampling
- synthesis
- sequencing
- mixer
- buses/sends/inserts
- automation lanes
- mastering chain
- offline render
- receipt-linked render reproducibility

### Acceptance Criteria

- Audio engine separates realtime DSP from kernel-audited symbolic state.
- DAW project changes emit state patches and receipts.
- Offline renders are reproducible by project state + receipt ID.
- Audio modality can feed high-priority phase witnesses.

---

## Phase 7 — Recursive Global Closure Certification

### Goal
Make global closure benchmark a deployment gate.

### Required Runs

```text
72 × 1
72 × 3
72 × 10
72 × N stress mode
```

### Acceptance Criteria

- Step-level receipts pass.
- Cycle-level receipts pass.
- Global aggregate hash is stable.
- Adaptive weights remain inside caps.
- Correction execution remains approval + consensus + re-lock + verify gated.

---

## Immediate Repo Actions

1. Create language spec stub.
2. Create IR spec stub.
3. Create effect model stub.
4. Create issue backlog with epics and acceptance criteria.
5. Add a no-bypass conformance matrix.
6. Add benchmark gate targets.
7. Add GUI panels for benchmark cycles, drift, and adaptive weights.
