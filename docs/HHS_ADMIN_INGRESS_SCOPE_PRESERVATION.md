# Administrator knowledge-ingress capability preservation

Status: additive proposed policy and regression check. This does not alter frozen native runtime authority.

1. Administrator intake is byte-universal and modality-agnostic. Do not impose a hardcoded whole-object size ceiling, extension list, MIME allowlist, or modality admission allowlist. Streaming transport chunk limits are not whole-object limits.
2. Accept new objects into isolated, untrusted SQL staging and preserve exact original bytes. Novelty alone is not cause for rejecting uploads or declaring a system modality unsupported.
3. Process staged material through existing Ubuntu capabilities, Lane 5 BIOS/C coprocessor hydration ROM, Pass 174/194 services, and existing signed PQC/VM81 admission. Staging never grants executable or canonical authority.
4. Hash216's native representation includes ordered SHA-256 verification, Hash72 indexing, and embedding vector tokenization, with Genesis-rooted provenance. Do not replace it with a separate unverified embedding database.
5. Before adding a new service or inferring a capability gap, inspect AGENTS.md, REPOSITORY_INDEX.md, the hydrated service graph, relevant source, contracts and recorded evidence. Preserve frozen foundations using additive composition.
6. Any narrowing requires an explicit governing requirement or demonstrated technical necessity with evidence. Distinguish a temporary worker resource constraint from an input eligibility restriction.
7. Protect private staged bytes, authorization, quota accounting, CSRF/origin controls, native egress gates, and exact source integrity. Do not equate unrestricted acceptance with unrestricted execution.
8. Require source -> tests -> CI -> merged exact main -> deployment -> native admission/readback evidence before claiming production closure.

## Automated guard scope

`tools/check_admin_ingress_scope.py` checks **added source lines** for obvious whole-payload size caps and modality admission allowlists in relevant knowledge-ingress files. It uses Git diff with rename detection disabled; moved files are scanned as additions, avoiding rename bypasses.

The guard is deliberately heuristic. It is not complete semantic verification, cannot prove all modalities work, and is not a substitute for native runtime, staged-streaming, source-integrity, and production tests. Findings require source-level diagnosis rather than keyword renaming or test bypass.

## Target architecture

Private DigitalOcean administrator upload -> untrusted SQL staging -> existing Lane 5 and Ubuntu integrated services -> signed VM81/PQC verification -> native Hash216 hydration, relational retrieval and RAG context.
