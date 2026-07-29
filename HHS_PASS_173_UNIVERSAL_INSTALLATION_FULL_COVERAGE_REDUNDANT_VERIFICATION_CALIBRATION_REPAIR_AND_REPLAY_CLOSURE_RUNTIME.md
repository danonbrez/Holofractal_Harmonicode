# HHS PASS 173 — UNIVERSAL INSTALLATION FULL-COVERAGE REDUNDANT VERIFICATION, CALIBRATION, REPAIR, AND REPLAY-CLOSURE RUNTIME

## Independent Multi-Lane Installer Verification, Complete Requirement and Dependency Coverage, Cross-Platform Calibration, Native ABI Equivalence, Profile Closure, Fault Injection, Deterministic Repair, Receipt Reconciliation, Historical-Evidence Correction, Hash216 Installation Identity, Hash72 Verification Receipts, and Bounded End-to-End Replay

# 1. Normative metadata

| Field | Normative value |
|---|---|
| Contract identifier | `HHS-P173-UIFCRV-CRRCR` |
| Pass number | `173` |
| Canonical pass name | `UNIVERSAL_INSTALLATION_FULL_COVERAGE_REDUNDANT_VERIFICATION_CALIBRATION_REPAIR_AND_REPLAY_CLOSURE_RUNTIME` |
| Short name | `P173 Installation Verification and Repair` |
| Contract version | `1.0.0` |
| Repository | `danonbrez/Holofractal_Harmonicode` |
| Historical scan baseline | `a01b08c34bb1bafee69ca8d57d1dc528e875011f` |
| Immediate inheritance parent | Complete authoritative Pass 172 inherited pass-history nucleus |
| Verified subject | Pass 172 universal one-command installation system |
| Source-language authority | HARMONICODE |
| Canonical execution authority | Exactly one VM81 Runtime authority |
| Installation implementation authority | Pass 172 |
| Verification and calibration authority | Pass 173 |
| Canonical mutation authority | Exactly one admitted VM81 commit path |
| Installation state identity | Hash216 |
| Verification, repair, and replay evidence | Hash72 |
| Canonical arithmetic | Exact integers, rationals, modular integers, symbolic structures, and prime-exponent representations |
| Floating-point authority | Forbidden for canonical identity or verdicts |
| Validation model | Independent, redundant, full-coverage, dependency-scoped, bounded, repair-forward |
| Initial status | `CONTRACT_AUTHORIZED — FULL IMPLEMENTATION REQUIRED` |

# 2. Parent-child boundary

Pass 172 SHALL implement:

```text
probe → plan → acquire → verify → provision → build → validate → activate → receipt
```

Pass 173 SHALL independently determine whether Pass 172 actually performs those operations correctly across every declared profile, dependency class, platform adapter, architecture, failure mode, recovery path, and replay boundary.

The governing distinction is:

```text
PASS 172 = INSTALLATION IMPLEMENTATION
PASS 173 = INSTALLATION VERIFICATION, CALIBRATION, REPAIR, AND CLOSURE
```

Pass 173 SHALL NOT replace Pass 172 with a second installer.

Pass 173 MAY:

- execute Pass 172;
- inspect its plans and receipts;
- inject controlled faults;
- compare independent results;
- detect implementation defects;
- generate bounded repairs;
- apply authorized repairs to Pass 172;
- rerun only affected validation scopes;
- produce a final full-system replay.

Pass 173 SHALL NOT:

- establish an alternate installation authority;
- create a second active installation state;
- bypass Pass 172 transaction controls;
- fabricate successful installation evidence;
- weaken an inherited HHS invariant to make an installation pass;
- classify an unexecuted environment as verified.

# 3. Purpose

Pass 173 SHALL provide full-coverage, redundant assurance that the Pass 172 one-command installation system:

1. detects compatible environments correctly;
2. rejects or degrades incompatible environments deterministically;
3. resolves every required dependency;
4. isolates optional dependencies by profile;
5. builds the correct native ABI for each supported platform;
6. installs and activates the requested runtime profile;
7. preserves singleton VM81 authority;
8. produces accurate Hash216 installation identities;
9. emits accurate Hash72 receipts;
10. survives interruptions and controlled failures;
11. repairs bounded defects without damaging user state;
12. reproduces equivalent results through deterministic replay;
13. does not repeat obsolete historical defects;
14. does not claim unsupported coverage.

# 4. Governing verification theorem

Let:

- \(H\) be the host environment;
- \(P\) be the requested installation profile;
- \(I_{172}\) be the Pass 172 installation result;
- \(V_1,V_2,\ldots,V_n\) be independent Pass 173 verification lanes;
- \(K\) be the calibrated reference expectations;
- \(R\) be the repair set;
- \(E\) be the collected evidence.

A Pass 172 installation SHALL be accepted only when:

\[
\operatorname{Accept}_{173}(I_{172})
\iff
\operatorname{Coverage}(E)
\land
\operatorname{Agreement}(V_1,\ldots,V_n)
\land
\operatorname{Calibration}(I_{172},K)
\land
\operatorname{InvariantClosure}(I_{172})
\land
\operatorname{ReplayClosure}(I_{172}).
\]

A repair SHALL be accepted only when:

