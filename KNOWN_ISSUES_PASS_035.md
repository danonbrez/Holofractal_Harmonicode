# Known Issues — Pass 035

- The enforcement binding currently exposes a preflight route/service rather than forcing every legacy runtime route through a mandatory global gate. That avoids breaking existing guarded routes while providing a canonical enforcement surface.
- Full pytest suites continue to be slow because the accumulated ledger and manifest files are large.
- Future work should progressively require this preflight for broader live execution surfaces.
