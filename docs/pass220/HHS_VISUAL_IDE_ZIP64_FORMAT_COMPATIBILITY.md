# IDE classic ZIP / ZIP64 compatibility extension

## Scope

The existing visual IDE and deployable-app export paths both use
`applications/holofractal_harmonizer/src/project-zip.mjs`.
The existing implementation emitted classic ZIP only, rejected entry count
greater than 65,535, and truncated record size/offset fields through
32-bit integer serialization.

The additive extension preserves the existing classic ZIP output for ordinary
projects, and emits standards-conforming ZIP64 directory and locator records
when entry count or archive offsets require it. ZIP64 per-entry size and offset
extra fields are encoded when needed. It uses the original stored/no-compression
record layout, UTF-8 filenames, deterministic timestamps, source bytes,
CRC32, path traversal checks, and duplicate-path rejection.

## Verification

`applications/holofractal_harmonizer/tests/project.zip64.test.mjs`
constructs a 65,536-entry archive with preserved relative source paths and
binary data. The test uses Python's independent standard-library
`zipfile.ZipFile` reader to enumerate, extract, CRC-check, and verify
the first and last entries. It also exercises classic ZIP backward compatibility.

This tests ZIP64 central-directory entry-count expansion. It does not simulate
or prove a >4 GiB file or archive offset; those cases require streamed
file-backed test fixtures and resource-appropriate production validation.

## Remaining native/application boundary

`createStoredZip` still assembles its archive in browser memory. This change
does **not** introduce streaming HTTP downloads, disk-backed source editing,
browser-native File System Access API storage, incremental archive writing, or
remove actual browser memory constraints. These are the next conventional IDE
integration tasks; none should be treated as VM81, Hash72, or Lane 5 limits.

The change does not modify VM81/Hash216 authority, virtual CPU semantics,
source ingestion, or signed admission.
