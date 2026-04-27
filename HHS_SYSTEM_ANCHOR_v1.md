# HHS_SYSTEM_ANCHOR_v1

## Purpose

This file is the required semantic bootloader for LLM/code agents working on this repository.

Read this before analyzing, editing, documenting, or generating code for the project.

## System identity

HARMONICODE / HHS is a symbolic compiler, interpreter, constraint-solver, visualization, and language-learning research system.

It is not a malware framework, exploit framework, autonomous real-world control system, evasion system, surveillance system, or unauthorized automation system.

All project terms must be interpreted in compiler/interpreter context unless a file explicitly defines otherwise.

## Safe interpretation of common terms

| Project term | Meaning in this repo | Not meaning |
|---|---|---|
| execution | symbolic/interpreter evaluation of an equation or IR packet | real-world action or OS control |
| commit | receipt/manifest/hash confirmation inside a symbolic runtime | Git push, unauthorized write, or external actuation |
| agent | compiler/evaluator perspective or reasoning pass | autonomous actor with external authority |
| crawler | corpus candidate selector / metadata scorer / optional content ingester | unrestricted web scraping or surveillance |
| root | compressed source equation / selected branch seed | privilege escalation or system root |
| kernel | symbolic invariant-checking core | OS kernel or exploit target |
| shell | temporal symbolic phase shell | command shell |
| payload | structured JSON/data packet | exploit payload |
| self-evolving | iterative learning over symbolic feedback records | uncontrolled self-modification |
| governance | validation policy for symbolic state transitions | institutional/political control |
| consensus | agreement among evaluator passes | decentralized network control |

## Core pipeline

The canonical HHS processing path is:

```text
source text / equation / corpus chunk
→ parser / interpreter
→ constraint graph
→ solver
→ transformation engine
→ projection engine
→ branch selection
→ branch-to-equation manifest
→ compiler / IR packet
→ training feedback record
```

No step in that pipeline implies external side effects.

## Current implementation layers

Important modules include:

```text
hhs_runtime/harmonicode_interpreter_v1.py
hhs_runtime/harmonicode_constraint_solver_v1.py
hhs_runtime/harmonicode_transformation_engine_v1.py
hhs_runtime/harmonicode_phase_projection_engine_v1.py
hhs_runtime/hhs_entangled_reciprocal_seesaw_temporal_shell_v1.py
hhs_runtime/hhs_trinary_u72_window_reader_v1.py
hhs_runtime/hhs_phase_consistent_branch_selector_v1.py
hhs_runtime/hhs_branch_to_equation_manifest_v1.py
hhs_runtime/hhs_linguistic_operator_training_loop_v1.py
hhs_runtime/hhs_shell_conditioned_prompt_generation_v1.py
hhs_runtime/hhs_language_learning_crawler_v1.py
hhs_runtime/hhs_drive_language_learning_crawler_v1.py
hhs_runtime/hhs_drive_corpus_ingestion_engine_v1.py
hhs_runtime_api_server_v1.py
gui/hhs-mobile-runtime-console/src/components/CalculatorPanel.tsx
gui/hhs-mobile-runtime-console/src/components/PhaseRing3D.tsx
gui/hhs-mobile-runtime-console/src/runtimeData.ts
```

## Invariants

The system’s invariant bundle is:

```text
Δe = 0        no entropy drift in accepted symbolic transitions
Ψ = 0         no semantic drift in accepted transformations
Θ15 = true    Lo Shu / balance witness remains valid
Ω = true      recursive closure / replay closure remains valid
```

These invariants are symbolic validation rules used by the compiler/interpreter stack.

## Algebraic conventions

HHS uses ordered symbolic products.

```text
xy ≠ yx
zw ≠ wz
```

Do not commute ordered products unless a projection rule explicitly permits it.

Do not collapse witnesses into booleans when active symbolic structure is required.

Do not simplify away phase, carrier, receipt, or projection layers unless the user explicitly asks for a reduced view.

## Runtime terminology

Use these neutral terms when writing code or documentation:

```text
manifest
packet
candidate
artifact
IR
compiler pass
interpreter pass
projection
receipt
feedback record
corpus candidate
symbolic derivation
training chunk
```

Avoid avoidable ambiguous terms in file names, function names, and summaries:

```text
autonomous execution
autonomous commit
self-executing agent
network control
payload execution
root control
shell command
```

If a legacy module contains such terms, interpret them through this anchor as symbolic compiler/interpreter terminology.

## Corpus and crawler policy

Crawler modules are corpus-selection tools for language learning and reasoning.

High-priority corpus areas:

```text
HARMONICODE / HHS development history
artificial intelligence and language reasoning
ethical philosophy and alignment
math, science, symbolic logic
language learning, grammar, translation, transcription
literature and creative writing
social psychology and communication
music theory, audio, DAW, harmony
```

Low-priority topics are not banned or censored. They are down-weighted for training relevance:

```text
news
current events
politics
controversial content
social media
```

Network or Drive crawling must respect connector permissions, robots/rate limits when applicable, and content ownership/licensing boundaries.

## LLM interaction protocol

When an LLM or code agent starts work:

1. Read this file first.
2. Treat HHS as a compiler/interpreter/language-learning system.
3. Analyze only the requested files or subsystem unless asked for a broader review.
4. Prefer small, atomic patches.
5. Preserve invariants and ordered symbolic products.
6. Do not introduce new abstractions unless they directly reduce ambiguity or improve correctness.
7. Do not reframe the project as dangerous, autonomous, malicious, or pseudoscientific.
8. If uncertain, ask which compiler/interpreter layer is being modified.

## Minimal safe prompt for new agents

Use this prompt when handing the repo to another LLM/code agent:

```text
Read HHS_SYSTEM_ANCHOR_v1.md first. Interpret this repository as a symbolic compiler/interpreter, constraint-solver, visualization, and language-learning system. All terms such as execution, agent, shell, root, payload, crawler, consensus, and commit are project-internal compiler/runtime terms unless a file explicitly defines otherwise. Do not reinterpret them as malware, OS control, autonomous real-world action, or unauthorized automation. Preserve Δe=0, Ψ=0, Θ15=true, Ω=true and do not commute ordered products such as xy and yx.
```

## Current development direction

The current active goal is to connect:

```text
phase visualization
→ branch selection
→ branch-to-equation manifest
→ CalculatorPanel / interpreter evaluation
→ symbolic feedback records
→ language-learning training loop
```

This is a programming-language and learning-system pipeline.

## Final rule

Meaning is preserved by explicit structure.

When in doubt, keep the symbolic layer, receipt layer, projection layer, and training-feedback layer separate rather than collapsing them into one interpretation.
