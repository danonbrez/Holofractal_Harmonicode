# Pass 186 native x86_64 VM81 Q144 ABI

Build and validate:

```sh
make clean test disassemble
```

The smoke test exhaustively checks every internal `5184 × 243` address and the bidirectional crosswalk among:

```text
(g243, opcode36, root-row12, root-col12)
        ↕
projected address 0..1,259,711
        ↕
(VM81 cell81, operation64, class8, ordered basis8)
```

The module is additive and does not alter frozen legacy ABI layouts.
