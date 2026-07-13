# KNOWN ISSUES PASS 004

1. Some backend, semantic, ML, and GUI-facing service modules may still call lower-level functions directly. They must be audited and routed through the authority gate or explicitly classified as diagnostic/deprecated.
2. `HHSRuntimeController.step()` remains available for diagnostics. Production entry points should use `authorized_tick()`.
3. GUI build verification still requires Node dependency installation outside the ZIP.
4. C runtime warnings remain non-blocking but should be cleaned before release candidate packaging.