\[
\operatorname{RepairAccepted}(R)
\iff
\operatorname{DefectLocalized}(R)
\land
\operatorname{DependencyScoped}(R)
\land
\operatorname{RegressionClosed}(R)
\land
\operatorname{NoAuthorityBypass}(R).
\]

Terminal verification requires:

```text
ALL REQUIRED COVERAGE EXECUTED
∧ ALL INDEPENDENT LANES AGREE
∧ ALL CALIBRATIONS WITHIN DECLARED BOUNDS
∧ ALL REPAIRS REVALIDATED
∧ ALL RECEIPTS RECONCILED
∧ FINAL REPLAY MATCHES
```

# 5. Required verification architecture

Pass 173 SHALL implement at least four logically independent verification tracks.

## 5.1 Track A — Static requirement and dependency audit

Track A SHALL inspect:

- Pass 172 contract requirements;
- implementation files;
- dependency manifests;
- lockfiles;
- native build definitions;
- platform adapters;
- profile definitions;
- schemas;
- installer command surfaces;
- receipt schemas;
- update and rollback code;
- offline bundle definitions;
- container definitions;
- Android integration;
- public installation-status routes.

Track A SHALL produce a requirement-to-implementation traceability matrix.

## 5.2 Track B — Executed clean-environment installation matrix

Track B SHALL execute Pass 172 in clean, isolated environments.

It SHALL verify:

- source acquisition;
- environment probing;
- dependency installation;
- native build;
- validation;
- activation;
- startup;
- status reporting;
- repair;
- update;
- rollback;
- uninstall;
- data preservation;
- deterministic replay.

## 5.3 Track C — Independent artifact and receipt reconstruction

Track C SHALL independently reconstruct:

- source identity;
- dependency identity;
- native artifact identity;
- frontend artifact identity;
- selected profile;
- provider classification;
- model identity where applicable;
- executed test counts;
- installation result;
- final Hash216 installation identity;
- Hash72 receipt chain.

Track C SHALL not trust values merely because they were emitted by Pass 172.

## 5.4 Track D — Fault injection and repair verification

Track D SHALL intentionally introduce bounded defects and verify:

- deterministic detection;
- correct failure classification;
- absence of false success;
- quarantine behavior;
- rollback behavior;
- repair-plan precision;
- preservation of user data;
- affected-scope retesting;
- final recovery closure.

# 6. Optional fifth lane

A fifth independent lane SHOULD execute the installation through a user-observable external interface such as:

- a clean virtual machine;
- a physical secondary host;
- an OCI container;
- an Android build host;
- a CI runner of a different architecture.

This lane SHALL use only documented public commands.

It SHALL not call private installer functions.

# 7. Redundancy requirement

At least two independent methods SHALL verify every load-bearing installation claim.

| Claim | Primary method | Independent method |
|---|---|---|
| Python version | Pass 172 probe output | Direct interpreter execution |
| Native symbols | Pass 172 native validation | Independent platform symbol inspector |
| Dependency closure | Installed-package manifest | Clean import and resolution traversal |
| Hash216 installation identity | Pass 172 receipt | Independent canonical reconstruction |
| Test count | Completion receipt | Parsed executed test output |
| Provider readiness | Installer probe | Direct `/v1/models` request |
| Port availability | Installer socket probe | Independent bind/connect test |
| File integrity | Installer manifest verifier | Independent digest traversal |
| Rollback success | Installer status | Direct active-version and runtime test |
| Data preservation | Uninstall receipt | Independent filesystem and database inspection |

A self-reported result without an independent check SHALL be classified:

```text
P173_EVIDENCE_SINGLE_SOURCE_ONLY
```

# 8. Full requirement coverage

Pass 173 SHALL assign every normative Pass 172 requirement one of:

```text
NOT_STARTED
STATICALLY_MAPPED
EXECUTED_POSITIVE
EXECUTED_NEGATIVE
CALIBRATED
REPAIRED
REVALIDATED
NOT_APPLICABLE_WITH_JUSTIFICATION
BLOCKED_BY_EXTERNAL_DEPENDENCY
VERIFIED
```

No requirement may disappear because:

- its implementation is difficult;
- the platform is unavailable;
- a dependency is optional;
- the test is expensive;
- an earlier pass claimed it worked;
- a receipt already exists.

Coverage SHALL be represented in a machine-readable matrix containing:

```text
requirement_id
requirement_text_hash
implementation_paths
test_paths
profiles
platforms
architectures
positive_evidence
negative_evidence
calibration_evidence
repair_evidence
terminal_status
```

# 9. Dependency coverage

Pass 173 SHALL validate every declared Pass 172 dependency class:

```text
HOST_TOOL
PYTHON_RUNTIME
PYTHON_PACKAGE
NATIVE_COMPILER
NATIVE_LINKER
NATIVE_SYMBOL_INSPECTOR
BUILD_ORCHESTRATOR
NODE_RUNTIME
NODE_PACKAGE
BROWSER_RUNTIME
MULTIMEDIA_TOOL
GPU_LOADER
GPU_DRIVER_PROBE
INFERENCE_PROVIDER
MODEL_ASSET
ANDROID_TOOLCHAIN
CONTAINER_RUNTIME
SYSTEM_SERVICE_ADAPTER
```

For every dependency, Pass 173 SHALL test:

