# Next Pass — Pass 032

Recommended next priority: authorized pure function expansion with closure-harness coverage.

Pass 031 proves the minimal authorized-pure execution gate.  Pass 032 should expand cautiously by adding more pure deterministic targets only when each target has:

```text
capability plan
→ dry-run trace
→ Pass 030 schema validation
→ static purity scan
→ authorized execution witness
→ closure-harness coverage
```

Candidate categories:

- pure Hash72 projection summaries
- pure schema-classification helpers
- pure closure-summary projections
- pure deterministic validation predicates

Do not promote mutation-capable functions yet.
