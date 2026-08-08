# Pass 214 Iteration 5 — Five-Family Callable Corpus

## Purpose

Iteration 5 turns the Iteration 4 repository-callable oracle pattern into a bounded five-family executable corpus. It does not migrate production authority. It measures whether generator/transition forms preserve exact callable results while reducing source representation across the families named in the restart boundary.

## Families

| Family | Baseline bytes | Target bytes | Gain bytes |
|---|---:|---:|---:|
| `vector_cache` | 3496 | 611 | 2885 |
| `wrapper_duplication` | 2223 | 592 | 1631 |
| `numeric_lookup` | 2972 | 566 | 2406 |
| `serialization_import` | 5296 | 748 | 4548 |
| `coprime_lookup` | 10543 | 610 | 9933 |

Aggregate fixture source bytes: **24530**. Aggregate target bytes: **3127**. Static gain before execution: **21403 bytes**.

## Execution gate

The runtime executes every compiled baseline and generator virtual-module callable in a clean Python subprocess with deterministic hashing and bytecode suppression. It rejects floating-point output, compares canonical JSON results, records SHA-256 result identities, measures source bytes, and repeats the complete five-family corpus three times.

`PILOT_READY` requires all fifteen pair evaluations to preserve exact results and every family to show positive representation gain. Any mismatch or non-positive family gain produces `HOLD`.

## Authority boundary

- No production module is replaced.
- No repository authority is promoted.
- No terminal Pass 214 root is minted.
- Live `PASS213_LIVE_GOVERNED_SURFACE` evidence remains mandatory before promotion.
- Pass 215 remains unauthorized.

## Commands

```bash
python -m pytest -q tests/test_hhs_pass214_iteration5_callable_corpus_v1.py
python tools/pass214_iteration5_callable_corpus.py --output-dir artifacts/pass214/iteration5
```
