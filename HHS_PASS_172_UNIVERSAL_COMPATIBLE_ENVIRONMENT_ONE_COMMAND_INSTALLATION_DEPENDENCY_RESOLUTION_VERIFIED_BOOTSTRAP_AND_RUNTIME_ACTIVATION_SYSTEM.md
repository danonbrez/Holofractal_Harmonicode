# HHS PASS 172 — UNIVERSAL COMPATIBLE-ENVIRONMENT ONE-COMMAND INSTALLATION, DEPENDENCY RESOLUTION, VERIFIED BOOTSTRAP, AND RUNTIME ACTIVATION SYSTEM
 
## Capability-Probed Host Provisioning, Transactional Source Acquisition, Profile-Scoped Dependency Installation, Portable Native ABI Compilation, LiteRT-LM Provider Selection, Model-Asset Governance, Container and Android Adapters, Offline Bundles, Atomic Repair and Upgrade, IDE-Registered Installation Management, Singleton VM81 Authority Preservation, Hash216 Installation Identity, Hash72 Execution Receipts, and Deterministic Installation Replay
 
# 1. Normative metadata
 
| Field | Normative value |
|---|---|
| Contract identifier | `HHS-P172-UCEOCI-DRVBRAS` |
| Pass number | `172` |
| Canonical pass name | `UNIVERSAL_COMPATIBLE_ENVIRONMENT_ONE_COMMAND_INSTALLATION_DEPENDENCY_RESOLUTION_VERIFIED_BOOTSTRAP_AND_RUNTIME_ACTIVATION_SYSTEM` |
| Short name | `P172 Universal Installer` |
| Contract version | `1.0.0` |
| Repository | `danonbrez/Holofractal_Harmonicode` |
| Authoritative baseline | Current authoritative `main`, including the complete Pass 171 contract nucleus |
| Immediate inheritance parent | Complete authoritative Pass 171 inherited pass-history nucleus |
| Source-language authority | HARMONICODE |
| Canonical execution authority | Exactly one VM81 Runtime authority |
| Canonical mutation authority | Exactly one admitted VM81 commit path |
| Installation authority | Bounded host-provisioning transaction defined by this contract |
| Application-development authority | IDE-registered public API workflow compilation |
| Native language requirement | Portable ISO C11 |
| Canonical arithmetic | Exact integer, rational, modular, symbolic, tensor, and prime-exponent representations |
| Floating-point authority | Forbidden for canonical HHS authority |
| Installation state identity | Hash216 |
| Installation action evidence | Hash72 |
| Validation policy | Test-first, dependency-scoped, bounded stage-gate, repair-forward |
| Initial status | `CONTRACT_AUTHORIZED — FULL IMPLEMENTATION REQUIRED` |
 
# 2. Purpose
 
Pass 172 SHALL provide a complete installation system through which a user can acquire, provision, validate, activate, repair, update, and remove HHS through one user-facing command in every environment that satisfies a declared compatibility profile.
 
The installation system SHALL convert:

```text
compatible host + one installation command + declared profile or automatic profile selection
```

into:

```text
verified HHS source + isolated dependency environment + portable native Runtime ABI + initialized HHS state directories + selected inference-provider topology + registered application and API surfaces + dependency-scoped validation + optional immediate startup + deterministic installation receipt
```

The installer SHALL NOT describe an environment as compatible merely because a shell script can begin execution.
 
Compatibility SHALL be established by an executable capability probe before authoritative installation mutation begins.
 
# 3. Governing installation theorem
 
For a host \(H\), requested profile \(P\), resolved dependency plan \(D\), source identity \(S\), native build \(N\), runtime configuration \(R\), and completion receipt \(C\):
 
\[
\operatorname{Installable}(H,P) \iff \operatorname{Probe}(H,P)=\mathrm{COMPATIBLE}.
\]
 
A completed installation SHALL satisfy:
 
\[
\operatorname{Installed}(H,P) \iff S_{\mathrm{verified}} \land D_{\mathrm{closed}} \land N_{\mathrm{verified}} \land R_{\mathrm{validated}} \land C_{\mathrm{closed}}.
\]
 
The one-command guarantee SHALL therefore mean:

```text
ONE USER-FACING COMMAND
⇒ ENVIRONMENT PROBED
∧ PROFILE RESOLVED
∧ SOURCE ACQUIRED
∧ SOURCE VERIFIED
∧ DEPENDENCIES RESOLVED
∧ NATIVE ABI BUILT
∧ RUNTIME INITIALIZED
∧ PROVIDER CLASSIFIED
∧ TARGETED TESTS PASSED
∧ INSTALLATION ACTIVATED
∧ RECEIPT CLOSED
```

It SHALL NOT mean:

```text
every operating system is automatically compatible
```

or:

```text
hardware, drivers, credentials, licenses, network access, or unavailable third-party packages may be fabricated
```

# 4. Authority boundary
 
## 4.1 Installer authority
 
Before the canonical Runtime exists on a host, the Pass 172 installer MAY perform only the following bounded host-provisioning operations:
 
1. inspect host capabilities;
2. create an installation plan;
3. acquire a declared HHS source or release;
4. verify manifests, signatures, and digests;
5. create HHS-owned directories;
6. create isolated language environments;
7. invoke allowlisted system package managers;
8. compile declared native targets;
9. acquire optional runtime assets;
10. register launchers and local services;
11. run installation validation;
12. activate or roll back the staged installation;
13. emit installation evidence.
 
The installer SHALL NOT:
 
- interpret HARMONICODE as an independent execution engine;
- perform authoritative tensor computation;
- instantiate a second VM81 Runtime;
- create an alternate Hash72 or Hash216 authority;
- create a second state ledger;
- mutate canonical HHS runtime state outside VM81 admission;
- treat successful host provisioning as a VM81 computation receipt;
- grant itself continuing unrestricted host authority after installation.
 
## 4.2 Post-installation management authority
 