1. present and compatible;
2. present but incompatible;
3. absent and automatically installable;
4. absent and not automatically installable;
5. installation denied;
6. corrupted or incomplete;
7. unexpected newer version;
8. unexpected older version;
9. path shadowing or substitution;
10. offline unavailability;
11. successful repair;
12. idempotent reuse.

# 10. Deep-scan issue binding

The following issues identified before Pass 172 SHALL become mandatory Pass 173 verification targets.

## P173-I01 — LiteRT-LM hard dependency contamination

Pass 173 SHALL prove that profiles not requiring local LiteRT-LM can install when the LiteRT-LM wheel is unavailable.

Required cases:

```text
core + unsupported LiteRT platform → PASS
runtime degraded + unsupported LiteRT platform → PASS
assistant external + unsupported local LiteRT wheel → PASS
assistant local + unsupported LiteRT wheel → CLASSIFIED FAILURE
```

## P173-I02 — Python-version boundary

Pass 173 SHALL verify:

- Python 3.11;
- Python 3.12;
- Python 3.13 only if Pass 172 claims support;
- below-minimum rejection;
- unsupported-future-version classification where dependency closure fails.

No Python version SHALL be claimed supported solely because the installer starts.

## P173-I03 — Dependency isolation and lock closure

Pass 173 SHALL verify that:

- system Python is not mutated by default;
- the selected virtual environment is isolated;
- dependency locks match installed packages;
- transitive dependencies are represented;
- profile-specific dependencies do not leak into smaller profiles;
- hard pins do not collide with unrelated global packages.

## P173-I04 — `noexec` filesystem fallback

Pass 173 SHALL execute installation from or into a `noexec` filesystem when the host supports such a test.

The installer SHALL either:

- use a verified executable build location such as a bounded temporary directory; or
- fail before partial activation with a precise classification.

It SHALL not classify a permission-denied native execution as a failed HHS invariant.

## P173-I05 — Source without Git metadata

Pass 173 SHALL test a verified source archive without `.git`.

The installer SHALL derive identity from:

- signed release metadata;
- source manifest;
- supplied immutable commit identity;
- archive digest.

Absence of `.git` SHALL not silently erase source identity.

## P173-I06 — Undeclared optional tooling

Pass 173 SHALL verify declaration and profile isolation for:

- Pillow/PIL;
- Playwright;
- FFmpeg;
- browser runtime assets;
- any other imported optional tool package.

A fresh installation SHALL not encounter an undocumented `ModuleNotFoundError` for an advertised profile.

## P173-I07 — Receipt and executed-test-count drift

Pass 173 SHALL compare:

```text
reported test count
reported pass count
reported failure count
collected test count
executed pass count
executed failure count
```

A stale historical count SHALL not be copied into a new completion receipt.

## P173-I08 — Stale test configuration

Warnings caused by invalid or obsolete test configuration SHALL be classified and repaired.

The verifier SHALL distinguish:

- benign third-party warnings;
- stale repository configuration;
- test-discovery changes;
- silently skipped test groups;
- unknown configuration options.

## P173-I09 — Heavy core-dependency contamination

Pass 173 SHALL verify that minimal profiles exclude packages not required for their callable surface.

It SHALL test clean imports and workloads with:

- no NumPy where not required;
- no SymPy where not required;
- no model provider;
- no frontend toolchain;
- no testing or formatting tools.

## P173-I10 — Node lockfile absence or drift

Every admitted Node application SHALL have a verified dependency lock or equivalent reproducible dependency identity.

Pass 173 SHALL test:

- clean locked installation;
- altered lockfile;
- package manifest/lock mismatch;
- missing lockfile;
- deterministic frontend build identity where claimed.

## P173-I11 — Port collision handling

Pass 173 SHALL test collisions involving:

- HHS API/UI port;
- LiteRT-LM provider port `9379`;
- selected alternate ports;
- compatible preexisting provider;
- incompatible listener;
- stale PID file;
- rapid restart.

No unrelated process may be terminated.

# 11. Historical supersession verification

Pass 173 SHALL preserve the distinction between historical evidence and current-state truth.

The following historical findings SHALL remain in the evidence lineage:

```text
historical Pass 163 absence
historical Hash72 validator closure defect
historical absence of callable Hash72(D||S)
```

The current inherited state SHALL independently verify:

```text
Pass 163 implementation present
Pass 163 Python surface callable
Pass 163 native C11 surface callable
Hash72 structural validation accepts canonical closure
Hash72 validation rejects malformed values
Hash72(D||S) is deterministic
Hash72(D||S) is domain separated
Hash72 verification rejects forged values
```

Historical evidence SHALL not be deleted merely because a defect was repaired.

Current completion receipts SHALL not repeat superseded defect claims.

# 12. Retained technical findings

Pass 173 SHALL preserve and rerun the following retained findings when affected by installation or packaging changes:

1. Hash216 has no 72-event historical ceiling;
2. fixed logical-object cardinality is distinct from versioned historical-chunk cardinality;
3. the 5184-bit payload geometry maps to 648 bytes and 864 Base64 symbols;
4. the Pass 158 descriptor registry contains the expected authoritative descriptor set;
5. fixed-length Hash216 parsing rejects truncation, overrun, and alphabet corruption;
6. Pass 163 remains callable after clean installation;
7. repaired Hash72 behavior survives packaging and installation.

# 13. External kernel-prototype classification

The previously executed 36-opcode repository-kernel prototype SHALL remain classified:

