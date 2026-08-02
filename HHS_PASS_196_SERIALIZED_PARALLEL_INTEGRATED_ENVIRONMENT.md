# HHS PASS 196 — SERIALIZED PARALLEL REPOSITORY INTEGRATION, ENCRYPTED VECTOR-MEMRISTOR DATABASE, AI-ASSISTED LINUX TOOL SERVER, AND VISUAL IDE CLOSURE

## 1. Normative metadata

| Field | Normative value |
|---|---|
| Contract identifier | `HHS-P196-SPIRAH-EVDB-LINUX-TOOLSERVER-VIDE-VM81-H72-H216` |
| Pass number | `196` |
| Canonical pass name | `SERIALIZED_PARALLEL_INTEGRATED_REPOSITORY_API_HYDRATION_ENCRYPTED_VECTOR_DATABASE_LINUX_TOOL_SERVER_VISUAL_IDE` |
| Short name | `P196 Integrated Environment Deep Scan` |
| Repository | `danonbrez/Holofractal_Harmonicode` |
| Authoritative implementation baseline | `main @ 5178787599dc02c477cc8160eee0e39047437660` |
| Merge target | `main` |
| Inherited scope | Genesis and every compatible accepted requirement through Pass 195 |
| Mutation authority | Exactly one VM81-authorized runtime tick and Hash72 receipt boundary |
| Parallelism policy | Parallel immutable observation; deterministic serialized classification and admission |
| State projection | Exact 5,184-bit / 648-byte VM projection |
| Persistent vector projection | Pass 174 SQLite + AES-GCM authenticated encrypted vector store |
| Runtime API | `/api/runtime/integration` |
| API-tool registry | `/api/runtime/integration/tools` |
| Visual IDE | Pass 161 Holofractal Harmonizer projection |
| Linux target | DigitalOcean Ubuntu systemd service using the canonical visual server |
| Initial classification | `IMPLEMENTED — GAP-CLOSURE SCAN REQUIRED` |
| Completion condition | Every discovered pass layer is `INTEGRATED` and every mandatory global surface is present |

## 2. Objective

Pass 196 performs a repository-wide deep scan and closes the structural separation between historical pass contracts and the executable runtime.

```text
REPOSITORY FILE TREE
→ bounded parallel immutable observation
→ deterministic path ordering
→ pass-number and surface classification
→ one serialized integration manifest
→ one VM81 authorized tick
→ one Hash72 receipt boundary
→ one Hash216 three-lane identity
→ one 5,184-bit VM projection
→ one AES-GCM encrypted vector-memory record
→ Linux environment status
→ API-tool server registry
→ Visual IDE projection
```

Parallel workers never receive mutation authority. They read repository-visible files and return immutable observations. Manifest creation, VM projection, vector admission, and public state transition are serialized under one process lock and one VM81-authorized API request.

## 3. Inherited authority joined by Pass 196

Pass 196 extends and joins, rather than replaces:

1. Pass 163 VMRC 5,184-bit snapshot representation.
2. Pass 174 Hash216 array construction and authenticated encrypted vector persistence.
3. Pass 190 Iteration 6 singleton operation/resource authority, persistent receipts, job registry, API, and SDK foundation.
4. Pass 191 Genesis-to-runtime repository hydration contract.
5. Passes 192–193 nested topology, lineage, and executable packaging contracts.
6. Pass 194 multimodal file/folder hydration, SQL context graph, encrypted vector, snapshot, and dataset authority contract.
7. Pass 195 governed Kimi K3 multimodal proposal engine.
8. The canonical FastAPI runtime, HHS Runtime Controller, guarded service registry, multimodal receipt graph, Linux deployment surface, and Holofractal Harmonizer IDE.

No new private truth pipeline is introduced.

## 4. Deep-scan algorithm

### 4.1 Bounded discovery

The scanner traverses repository-visible files in canonical path order and excludes generated/private runtime state including `.git`, `.hhs`, virtual environments, `node_modules`, caches, `build`, `dist`, and `coverage`. The initial bound is 100,000 files. Exceeding it fails closed.

### 4.2 Parallel observation

Each worker computes:

```text
relative path
byte length
SHA-256 content digest
Hash72 file witness
primary pass identity where discoverable
surface-role set
text-scan status
```

A worker cannot mutate runtime state, persist vectors, issue receipts, or decide closure.

### 4.3 Serialized classification

One ordered serializer constructs:

```text
file observation registry
pass-layer matrix
global surface matrix
integration-gap report
manifest Hash72
manifest Hash216
VM5184 snapshot
```

The manifest is deterministic for the same repository bytes, paths, scan policy, and VM81 receipt input.

## 5. Pass-layer states

Every pass number from 1 through the maximum discovered pass receives one explicit state:

| State | Meaning |
|---|---|
| `INTEGRATED` | An executable surface and test or evidence surface are present. |
| `PARTIAL` | Some executable/supporting surface exists, but verified closure evidence is incomplete. |
| `CONTRACT_ONLY` | A pass contract exists without an executable integration surface. |
| `UNRESOLVED` | No repository-visible artifact is bound to the pass number. |

Pass 196 SHALL NOT silently convert a non-integrated state into success.

