# Pass 219 — Lane 5 Instruction Object Boundary v1

Status: **MANDATORY / PLUG-AND-PLAY OBJECT INGRESS / LANE5-INSTRUCTION-ONLY EXECUTION**

## Core rule

The repository may accept arbitrary plug-and-play objects upstream.

VM81 execution and HHS-controlled Linux host/kernel execution SHALL NOT accept
those objects directly. Lane 5 is the mandatory object-lowering membrane.

```text
arbitrary repository object
    -> classify / zero-bypass intercept
    -> sandbox queue
    -> dependency-safe reorder
    -> mandatory Lane 5 optimization
    -> object lowering
    -> Lane5Instruction
        -> VM81 gateway
        -> Linux host/kernel gateway
```

Only a validated `Lane5Instruction` may cross either execution gateway.

## Instruction states

```text
QUEUED_OPTIMIZED
OBSERVATION_ADMITTED
RNA_CELL_WALL_BOUND
PQC_ADMITTED
EXECUTED
REJECTED
```

State-affecting VM81 or Linux-host instructions require `PQC_ADMITTED` before
execution. Read-only instructions may reach `OBSERVATION_ADMITTED` without
canonical mutation authority.

## Object semantics

The source object may be any repository-supported object type, including:

- dataclass / typed Python object;
- mapping / JSON-compatible object;
- exact byte carrier;
- VMRC candidate;
- vector/cache/replay object;
- plugin object;
- multimodal ingress object;
- process/native-call request;
- file/socket request.

Lane 5 records source type, exact content/provenance digest, dependency root and
traffic class before lowering. Object identity is preserved as evidence; the
execution gateway consumes the Lane 5 instruction, not the original object.

## VM81 acceptance

The VM81 execution gateway SHALL reject:

- raw `CandidateTransition`;
- raw frame without Lane 5 instruction evidence;
- compatibility ABI request without Lane 5 instruction evidence;
- instruction without queue optimization;
- state-affecting instruction without RNA/C++ cell-wall evidence;
- state-affecting instruction without signed environmental/PQC admission.

A rejected raw object is queued for Lane 5 lowering. It is not silently
executed and no direct fallback exists.

## Linux host/kernel acceptance

HHS-controlled Linux execution adapters SHALL accept only `Lane5Instruction`.

This applies to subprocess/native worker, ctypes/native-library, file, socket,
deployment-process, and other HHS-originated Linux ABI traffic. It does not
claim control over unrelated host processes outside the HHS process tree.

The Linux result is external execution evidence. Any result that would mutate
canonical HHS state must separately re-enter Lane 5 and signed VM81 admission.

## Capacity calibration

Lane 5 sandbox capacity authority is the local
`RAW_LINUX_SERIAL_ABI_BYTES` measured maximum. 5184/648 framing is derived
only after calibration and is not the hardware capacity unit.

## Authority

`Lane5Instruction` is an execution permit/evidence object. It does not itself
own:

- canonical VM81 mutation;
- canonical Hash72/Hash216 mint/persistence;
- PQC keys;
- receipt clock;
- floating-point canonical authority.

Canonical VM81 mutation remains inside the signed native admission boundary
after the instruction has been PQC-admitted.

## Acceptance

1. arbitrary upstream objects can be lowered deterministically;
2. every lowered object carries Pass036 + sandbox queue + mandatory optimization evidence;
3. VM81 gateway accepts only `Lane5Instruction`;
4. Linux host gateway accepts only `Lane5Instruction`;
5. raw bypass objects are queued and return redirect-required evidence;
6. state-affecting execution fails closed without RNA/PQC evidence;
7. read-only instruction flow remains available without mutation authority;
8. repository audit reports direct execution sites not yet migrated.
