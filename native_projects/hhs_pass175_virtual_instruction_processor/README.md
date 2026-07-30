# Pass 175 native virtual instruction processor

This directory contains the strict C11 native support layer for the Pass 175
`VM5184 × G243` virtual instruction processor.

Implemented native primitives:

- reversible `s = 64c + o` address mapping;
- reversible `q = 243s + g` projected mapping;
- exact five-trit base-3 controls;
- immutable ordered 64-operation phase table;
- dependency conflict detection;
- immutable candidate identity construction;
- singular deterministic commit-root folding.

The C layer calculates and serializes candidates. It does not independently
admit VM81 state, advance Hash72, or acquire host privileges.

```bash
make test
```

The Python runtime under `hhs_runtime/pass175` supplies exact x86_64 hydration,
Hash216 records, parallel candidate waves, and delegation to the inherited
Pass 174 singleton VM81 authority.