After installation, update, repair, profile migration, model import, service registration, and removal operations SHALL be exposed as registered installation-management operations.
 
They SHALL use:

```text
LOCAL USER REQUEST
→ PUBLIC INSTALLATION OPERATION
→ INSTALLATION CAPABILITY CHECK
→ DECLARED HOST-MUTATION PLAN
→ EXPLICIT LOCAL AUTHORIZATION
→ TRANSACTIONAL EXECUTION
→ VALIDATION
→ HASH72 RECEIPT
```
 
No browser route, model response, remote API client, IDE extension, or unauthenticated network request may silently trigger privileged package installation or host mutation.
 
## 4.3 Runtime authority preservation
 
The following invariant is binding:

```text
INSTALLER AUTHORITY ≠ RUNTIME AUTHORITY
```
 
The installer provisions and verifies the Runtime.
 
It does not replace the Runtime.
 
# 5. Definition of a compatible environment
 
A compatible environment SHALL satisfy one complete installation profile.
 
Every profile SHALL require:
 
- a supported processor and operating-system execution model;
- an eight-bit byte;
- exact fixed-width 64-bit integer support;
- a writable installation or portable-runtime location;
- sufficient storage for the selected profile;
- a supported Python 3.11 or newer interpreter, or permission to install one;
- a supported native C11 compiler, or a verified prebuilt native artifact;
- a mechanism for launching child processes;
- a loopback network stack for local API operation;
- cryptographic digest support;
- an environment in which the source and dependency manifests can be verified.
 
Network access SHALL NOT be mandatory when a complete verified offline bundle is supplied.
 
Administrative access SHALL NOT be mandatory when the user-local profile can satisfy all dependencies.
 
# 6. Compatibility classifications
 
The probe SHALL return exactly one primary classification:

```text
HHS_ENVIRONMENT_FULLY_COMPATIBLE
HHS_ENVIRONMENT_COMPATIBLE_WITH_EXTERNAL_PROVIDER
HHS_ENVIRONMENT_COMPATIBLE_WITH_CPU_PROVIDER
HHS_ENVIRONMENT_COMPATIBLE_IN_ASSISTANT_DEGRADED_MODE
HHS_ENVIRONMENT_CORE_ONLY_COMPATIBLE
HHS_ENVIRONMENT_ANDROID_BUILD_COMPATIBLE
HHS_ENVIRONMENT_CONTAINER_COMPATIBLE
HHS_ENVIRONMENT_OFFLINE_BUNDLE_COMPATIBLE
HHS_ENVIRONMENT_REPAIRABLE
HHS_ENVIRONMENT_INCOMPATIBLE
```
 
An environment MAY be compatible with several profiles. The probe SHALL report all compatible profiles and SHALL select only one resolved profile for a given transaction.
 
An incompatibility report SHALL identify:
 
- failed capability;
- required capability;
- detected value;
- affected profile;
- whether automatic repair is available;
- whether a reduced profile remains compatible;
- exact remediation guidance;
- whether any host mutation occurred.
 
# 7. Canonical installation profiles
 
## 7.1 `auto`
 
The default profile SHALL select the greatest safely supportable profile without claiming absent capabilities.
 
Resolution order:

```text
local GPU assistant → local CPU assistant → protected external provider → assistant-degraded API/UI → core runtime
```
 
The resolution SHALL account for:
 
- platform;
- architecture;
- available compiler;
- provider support;
- GPU and driver availability;
- Vulkan or Metal capability;
- model availability;
- network policy;
- disk and memory capacity;
- interactive versus noninteractive execution;
- explicit user restrictions.
 
## 7.2 `core`
 
Installs:
 
- canonical Python runtime;
- native HHS C ABI;
- VM81 executable;
- HARMONICODE runtime surfaces;
- Hash72 and Hash216 authority modules;
- CLI;
- runtime schemas;
- dependency-scoped core validation.
 
Does not require:
 
- Node.js;
- browser build tooling;
- LiteRT-LM;
- model weights;
- GPU;
- Vulkan;
- Android tooling;
- multimedia capture tools.
 
## 7.3 `runtime`
 
Adds:
 
- FastAPI and WebSocket runtime;
- visual server;
- static Pass 161 interface;
- persistent runtime directories;
- API health and status routes;
- provider-disabled or degraded assistant state.
 
## 7.4 `assistant-external`
 
Adds:
 
- external LiteRT-LM provider configuration;
- authenticated or protected provider-endpoint validation;
- model-registry verification;
- provider health validation.
 
It SHALL NOT install local GPU drivers or model weights.
 
## 7.5 `assistant-local-cpu`
 
Adds:
 
- isolated LiteRT-LM environment;
- compatible local CPU inference backend;
- optional model acquisition and import;
- bounded local provider supervision.
 
This is a compatibility and diagnostic profile unless promoted by later evidence.
 
## 7.6 `assistant-local-gpu`
 
Adds:
 
- supported physical accelerator;
- vendor driver verification;
- Vulkan loader and device verification on Linux or Windows;
- Metal verification on macOS;
- container device-access verification where applicable;
- LiteRT-LM local provider;
- model acquisition and import;
- provider startup and model-registry verification.
 
The installer SHALL NOT claim to install:
 
- physical GPU hardware;
- proprietary vendor drivers unless a separately authorized adapter exists;
- kernel-level device access;
- hypervisor GPU assignment;
- container GPU passthrough.
 
## 7.7 `developer`
 
Adds:
 
- Node.js 22 or newer;
- npm;
- Pass 161 verification and packaging surfaces;
- Vite and Three.js dependencies where required;
- Playwright and browser dependencies where requested;
- formatting and development Python dependencies;
- test compilers and diagnostics;
- optional FFmpeg media-evidence tooling.
 
## 7.8 `android-build`
 
Adds:
 
