# Pass 146 CLI

The root `hhs` command preserves inherited Pass 145 commands and automatically wraps them in minimum-capability boundaries.

## Security administration

```text
hhs security status
hhs security bootstrap-local
hhs security identity create <name> ...
hhs security grant create <identity> ...
hhs security peer public-identity <identity-id>
hhs security peer trust <peer-id> <public-key-b64> ...
hhs security peer list
```

## Path lifecycle

```text
hhs security path construct <operation> '<request-json>' ...
hhs security path execute <contract-id> ...
hhs security path inspect <contract-id>
hhs security path list
hhs security path replay <contract-id>
```

## Propagation

```text
hhs security message inspect <message-id>
hhs security message receive <message-id> ...
hhs security message admit @signed-envelope.json ...
```

`message receive` revalidates a message already present in one database. `message admit` imports a signed envelope into another node by constructing a `RECEIVE_PROPAGATION` boundary.
