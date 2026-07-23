# HHS PASS 147 — FUNCTIONALLY COMPLETE EXTERNAL AGENT OPACITY

**Contract Identifier:** HHS-P147  
**Status:** Normative implementation contract  
**Parent:** HHS-P146 full inherited pass-history nucleus  
**Governance:** HHS-I132 CEUAC and HHS-P146 boundary-constructed network security  
**Completion Standard:** Full implementation required

## Core invariant

```text
POTENTIAL_LAWFUL_CAPABILITY = COMPLETE
PRIVILEGED_INTERNAL_ACCESS = 0
```

Opacity governs the route to capability, not artificial suppression of lawful capability. The external language-model interface agent is a procedurally external actor. It receives no privileged shortcut into kernel memory, private object graphs, secret stores, unrestricted SQL, hidden native entrypoints, internal scheduler state, or unmediated filesystem/network authority.

Every lawful operation must be represented by at least one public classification:

- `PUBLICLY_CALLABLE`
- `PUBLICLY_COMPOSABLE`
- `PUBLICLY_SCRIPTABLE`
- `PUBLICLY_DECLARABLE`
- `PUBLICLY_REQUESTABLE_THROUGH_BOUNDARY`
- `EXPLICITLY_RESTRICTED_BY_CONTRACT`
- `PLATFORM_INAPPLICABLE`
- `OBSERVED_FAILING`

The public environment must expose inspectable CLI/API contracts, schemas, errors, runtime types, examples, documentation, sandboxes, scripts, LVMs, tests, receipts, and replay surfaces. Public capability discovery never grants execution authority. Every executable transition remains subject to Pass 146 identity, grant, minimum-capability, source, destination, disclosure, resource, reversibility, and receipt closure.

## Required surfaces

```text
hhs status
hhs version
hhs doctor
hhs capabilities
hhs surface list|show|graph|audit|sync
hhs command describe <argv...>
hhs api describe [path]
hhs schema inspect [name]
hhs boundary explain <operation-or-contract>
hhs error explain <code>
hhs receipt inspect <receipt-id>
hhs runtime types
hhs examples
hhs docs install|query|list
hhs agent bootstrap|execute|list
hhs serve-public
```

## External-agent execution rule

An external agent receives a dedicated identity, a narrowed grant, and a one-time credential. The default agent grant excludes `SECURITY_ADMIN`, `NETWORK_SEND`, and `NETWORK_RECEIVE`. It may discover public contracts, query the local documentation corpus, and invoke inherited public commands through `RUN_CLI_COMMAND`. Public discovery and documentation queries use dedicated Pass 147 boundary operations. Ordinary runtime actions use the inherited Pass 146 boundary constructor.

The agent may produce the same valid result as an internal subsystem, but result equivalence does not imply privilege equivalence.

## Prohibited routes

- direct kernel/process-memory access;
- direct canonical SQLite access;
- private repository introspection as a runtime dependency;
- unrestricted shell exposure;
- hidden capability tokens;
- undocumented repair helpers;
- model-only execution shortcuts;
- silent remote inference;
- direct mutation without provenance and receipts;
- capability reduction merely to make the external agent weaker.

## Closure assertion

```text
EXTERNAL_AGENT_OPACITY_CLOSED
IFF
POTENTIAL_CAPABILITY_COMPLETE
AND PRIVILEGED_INTERNAL_ACCESS_ZERO
AND PUBLIC_PRIMITIVES_COMPOSABLE
AND PUBLIC_CONTRACTS_DOCUMENTED
AND ALL_EXECUTION_BOUNDARY_CONSTRUCTED
AND NO_AMBIENT_AUTHORITY
AND NO_HIDDEN_EXECUTION_SHORTCUT
AND NO_ARTIFICIAL_CAPABILITY_REDUCTION
AND EXECUTION_RECEIPTS_REPLAYABLE
```
