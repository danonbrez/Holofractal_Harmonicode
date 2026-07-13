# Known Issues — Pass 010

- Existing repository modules still contain direct `json.dumps`, `write_text`, and serialization logic that must be audited and migrated where those operations influence runtime state or external outputs.
- Snapshot pickle serialization remains present and should be reviewed for authority wrapping and safety policy in a later pass.
- GUI build/typecheck is still blocked until Node dependencies are installed outside the ZIP.
