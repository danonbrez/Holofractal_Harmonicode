# HHS Pass 163 VMRC native reference

This directory contains the fixed-width C11 snapshot and canonical full-snapshot Base64 surface for `HHS-P163-LLABI-B64-VMRC`.

```sh
make test
```

The native surface enforces:

- exactly 81 VM81 positions and 64 thread lanes;
- position-major 5,184-bit storage;
- exactly 648 snapshot bytes;
- exactly 864 unpadded Base64 symbols;
- explicit bounds and output capacities;
- authority-token-gated canonical writes;
- strict canonical decode by decode/re-encode equality.

The Python reference runtime in `hhs_runtime/pass163/vmrc.py` supplies the governed candidate, Hash72(D||S), Hash216, cache, journal, index, and replay behavior.
