# KNOWN ISSUES PASS 018

1. SRCG is currently implemented as a single primitive A/B gate plus Python fabric; full multi-gate parallel execution across every equality relation remains a Pass 019 target.
2. The asynchronous monitor is represented by deterministic trace/audit execution, not yet a long-running runtime thread.
3. C primitive uses scalar A/B state. Higher-dimensional quartic carrier semantics are preserved and audited in Python fabric pending deeper C tensor-carrier ABI support.
4. Full GUI exposure of SRCG services is not yet implemented.
