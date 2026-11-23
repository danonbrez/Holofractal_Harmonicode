# Optimization calibration repair restart record

- Base branch: `main`
- Base commit: `89a52a879049a637a44ce64a26b1c3f0a00388a5`
- Repair branch: `agent/restore-calibrated-optimization-defaults`
- Merge target: `main`
- Frozen Pass 215 evidence modified: no
- Authority rule: no floats in authoritative operations

## Intended changed files

- `hhs_backend/runtime/hhs_optimization_calibration_v1.py`
- `hhs_backend/runtime/hhs_pass207_vm81_gpu_runtime_v1.py`
- `hhs_backend/runtime/hhs_pass208_gpu_branch_manifold_v1.py`
- `tests/test_hhs_optimization_calibration_v1.py`
- `.github/workflows/optimization-calibration-guard.yml`
- `docs/runtime/OPTIMIZATION_CALIBRATION_REPAIR.md`
- `docs/runtime/OPTIMIZATION_CALIBRATION_RESTART_RECORD.md`

## Recovered validated defaults

- Pass 205 retrieval `top_k`: `32`
- Pass 207 cache bytes: `536870912`
- Pass 207 cache entries: `512`
- Pass 208 maximum branches: `256`
- calibration vector objects: `2048`
- calibration queries: `512`
- continuation ticks per seed: `360`
- calibration seeds: `1,5,7,41,64,72,81,144,216,243,5040,5184,1259713`

## Validation

Required branch validation:

```text
python -m pytest -q tests/test_hhs_optimization_calibration_v1.py
python -m pytest -q tests/test_hhs_pass207_gpu_driver_v1.py tests/test_hhs_pass208_gpu_branch_manifold_v1.py
```

The dedicated GitHub Actions guard runs the first command on pull requests and
pushes affecting this subsystem. Existing Pass 207/208 workflows remain the
dependency-scoped runtime validation authority.