- supported Java Development Kit;
- Android SDK;
- Android NDK;
- CMake;
- Gradle or the repository Gradle wrapper;
- Android platform and build-tool versions declared by the project;
- ARM64 and x86-64 JNI build validation;
- APK receipt generation.
 
This profile builds the Android projection. It SHALL NOT silently classify a desktop runtime installation as an Android application installation.
 
## 7.9 `container`
 
Builds or installs a current HHS OCI image through a declared container adapter.
 
It SHALL distinguish:
 
- CPU-only API/UI container;
- external-provider container;
- local-GPU provider container;
- split web-host/provider topology;
- development container.
 
## 7.10 `offline`
 
Uses only verified local source, dependency, wheel, package, native-artifact, and optional model bundles.
 
No network fallback is permitted after offline mode has been selected.
 
# 8. One-command user surfaces
 
Pass 172 SHALL implement equivalent command semantics through the following entrypoints.
 
## 8.1 POSIX network bootstrap

```sh
curl -fsSL \
  https://github.com/danonbrez/Holofractal_Harmonicode/releases/latest/download/hhs-install.sh \
  | sh -s -- --profile auto --start
```
 
## 8.2 Windows PowerShell bootstrap

```powershell
irm https://github.com/danonbrez/Holofractal_Harmonicode/releases/latest/download/hhs-install.ps1 | iex
```
 
The PowerShell bootstrap SHALL accept the same logical profile and policy options as the POSIX bootstrap.
 
## 8.3 Repository-local installation

```sh
./hhs install --profile auto --start
```
 
## 8.4 Portable Python bootstrap

```sh
python3 hhs-bootstrap.py install --profile auto --start
```
 
## 8.5 Offline installation

```sh
./hhs install \
  --profile offline \
  --bundle /path/to/hhs-offline-bundle \
  --start
```
 
The public commands MAY differ syntactically by shell, but SHALL compile to the same canonical installation request schema.
 
# 9. One-command semantics
 
A command SHALL remain one-command compliant when it:
 
- requests a password through the host’s normal privilege mechanism;
- asks the user to accept an explicitly displayed license;
- asks whether a large optional model should be downloaded;
- asks which of two equally valid installation locations should be used;
- requests a required credential through a non-echoing prompt.
 
A command SHALL not be one-command compliant when it requires the user to:
 
- manually clone the repository;
- manually create a virtual environment;
- manually run multiple package-manager commands;
- manually compile the native runtime;
- manually copy shared libraries;
- manually edit environment files;
- manually import a model;
- manually invoke a second validation script;
- manually repair a predictable path or shell incompatibility.
 
# 10. Canonical command set
 
The installed `hhs` launcher SHALL provide:

```text
hhs install
hhs start
hhs stop
hhs restart
hhs status
hhs doctor
hhs verify
hhs repair
hhs update
hhs rollback
hhs uninstall
hhs profile
hhs provider
hhs model
hhs environment
hhs receipt
hhs replay-install
```
 
The following aliases MAY exist:

```text
make setup
make start
make setup-start
bash init.sh
bash start.sh
```
 
They SHALL become thin compatibility adapters over the Pass 172 installer rather than separate provisioning authorities.
 
# 11. Installation request schema
 
Every request SHALL normalize to:

```json
{
  "contract_id": "HHS-P172-UCEOCI-DRVBRAS",
  "operation": "install",
  "source": {
    "kind": "release|git|local|offline_bundle",
    "reference": "string",
    "expected_identity": "optional"
  },
  "profile": "auto",
  "install_mode": "user|portable|system|container",
  "start_after_install": true,
  "network_policy": "online|cached_only|offline",
  "privilege_policy": "prompt|never|preauthorized",
  "provider_policy": "auto|local|external|disabled",
  "model_policy": "auto|download|existing|skip",
  "preserve_user_data": true,
  "noninteractive": false
}
```
 
Unknown fields SHALL be rejected unless introduced through a versioned schema extension.
 
# 12. Dependency graph
 
Pass 172 SHALL maintain a machine-readable dependency graph rather than a flat undocumented package list.
 
Every dependency record SHALL contain:

```text
dependency_id
dependency_class
version_constraint
source
license
digest or lock identity
required_profiles
required_platforms
required_architectures
installation_adapter
verification_operation
optional flag
fallback dependency
rollback policy
security classification
```
 
Dependency classes SHALL include:

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
 
# 13. Dependency separation
 
The existing combined dependency surface SHALL be separated into at least:

```text
requirements-core.txt
requirements-runtime.txt
requirements-provider-litert-lm.txt
requirements-test.txt
requirements-dev.txt
requirements-android-tools.txt
```
 
A locked installation SHALL use generated, reviewed lock artifacts such as:

```text
requirements-lock/linux-x86_64.txt
requirements-lock/linux-aarch64.txt
requirements-lock/macos-arm64.txt
requirements-lock/macos-x86_64.txt
requirements-lock/windows-x86_64.txt
```
 
Equivalent lock formats MAY be used when they preserve:
 
- exact package identity;
- transitive dependency identity;
- hash verification;
- environment marker;
- Python version;
- platform and architecture;
- reproducible resolution.
 
The default runtime installation SHALL NOT install formatters, browser-test frameworks, or unrelated development tools.
 
The core or degraded profile SHALL NOT install LiteRT-LM merely because the full development requirements file references it.
 
# 14. Environment probing
 
The probe SHALL inspect, without mutation:
 
- operating system and version;
- architecture;
- shell;
- Python candidates and versions;
- venv capability;
- pip capability;
- compiler candidates;
- linker;
- symbol-inspection tool;
- Make or alternate build orchestrator;
- available package managers;
- writable locations;
- available disk space;
- available memory;
- loopback socket support;
- candidate ports;
- Node.js and npm;
- Java;
- Android environment variables;
- Android SDK/NDK/CMake/Gradle;
- container runtime;
- GPU devices;
- Vulkan loader;
- Vulkan ICD manifests;
- Metal capability;
- external provider reachability;
- configured proxy and certificate policy;
- existing HHS installations;
- existing model registry;
- offline cache state.
 