```text
EXTERNAL_EXECUTED_EVIDENCE
NOT_PRESENT_IN_AUTHORITATIVE_TREE
NOT_INSTALLED_BY_PASS_172
NOT_VERIFIED_BY_PASS_173_AS_REPOSITORY_SOURCE
```

Pass 173 SHALL not imply that this external prototype was merged or installed unless its actual source becomes part of the authoritative dependency graph.

# 14. Platform verification matrix

The mandatory matrix SHALL include every environment Pass 172 labels supported.

At minimum:

| Platform | Architecture | Required profile coverage |
|---|---|---|
| Ubuntu 24.04 | x86-64 | core, runtime, degraded, external provider, developer |
| Ubuntu 24.04 | ARM64 | core, runtime, degraded, external provider |
| Debian-family Linux | x86-64 | core, runtime |
| Fedora/RHEL-family | x86-64 | core |
| Arch-family | x86-64 | core |
| Alpine | x86-64 or ARM64 | core if musl support is claimed |
| macOS | Apple Silicon | every claimed profile |
| macOS | Intel | every claimed profile where runner exists |
| Windows native | x86-64 | every claimed profile |
| WSL | x86-64 | every claimed profile |
| OCI container | x86-64 | core, runtime, external provider |
| OCI container | ARM64 | core, runtime |
| Android build host | declared host architecture | Android build profile |
| Termux/Android shell | ARM64 | only profiles explicitly claimed |

A platform SHALL remain:

```text
P173_PLATFORM_NOT_VERIFIED
```

until executed on a real compatible runner or physical host.

Emulation MAY supplement but SHALL not replace real-host evidence for terminal support claims.

# 15. Profile verification matrix

Every Pass 172 profile SHALL be tested independently:

```text
auto
core
runtime
assistant-external
assistant-local-cpu
assistant-local-gpu
developer
android-build
container
offline
```

For each profile, Pass 173 SHALL verify:

- exact included dependencies;
- exact excluded dependencies;
- callable public surfaces;
- startup behavior;
- shutdown behavior;
- receipt content;
- repair behavior;
- update behavior;
- uninstall behavior;
- preservation of shared state.

# 16. Auto-profile calibration

The `auto` profile SHALL be calibrated against a reference decision table.

Examples:

```text
GPU + supported provider + model allowed → assistant-local-gpu
No GPU + CPU provider supported + model allowed → assistant-local-cpu
No local provider + protected external endpoint → assistant-external
No provider + runtime dependencies → runtime degraded
Native build only → core
Missing minimum Python or native artifact → incompatible
```

Pass 173 SHALL test ambiguous and conflicting conditions.

The selected profile SHALL be deterministic for the same canonical probe state.

# 17. Calibration corpus

Pass 173 SHALL maintain a versioned calibration corpus containing:

- environment-probe fixtures;
- dependency manifests;
- platform manifests;
- version boundary cases;
- valid and invalid release manifests;
- valid and invalid offline bundles;
- native artifact fixtures;
- provider health responses;
- model registry responses;
- port-collision fixtures;
- interrupted journals;
- previous-version installation states;
- corrupted installation states;
- receipt chains;
- historical Pass 163/Hash72 defect fixtures;
- Hash216 chain fixtures beyond 72 events.

Every calibration item SHALL have:

```text
fixture_id
fixture_version
input_identity
expected_classification
expected_profile
expected_mutation_scope
expected_receipt_class
expected_repairability
```

# 18. Calibration metrics

Pass 173 SHALL measure and record:

```text
environment probe duration
dependency resolution duration
dependency installation duration
native compile duration
native verification duration
frontend build duration
provider startup duration
model import duration
runtime startup duration
health-check duration
repair duration
rollback duration
uninstall duration
cold installation duration
warm installation duration
offline installation duration
```

Performance measurements SHALL be advisory unless an explicit bound is declared.

Canonical correctness verdicts SHALL not depend on floating-point benchmark comparisons.

Durations MAY be represented as integer nanoseconds or another exact integer unit.

# 19. Calibration boundaries

Pass 173 SHALL define bounded expectations for:

- maximum retry counts;
- maximum probe retries;
- maximum provider readiness attempts;
- maximum lock age;
- maximum journal growth;
- maximum receipt-chain scan scope;
- maximum archive expansion;
- maximum acceptable duplicated downloads;
- maximum tolerated port-selection attempts;
- maximum retained rollback versions.

A boundary failure SHALL produce a classified result rather than an indefinite wait.

# 20. Native build equivalence

For each supported native target, Pass 173 SHALL verify:

- clean compilation;
- strict C11 conformance;
- expected compile flags;
- expected linked source set;
- required library dependencies;
- required exported symbols;
- correct platform extension;
- correct architecture;
- Python bridge loading;
- VM81 executable operation;
- deterministic positive workload;
- deterministic negative workload;
- repeat-build equivalence where claimed.

Pass 158 SHALL include its required Hash216 and Runtime ABI link dependencies.

Pass 163 SHALL be built and executed independently.

CMake and Make surfaces SHALL be compared when both are authoritative for the same project.

# 21. Native-project inventory

Pass 173 SHALL generate the native-project inventory from the live tree rather than hardcoding an assumed count.

Each discovered project SHALL be classified:

