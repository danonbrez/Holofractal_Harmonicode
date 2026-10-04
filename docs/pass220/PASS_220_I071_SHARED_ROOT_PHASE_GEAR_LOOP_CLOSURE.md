# Pass 220 I071 — Shared-Root Phase-Gear Loop Closure

Date: 2026-10-04

## Scope

I071 aligns the existing VM81 orbit detector with the merged I070 tensor/Lo-Shu
qudit geometry and nested hydration.

The governing rule is copied semantically from the authoritative C kernel:

\`\`\`text
for each previously seen Hash72 state, in insertion order:
    if current Hash72 == seen Hash72:
        orbit_period = current_step - first_seen_step
        return orbit_period

if no match and seen_count < 8192:
    append (Hash72, current_step)

return 0
\`\`\`

The I071 bridge does not replace or reinterpret that detector.

## Kernel distinction preserved

The VM81 kernel keeps three separate concepts:

\`\`\`text
OP_HALT
orbit_halted
CONVERGED
\`\`\`

They remain separate in I071.

A repeated state gives:

\`\`\`text
orbit_period > 0
transport_closed = true
orbit_halted = true
\`\`\`

The runner may stop when:

\`\`\`text
halt_on_orbit && orbit_halted
\`\`\`

but full convergence is only:

\`\`\`text
transport_closed
&& orientation_closed
&& constraint_closed
\`\`\`

I071 therefore never upgrades orbit recurrence into an orientation or
constraint proof.

## 72-position modular Lo Shu qudit nucleus

The ordered phase basis is:

\`\`\`text
{x,y,z,w,xy,yx,zw,wz}
\`\`\`

and the Lo Shu surface has nine ordered positions.

Therefore:

\`\`\`text
8 * 9 = 72
\`\`\`

with exact encoding:

\`\`\`text
phase_slot = 9*phase_channel + outcome
phase_channel in 0..7
outcome in 0..8
\`\`\`

and deterministic successor:

\`\`\`text
next = (phase_slot + 1) mod 72
\`\`\`

The first 72 states are unique. State 72 returns to state 0, so the inherited
first-repeat detector returns an exact period of 72 and no earlier period.

## VM81 binding

Each outcome retains the I070 address:

\`\`\`text
vm81_cell_id = 9*nucleus_index + outcome
\`\`\`

Across all nine nuclei and nine outcomes, this remains the exact bijection
\`0..80\`.

The phase channel is an additional ordered coordinate; it does not create a
second VM81 address space.

## Harmonic phase lock

I071 preserves the inherited exact closure:

\`\`\`text
64*81 = 5184
72*72 = 5184
144*36 = 5184
64*81 - 72*72 = 0
lcm(64,72,81) = 5184
\`\`\`

Thus the local 72-cycle detector and the global 5184 phase-lock geometry are
different scales of one exact phase-gear construction.

## Lowering and lifting

A local I071 geometry identity contains:

\`\`\`text
shared root
I070 binding root
nucleus
phase channel
Lo Shu outcome
Lo Shu value
VM81 cell
\`\`\`

and produces one \`geometry_hash72\`.

Lifting adds:

\`\`\`text
nesting depth
hydration root
Hash216 lineage
\`\`\`

without changing the local orbit identity.

Therefore:

\`\`\`text
lower(lift(G, depth, lineage, hydration)) = G
\`\`\`

at the Hash72 orbit-identity layer.

The same VM81 first-repeat detector consequently reports period 72 at local and
lifted scales.

## Geometry versus history

This separation is mandatory:

\`\`\`text
geometry(t+72) = geometry(t)
lineage(t+72) != lineage(t)
\`\`\`

The geometric loop closes, but the ordered Hash216 ancestry advances.

I071 constructs each candidate lineage as:

\`\`\`text
PREVIOUS = previous receipt Hash72
CHANGE   = Hash72(from geometry, to geometry, step)
RECEIPT  = Hash72(shared root, previous Hash216, PREVIOUS, CHANGE)
Hash216  = PREVIOUS || CHANGE || RECEIPT
\`\`\`

This is candidate provenance only; it does not mint canonical runtime state.

## Formal evidence

Connected Wolfram Language validation:

\`\`\`text
schema = HHS_PASS_220_I071_SHARED_ROOT_PHASE_GEAR_LOOP_CLOSURE_WOLFRAM_V1
status = PASS
checks = 36/36
first repeat period = 72
VM81 addresses = 81
shared coordinate closure = 5184
phase lock period = 5184
geometry returns = true
lineage advances = true
\`\`\`

## Authority

I071 grants no new:

- VM81 mutation authority;
- canonical Hash72 authority;
- canonical Hash216 authority;
- persistence authority;
- floating-point authority;
- external-egress authority.

It is a deterministic candidate traversal and closure membrane over already
authoritative surfaces.