The probe SHALL not execute arbitrary binaries discovered in untrusted project directories without validating their origin and path.
 
# 15. Platform adapters
 
## 15.1 Linux
 
Initial package-manager adapters SHALL support:

```text
apt/apt-get
dnf
yum
pacman
apk
zypper
```
 
Adapters SHALL resolve distribution-appropriate packages for:
 
- Python 3.11+;
- venv support;
- pip;
- C11 compiler;
- linker;
- standard build tools;
- optional Vulkan loader;
- optional Vulkan diagnostics;
- optional Node.js;
- optional FFmpeg;
- optional Java and Android prerequisites.
 
No adapter may assume package names are identical across distributions.
 
## 15.2 macOS
 
The macOS adapter SHALL support:
 
- Apple Silicon and Intel where validated;
- system or Homebrew Python;
- Apple Clang or validated LLVM;
- `.dylib` output;
- macOS-compatible symbol inspection;
- Metal provider probing;
- user-local launch agents where requested;
- no Linux Vulkan-loader installation.
 
Homebrew MAY be used when already present or explicitly authorized. Its installation SHALL not be silently bootstrapped without user authorization.
 
## 15.3 Windows
 
The Windows adapter SHALL provide native PowerShell operation and MAY provide a WSL adapter.
 
Native Windows support SHALL account for:
 
- Python launcher resolution;
- isolated virtual environments;
- LLVM/Clang, MinGW-w64, or another validated C11 toolchain;
- `.dll` output;
- Windows import/export behavior;
- `dumpbin`, `llvm-nm`, or another verified symbol inspector;
- PowerShell execution policy;
- long paths;
- path separators;
- spaces and Unicode in paths;
- service or startup registration;
- Windows Vulkan-loader and driver probing;
- firewall prompts;
- process cleanup.
 
Native Windows SHALL not invoke GNU-only `nm -D` or assume `.so` output.
 
## 15.4 Android and Termux
 
A Termux or Android-shell environment MAY qualify for core or runtime installation when its capabilities pass the probe.
 
The Android adapter SHALL recognize that:
 
- Android supplies its Vulkan loader through the operating system;
- package management differs from desktop Linux;
- application sandboxing affects writable paths;
- background services and loopback binding may be restricted;
- local model-provider support must be independently verified;
- APK production requires the separate Android build profile.
 
## 15.5 BSD and other POSIX environments
 
A POSIX environment not named above MAY qualify through capability-based probing.
 
It SHALL not be labeled supported until:
 
- the native ABI compiles;
- shared-library loading works;
- required Python wheels or source builds succeed;
- the bounded validation matrix passes;
- an installation receipt is produced.
 
## 15.6 Containers and restricted clouds
 
The installer SHALL detect:
 
- read-only root filesystems;
- missing init systems;
- ephemeral storage;
- non-root execution;
- unavailable package managers;
- injected ports;
- mounted persistent volumes;
- GPU device visibility;
- external provider configuration.
 
It SHALL prefer user-local or image-build operations over runtime mutation of immutable container layers.
 
# 16. Portable native build
 
The Pass 172 native builder SHALL remove platform identity from hardcoded Makefile assumptions.
 
It SHALL resolve:

```text
compiler
compile flags
position-independent-code flags
shared-library suffix
executable suffix
linker flags
math-library requirements
symbol-inspection operation
runtime search path
```
 
Expected native artifacts SHALL be platform mapped:

```text
Linux:   libhhs_runtime.so
macOS:   libhhs_runtime.dylib
Windows: hhs_runtime.dll
```
 
The builder SHALL support at least:

```text
gcc
clang
Apple Clang
validated MinGW-w64 GCC
validated Windows LLVM/Clang
```
 
MSVC support MAY be admitted only after the strict native matrix passes without semantic substitution.
 
The canonical build driver SHALL be callable from Python so installation does not require GNU Make when the native compiler can be invoked directly.
 
Make SHALL remain a development and compatibility surface.
 
# 17. Native ABI validation
 
Native validation SHALL verify:
 
- compiler success;
- zero unexpected warnings under the selected strict profile;
- expected artifact location;
- expected artifact type;
- required exported symbols;
- VM81 executable startup;
- ABI version;
- Hash216 operation;
- Hash72 operation;
- positive native matrix;
- negative native matrix;
- Python-to-C loading;
- exact platform library resolution;
- repeated clean-build identity where reproducibility is claimed.
 
A file merely existing at the expected path SHALL not satisfy validation.
 
# 18. Python environment
 
The installer SHALL default to an isolated HHS-owned virtual environment.
 
It SHALL NOT install Python dependencies into the global interpreter unless:
 
- system mode was explicitly selected;
- the environment is externally managed for that purpose;
- the mutation plan identifies the target environment;
- the user authorized the operation.
 
Default locations:

```text
portable mode: <repository>/.hhs/python/
user mode:     <HHS_HOME>/runtime/python/
system mode:   platform-defined managed prefix
```
 
The installer SHALL verify:
 
- Python version;
- architecture;
- venv creation;
- pip version;
- TLS/certificate functionality when online;
- wheel compatibility;
- package hashes;
- import closure;
- dependency conflicts.
 
# 19. Node and frontend dependencies
 
Node.js SHALL be required only for profiles that build, test, audit, or package frontend applications.
 
A runtime installation MAY use prebuilt static assets and SHALL not require Node.js solely to serve them.
 
The developer profile SHALL verify:
 
- Node.js 22 or newer;
- npm availability;
- package-manifest consistency;
- lockfile presence;
- reproducible dependency installation;
- browser application tests;
- frontend build;
- packaging scripts.
 
Pass 172 implementation SHALL add and maintain lockfiles for all npm-managed applications admitted into the installation profile.
 
