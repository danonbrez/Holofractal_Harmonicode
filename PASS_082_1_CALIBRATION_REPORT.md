# Pass 082.1 — Offset-Entangled Lane Scalability Calibration

## Status

`OFFSET_ENTANGLEMENT_CLOSURE_VERIFIED`

Pass 082.1 is an additive extension of the frozen Pass 082 bifurcation benchmark. It commits branch offsets as first-class canonical operands, preserves distinct raw branch roots, applies exact inverse normalization, and proves common normalized closure without merging branch identity.

## Verified workload ladder

- W11: two lanes, offsets 0 and 1
- W12: two lanes, opposite phase offsets 0 and 36
- W13: eight consecutive offsets
- W14: eight offsets with coprime stride 5
- W15: sixteen evenly spaced offsets
- W16: thirty-two combined phase and VM81 cell offsets
- W17: sixty-four dense unique offsets
- W18: duplicate-offset rejection
- W19: inverse-normalization failure rejection
- W20: noncommutative phase/cell order comparison

## Closure distinction

`DIRECT_EQUALITY != EQUALITY_UNDER_DECLARED_OFFSET_TRANSFORM`

Raw closure-coordinate roots remain branch-specific. The inverse-normalized coordinate roots are identical only under the committed offset transform and inverse.

## Release root

`0000000000000000000000000000003HBLg4OyD9pwYdrbv2fV3ExsFHfyD5osuIhJ7qNBN!`