```text
REQUIRED_CORE
REQUIRED_PROFILE
OPTIONAL_DEVELOPER
HISTORICAL_ONLY
EXPERIMENTAL
ORPHANED
UNREACHABLE
EXTERNAL
```

Every `REQUIRED_CORE` or `REQUIRED_PROFILE` target SHALL have an installation and verification path.

# 22. Python dependency verification

Pass 173 SHALL:

1. parse all requirement files;
2. resolve recursive includes;
3. identify version conflicts;
4. identify platform markers;
5. identify undeclared imports;
6. identify optional imports;
7. verify profile membership;
8. compare installed distributions to the lock;
9. run clean import closure;
10. run dependency-scoped workloads.

A package appearing in source imports but absent from all applicable dependency manifests SHALL produce:

```text
P173_UNDECLARED_PYTHON_DEPENDENCY
```

# 23. Node dependency verification

For every admitted Node application, Pass 173 SHALL verify:

- Node engine requirement;
- package manager;
- package manifest;
- lock identity;
- clean dependency install;
- test command;
- build command;
- browser test where applicable;
- output artifact identity;
- offline-cache behavior;
- dependency audit classification.

Applications containing only committed static assets SHALL be distinguished from applications requiring a Node build.

# 24. Provider verification

## 24.1 Local GPU provider

Required evidence:

- supported platform;
- detected physical accelerator;
- valid vendor driver;
- valid Vulkan or Metal substrate;
- process-level device access;
- LiteRT-LM executable;
- model import;
- provider startup;
- `/v1/models`;
- one bounded inference request;
- clean shutdown;
- restart;
- receipt closure.

## 24.2 Local CPU provider

Required evidence:

- supported LiteRT-LM CPU execution;
- provider startup;
- model load;
- bounded inference request;
- resource-bound behavior;
- shutdown and restart.

## 24.3 External provider

Required evidence:

- endpoint configuration;
- transport classification;
- authentication or private-network protection;
- model registry;
- timeout behavior;
- unreachable-endpoint degradation;
- no local-provider dependency contamination.

## 24.4 Degraded mode

Pass 173 SHALL prove that the API and UI remain available without falsely reporting assistant readiness.

# 25. Model calibration

Model acquisition and import SHALL be tested for:

- existing valid model;
- missing model;
- interrupted download;
- resumed download;
- altered model;
- insufficient storage;
- missing credential;
- rejected license;
- wrong repository;
- wrong filename;
- duplicate model ID;
- provider/model incompatibility;
- successful repair.

Model bytes SHALL not be included in canonical source identity.

Their declared model identity SHALL be included in the installed provider state.

# 26. Fault-injection catalog

Pass 173 SHALL inject at least the following faults:

```text
missing Python
wrong Python version
missing venv
missing pip
broken TLS certificates
missing compiler
compiler returns failure
compiler produces wrong architecture
missing linker
missing symbol inspector
missing Make
read-only target
noexec target
insufficient storage
archive traversal entry
archive symlink escape
altered source file
altered manifest
altered dependency lock
partial virtual environment
partial native artifact
missing native symbol
occupied API port
occupied provider port
stale installation lock
concurrent installation request
interrupted source download
interrupted dependency installation
interrupted native build
interrupted activation
corrupted current-version pointer
corrupted receipt chain
unreachable external provider
wrong provider model
missing GPU device
missing Vulkan loader
missing Vulkan ICD
denied package-manager privilege
offline network attempt
malformed offline bundle
failed update
corrupted rollback target
uninstall preservation conflict
```

# 27. Failure-classification calibration

Each injected fault SHALL map to one stable classification family:

```text
P173_ENVIRONMENT_*
P173_SOURCE_*
P173_SECURITY_*
P173_DEPENDENCY_*
P173_NATIVE_*
P173_FRONTEND_*
P173_PROVIDER_*
P173_MODEL_*
P173_PORT_*
P173_TRANSACTION_*
P173_VALIDATION_*
P173_REPAIR_*
P173_UPDATE_*
P173_ROLLBACK_*
P173_UNINSTALL_*
P173_REPLAY_*
```

The same canonical fault SHALL not randomly produce unrelated classifications across repeated runs.

# 28. Repair policy

Pass 173 SHALL use repair-forward behavior.

A discovered defect SHALL produce:

```text
defect identity
→ dependency impact graph
→ minimal repair proposal
→ repair authorization
→ implementation
→ affected tests
→ affected integration tests
→ receipt reconciliation
```

The repair SHALL modify the smallest authoritative surface capable of correcting the defect.

It SHALL not:

- edit historical evidence to conceal failure;
- reduce test coverage;
- weaken strict compiler flags;
- skip unavailable dependencies without changing profile classification;
- mark a failed environment compatible;
- duplicate an existing authority module;
- rerun the entire inherited repository repeatedly when only a bounded dependency scope changed.

# 29. Repair classes

Required repair classes:

```text
MANIFEST_REPAIR
LOCKFILE_REPAIR
PROFILE_MEMBERSHIP_REPAIR
PLATFORM_ADAPTER_REPAIR
PATH_ADAPTER_REPAIR
NOEXEC_FALLBACK_REPAIR
NATIVE_BUILD_REPAIR
SYMBOL_EXPORT_REPAIR
PYTHON_ENVIRONMENT_REPAIR
FRONTEND_DEPENDENCY_REPAIR
PORT_SELECTION_REPAIR
PROVIDER_CLASSIFICATION_REPAIR
MODEL_IMPORT_REPAIR
RECEIPT_COUNT_REPAIR
TEST_CONFIGURATION_REPAIR
INTERRUPTION_RECOVERY_REPAIR
ROLLBACK_REPAIR
UNINSTALL_PRESERVATION_REPAIR
DOCUMENTATION_REPAIR
```