# 20. LiteRT-LM provider resolution
 
Provider resolution SHALL occur after core Runtime installation is validated.
 
The provider state SHALL be exactly one of:

```text
LOCAL_GPU_READY
LOCAL_CPU_READY
EXTERNAL_READY
DISABLED
DEGRADED
INCOMPATIBLE
```
 
## 20.1 Local GPU
 
The installer SHALL verify:
 
- LiteRT-LM platform support;
- GPU device presence;
- vendor-driver availability;
- Vulkan or Metal availability;
- process device access;
- model compatibility;
- sufficient resources;
- provider startup;
- `/v1/models` response;
- selected model registration.
 
## 20.2 Local CPU
 
The installer SHALL verify actual provider startup and model loading. Availability of a Python package alone is insufficient.
 
## 20.3 External provider
 
The installer SHALL require:
 
- a valid URL;
- protected transport or an explicit local/private-network classification;
- provider health;
- model identity;
- request timeout;
- no direct unauthenticated public exposure claim.
 
Credentials SHALL be stored through a platform-appropriate secret mechanism or explicit protected configuration file with restrictive permissions.
 
## 20.4 Degraded mode
 
Failure of an optional provider SHALL not invalidate a compatible API/UI installation unless strict provider startup was requested.
 
The completion receipt SHALL clearly state:

```text
assistant_available: false
assistant_mode: degraded
core_runtime_verified: true
```
 
# 21. Model-asset governance
 
Model files SHALL remain runtime assets rather than Git source.
 
Before model acquisition, the installer SHALL determine:
 
- model registry identifier;
- source repository;
- filename;
- declared version;
- license;
- authentication requirement;
- expected download size when discoverable;
- available disk capacity;
- digest or upstream identity;
- import destination;
- provider compatibility.
 
The installer SHALL:
 
- use temporary partial-download paths;
- support bounded resume where safe;
- verify the complete asset before import;
- quarantine mismatches;
- never log access tokens;
- avoid duplicate imports;
- emit a model-import receipt;
- preserve user choice to skip the model.
 
# 22. Source acquisition and supply-chain verification
 
Supported source forms:

```text
signed release
immutable commit
declared branch
local checkout
verified offline bundle
```
 
The default network bootstrap SHOULD use a signed release rather than mutable branch source.
 
Every release SHALL include:

```text
source manifest
dependency manifest
file digests
installer digests
supported-profile manifest
platform matrix
release signature or signed attestation
SBOM
license inventory
completion receipt
```
 
The minimal downloaded bootstrap SHALL verify the larger installer payload before executing it.
 
No archive SHALL be extracted before:
 
- archive type validation;
- total expanded-size bounds;
- entry-count bounds;
- path traversal checks;
- absolute-path rejection;
- symlink policy checks;
- duplicate-path rejection;
- digest validation.
 
# 23. Installation filesystem layout
 
The default user installation SHALL use:

```text
<HHS_HOME>/
├── versions/
│   └── <version-or-source-id>/
├── current -> versions/<active>/
├── runtime/
│   ├── python/
│   ├── native/
│   ├── graphics/
│   ├── provider/
│   └── models/
├── state/
│   ├── databases/
│   ├── ledgers/
│   ├── vector-store/
│   ├── receipts/
│   └── workspaces/
├── install/
│   ├── probes/
│   ├── plans/
│   ├── journals/
│   ├── locks/
│   ├── receipts/
│   └── quarantine/
├── logs/
└── bin/
    └── hhs
```
 
`HHS_HOME` SHALL be configurable.
 
User data SHALL be separated from versioned source and executable artifacts so update and rollback do not overwrite canonical user state.
 
# 24. Installation state machine
 
The authoritative installation transaction SHALL use:

```text
UNSEEN
→ PROBED
→ COMPATIBLE
→ PLANNED
→ AUTHORIZED
→ SOURCE_ACQUIRED
→ SOURCE_VERIFIED
→ STAGED
→ HOST_DEPENDENCIES_READY
→ PYTHON_READY
→ NATIVE_READY
→ RUNTIME_READY
→ PROVIDER_CLASSIFIED
→ VALIDATED
→ ACTIVATED
→ RECEIPT_CLOSED
```
 
Failure transitions:

```text
ANY PRE-ACTIVATION STATE → FAILED → QUARANTINED → ROLLED_BACK
```
 
Interrupted transactions SHALL enter:

```text
INTERRUPTED → RECOVERY_REQUIRED
```
 
Recovery SHALL either:
 
- continue from the last verified idempotent boundary; or
- roll back to the previous active installation.
 
It SHALL never guess that an interrupted step completed.
 
# 25. Transactionality and activation
 
All HHS-owned installation content SHALL be staged outside the active installation.
 
Activation SHALL use an atomic platform-appropriate operation such as:
 
- atomic rename;
- symlink or junction switch;
- version pointer replacement;
- manifest-controlled launcher update.
 
The previous working version SHALL remain available until the new version passes activation validation.
 
Host package-manager operations that cannot be atomically rolled back SHALL be:
 
- listed in advance;
- executed before HHS activation;
- recorded individually;
- excluded from false full-rollback claims.
 
# 26. Idempotence
 
Repeating the same installation request against the same verified state SHALL produce:

```text
NO_UNNECESSARY_DOWNLOAD
NO_DUPLICATE_MODEL_IMPORT
NO_DUPLICATE_SERVICE
NO_DUPLICATE_PATH_ENTRY
NO_DUPLICATE_RUNTIME_STATE
NO_CANONICAL_STATE_MUTATION
```
 
The installer MAY emit a new execution receipt while preserving the same installation identity.
 
# 27. Update and rollback
 
`hhs update` SHALL:
 
1. probe current installation health;
2. acquire the target version;
3. verify the target;
4. calculate a migration plan;
5. back up mutable configuration;
6. stage the new version;
7. run dependency-scoped validation;
8. activate atomically;
9. run post-activation verification;
10. retain a rollback pointer;
11. close an update receipt.
 
