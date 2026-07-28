# HHS Pass 164 native GCMSL ABI

This project provides the fixed-width C11 reference ABI for the Pass 164 `81:72:64` scaling law.

Implemented operations:

- canonical geometry status and validation;
- `81 × 64 -> 72 × 72` coordinate mapping;
- inverse `72 × 72 -> 81 × 64` mapping;
- bounded homogeneous scale calculation;
- vector-valued invariant closure;
- stable operation-key comparison.

Run:

```bash
make clean test
```

The test exhaustively visits all 5,184 coordinates and compiles with:

```text
-std=c11 -Wall -Wextra -Werror -pedantic -O2
```

The native surface does not claim physical GPU execution. GPU and accelerator workers remain speculative backends beneath the singleton VM81 authority.
