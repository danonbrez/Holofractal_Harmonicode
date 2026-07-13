# KNOWN ISSUES PASS 003

## C Compiler Warnings

`make verify-c` still reports existing C warnings around missing struct initializer fields and unused functions. These should be cleaned in a later C-hardening pass.

## Backend Still Uses Raw Controller

The backend runtime routes still instantiate `HHSRuntimeController` directly. Pass 003 adds the emulator surface, but the backend has not yet been rewired to use it as the primary runtime lifecycle authority.

## GUI Has No Emulator Controls Yet

The GUI can connect to runtime endpoints, but there is not yet a polished boot/run/halt/status control surface for the automatic emulator lifecycle.

## No Persistent Emulator State File Yet

The emulator state is runtime-memory only. A later pass should persist boot/session metadata and receipt packet history into the storage layer.