Rollback SHALL restore:
 
- prior executable version;
- prior dependency environment where version-bound;
- prior configuration schema;
- prior launcher target;
- prior service definition.
 
User-created artifacts SHALL not be deleted by rollback.
 
# 28. Repair
 
`hhs doctor` SHALL be read-only.
 
`hhs repair` MAY correct:
 
- missing virtual environment;
- incomplete dependency installation;
- stale native build;
- broken launcher;
- incorrect file permissions;
- missing runtime directories;
- invalid current-version pointer;
- unavailable optional provider;
- corrupted generated environment file;
- incomplete model import;
- stale service definition.
 
Repair SHALL not weaken an invariant or bypass a failed authority check.
 
# 29. Uninstallation
 
Default uninstallation SHALL remove:
 
- executable versions;
- managed virtual environments;
- managed native artifacts;
- managed launchers;
- managed service definitions;
- generated caches;
- installation journals no longer required.
 
It SHALL preserve by default:
 
- user workspaces;
- canonical ledgers;
- receipts;
- databases;
- imported documents;
- model assets not exclusively owned by the installation;
- explicit user configuration.
 
Permanent data deletion SHALL require a separate explicit option and a displayed deletion manifest.
 
# 30. Offline bundle
 
The offline bundle SHALL contain every artifact required for its declared profiles:

```text
HHS source or release
Python wheels
Python lock files
native source or verified prebuilt artifacts
Node packages or prebuilt frontend
installer adapters
system-dependency declarations
optional LiteRT-LM package
optional model asset
SBOM
licenses
digests
signatures
platform manifest
```
 
The bundle SHALL declare which host-level packages must already exist.
 
Offline installation SHALL fail rather than contact the network.
 
# 31. Container installation
 
Pass 172 SHALL replace pass-specific container assumptions with a current inherited-runtime container definition.
 
Required image stages:

```text
source verification
dependency resolution
native build
frontend build when selected
runtime image assembly
non-root execution setup
health verification
SBOM generation
image identity receipt
```
 
The default runtime container SHALL:
 
- run as a non-root user;
- use a read-only application layer where practical;
- expose configurable ports;
- mount persistent state explicitly;
- support external-provider mode;
- avoid embedding private model credentials;
- support optional GPU-device pass-through without claiming to create it.
 
# 32. Android integration
 
The Pass 172 installer SHALL register the existing Pass 145 Android build as an optional target.
 
It SHALL:
 
- probe Java;
- probe Android SDK;
- probe NDK;
- probe CMake;
- probe Gradle;
- verify required platform packages;
- build JNI native artifacts;
- build declared ABIs;
- generate APK or AAB only when the toolchain is complete;
- hash the produced package;
- emit an explicit failure receipt when unavailable;
- never fabricate an APK.
 
# 33. Public API and IDE registration
 
The installation-management workflow SHALL be registered in the Pass 161/170/171 application environment.
 
At minimum, the post-install runtime SHALL expose read-only routes:

```text
GET /api/runtime/installation/status
GET /api/runtime/installation/environment
GET /api/runtime/installation/profile
GET /api/runtime/installation/dependencies
GET /api/runtime/installation/receipts
GET /api/runtime/installation/health
```
 
Host-mutating operations SHALL not be generally callable through an unauthenticated HTTP route.
 
An optional local-only management route MAY produce a signed proposal:

```text
POST /api/runtime/installation/proposals
```
 
Execution of that proposal SHALL require:
 
- local installation capability;
- explicit user authorization;
- loopback or authenticated administrative transport;
- command-plan review;
- bounded operation identity;
- fresh expiry;
- replay protection.
 
# 34. Installation identity
 
The installation identity SHALL bind:

```text
contract version
source commit or release identity
source manifest
profile
platform
architecture
dependency lock identities
native artifact identities
frontend artifact identity
provider classification
model identity when installed
configuration schema
validation evidence
```
 
Canonical identity:
 
\[
I_{172}=\operatorname{Hash216}
\left(
C\parallel S\parallel P\parallel A\parallel D\parallel N\parallel F\parallel V\parallel M\parallel E
\right).
\]
 
Host-specific paths, timestamps, process identifiers, and random temporary names SHALL not contaminate reproducible content identities.
 
They MAY appear in noncanonical execution metadata.
 
# 35. Hash72 installation receipts
 
Required receipt classes:

```text
P172_ENVIRONMENT_PROBE_RECEIPT
P172_COMPATIBILITY_DECISION_RECEIPT
P172_INSTALLATION_PLAN_RECEIPT
P172_PRIVILEGE_AUTHORIZATION_RECEIPT
P172_SOURCE_ACQUISITION_RECEIPT
P172_SOURCE_VERIFICATION_RECEIPT
P172_HOST_DEPENDENCY_RECEIPT
P172_PYTHON_ENVIRONMENT_RECEIPT
P172_NATIVE_BUILD_RECEIPT
P172_FRONTEND_BUILD_RECEIPT
P172_PROVIDER_CLASSIFICATION_RECEIPT
P172_MODEL_IMPORT_RECEIPT
P172_RUNTIME_INITIALIZATION_RECEIPT
P172_VALIDATION_RECEIPT
P172_ACTIVATION_RECEIPT
P172_REPAIR_RECEIPT
P172_UPDATE_RECEIPT
P172_ROLLBACK_RECEIPT
P172_UNINSTALL_RECEIPT
P172_COMPLETION_RECEIPT
```
 
Every mutating step SHALL bind:
 
- prior installation tip;
- operation class;
- requested profile;
- resolved profile;
- plan identity;
- affected paths;
- affected external packages;
- result;
- failure classification;
- resulting installation identity.
 
# 36. Security requirements
 
The installer SHALL defend against:
 
