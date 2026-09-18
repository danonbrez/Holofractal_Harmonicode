# Pass 219 — Universal ABI / Linux Kernel Lane 5 Interception Contract v1

Status: **MANDATORY / ZERO-BYPASS / ALL-HHS-TRAFFIC / LANE-5-MEDIATED / PQC-BLOCK-AND-REDIRECT**

## 1. Governing law

Every HHS-controlled crossing into either:

1. the HHS runtime / VM execution ABI; or
2. an HHS-controlled Linux-host/kernel ABI boundary

SHALL traverse Lane 5 before downstream dispatch.

This requirement applies regardless of caller generation or compatibility surface.

```text
HHS traffic
  -> Pass035/036 constraint + zero-bypass interposition
  -> Lane5 mandatory optimization / validation membrane
  -> RNA / VM5184 lowering
  -> C++ RNA cell wall
  -> signed environmental / PQC envelope
  -> singleton VM81 or governed Linux-host dispatch on ADMIT only
```

## 2. Traffic scope

Mandatory interception includes, at minimum:

- public HTTP and WebSocket runtime traffic;
- compatibility API and ABI surfaces;
- VMRC candidate/commit/replay/retrieval surfaces;
- Python ctypes/native-library calls;
- x86_64 ingress/egress and SysV AMD64 bridges;
- plugins and compatibility adapters;
- cache/vector/superedge/replay operations;
- GPU/worker candidate routes;
- subprocess/native worker launch;
- filesystem and socket I/O initiated by HHS runtime services;
- deployment/runtime Linux process and kernel-facing adapters.

The contract governs HHS-originated traffic. It does not claim control over unrelated host processes outside the HHS runtime/process tree.

## 2.1 Supersession of the earlier host-interception exclusion

For HHS-originated traffic, this contract supersedes the RLM20 1.37 statement that host syscall/hardware-bytecode interception is not required.

The updated rule is:

```text
HHS process/runtime -> runtime ABI or Linux kernel/host ABI
    => Lane5 interception REQUIRED
```

This does not claim authority over unrelated operating-system processes outside the HHS process/runtime tree.

## 3. Direct-path semantics

A direct runtime/kernel dispatch attempt is never silently accepted.

```text
DIRECT_ATTEMPT
  -> PQC/authority boundary classification = BLOCK_DIRECT
  -> redirect requirement = LANE5_REMEDIATION_REQUIRED
  -> Lane5 processing
  -> C++ RNA cell wall
  -> signed environmental/PQC validation
  -> ADMIT or REJECT
```

There is no direct fallback after Lane 5 or PQC rejection.

Compatibility surfaces may preserve their external signatures, but they may not preserve an alternate authority path.

## 4. Read-only traffic

Observation/status traffic SHALL still pass through Lane 5 interposition and capability classification.

Read-only traffic:
- carries no VM81 mutation authority;
- carries no Hash72/Hash216 mint authority;
- does not require a canonical mutation receipt;
- may use bounded cached Lane 5 capability/status evidence.

A read-only classification SHALL NOT be used to smuggle state-affecting work through the observation path.

## 5. State-affecting traffic

Before any state-affecting runtime/kernel dispatch is permitted, evidence SHALL establish:

```text
zero_bypass_interposition = ADMITTED
lane5_mediation = VERIFIED
mandatory_optimization_dispatch = VERIFIED
rna_cpp_cell_wall = VERIFIED
signed_environmental_admission = VERIFIED
pqc_authenticated = VERIFIED
singleton_authority_target = VERIFIED
```

Missing evidence fails closed.

## 6. Optimization inheritance

All proven compatible Pass 219 optimizations remain mandatory Lane 5 defaults. The interceptor SHALL expose the current mandatory capability lineage so compatibility callers cannot bypass cache/hydration/composition/latency optimization by using an older ABI.

The interceptor does not grant any optimizer canonical mutation authority.

## 7. Linux host boundary

Linux-facing runtime work remains host execution, not a second canonical VM.

