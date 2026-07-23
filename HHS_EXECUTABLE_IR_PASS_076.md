# HHS_EXECUTABLE_IR_V1 — Pass 076

`HHS_EXECUTABLE_IR_V1` is a deterministic execution projection derived from a committed and independently revalidated `HHS_TYPED_IR_V1` artifact.

It restores executable gate structure from the committed source reconstruction recipe while preserving typed-IR block identity, source spans, effects, authority requirements, invariant bindings, and ordered product identity.

Lowering is admitted only when:

1. the source artifact root verifies;
2. the typed-IR artifact root verifies;
3. source and typed-IR lineage roots match;
4. the typed IR independently revalidates against source content;
5. deterministic reparsing reproduces the committed AST root;
6. every AST node resolves to exactly one typed-IR block;
7. no unsupported execution effect is silently admitted.

The lowering stage executes no program effect. Runtime authority is still required before interpretation.

Canonical executable-IR root:

```text
0000000000000000000000000000003nz(rIc=TJv68wNxB1?EX(8axOjviJDyzdpoAqZ2?g
```