- archive path traversal;
- malicious symlinks;
- command injection;
- shell-argument injection;
- dependency confusion;
- unverified package indexes;
- mutable unpinned release assets;
- poisoned PATH entries;
- writable compiler substitution;
- malicious environment variables;
- insecure temporary files;
- credential leakage;
- world-readable secrets;
- untrusted proxy certificates;
- partial downloads;
- digest downgrade;
- signature bypass;
- replayed management proposals;
- privilege escalation outside the declared plan;
- remote browser-triggered host mutation;
- model-file substitution;
- DLL or shared-library search-order attacks.
 
Temporary files SHALL use secure creation semantics and restrictive permissions.
 
# 37. Privilege policy
 
Default installation SHALL be user-local and unprivileged.
 
Privilege elevation SHALL be used only for declared host dependencies that cannot be satisfied locally.
 
Before elevation, the installer SHALL display or emit:

```text
command
package manager
packages
reason
expected filesystem scope
rollback limitations
```
 
Noninteractive elevation SHALL require explicit preauthorization.
 
No password or token may be recorded in logs or receipts.
 
# 38. Port and process management
 
The installer SHALL detect conflicts for:

```text
HHS API/UI port
LiteRT-LM provider port
optional development-server ports
```
 
It SHALL:
 
- reuse a verified compatible provider when configured;
- select an alternate user-approved port when permitted;
- reject incompatible listeners;
- avoid killing unrelated processes;
- record selected ports;
- install clean process-shutdown handling.
 
# 39. Configuration generation
 
Generated configuration SHALL be:
 
- schema validated;
- minimally scoped;
- deterministic where host values permit;
- written atomically;
- permission restricted;
- separated from source-controlled defaults;
- migration versioned.
 
Environment-variable overrides SHALL remain available.
 
Generated shell files SHALL never interpolate untrusted values without safe quoting.
 
# 40. Validation strategy
 
Pass 172 SHALL follow:

```text
tests developed first
→ installer implementation
→ dependency-scoped regression
→ clean-environment integration
→ cross-platform installation
→ interruption and repair tests
→ one bounded final replay
```
 
Previously verified unrelated pass evidence SHALL not be repeatedly rerun unless affected by dependency changes.
 
# 41. Required positive test matrix
 
The implementation SHALL execute tests for:
 
1. clean Linux user-local core installation;
2. clean Linux runtime installation;
3. Linux local CPU-provider installation;
4. Linux external-provider installation;
5. Linux assistant-degraded installation;
6. at least one real Linux local-GPU installation when suitable hardware is available;
7. Debian-family package adapter;
8. Fedora/RHEL-family adapter;
9. Arch-family adapter;
10. Alpine-family adapter;
11. openSUSE-family adapter;
12. macOS Apple Silicon installation;
13. macOS Intel installation where available;
14. native Windows installation;
15. WSL installation;
16. Linux x86-64 native build;
17. Linux ARM64 native build;
18. macOS `.dylib` loading;
19. Windows `.dll` loading;
20. container CPU-only image;
21. container external-provider image;
22. offline installation;
23. installation in a path containing spaces;
24. installation in a Unicode path;
25. installation without administrative privileges;
26. repeated idempotent installation;
27. update from previous version;
28. failed update followed by rollback;
29. interrupted install followed by resume;
30. interrupted install followed by rollback;
31. repair of deleted virtual environment;
32. repair of stale native artifact;
33. preservation of user data during uninstall;
34. Pass 145 Android build when the toolchain is available;
35. immediate `--start` activation;
36. completion-receipt deterministic replay.
 
# 42. Required negative test matrix
 
The implementation SHALL reject or safely classify:
 
- Python below 3.11;
- missing venv support;
- missing compiler;
- non-C11 compiler;
- invalid shared-library output;
- missing required symbols;
- altered source manifest;
- altered installer payload;
- altered dependency package;
- archive traversal;
- symlink escape;
- insufficient disk;
- read-only target;
- unsupported architecture;
- package-manager failure;
- denied elevation;
- model-license rejection;
- model authentication failure;
- model digest mismatch;
- provider model mismatch;
- public unauthenticated external provider;
- occupied API port;
- occupied provider port;
- partial virtual environment;
- partial native artifact;
- stale installation lock;
- concurrent installers;
- malformed offline bundle;
- network access attempted in offline mode;
- path containing shell metacharacters;
- poisoned compiler path;
- invalid management capability;
- expired management proposal;
- replayed update proposal;
- browser-originated privileged mutation;
- rollback target corruption;
- uninstallation data-loss attempt without explicit authorization.
 
# 43. Concurrency
 
Exactly one mutating installation transaction MAY hold the installation lock for an `HHS_HOME`.
 
Concurrent read-only `status` and `doctor` operations MAY proceed against the last committed installation state.
 
A second mutating operation SHALL return:

```text
HHS_INSTALLATION_TRANSACTION_ALREADY_ACTIVE
```
 
It SHALL not wait indefinitely or begin partial mutation.
 
# 44. Performance and boundedness
 
The installer SHALL place explicit bounds on:
 
- network retries;
- connection timeouts;
- provider readiness polling;
- archive expansion;
- dependency-resolution time;
- compilation time;
- model-download retries;
- journal size;
- log retention;
- rollback versions;
- quarantine retention;
- lock age.
 
Large model download time SHALL be reported separately from core installation time.
 
Benchmarks SHALL distinguish:

```text
warm cached install
cold network install
core install
runtime install
provider install
model acquisition
native compilation
validation
startup
```
 
# 45. Logging and diagnostics
 
Logs SHALL be structured and human readable.
 
Each line SHALL identify:

```text
stage
operation
severity
profile
result
```
 
Secret values SHALL be redacted.
 
On failure, the installer SHALL print:
 
- terminal classification;
- failed stage;
- relevant log path;
- receipt path;
- whether rollback completed;
- whether the previous installation remains active;
- exact remediation.
 
# 46. Implementation layout
 