Lane 5 SHALL mediate HHS-originated Linux ABI traffic before the operation is delegated to the host adapter. The host/kernel result remains external execution evidence until any resulting canonical HHS state change separately traverses the signed PQC/VM81 admission boundary.

## 8. Authority

The universal interceptor has:

```text
canonical_vm81_mutation_authority = FALSE
canonical_hash72_authority = FALSE
canonical_hash216_authority = FALSE
canonical_persistence_authority = FALSE
pqc_key_authority = FALSE
receipt_clock_authority = FALSE
floating_point_canonical_authority = FALSE
```

It may block, classify, redirect, optimize, validate and issue mediation evidence only.

## 9. Required negative behavior

The implementation SHALL reject at least:

- missing zero-bypass token;
- token scoped to the wrong ABI/kernel surface;
- state-affecting dispatch without Lane 5 mediation;
- state-affecting dispatch without C++ RNA-cell-wall evidence;
- state-affecting dispatch without signed environmental/PQC admission;
- direct VMRC commit bypass;
- direct compatibility ABI canonical mutation;
- Linux-host dispatch marked as HHS canonical mutation;
- fallback-to-direct after Lane 5 rejection.

## 9.1 Sandboxed execution queue/cache

All traffic classified as bypass/direct/compatibility traffic SHALL enter a Lane 5-owned sandbox queue before downstream dispatch.

The sandbox uses the inherited exact carrier:

```text
5184 serial bits
<-> 648 little-endian bytes
<-> 81 x uint64 VM81 words
```

The queue/cache SHALL:

- remain candidate-only and non-authoritative;
- never persist a canonical VM81 state merely because it is cached;
- retain exact 648-byte carrier identity for cacheable execution candidates;
- key reusable entries by exact content/provenance identity;
- reorder only where dependency ordering permits;
- preserve FIFO order inside one state-affecting dependency chain;
- prioritize exact cache/replay/composition reuse over fresh recomputation when compatible;
- send every dequeued state-affecting request back through Lane 5 optimization, RNA/C++ lowering, and signed PQC admission;
- provide no direct fallback if optimization or admission rejects.

### Hardware calibration

Cache capacity SHALL be expressed in exact 648-byte records.

A hardware calibration receipt SHALL identify:

```text
serial_bits = 5184
record_bytes = 648
byte_order = LITTLE_ENDIAN
benchmark_window_ns
measured_linear_records
measured_linear_bytes = measured_linear_records * 648
runner / CPU / logical CPU count
benchmark implementation identity
```

For one environment, the cache maximum is the largest measured linear 5184-record capacity from the accepted benchmark profile.

When several supported hardware-environment profiles are supplied, the implementation records every profile and the selected environment-specific maximum. It SHALL NOT silently apply a measurement from a different environment as though it were local evidence.

The existing saturation-v3 65,536-record / 42,467,328-byte workset may be used only as a `VERIFIED_WORKSET_FLOOR` when no maximum-capacity receipt is installed. That state is development-safe but is **not production calibration acceptance**.

Cache storage is lazily allocated and evicted to the calibrated byte/record bound; the implementation SHALL NOT preallocate the entire measured maximum.

## 10. Acceptance

Acceptance requires:

1. Pass036 surface map includes runtime ABI and Linux kernel/host classes;
2. every universal envelope carries a valid Pass036 token;
3. current mandatory Lane 5 capability lineage is visible in the envelope;
4. direct state-affecting dispatch remains blocked until Lane 5 + RNA + PQC evidence is supplied;
5. read-only traffic is still intercepted;
6. repository audit identifies unmediated production/runtime crossings;
7. dependency-scoped repairs drive that violation count to zero for the production runtime scope before deployment acceptance;\n8. the Lane 5 sandbox cache carries a local hardware `MEASURED_MAXIMUM` calibration receipt rather than only the verified workset floor;\n9. bypass/direct traffic is queued and deterministically reordered through Lane 5 optimization before downstream dispatch.
