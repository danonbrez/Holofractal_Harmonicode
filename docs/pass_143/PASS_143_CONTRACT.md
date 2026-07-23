# Pass 143 — Continuous Constraint Conflict Gradients / Temperature Orthogonality

Pass 143 evaluates conflicting linear constraints in parallel exact-rational branches. Each raw priority gradient is divided by its declared temperature, recursively attenuated by child-constraint burden, projected orthogonally to the global temperature axis, and merged without silently deleting any constraint.

## Invariants

- No IEEE float is admitted.
- Every branch preserves its selected constraint identity.
- Temperature projection must satisfy `dot(projected_gradient, temperature_axis) = 0` exactly.
- Quantum/audio/visual outputs are deterministic simulation projections only.
- Lower final weighted conflict energy is evidence of smoothing, not proof that all conflicts disappeared.
- Nested constraint cycles and unknown children fail closed.
- Iteration and branch counts are bounded to 81.