Pass 172 SHALL create at least:

```text
HHS_PASS_172_UNIVERSAL_COMPATIBLE_ENVIRONMENT_ONE_COMMAND_INSTALLATION_DEPENDENCY_RESOLUTION_VERIFIED_BOOTSTRAP_AND_RUNTIME_ACTIVATION_SYSTEM.md

install.sh
install.ps1
hhs-bootstrap.py
hhs

hhs_installer/
├── __init__.py
├── cli.py
├── schema.py
├── probe.py
├── planner.py
├── transaction.py
├── acquisition.py
├── verification.py
├── dependencies.py
├── python_environment.py
├── native_builder.py
├── frontend.py
├── provider.py
├── model_assets.py
├── activation.py
├── repair.py
├── update.py
├── rollback.py
├── uninstall.py
├── receipts.py
├── security.py
├── offline.py
└── platforms/
    ├── base.py
    ├── linux.py
    ├── macos.py
    ├── windows.py
    ├── android.py
    └── container.py

schemas/pass172/
├── installation_request.schema.json
├── environment_probe.schema.json
├── compatibility_decision.schema.json
├── installation_plan.schema.json
├── dependency_manifest.schema.json
├── installation_receipt.schema.json
└── offline_bundle.schema.json

manifests/pass172/
├── dependencies.json
├── platforms.json
├── profiles.json
├── native_targets.json
└── release_assets.json

tests/pass172/
├── test_probe.py
├── test_planner.py
├── test_transaction.py
├── test_security.py
├── test_native_builder.py
├── test_provider_resolution.py
├── test_offline_bundle.py
├── test_repair.py
├── test_update_rollback.py
├── test_uninstall.py
└── integration/

docs/pass172/
├── INSTALLATION.md
├── PLATFORM_SUPPORT.md
├── OFFLINE_INSTALLATION.md
├── PROVIDER_PROFILES.md
├── UPDATE_AND_ROLLBACK.md
├── UNINSTALLATION.md
├── SECURITY_MODEL.md
└── TROUBLESHOOTING.md

.github/workflows/pass172-installation.yml
evidence/pass172/
```
 
# 47. Existing-surface migration
 
The following current surfaces SHALL become adapters to Pass 172:

```text
init.sh
start.sh
GNUmakefile setup
GNUmakefile start
GNUmakefile setup-start
tools/bootstrap_litert_lm.sh
tools/install_vulkan_loader.sh
tools/import_hhs_gemma4_model.sh
deployment/pass153/Dockerfile
deployment/pass153/huggingface/Dockerfile
```
 
Their useful behavior SHALL be preserved.
 
Their duplicate authority and platform assumptions SHALL not be preserved.
 
# 48. Completion criteria
 
Pass 172 SHALL not be classified terminal until all of the following are true:

```text
one-command clean install exists
source acquisition is verified
dependency profiles are separated
dependency locks exist
user-local isolation is default
portable native build exists
Linux installation passes
macOS installation passes
Windows installation passes
ARM64 installation passes
x86-64 installation passes
core profile passes
runtime profile passes
external-provider profile passes
degraded profile passes
offline profile passes
transaction rollback passes
repair passes
update passes
uninstall data preservation passes
installation replay passes
public status surfaces are registered
host mutation cannot bypass capability checks
Hash216 installation identity closes
Hash72 receipts close
```
 
# 49. Required classifications
 
Permitted intermediate classifications:

```text
HHS_PASS_172_CONTRACT_BOUND
HHS_PASS_172_INSTALLER_SCAFFOLDED
HHS_PASS_172_ENVIRONMENT_PROBE_IMPLEMENTED
HHS_PASS_172_DEPENDENCY_RESOLUTION_IMPLEMENTED
HHS_PASS_172_PORTABLE_NATIVE_BUILD_IMPLEMENTED
HHS_PASS_172_TRANSACTIONAL_INSTALLATION_IMPLEMENTED
HHS_PASS_172_ONE_COMMAND_INSTALLATION_VALIDATED
```
 
Terminal classification:

```text
HHS_PASS_172_UNIVERSAL_COMPATIBLE_ENVIRONMENT_ONE_COMMAND_INSTALLATION_DEPENDENCY_RESOLUTION_VERIFIED_BOOTSTRAP_AND_RUNTIME_ACTIVATION_SYSTEM_VERIFIED
```
 
Terminal state SHALL require:

```text
omega_172 = true
terminal = true
failures = 0
```
 
# 50. Explicit nonclaims
 
Before terminal closure, Pass 172 SHALL NOT claim:
 
- every operating system is supported;
- every processor architecture is supported;
- every GPU is supported;
- GPU drivers can be universally installed;
- every model can run locally;
- one command eliminates license acceptance;
- one command eliminates required credentials;
- a degraded assistant is a full local-model installation;
- a successful container build proves physical GPU execution;
- simulated platform tests prove real platform support;
- source inspection proves installation success;
- a generated receipt proves an unexecuted test;
- host provisioning creates a second Runtime authority.
 
# 51. Final normative statement
 
Pass 172 establishes installation as a verified, transactional, capability-probed operation rather than an informal sequence of shell commands.
 
The resulting invariant is:

```text
ONE COMMAND ≠ BLIND INSTALLATION
```
 
Instead:

```text
ONE COMMAND = PROBE + PLAN + VERIFY + PROVISION + BUILD + VALIDATE + ACTIVATE + RECEIPT
```
 
For every compatible environment:

```text
COMPATIBLE HOST
→ EXACT PROFILE
→ VERIFIED INSTALLATION
→ ONE VM81 RUNTIME
→ REGISTERED PUBLIC SURFACES
→ HASH216 INSTALLATION IDENTITY
→ HASH72 RECEIPT CLOSURE
```
 
No environment may be declared installed when dependencies are unresolved, native authority is absent, validation has not executed, activation is partial, or the completion receipt does not close.
