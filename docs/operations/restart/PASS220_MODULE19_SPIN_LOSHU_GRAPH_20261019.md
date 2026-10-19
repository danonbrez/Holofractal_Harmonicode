# Pass 220 Module 19 ordered graph ingestion restart

- Base: `main` at branch creation on 2026-10-19 (retrieve exact ancestry before merge).
- Branch: `pass220/module19-ordered-spin-loshu-relations-20261019`; merge target `main`.
- Modified files: `hhs_runtime/hhs_pass220_module19_spin_loshu_graph_ingestion_v1.py`, `tests/pass220/test_hhs_pass220_module19_spin_loshu_graph_ingestion_v1.py`, `.github/workflows/pass220-module19-spin-loshu-relations.yml`, this record.
- Commits: `29eaf586f874362b067811a324dab5c1391e7025`, `0cc2fd323a6eef24498e31f27bb27d63f8c076ad`, `4ccaf663cd9104e1e355a647b1dad96b2ffa1b70`.
- Existing interfaces retained: `CanonicalKnowledgeGraphEngine.verify_node/relate/assert_no_execution_escalation` (Pass128); native I028 C ABI untouched; phase/address H36 bridge untouched. This path ingests already admitted nodes, not arbitrary user claims as new canonical nodes.
- Implemented: four directed Module19 proposition relations, exact ordered operands `x·S, L, y·(−S), xy`, fixed Lo Shu/spin matrices, immutable SHA256 evidence fingerprint (not minted Hash72), zero authority flags, fail-closed reversed endpoint/modified witness.
- Scope: this is knowledge graph candidate evidence. It does **not** establish exact symbolic determinant proof, full Cardano spectrum, signed Hash216 receipt, or canonical native mutation.
- CI workflow runs `python -m py_compile ...` and `PYTHONPATH=. python -m unittest tests/pass220/test_hhs_pass220_module19_spin_loshu_graph_ingestion_v1.py`. No passing CI result yet recorded; tests still require execution in clean repository and observed job receipt.
- Environment: connected GitHub API source writes; production not accessed.
- Next: read workflow results and logs, repair any scoped test failure. Then link an already admitted Pass128 node pair from the existing constructor metadata ingestion route, map Module19 exact-address witness into inherited I028 Lane5 G3 constructor, keep all mint and persistence flags zero, validate native ABI and signing boundary. No merge until verified dependency closure.
