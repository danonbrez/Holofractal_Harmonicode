# Known Issues — Pass 022

1. `PLUGIN_READY` does not mean executable. It means retained for future guarded adapter integration.
2. Some plugin-ready modules may fail direct import because they predate the canonical runtime contract. They must not be exposed without wrappers.
3. Full monolithic pytest can become slow after repeated tests append large receipt/manifest data to runtime ledgers. Split verification remains the safer release workflow.
4. The next passes must prioritize converting plugin-ready categories into guarded adapters by subsystem rather than attempting broad direct imports.
