# NEXT PASS — PASS 012

## Recommended focus
GUI/API contract binding and frontend service reachability.

## Objective
Expose the canonical contract through the consumer-facing runtime surface so the GUI, API, and future IDE tools do not invent local schemas.

## Targets
1. Bind GUI service discovery panels to canonical service descriptors.
2. Normalize frontend runtime packets against `HHS_RUNTIME_PACKET_CONTRACT_V1`.
3. Ensure command palette/service invocation uses the guarded service dispatch route.
4. Add compact contract projections for frontend use.
5. Add a backend route or service to report contract registry/status.

## Rule
No frontend action should become an alternate execution path. GUI events are projections into canonical runtime contracts, not independent authority.