# 30. Receipt-count reconciliation

Pass 173 SHALL prohibit static or inherited test counts in current completion receipts.

Every current receipt SHALL derive counts from the current executed test event set.

The receipt SHALL bind:

```text
collection count
selected count
executed count
passed count
failed count
skipped count
expected-failure count
unexpected-pass count
test-set identity
output identity
```

A discrepancy SHALL produce:

```text
P173_RECEIPT_EXECUTION_COUNT_MISMATCH
```

# 31. Hash72 receipt verification

Pass 173 SHALL independently verify each Pass 172 receipt class.

It SHALL validate:

- exact receipt schema;
- parent tip;
- operation;
- request identity;
- profile;
- platform;
- architecture;
- mutation scope;
- success or failure result;
- output identities;
- next tip;
- deterministic replay fields.

The verifier SHALL reject:

- missing parent;
- altered parent;
- reordered receipt sequence;
- duplicated receipt;
- truncated receipt;
- forged result;
- stale test count;
- mismatched installation identity.

# 32. Hash216 installation-identity reconstruction

Pass 173 SHALL independently reconstruct:

\[
I_{172}=
\operatorname{Hash216}
\left(
C\parallel S\parallel P\parallel A\parallel D\parallel N\parallel F\parallel V\parallel M\parallel E
\right).
\]

The reconstruction SHALL use canonical serialization and exact component ordering.

It SHALL prove:

- identical canonical installation content produces identical identity;
- profile changes alter identity;
- dependency-lock changes alter identity;
- native-artifact changes alter identity;
- model changes alter provider-state identity when the model is installed;
- timestamps and temporary paths do not alter canonical identity;
- host-specific noncanonical metadata remains outside identity.

# 33. Installation replay

Pass 173 SHALL support two replay modes.

## 33.1 Logical replay

Logical replay reconstructs:

- probe decision;
- profile resolution;
- dependency plan;
- source verification;
- artifact identities;
- validation verdict;
- receipt closure.

It SHALL not repeat host mutation.

## 33.2 Full clean-environment replay

Full replay SHALL run the complete Pass 172 installation in a fresh environment using the same canonical request and inputs.

The resulting canonical installation identity SHALL match where platform and architecture are identical.

Cross-platform identities MAY differ only in declared platform-bound components.

# 34. Cross-platform equivalence

Pass 173 SHALL distinguish:

```text
SOURCE_EQUIVALENCE
SEMANTIC_RUNTIME_EQUIVALENCE
ABI_SURFACE_EQUIVALENCE
PLATFORM_ARTIFACT_EQUIVALENCE
RECEIPT_SCHEMA_EQUIVALENCE
BYTE_IDENTITY
```

Linux `.so`, macOS `.dylib`, and Windows `.dll` artifacts are not expected to be byte-identical.

They SHALL expose the declared equivalent ABI and pass equivalent semantic workloads.

# 35. Installation-path calibration

Required path tests:

- ordinary user-home path;
- path containing spaces;
- Unicode path;
- long path;
- symlinked source path;
- symlinked installation parent where allowed;
- read-only parent;
- removable or ephemeral storage;
- `noexec` source;
- `noexec` target;
- separate state and executable volumes.

Unsafe path forms SHALL be rejected before activation.

# 36. Security verification

Pass 173 SHALL independently test protection against:

- shell injection;
- PowerShell injection;
- argument injection;
- path traversal;
- symlink escape;
- dependency confusion;
- unsigned source substitution;
- digest downgrade;
- compiler substitution;
- poisoned `PATH`;
- DLL search-order attacks;
- insecure temporary files;
- token leakage;
- world-readable secrets;
- replayed management proposals;
- remote privileged mutation;
- unbounded archive extraction;
- malicious environment-variable overrides.

Security tests SHALL include positive controls proving that valid ordinary paths and parameters still work.

# 37. Upgrade calibration

Pass 173 SHALL test:

1. same-version update;
2. forward update;
3. update requiring dependency change;
4. update requiring native rebuild;
5. update requiring configuration migration;
6. interrupted update;
7. failed post-activation verification;
8. rollback to prior version;
9. corrupted prior rollback target;
10. preservation of user state.

A failed update SHALL not replace the last verified active installation.

# 38. Uninstall calibration

Pass 173 SHALL verify that default uninstall preserves:

- user workspaces;
- ledgers;
- receipts;
- databases;
- imported documents;
- explicit configuration;
- nonexclusive model assets.

Permanent deletion SHALL require a separate explicit operation.

The uninstall receipt SHALL list every deleted and preserved path class.

# 39. Offline verification

The offline profile SHALL be tested with network access blocked.

Pass 173 SHALL verify that the bundle contains every declared required artifact.

Any attempted network fallback SHALL produce:

```text
P173_OFFLINE_NETWORK_POLICY_VIOLATION
```

An offline bundle SHALL be tested for:

- complete valid content;
- missing Python wheel;
- missing native dependency;
- missing Node package;
- altered model;
- expired or invalid signature;
- unsupported platform;
- architecture mismatch.