```text
operational
= every mandatory global environment surface is present

integration_closed
= operational
  AND every pass layer is INTEGRATED

ok
= integration_closed
```

## 6. Mandatory global surfaces

The integrated environment is operational only when these surfaces exist:

```text
runtime
API
operation registry
hydration
vector store
Linux environment
tool server
Visual IDE
tests
CI
```

Contracts, deployment, and evidence are additionally classified and retained.

## 7. VM81 and Hash216 admission

A scan mutation may be requested only through:

```text
POST /api/runtime/integration/scan
```

or the equivalent API-tool invocation. Before vector persistence, the route executes:

```text
HHSRuntimeController.authorized_tick(
  source = api.runtime.integration.scan
)
```

The resulting receipt Hash72 is embedded in the manifest.

Hash216 lanes are:

```text
predecessor = prior admitted manifest Hash72 or zero genesis lane
current     = current manifest Hash72
successor   = deterministic successor witness
```

The inherited Pass 174 character index root and logical identity remain intact.

## 8. Encrypted virtual-memristor vector database

The manifest is projected into exactly 648 bytes, equivalent to 5,184 bits. The vector database uses the inherited Pass 174 persistent store:

```text
SQLite
WAL journaling
FULL synchronization
AES-GCM authenticated encryption
Hash216 verification
bounded active suffix
restart recovery
```

The plaintext repository manifest is not written into the vector-object payload. The encrypted record contains the VM snapshot and linked Hash72/Hash216 identities. Original repository files remain source authority; vector memory is a retrieval/state projection.

## 9. Multimodal and AI-assisted environment

Pass 196 exposes one integration status across source and contract files, runtime/API modules, operation registries, hydration adapters, multimodal pipelines, provider/assistant surfaces, Linux deployment, Visual IDE controls, receipts, and evidence.

Pass 195 Kimi K3 and all external providers remain governed proposal engines. Their output cannot bypass VM81 admission, directly mutate repository truth, or become canonical merely by entering vector memory.

## 10. Linux environment

The status surface reports Linux kernel release, architecture, Python runtime, state root, and systemd unit identity. The DigitalOcean service starts:

```text
python -m uvicorn hhs_backend.visual_server:app
```

Persistent Pass 196 state is stored under `/var/lib/hhs/pass196`. The service uses one worker, restrictive umask, restart-on-failure, and a protected system filesystem. Vercel is not an authority or acceptance dependency.

## 11. API-tool server

Tools:

```text
integration.status
integration.scan
integration.manifest
integration.gaps
```

Routes:

```text
GET  /api/runtime/integration/status
POST /api/runtime/integration/scan
GET  /api/runtime/integration/manifest
GET  /api/runtime/integration/gaps
GET  /api/runtime/integration/tools
POST /api/runtime/integration/tools/invoke
```

The tool server is a governed projection. `integration.scan` requires a VM81-authorized tick. Read operations do not create mutation authority.

## 12. Visual IDE projection

The Holofractal Harmonizer loads `pass196-integration.mjs` during production startup. The panel displays maximum discovered pass, integrated count, file count, AES-GCM vector state, manifest Hash72, vector object identity, and unresolved pass-layer count.

Controls:

```text
Run deep integration scan
Show gaps
Inspect API tools
```

The IDE registers:

```text
hhs:runtime:pass196-integrated-environment
```

The frontend remains non-authoritative.

## 13. Failure and degradation rules

The environment remains `DEGRADED` when any of these holds:

1. any pass is `PARTIAL`, `CONTRACT_ONLY`, or `UNRESOLVED`;
2. a mandatory global surface is absent;
3. repository scan bounds are exceeded;
4. VM81 authorization fails;
5. Hash72 or Hash216 validation fails;
6. encrypted vector admission fails;
7. the vector database cannot restore/authenticate records;
8. API or IDE projection cannot reach the canonical runtime.

The gap report is required evidence, not an error to hide.

## 14. Validation

Pass 196 validates:

1. parallel observation and deterministic serialized output;
2. pass-state classification;
3. mandatory surface detection;
4. explicit contract-only gap reporting;
5. deterministic manifest Hash72/Hash216;
6. exact 648-byte snapshot creation;
7. AES-GCM encrypted persistence;
8. absence of plaintext repository paths from vector payload storage;
9. API-tool registry policy;
10. Python compilation, browser-module syntax, route wiring, IDE startup wiring, and systemd declarations.

## 15. Claim boundary

Pass 196 implements the scan, manifest, VM81 authorization bridge, encrypted vector-memory projection, API-tool surface, Linux deployment projection, and Visual IDE controls.

It does not predeclare all historical passes integrated. Full completion may be claimed only when:

```text
unresolved_pass_count = 0
AND missing_mandatory_surfaces = []
AND integration_closed = true
AND deterministic replay succeeds
AND authoritative main contains validated implementation and evidence
```

## 16. Closure rule

```text
PARALLEL OBSERVE
→ SERIALIZE
→ VM81 AUTHORIZE
→ HASH72 COMMIT
→ HASH216 INDEX
→ ENCRYPTED VECTOR ADMIT
→ API/TOOL/IDE PROJECT
→ REPORT EVERY GAP
→ REPAIR FORWARD
→ RE-SCAN
→ CLOSE ONLY WHEN ZERO GAPS REMAIN
```
