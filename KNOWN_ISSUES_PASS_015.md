# KNOWN ISSUES PASS 015

- Some non-authority display/projection helpers still import legacy `hash72_digest`; future passes should distinguish harmless display projection from authoritative receipt generation.
- GUI/IDE layers are not yet fully bound to the kernel-backed Hash72 witness metadata.
- The C ring currently exposes the core `u^72` state machine primitives; deeper Golay parity and expanded `u^216` transport remain future kernel passes.
- Full GUI build still requires Node dependency installation outside the ZIP.
