# Pass 146 Architecture

## Execution sequence

```text
request
→ authenticate identity
→ resolve active grant
→ derive exact operation capabilities
→ validate source and destination scopes
→ validate disclosure and resource bounds
→ construct immutable boundary contract
→ create inactive pathway
→ revalidate relevant state
→ activate temporary capabilities
→ execute registered adapter
→ validate output/resource/disclosure result
→ record ordered pathway steps
→ satisfy reversibility or recovery condition
→ close receipt
→ dissolve temporary capabilities
```

No public Pass 146 adapter accepts a direct runtime call that bypasses contract construction.

## Canonical objects

- `security_identities`
- `security_authority_grants`
- `security_boundary_contracts`
- `security_pathways`
- `security_pathway_steps`
- `security_messages`
- `security_peer_trust`
- `security_negotiations`

All participate in the canonical SQLite database root and inherited receipt chain.

## Minimum-path derivation

Each operation has a registered fixed capability floor. Dynamic capabilities are added only from an inspected script manifest, LVM manifest, or inherited CLI command class. A caller may declare the exact derived set. A broader declaration returns `CAPABILITY_OVERBROAD`; an incomplete declaration returns `AUTHORITY_INSUFFICIENT`.

## Recursive boundaries

A child contract may be constructed only while its parent is admitted or active. Child capabilities, disclosure fields, classification, resource budgets, identity, and recursive depth must remain within the parent surface.
