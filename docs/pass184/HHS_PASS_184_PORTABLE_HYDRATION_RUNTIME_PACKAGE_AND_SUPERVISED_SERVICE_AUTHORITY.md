# HHS PASS 184 — PORTABLE HYDRATION RUNTIME PACKAGE AND SUPERVISED SERVICE AUTHORITY

## 1. Normative metadata

| Field | Normative value |
|---|---|
| Contract identifier | `HHS-P184-PHRP-PSRA-VM81-H72-H216` |
| Pass number | `184` |
| Canonical name | `PORTABLE_HYDRATION_RUNTIME_PACKAGE_AND_SUPERVISED_SERVICE_AUTHORITY` |
| Short name | `P184 Portable Runtime Authority` |
| Contract version | `1.0.0` |
| Repository | `danonbrez/Holofractal_Harmonicode` |
| Authoritative baseline | `main` at Pass 183 completion plus inherited closure receipts |
| Merge target | `main` |
| Parent foundation | All inherited contracts through Pass 183 |
| Immediate parent | Pass 183 Probability Equation Hydration Membrane Runtime |
| Authority | `HHS_VM81_SINGLETON_PORTABLE_RUNTIME_SERVICE_AUTHORITY_V1` |
| Initial status | `CONTRACTED — IMPLEMENTATION AND REPOSITORY-NATIVE ACCEPTANCE REQUIRED` |

## 2. Purpose

Pass 184 closes the unresolved portable-installation obligation inherited from Pass 182 and the production-service obligations inherited through Passes 170, 174, 176, 180, 181, and 183.

A repository checkout is not a completed server installation merely because a Python process exists. A service is admitted only when its package identity, profile dependency closure, executable entry point, listener, health endpoint, runtime authority, restart path, and installation evidence are all finite, inspectable, and replayable.

Pass 184 therefore compiles the inherited HHS runtime into a deterministic installation package and supervises startup until the public application IDE is genuinely reachable.

## 3. Canonical lifecycle

```text
AUTHORITATIVE_REPOSITORY_STATE
→ ENVIRONMENT_DETECTION
→ INSTALLATION_PROFILE_RESOLUTION
→ DEPENDENCY_CLOSURE
→ DETERMINISTIC PACKAGE PLAN
→ PACKAGE MATERIALIZATION
→ FILE HASH MANIFEST
→ PACKAGE VERIFICATION
→ PORT AUTHORITY PREFLIGHT
→ SUPERVISED UVICORN START
→ TCP LISTENER CONFIRMATION
→ HTTP /health CONFIRMATION
→ RUNTIME AUTHORITY PROJECTION
→ INSTALLATION RECEIPT
→ COLD-START REPLAY
```

No process-running observation may substitute for listener or health verification.

## 4. Supported profiles

The implementation shall support:

```text
minimal
text
audio
graphics
video
games
documents
applications
multimodal
full
```

Every profile resolves to an ordered component closure. The closure must include the VM81 singleton authority, Hash72 receipt clock, Hash216 identity layer, configuration, manifests, service launcher, health probe, and installation evidence.

## 5. Environment detection

The detector shall record, at minimum:

```text
operating system
kernel release
machine architecture
Python version and executable
CPU count
repository root
writable package root
available native tools
available process and service managers
selected public host and port
```

Detection is evidence. It does not mutate the host.

## 6. Deterministic package plan

A package plan shall preserve:

```text
contract identity
runtime version
profile
ordered component closure
repository root
installation root
application import target
host
port
health path
environment identity
plan Hash216-compatible digest
```

Identical canonical inputs must produce identical plan identities.

## 7. Installation package layout

```text
hhs-runtime/
├── bin/
│   └── hhs-runtime
├── configuration/
│   └── hhs.env
├── profiles/
│   └── <profile>.json
├── manifests/
│   └── runtime-package.json
├── service/
│   └── hhs.service
└── installation-evidence/
    └── build-receipt.json
```

The package references the authoritative repository; it does not copy or silently fork runtime authority.

## 8. Manifest authority

The package manifest shall include every generated package file except the manifest itself, with:

```text
relative path
byte length
SHA-256 digest
file role
```

Verification fails closed on a missing, added-authority, truncated, or mutated required file.

## 9. Public application authority

The production entry point is:

```text
hhs_backend.application_ide_server:app
```

The package must not downgrade the public surface to a diagnostic console, static placeholder, raw API viewer, or detached runtime shell.

The public service shall bind the configured host and port and expose:

```text
/
/health
/api/health
```

## 10. Port and listener authority

Before launch, the selected port must be bindable. A conflict returns a typed rejection.

After launch, supervision shall distinguish:

```text
PROCESS_NOT_STARTED
PROCESS_EXITED_BEFORE_LISTEN
PROCESS_RUNNING_NO_LISTENER
TCP_LISTENER_READY_HTTP_NOT_READY
HTTP_HEALTH_READY
STARTUP_TIMEOUT
CANCELLED
```

`systemctl status = active` without a reachable listener is not accepted.

## 11. Bounded startup

