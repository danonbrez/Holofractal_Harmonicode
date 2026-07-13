# Known Issues — Pass 048

- Live mutation execution remains deliberately conservative. Broad plugin execution, arbitrary persistence writes, and unbounded user payload mutation remain outside the allow-list.
- Non-tick authorized operations are receipt-backed control/snapshot actions; they do not directly mutate the C kernel state.
- Full browser automation was not added in this pass; the dependency-free GUI source verifier checks the mutation client/panel wiring.
- Aggregate Make targets can exceed container time limits because prior passes have accumulated many service and conformance self-tests.
