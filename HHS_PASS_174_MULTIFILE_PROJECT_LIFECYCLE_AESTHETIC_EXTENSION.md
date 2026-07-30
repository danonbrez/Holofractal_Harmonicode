# HHS PASS 174 — MULTIFILE PROJECT LIFECYCLE AND AESTHETIC EXTENSION

## Normative identity

- Repository: `danonbrez/Holofractal_Harmonicode`
- Protected baseline: authoritative `main` at `39261b3b0af3fad7b5873d20a2fd7421913274a3`
- Extension identifier: `HHS-P174-MPCL-AE-V1`
- Merge target: `main`
- Compatibility rule: the stable Heroku production entrypoint, FastAPI route composition, current single-file lifecycle, assistant, VM81 snapshot, Hash72, and Hash216 surfaces remain unchanged.

## Required result

The visual IDE SHALL support a real project working-copy lifecycle from file and folder creation/import through backend-admitted per-file lifecycle execution, multiple authorized compiler targets, and ZIP folder export.

The extension SHALL remain additive. It SHALL NOT replace the deployed page shell, production server, existing CSS files, existing lifecycle endpoint, or current local working-copy persistence.

## Delivered project workflow

1. Create a path-aware project file without resetting existing files.
2. Add non-destructive starter files for a web application, content package, or HHS automation project.
3. Import a browser-selected folder while preserving relative paths.
4. Select one or more existing authorized compiler targets:
   - `HHS_IR`
   - `C_KERNEL_PLAN`
   - `C_SOURCE`
   - `PYTHON_ADAPTER`
   - `JSON_EXECUTION_GRAPH`
   - `DOT_GRAPH`
   - `BYTECODE_OR_VM_PLAN`
   - `RECEIPT_ONLY_PLAN`
5. Submit each text-capable source through `/api/runtime/development/lifecycle` and submit additional target compilations through `/api/runtime/workspace/command` using `compile.execute`.
6. Submit preserved binary modalities through Pass 165 ingress and exact snapshot retrieval.
7. Generate a standards-compatible ZIP containing:
   - `source/` — original project files with relative paths preserved;
   - `build/<target>/` — unmodified backend compiler results;
   - `evidence/` — lifecycle, ingress, snapshot, and execution evidence;
   - `receipts/` — returned Hash72/Hash216-related receipt material;
   - `project.hhs-manifest.json` — archive manifest;
   - `ARCHIVE_README.txt` — authority boundary statement.

## Authority boundary

The browser ZIP writer performs packaging only. It does not invent runtime results and does not become VM81, compiler, Hash72, Hash216, ingress, or execution authority. Backend evidence is stored unmodified in the archive.

The currently authorized compiler targets produce the repository's existing HHS compiled-artifact representations and plans. This extension does not claim that those artifacts are already host-native executables, rendered media binaries, or independently deployed target applications.

## Aesthetic integration

The uploaded Harmonicode Studio reference supplied the warm charcoal, amber, gold, restrained glow, compact panel, and monospace-accent direction. The extension applies that direction through a new stylesheet loaded after the current style stack. Existing layout, responsiveness, selectors, accessibility surfaces, and runtime wiring remain intact.

## Bounded operation

A browser project build is bounded to 64 files and 24 MiB of source bytes per archive invocation. Files are processed sequentially to avoid destabilizing the deployed Heroku runtime.

## Validation

- `node --test applications/holofractal_harmonizer/tests/project.lifecycle.test.mjs`
- `node --check` for all added or modified JavaScript modules
- independent Python `zipfile` readback of a generated archive

The validation covers ZIP signatures and CRC-32, path preservation, multiple compiler targets, authority endpoints, source preservation markers, additive visual-IDE boot integration, and warm-theme variables.