Startup shall have a finite deadline. The supervisor shall:

1. validate the repository and application module;
2. reject an occupied port;
3. start one Uvicorn worker;
4. poll the loopback listener and `/health`;
5. terminate the child on startup failure or timeout;
6. preserve the child exit code and failure reason;
7. remain attached after readiness so the service manager owns the process lifecycle.

## 12. Systemd authority

The generated systemd unit shall use a foreground process, explicit working directory, explicit environment file, restart-on-failure, bounded stop behavior, and the Pass 184 launcher.

It shall not use background shell detachment, indefinite readiness loops, or a PID file as a substitute for process ownership.

## 13. Required command surface

```bash
python -m hhs_runtime.pass184.cli detect
python -m hhs_runtime.pass184.cli plan
python -m hhs_runtime.pass184.cli build
python -m hhs_runtime.pass184.cli verify
python -m hhs_runtime.pass184.cli probe
python -m hhs_runtime.pass184.cli serve
python -m hhs_runtime.pass184.cli status
```

Human-readable output is the default. JSON is optional through `--json`.

## 14. Required HTTP surface

```text
GET  /api/v1/pass184/status
POST /api/v1/pass184/plan
POST /api/v1/pass184/package
POST /api/v1/pass184/verify
POST /api/v1/pass184/probe
```

Package writes are restricted to the configured Pass 184 package root. Probe requests are restricted to loopback targets by default.

## 15. Human IDE surface

A runtime-package studio shall expose:

```text
profile selection
host and port
package output identity
environment summary
resolved component closure
build action
verification action
listener and health probe
human-readable failure reason
systemd installation guidance
```

Raw JSON alone does not satisfy this surface.

## 16. Security requirements

The implementation shall reject:

```text
path traversal outside the package root
unsafe service-unit interpolation
invalid ports
non-loopback arbitrary probe targets
manifest tampering
symlink substitution in required package files
occupied-port launch
missing application module
unbounded startup
shell command injection
```

## 17. Restartability

Every execution cycle shall preserve repository-visible state including:

```text
base commit
branch and merge target
files changed
commands executed
validation results
remaining checks
blockers
next action
```

Every generated installation package shall be independently verifiable without chat state or an active agent process.

## 18. Required tests

The acceptance matrix shall include:

```text
all profile closures
stable plan identity
stable package manifest
successful package verification
manifest tamper rejection
invalid profile rejection
invalid port rejection
occupied-port rejection
loopback HTTP health success
no-listener classification
systemd foreground-process contract
launcher application-target contract
API plan/package/verify/probe boundaries
runtime-package studio contract
```

## 19. Required acceptance command

```bash
./scripts/test_pass184_portable_runtime.sh
```

The command shall compile Python surfaces, run dependency-scoped tests, validate deployment files, build and verify a package, and emit a machine-readable completion receipt.

## 20. Acceptance criteria

Pass 184 is complete only when repository-native evidence proves:

- deterministic profile and dependency resolution;
- deterministic package planning and file manifests;
- package verification detects mutation;
- generated launcher reaches the full application IDE import target;
- generated systemd unit owns one foreground supervised process;
- occupied ports fail before launch;
- process-running-without-listener is not accepted;
- HTTP `/health` readiness is bounded and verified;
- CLI, API, and IDE surfaces use the same package authority;
- positive, negative, tamper, timeout, and listener tests pass;
- the implementation is merged and verified on authoritative `main`.

## 21. Terminal classifications

```text
HHS_PASS_184_ENVIRONMENT_DETECTION_VERIFIED
HHS_PASS_184_PROFILE_DEPENDENCY_CLOSURE_VERIFIED
HHS_PASS_184_DETERMINISTIC_PACKAGE_PLAN_VERIFIED
HHS_PASS_184_PACKAGE_MANIFEST_VERIFIED
HHS_PASS_184_PACKAGE_TAMPER_REJECTION_VERIFIED
HHS_PASS_184_PORT_PREFLIGHT_VERIFIED
HHS_PASS_184_LISTENER_READINESS_VERIFIED
HHS_PASS_184_HTTP_HEALTH_READINESS_VERIFIED
HHS_PASS_184_SYSTEMD_FOREGROUND_AUTHORITY_VERIFIED
HHS_PASS_184_PUBLIC_APPLICATION_IDE_TARGET_VERIFIED
HHS_PASS_184_COLD_START_REPLAY_VERIFIED
HHS_PASS_184_PORTABLE_HYDRATION_RUNTIME_PACKAGE_AND_SUPERVISED_SERVICE_AUTHORITY_VERIFIED
```

## 22. Final operating law

```text
A RUNNING PID IS NOT A READY SERVICE.
A READY SERVICE OWNS A VERIFIED PACKAGE, A BOUND PORT,
A RESPONSIVE HEALTH ENDPOINT, AND A REPLAYABLE INSTALLATION RECEIPT.

THE PACKAGE MAY PROJECT THE HHS RUNTIME.
IT MAY NOT CREATE A SECOND VM81 AUTHORITY.
```