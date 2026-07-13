# Known Issues — Pass 072

- The current phase-gear pathfinder intentionally exercises the bounded clockwise quarter-turn operator; every local orbit therefore has period 4. Pass 073 should admit inter-subgrid and phase-routing choices to discover emergent periods.
- The repository-wide conformance pytest file repeatedly rebuilds the full surface map and is performance-bound in this environment. Pass 072 uses one direct canonical map build and records its deterministic root.
- Pytest plugin autoload can retain unrelated post-test worker state. Dedicated suites are verified with plugin autoload disabled; this does not alter test semantics.
