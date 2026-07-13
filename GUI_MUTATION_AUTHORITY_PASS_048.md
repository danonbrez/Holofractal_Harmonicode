# GUI Mutation Authority Boundary — Pass 048

The browser GUI may request mutation, but it cannot mutate runtime truth.

The new `RuntimeMutationClient` and `RuntimeMutationPanel` submit `AUTHORIZED_MUTATION` commands through the existing FastAPI command endpoint.  The GUI deliberately sets `assume_success_locally: false`.  The panel displays only receipt-backed mutation fields returned by the authority loop and projected by WebSocket feedback.

Failure states include:

- `REJECT_UI_EVENT_AS_RUNTIME_TRUTH`
- `REJECT_MUTATION_NOT_ALLOWLISTED`
- `REJECT_MUTATION_WITHOUT_KERNEL_DERIVATION`
- `REJECT_MUTATION_WITHOUT_PRE_STATE`
- `REJECT_MUTATION_WITHOUT_TRANSFORMATION_IDENTITY`
- `REJECT_MUTATION_WITHOUT_POST_STATE`
- `REJECT_MUTATION_WITHOUT_REVERSAL_WITNESS`
- `REJECT_MUTATION_WITHOUT_RECEIPT`
