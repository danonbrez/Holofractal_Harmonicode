# Pass 147 Public Environment

Pass 147 exposes the complete lawful HHS capability graph through public, documented, boundary-constructed primitives while preserving zero privileged internal access for the external agent.

Start with:

```text
hhs surface audit
hhs surface list
hhs command describe ingest file
hhs api describe /api/v1/query
hhs schema inspect public-capability
hhs boundary explain RUN_CLI_COMMAND
hhs runtime types
hhs docs install
hhs docs query "How does external-agent opacity work?"
```

Create a procedurally external identity:

```text
hhs agent bootstrap external-model
hhs agent execute --identity <id> --grant <grant> --token <token> -- surface audit
```

The returned token is displayed once. The default external grant excludes security administration and network send/receive authority.
