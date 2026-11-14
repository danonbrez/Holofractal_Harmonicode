# Pass 220 — canonical 196-module HARMONICODE course authority

## Normative source hierarchy

The **complete 196-module HARMONICODE Algebra course** is the mathematical and
architectural specification for the course gates and their ordered native
implementation. The historical 13-module course blob
`2744e9ecf1f260ff9a5a02870320698ee2d7dcaf` is a **legacy stub**, retained
for historical source integrity and comparison only. The stub is not normative
over the complete 196-module course.

The repository-visible `whitepapers/Harmonicode Algebra - Course` is a
course-source input; its inspected blob at the time this contract was drafted is
`968735b21bb0fda42f9c944ae6987099e624e7a7`. A numbered-heading
parser detected 100 distinct `# Module N` headings in that blob. That count
is **not** a finding that the authoritative course contains only 100 modules:
the complete 196-module corpus, its exact byte identity, and module-boundary
inventory must be recovered and verified before declaring full-source coverage.
Do not silently equate this one repository file to all 196 modules without
verifying that coverage.

## Prohibitions

- Do **not** demand the complete course prove equivalence *to the stub*
  as a precondition for recognizing the canonical specification.
- Do **not** replace the canonical algebra with the stub's 13-module subset,
  or rewrite the canonical full course to satisfy the old frozen blob hash.
- Do **not** weaken the legacy freeze checker or alter frozen records to obtain
  a green status; scope its result to the legacy stub's provenance.
- Do **not** call a stub mismatch a failure of full-course mathematics.
- Do **not** infer executable native proof, trustworthy physical-producer
  provenance, or VM81 admission from the user's designation of source authority
  alone. Native admission still uses the existing exact proof/receipt gates.

## Implementation boundary

Source authority and executable admission are different contracts.
The authoritative 196-module course determines what must be implemented and
verified. Native C/C++/Lean and inherited Lane 5/VM81 checkers determine
whether a specific ordered gate and source-to-runtime transition is admitted.

The V161 Module194 check currently calls
`course_module_gate_inventory`, which is coupled to the historical
13-module blob freeze. Its `SOURCE_BLOB_CHANGED` result must be labeled
`LEGACY_STUB_FREEZE_MISMATCH` in planning and diagnostic reports, **not**
`CANONICAL_196_MODULE_COURSE_INVALID`. This remains an unresolved
implementation/coverage gap; the current native checker must not be
automatically marked successful.

The V162 diagnostic and V163 index crosswalk are historical tools. They
must not be used as mathematical gates over the full course. Next recover
the exact complete 196-module artifact and establish a canonical source
manifest, retaining the historical stub separately; then bind the ordered
module requirements to inherited native checkers and their actual receipts.
No merge, deployment, or authority fork follows solely from this document.
