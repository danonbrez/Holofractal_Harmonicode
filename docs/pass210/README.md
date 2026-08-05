# Pass 210 Holographic Frame Compression

Pass 210 implements `HHS-P210-HFC-VM81-H72-H216` as an exact Python runtime and public FastAPI router.

## Runtime

- one 64-byte-aligned 5184-byte Boolean register allocation;
- 36 lazy ring snapshots, width 288, stride 144;
- exact two-witness coverage;
- 89/55/89/55 sectioning;
- 12×12 matrix views;
- registered affine-modular bijections;
- raw, Hash72, Hash216, phase, and frame agreement;
- all-36 erasure recovery;
- deterministic Hash72 receipt replay;
- strict compression only for a declared recurrence domain.

## Validation

```bash
bash scripts/run_pass210_hfc_validation.sh
```

The script compiles the implementation, runs runtime and API conformance, and verifies the committed evidence byte-for-byte.

## API

Base path: `/api/runtime/holographic-frame-compression`

Endpoints include `/status`, `/frames/encode`, frame decode/snapshot/recovery, `/views/admit`, `/project`, `/agree`, and strict compression/decompression.
