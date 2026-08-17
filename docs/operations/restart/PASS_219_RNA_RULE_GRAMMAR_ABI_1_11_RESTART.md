# Pass 219 Iteration 1.11 — RNA Rule Grammar ABI Restart Record

Status: IMPLEMENTATION IN PROGRESS — DRAFT/UNMERGED

Repository: `danonbrez/Holofractal_Harmonicode`

Authoritative parent checkpoint:
- Pass 219 1.10 frozen head: `e46c51dad6c318e005da1ca775b5d06c9dbd7788`
- Parent branch: `agent/pass219-iteration110-native-rna-transcription-abi`
- Parent PR: #260
- Parent classification: exact-head terminal green, draft, unmerged

Iteration branch:
- `agent/pass219-iteration111-rna-rule-grammar-abi`
- Merge target: `main`
- Canonical merge/deployment: NOT AUTHORIZED

Prompt authority:
- `HHS_PASS_219_APPEND_ONLY_NATIVE_RNA_TRANSCRIPTION_ABI_AMENDMENT_1_5_0.md`
- normative Appendixes A/B/C
- specifically E13/E14 for this bounded iteration

Iteration objective:
Implement the remaining explicit Pass 219 RNA rule grammar as executable reusable C++ types lowering to stable C-compatible records, without changing inherited VM81/Hash72/Hash216 semantics or reopening frozen pass history.

Bounded additive surface:
1. stable C records for strand/domain/rule/program/witness identity;
2. exact rule kinds: complement, binding, toehold, hairpin, activation, inhibition, cleavage, release;
3. C++ `hhs::rna` value/view classes named by E13;
4. deterministic program composition over fixed-capacity stable records, with no STL/vtable/allocator representation crossing the ABI;
5. candidate/witness lowering that retains predecessor/phase/trinary/coordinate lineage from the 1.10 records;
6. focused C/C++ conformance and negative tests for the new rule grammar only.

Validation policy:
- strict C11 and C++17 warnings-as-errors on the new delta;
- no float/double authority in the new Pass 219 rule layer;
- dependency-scoped regression against frozen 1.10 admission/wiring only;
- GitHub worker runs are the execution gate;
- repair forward only from concrete failures.

No historical deep scan is authorized by this iteration.

Next action:
- inspect only the frozen 1.10 ABI record shapes needed for extension;
- implement the additive 1.11 records/classes/tests/workflow;
- checkpoint and stop at the iteration boundary.

Deployment state:
- none requested or performed.

Blockers:
- none known at iteration start.
