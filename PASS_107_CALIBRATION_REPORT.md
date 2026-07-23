# Pass 107 Calibration Report

## Result

- Status: **PASS**
- Agent final state: `REPAIRED`
- Background scan observed broken dependency: `1`
- Root cause: `BROKEN_DEPENDENCY_BINDING`
- Failed repair rollback: `ROLLED_BACK`
- Final repair: `REPAIRED_AND_PRODUCTION_VALIDATED`
- New Pass 106 admission root: `0000000000000000000000000000002QVG=XG6(-DT1y4r)I(lQbNUuWXt14LFbh6r(sQ=I8`
- Mock components: `0`
- Parallel repair implementation: `false`

## Executed production path

```text
broken dependency binding
→ real production invocation failure
→ binding-to-contract dependency trace
→ proven root-cause localization
→ open repair obligation
→ exact one-mutation repair lease
→ failed repair attempt and exact rollback
→ correct dependency reconnection
→ real Pass 105.6 C/ASM compile-and-run workload
→ Pass 106 capability readmission
→ witnessed repair closure
```

## Focused regression

`19 passed` across Pass 107, Pass 106, and the real Pass 105.6 backend suite.