# 40. Container verification

Pass 173 SHALL verify:

- image builds from the current inherited Runtime;
- non-root execution;
- health check;
- external-provider configuration;
- persistent state mount;
- read-only application layer where declared;
- signal handling;
- clean shutdown;
- x86-64 image;
- ARM64 image;
- architecture manifest;
- absence of embedded credentials;
- optional GPU-device visibility classification.

A container image SHALL not be treated as evidence of native desktop support.

# 41. Android verification

The Android build profile SHALL verify:

- Java;
- SDK;
- NDK;
- CMake;
- Gradle;
- declared Android platform;
- declared build tools;
- JNI native build;
- ARM64 ABI;
- x86-64 ABI where declared;
- APK or AAB identity;
- no fabricated package after failure;
- install or emulator smoke test where possible.

# 42. Public installation-status verification

Pass 173 SHALL verify the registered read-only surfaces:

```text
GET /api/runtime/installation/status
GET /api/runtime/installation/environment
GET /api/runtime/installation/profile
GET /api/runtime/installation/dependencies
GET /api/runtime/installation/receipts
GET /api/runtime/installation/health
```

These routes SHALL:

- report committed installation state;
- avoid host mutation;
- avoid secret exposure;
- report degraded provider state accurately;
- preserve public API authority;
- remain subordinate to singleton VM81 authority.

# 43. Prohibited verification shortcuts

Pass 173 SHALL not accept:

- file existence as proof of functionality;
- successful compilation as proof of runtime correctness;
- mocked provider response as proof of real provider support;
- one architecture as proof of another;
- Docker emulation as proof of physical hardware;
- historical receipts as proof of current tests;
- static code inspection as proof of clean installation;
- a generated Hash72 value as proof that its underlying operation ran;
- successful core installation as proof of full-profile installation;
- successful degraded mode as proof of assistant availability.

# 44. Evidence layout

Pass 173 SHALL produce:

```text
evidence/pass173/
├── requirements/
│   ├── traceability_matrix.json
│   ├── dependency_coverage.json
│   └── profile_coverage.json
├── environments/
│   ├── probes/
│   ├── platform_matrix.json
│   └── architecture_matrix.json
├── executions/
│   ├── clean_installs/
│   ├── upgrades/
│   ├── rollbacks/
│   ├── repairs/
│   └── uninstalls/
├── native/
│   ├── build_logs/
│   ├── symbol_reports/
│   └── equivalence/
├── providers/
├── models/
├── offline/
├── containers/
├── android/
├── faults/
├── calibration/
├── receipts/
├── replay/
└── final/
```

# 45. Required implementation layout

Pass 173 SHALL create at least:

```text
HHS_PASS_173_UNIVERSAL_INSTALLATION_FULL_COVERAGE_REDUNDANT_VERIFICATION_CALIBRATION_REPAIR_AND_REPLAY_CLOSURE_RUNTIME.md

hhs_verification/pass173/
├── __init__.py
├── requirement_scanner.py
├── dependency_scanner.py
├── coverage_matrix.py
├── environment_matrix.py
├── profile_matrix.py
├── static_audit.py
├── clean_install_runner.py
├── artifact_reconstructor.py
├── receipt_reconciler.py
├── calibration.py
├── fault_injection.py
├── repair_planner.py
├── repair_executor.py
├── replay.py
├── verdicts.py
└── report.py

schemas/pass173/
├── coverage_matrix.schema.json
├── calibration_result.schema.json
├── fault_case.schema.json
├── repair_plan.schema.json
├── verification_receipt.schema.json
└── final_verdict.schema.json

tests/pass173/
├── test_requirement_coverage.py
├── test_dependency_coverage.py
├── test_profile_matrix.py
├── test_environment_matrix.py
├── test_artifact_reconstruction.py
├── test_receipt_reconciliation.py
├── test_fault_injection.py
├── test_repair_planner.py
├── test_replay.py
└── integration/

.github/workflows/pass173-installation-verification.yml
```

# 46. CI topology

The Pass 173 workflow SHALL use separate jobs for:

```text
static requirement audit
Python dependency matrix
native Linux x86-64
native Linux ARM64
clean core installation
clean runtime installation
degraded assistant installation
external-provider installation
Node/frontend installation
offline installation
container installation
fault injection
repair and rollback
receipt reconstruction
final replay
```

macOS, Windows, Android, and real GPU jobs SHALL be required before those environments receive terminal verified status.

Unavailable specialized runners SHALL yield explicit nonterminal classifications rather than false success.

# 47. Validation cadence

Pass 173 SHALL follow the repair-forward validation policy:

```text
freeze unaffected verified evidence
→ identify changed dependency scope
→ run affected unit tests
→ run affected integration tests
→ update coverage and receipts
→ continue
→ execute one final bounded full replay
```

It SHALL avoid repeatedly running unchanged complete suites after every small repair.

# 48. Required positive acceptance cases

At minimum:

