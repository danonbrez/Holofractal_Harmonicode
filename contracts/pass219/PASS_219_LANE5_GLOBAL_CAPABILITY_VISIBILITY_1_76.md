# Pass 219 — Lane 5 Global Capability Visibility and Hash216 Hydration 1.76

Status: **ADDITIVE / EXACT / REVERSE-PASS VISIBILITY / CANDIDATE-ONLY / NO AUTHORITY ESCALATION**

## Purpose

Pass 219 Lane 5 is the C++ RNA cell-wall composition manifold, not an optional service layered on top of Pass 219. This successor closes a repository-integration divergence: discovered capabilities MUST remain visible to Lane 5 even when their source carries labels such as `demo`, `example`, `reference`, `candidate_only`, `disabled`, `not_ready`, `needs_adapter`, or `needs_configuration`.

Those labels are evidence and state metadata. They are never discovery filters.

The governing law is:

```text
Discover broadly
-> preserve provenance and unresolved state
-> Hash216 hydrate
-> Lane 5 optimize/compose
-> 5184 candidate transition plan
-> runtime/kernel validation
-> canonical admission or rejection
```

## Global visibility invariant

For every capability surface statically discovered from the tracked repository or a fetched Git branch / pull-request head:

```text
VisibleToLane5(c) = TRUE
ClassificationIsVisibilityFilter(c) = FALSE
```

In particular:

```text
Unresolved(c) => VisibleToLane5(c)
DemoLabel(c) => VisibleToLane5(c)
DisabledLabel(c) => VisibleToLane5(c)
NeedsAdapterLabel(c) => VisibleToLane5(c)
NeedsConfigurationLabel(c) => VisibleToLane5(c)
```

No agent, registry, runtime adapter, frontend, or deployment layer may reinterpret uncertainty or a restrictive label as permission to erase the capability from the Pass 219 knowledge manifold.

## Separation of concerns

Visibility, composition, validation, admission, and mutation are separate typed states:

```text
Visible != Executable
Visible != Validated
Visible != Admitted
Visible != Mutable
```

The 1.76 visibility layer grants none of the following:

```text
direct Linux or service bypass authority
canonical VM81 mutation
Hash72 mint authority
canonical Hash216 mint authority
canonical persistence authority
runtime validation authority
```

A discovered capability remains candidate-only until inherited Pass 219/Lane 5 composition and downstream runtime/kernel validation produce the required evidence.

## Static reverse-pass discovery

1.76 reads Git objects and parses source text statically. It MUST NOT import or execute discovered branch, PR, orphan, demo, example, reference, or unresolved code merely to establish visibility.

The current tracked tree is discovered from Git. When branch or pull-request refs are present locally, source changes on those refs are also discovered and represented with their ref name and commit identity.

A parse failure does not make a source invisible. It produces `PARSE_ERROR_VISIBLE` state and preserves the source-file capability node for later analysis.

## Hash216 vector hydration

Every visibility node receives a 216-character Hash216 identity. The restartable SQLite projection stores:

- the complete typed node payload;
- its Hash216 identity;
- all 216 positional glyphs;
- SHA-256 of every individual glyph position.

The database is a derived candidate-memory projection. Repository source and inherited canonical receipts remain authority. Rehydration MUST NOT mint canonical Hash216 state or create a canonical persistence path.

## Interface and host boundary

The user interface remains ingress/egress only for HHS computation. It may render, collect input, and decode validated output, but it may not replace Pass 219/Lane 5 computation with browser, client CPU/GPU, WASM, direct service calls, or direct Linux-kernel computation.

Likewise, a capability is not made `demo` or `non-executable` merely because it cannot bypass the kernel. Inability to bypass the membrane is expected conformance behavior.

## Regression acceptance

1.76 MUST fail if:

- any discovered node is hidden from Lane 5;
- classification metadata is used as a visibility filter;
- discovery imports or executes discovered source;
- visibility grants execution, validation, admission, mutation, mint, or persistence authority;
- a Hash216 identity is not exactly 216 characters;
- vector hydration does not preserve exactly 216 positional records per hydrated capability node.

Existing 1.44, 1.69, 1.75 and other frozen Pass 219 evidence remain inherited and unchanged.
