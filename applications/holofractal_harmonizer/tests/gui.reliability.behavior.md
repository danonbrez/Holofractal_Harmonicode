# GUI reliability acceptance matrix

This dependency-scoped interface pass preserves all runtime authority and software lifecycle behavior while enforcing the following presentation guarantees:

- Every temporary overlay or mobile sheet has a visible close control.
- Escape, backdrop tap, and mobile browser Back dismiss the active temporary surface.
- Opening one temporary surface closes every other temporary surface.
- Focus returns to the calling control after dismissal.
- Command and panel surfaces use translucent glass backgrounds with readable contrast.
- Mobile Code, Lifecycle, Output, and 3D panes are mutually exclusive and persist the last selected pane.
- Explorer and Inspector behave as bounded side sheets with safe-area-aware dimensions.
- Dynamic viewport height changes do not strand controls beneath the mobile browser chrome.
- No frontend surface acquires runtime, VM81, Hash216, ingress, compiler, or egress authority.
