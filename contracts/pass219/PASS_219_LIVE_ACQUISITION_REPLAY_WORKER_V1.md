# Pass 219 — Live Acquisition and Replay Worker v1

## 1. Purpose

This contract defines the application-boundary worker that connects the merged
translation-invariant multimodal ingress and real-source calibration layers to
actual revision-pinned public repository artifacts.

The worker is intentionally outside canonical VM81 mutation authority.
Network transfer and external model execution produce candidate evidence only.

The required flow is:

```text
immutable repository descriptor
→ provider-derived HTTPS URL
→ bounded external acquisition
→ exact byte-length check
→ SHA-256 source check
→ RepositoryArtifact
→ externally executed projector
→ sealed output/vector byte identities
→ ExactSemanticProjection
→ merged translation-invariant ingress
→ candidate semantic-family receipt
→ archived replay closure
```

## 2. Inheritance

This layer inherits rather than replaces:

- Pass 166 source/model acquisition integrity rules;
- Pass 165 multimodal ingestion;
- Pass 219 translation-invariant multimodal ingress v1;
- Pass 219 real-source translation calibration v1;
- I29/equivalent validation before any Lane 5 canonical-state carrier is used.

The merged ingress remains authoritative for semantic candidate admission.
This worker SHALL NOT independently reproduce or redefine its semantic-family
logic.

## 3. Source identity

Every live acquisition SHALL bind:

```text
provider
repo_id
immutable 40-hex revision
license_id
repo_kind
artifact_path
expected_byte_length
expected_sha256
declared_media_type
source_language
```

The worker SHALL derive the remote URL from the provider, repository identity,
immutable revision, and artifact path. An arbitrary operator-supplied moving URL
is not an acquisition identity.

Provider URL forms are:

```text
GITHUB:
https://raw.githubusercontent.com/{repo_id}/{revision}/{artifact_path}

HUGGING_FACE:
https://huggingface.co/{repo_id}/resolve/{revision}/{artifact_path}
```

## 4. Network boundary

The default transport SHALL:

- require HTTPS;
- disable environment proxy inheritance;
- permit only provider-compatible public hosts;
- reject loopback, private, link-local, multicast, reserved, and unspecified IPs;
- validate every redirect before following it;
- validate the final response URL;
- require HTTP 200;
- request identity transfer encoding;
- read at most the declared expected byte length plus one sentinel byte;
- reject over-length content before analysis.

A custom/injected transport remains external and noncanonical. The worker SHALL
still reject request-URL divergence, non-200 status, or final-provider-domain
divergence before source admission.

## 5. Source verification precedes model execution

External model execution SHALL NOT occur until:

```text
actual_byte_length == expected_byte_length
AND
SHA256(actual_bytes) == expected_sha256
```

A source length or digest mismatch SHALL terminate the cycle before the external
projector is invoked.

This ordering prevents an unverified remote payload from becoming semantic
projection input.

## 6. External projection evidence

The external projector SHALL return bounded evidence containing:

```text
revision-pinned model repository
pivot_text
source_language
pivot_language
source_modality
raw model-output bytes
raw vector-identity bytes
exact similarity numerator
exact similarity denominator
semantic labels
translation chain
```

The worker SHALL compute rather than trust:

```text
model_output_sha256 = SHA256(raw model-output bytes)
vector_identity_sha256 = SHA256(raw vector-identity bytes)
```

Similarity SHALL be represented as an exact rational in `[0, 1]`.
External floating-point inference MAY occur outside the canonical kernel, but
its archived result SHALL cross this boundary as explicit bytes plus an exact
serialized rational observation.

## 7. Existing ingress composition

Verified source bytes SHALL enter the existing `RepositoryArtifact` surface.
Sealed projection evidence SHALL be converted to the existing
`ExactSemanticProjection` surface.

The existing `TranslationInvariantMultimodalIngress` SHALL then produce the
candidate semantic-family result.

Therefore:

```text
worker verification != semantic truth proof
worker projection receipt != canonical Hash216
worker report != VM81 mutation authority
```

## 8. Replay closure

Every completed live run SHALL emit a replay closure over:

```text
verified source SHA-256
ordered external projection receipts
translation-invariant ingress record
```

The replay closure SHALL be Hash72-sealed under a dedicated domain.

Archived replay SHALL accept the exact archived source bytes and exact external
projection evidence bytes and SHALL perform no network transfer or external
model execution.

A replay using altered source bytes or altered projection-output bytes SHALL
fail to reproduce the prior closure.

The full live report and archived replay report are not required to be bytewise
identical because transport metadata and execution mode differ. Their replay
closure MUST be identical when the verified source, projection evidence, and
ingress result are identical.

## 9. Authority boundary

The following values SHALL remain true for every worker report:

```text
candidate_only = true
truth_promotion = false
action_authority_minted = false
canonical_learning_commit_invoked = false
vm81_commit_invoked = false
canonical_hash72_minted = false
canonical_hash216_minted = false
permanent_prune_authorized = false
```

Hash72 receipts produced by this worker are evidence receipts. They are not a
claim that canonical runtime Hash72 authority has been minted.

## 10. Lane 5 boundary

The worker MAY produce translation-invariant candidate evidence that later
participates in warm hydration.

It SHALL NOT construct, infer, or synthesize a canonical 216-symbol Hash216
carrier merely because source and projection evidence close successfully.

Lane 5 eligibility continues to require I29 or equivalent validation and the
existing CPU canonical-replay authority rules.

## 11. Failure classes

Required fail-closed conditions include:

- moving/unpinned repository revision;
- unsupported provider/license/repository kind;
- invalid or traversal artifact path;
- invalid expected SHA-256;
- unbounded declared byte length;
- provider-host mismatch;
- non-public network address;
- HTTPS downgrade;
- redirect outside provider-compatible domains;
- request URL divergence;
- final URL provider mismatch;
- non-200 response;
- response longer than declared length;
- source length mismatch;
- source digest mismatch;
- model-output/vector-evidence bounds exceeded;
- invalid exact similarity;
- too many projection candidates;
- archived replay closure mismatch.

## 12. Deterministic CI policy

The required PR gate SHALL NOT depend on live network availability.

Dependency-scoped CI SHALL use an injected deterministic transport and external
projector fixture to prove:

- immutable URL construction;
- verification-before-model-execution ordering;
- source/output/vector digest sealing;
- existing ingress composition;
- candidate-only authority preservation;
- network-free replay closure;
- tampered source rejection;
- tampered projection rejection;
- transport URL/status rejection;
- exact rational score bounds.

A separate operator or deployment smoke MAY exercise the real HTTPS transport
against an independently pinned source manifest. Such a smoke is evidence of
connectivity and source availability, not canonical admission authority.

## 13. Restartability

A restart checkpoint for this cycle SHALL record:

- base main commit;
- branch and PR;
- changed files;
- exact implementation head;
- validation commands/workflows;
- defects repaired during the cycle;
- merge status and verified main head;
- next integration boundary.

## 14. Completion criterion

This cycle is complete when:

1. the worker, tests, contract, CI, and restart record are repository-visible;
2. the dedicated dependency-scoped gate passes on the exact head;
3. the PR is mergeable with no main drift or is reconciled repair-forward;
4. the PR is merged;
5. `main` is verified at the merge commit.

The next boundary after completion is an application-service adapter that can
submit explicit acquisition jobs, retain archived replay bundles outside Git
history, and expose their receipts/status to the mobile/web control surface.