1. clean core install;
2. clean runtime install;
3. degraded assistant install;
4. external-provider install;
5. local CPU-provider install where supported;
6. local GPU-provider install on real supported hardware;
7. x86-64 native build;
8. ARM64 native build;
9. source archive without `.git`;
10. `noexec` source fallback;
11. idempotent reinstall;
12. offline install;
13. path with spaces;
14. Unicode path;
15. update;
16. rollback;
17. repair;
18. uninstall preserving data;
19. receipt reconstruction;
20. Hash216 installation-identity reconstruction;
21. Hash72 chain verification;
22. 100-event Hash216 no-ceiling probe;
23. Pass 163 clean-install verification;
24. repaired Hash72 validation probe;
25. Hash72(D||S) domain-separation probe;
26. final clean-environment replay.

# 49. Required negative acceptance cases

At minimum:

1. unsupported Python;
2. unavailable compiler;
3. malformed source archive;
4. source digest mismatch;
5. dependency-lock mismatch;
6. profile dependency leak;
7. missing optional dependency in advertised profile;
8. native symbol missing;
9. wrong architecture artifact;
10. occupied port;
11. invalid external provider;
12. model mismatch;
13. insufficient disk;
14. denied privilege;
15. stale lock;
16. concurrent mutation;
17. interrupted activation;
18. failed update;
19. corrupted rollback target;
20. offline network attempt;
21. receipt count mismatch;
22. forged Hash72 receipt;
23. altered Hash216 identity component;
24. browser-triggered privileged mutation;
25. destructive uninstall without explicit authorization.

# 50. Verdict hierarchy

Pass 173 SHALL use the following verdict hierarchy:

```text
H. INSUFFICIENT_EVIDENCE
G. STATICALLY_MAPPED
F. PARTIALLY_EXECUTED
E. DEFECT_CONFIRMED
D. REPAIR_IMPLEMENTED
C. DEPENDENCY_SCOPE_REVALIDATED
B. FULL_MATRIX_EXECUTED
A. REDUNDANTLY_VERIFIED
A+. CALIBRATED_REPAIR_REPLAY_CLOSED
```

A terminal pass requires `A+`.

# 51. Intermediate classifications

Permitted classifications:

```text
HHS_PASS_173_CONTRACT_BOUND
HHS_PASS_173_REQUIREMENT_SCAN_COMPLETED
HHS_PASS_173_DEPENDENCY_SCAN_COMPLETED
HHS_PASS_173_COVERAGE_MATRIX_BOUND
HHS_PASS_173_STATIC_AUDIT_COMPLETED
HHS_PASS_173_EXECUTED_MATRIX_PARTIAL
HHS_PASS_173_DEFECTS_CONFIRMED
HHS_PASS_173_REPAIRS_IMPLEMENTED
HHS_PASS_173_DEPENDENCY_SCOPED_REVALIDATION_PASSED
HHS_PASS_173_REDUNDANT_VERIFICATION_PASSED
HHS_PASS_173_CALIBRATION_PASSED
HHS_PASS_173_FINAL_REPLAY_PASSED
```

Terminal classification:

```text
HHS_PASS_173_UNIVERSAL_INSTALLATION_FULL_COVERAGE_REDUNDANT_VERIFICATION_CALIBRATION_REPAIR_AND_REPLAY_CLOSURE_RUNTIME_VERIFIED
```

# 52. Terminal closure requirements

Terminal closure SHALL require:

```text
pass172_contract_fully_mapped = true
required_profiles_verified = true
required_platforms_verified = true
required_architectures_verified = true
dependency_coverage_complete = true
positive_matrix_failures = 0
negative_matrix_unclassified = 0
receipt_mismatches = 0
unrepaired_confirmed_defects = 0
authority_bypasses = 0
data_loss_events = 0
independent_lane_agreement = true
hash216_identity_reconstructed = true
hash72_receipt_chain_verified = true
final_clean_replay_match = true
omega_173 = true
terminal = true
```

# 53. Honest nonclaims

Until terminal closure, Pass 173 SHALL not claim:

- Pass 172 works in every environment;
- Windows is verified;
- macOS is verified;
- Python 3.13 is supported;
- ARM64 LiteRT-LM is supported;
- local GPU installation works;
- offline installation is complete;
- every native project is installed;
- every Node GUI is reproducible;
- all historical receipt counts remain current;
- all declared repairs have been executed;
- full repository CI is closed;
- external kernel-prototype code is part of the repository.

# 54. Final normative statement

Pass 172 establishes:

```text
ONE COMMAND → VERIFIED INSTALLATION
```

Pass 173 establishes whether that statement is actually true.

The Pass 173 invariant is:

```text
INSTALLATION CLAIM ≠ INSTALLATION EVIDENCE
```

Instead:

```text
INSTALLATION CLAIM
→ REQUIREMENT TRACE
→ INDEPENDENT EXECUTION
→ REDUNDANT RECONSTRUCTION
→ CALIBRATION
→ FAULT INJECTION
→ BOUNDED REPAIR
→ DEPENDENCY-SCOPED REVALIDATION
→ FINAL REPLAY
→ RECEIPT CLOSURE
```

Therefore:

```text
PASS 172 INSTALLED
∧ PASS 173 REDUNDANTLY VERIFIED
∧ PASS 173 CALIBRATED
∧ PASS 173 REPAIRED
∧ PASS 173 REPLAY CLOSED
⇒ UNIVERSAL INSTALLATION CLAIM ADMISSIBLE
```

No installation profile, operating system, architecture, provider topology, model path, native artifact, dependency set, repair, or completion receipt may be classified verified without executed evidence at its actual declared boundary.
