# HHS PASS 162 — VM81 CREATIVE NOVEL AND LANGUAGE-MODEL OPTIMIZATION

## Runtime-Only Novel Generation, Receipt-Governed Provider Execution, Compact Story-Bible Context, Bounded Parallel Chapter Synthesis, Engine-Token Allocation Control, Prompt-Cache Reuse, and Guarded Creative-Artifact Persistence

## 1. Normative metadata

| Field | Normative value |
|---|---|
| Contract identifier | `HHS-P162-VM81-CN-LMO` |
| Pass number | `162` |
| Canonical pass name | `VM81_CREATIVE_NOVEL_LANGUAGE_MODEL_OPTIMIZATION` |
| Contract version | `1.0.0` |
| Repository | `danonbrez/Holofractal_Harmonicode` |
| Inheritance parent | Complete authoritative Pass 161 inherited pass-history nucleus |
| Delivery model | Additive, incremental, source-oriented |
| External generation authority | VM81 runtime API only |
| Creative artifact root | `creative_writing/novels` |

## 2. Required result

Pass 162 SHALL provide a callable VM81 runtime operation that accepts a bounded novel-generation contract, produces a complete chaptered manuscript through the governed HHS language-model provider fabric, and persists the admitted manuscript beneath the creative-writing root.

The language model SHALL NOT be exposed as an alternate application API, filesystem authority, VM81 mutation authority, receipt authority, or canonical state authority.

## 3. Sole external generation surface

The normative generation surface is:

```text
POST /api/runtime/creative/novel
```

A conforming external client SHALL call this surface and SHALL NOT call LiteRT-LM `/v1/chat/completions` directly.

The runtime MAY call the configured provider internally after VM81 authorization and HHS provider-policy admission.

## 4. Execution chain

A conforming execution SHALL preserve this order:

```text
runtime ingress
-> VM81 authorized tick
-> validated TEXT_GENERATION provider proposal
-> capability-policy admission
-> provider invocation
-> invocation receipt
-> provider-result ingress
-> Hash72-rooted outline/chapter assembly
-> persistence-guard egress
-> creative artifact write
-> runtime egress
```

Failure at any required stage SHALL close without asserting successful generation or persistence.

## 5. Novel architecture

The runtime SHALL generate:

1. one complete story bible and chapter outline;
2. exactly the requested number of chapter contracts;
3. one prose chapter for every admitted chapter contract;
4. one ordered manuscript;
5. one outline root, chapter root set, manuscript root, and result root;
6. guarded persistence evidence when persistence is requested.

The ending contract SHALL require narrative closure rather than an automatic sequel hook.

## 6. Performance invariants

### 6.1 No quadratic transcript replay

Generated chapter text SHALL NOT be appended to every later model request. Continuity SHALL be carried by the compact story bible and per-chapter `continuity_in` / `continuity_out` contracts.

### 6.2 Bounded engine allocation

The creative transport SHALL encode an explicit maximum engine-token bound in the LiteRT-LM model request identity.

### 6.3 Bounded concurrency

Chapter generation MAY execute concurrently, but provider concurrency SHALL remain bounded to the range 1–4.

### 6.4 Tool-schema exclusion

Unrelated general-assistant HHS tool schemas SHALL NOT be injected into creative prose calls. Provider governance and receipts SHALL remain active.

### 6.5 Bounded cache

Deterministic repeated prompt contracts MAY reuse a bounded process-local cache keyed by Hash72-domain-separated generation identity.

### 6.6 Separate creative sampling profile

Creative prose sampling MAY differ from diagnostic assistant sampling, but all values SHALL remain explicit, bounded, and environment configurable.

## 7. Persistence boundary

The API caller SHALL NOT choose an arbitrary directory. The runtime SHALL select the configured creative-writing root, validate the filename as a single Markdown path component, and persist through the HHS persistence guard.

Direct model-to-filesystem writes are prohibited.

## 8. Evidence and non-claims

A committed seed manuscript MAY exist before a live provider run, but it SHALL identify itself as a seed/reference artifact and SHALL NOT claim a VM81 execution receipt that was not produced.

Live completion status requires an admitted runtime response containing the VM81 tick projection, provider evidence, Hash72 roots, and persistence evidence.

## 9. Targeted validation

Pass validation SHALL include:

- syntax/compile validation of new Python surfaces;
- engine-token request identity validation;
- deterministic fake-provider novel assembly;
- exact requested chapter count;
- isolated thread verification;
- no prior chapter replay;
- creative-root containment;
- Hash72 root presence;
- guarded persistence projection.

Previously verified inherited suites remain frozen unless changed dependencies require rerun. A later integration failure SHALL be repaired forward.

## 10. Terminal state

The implementation may be classified:

```text
HHS_PASS_162_VM81_CREATIVE_NOVEL_IMPLEMENTED
```

only after source, tests, documentation, and the reference creative artifact are committed.

It may be classified:

```text
HHS_PASS_162_VM81_CREATIVE_NOVEL_LIVE_EXECUTION_VERIFIED
```

only after a reachable LiteRT-LM provider produces an admitted VM81 runtime response and persistence receipt. The present repository-connector execution environment does not supply that live provider evidence.
