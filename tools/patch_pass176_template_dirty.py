#!/usr/bin/env python3
from pathlib import Path

path = Path('applications/holofractal_harmonizer/src/application-templates-runtime.mjs')
source = path.read_text(encoding='utf-8')
old = "      dirty: false,\n      checkpoint: `Created from ${template.label} starter`,"
new = "      dirty: true,\n      checkpoint: `Created from ${template.label} starter`,"
if old not in source:
    raise SystemExit('PASS176_TEMPLATE_DIRTY_PATCH_ANCHOR_MISSING')
source = source.replace(old, new, 1)
if 'dirty: false' in source[source.index('export function materializeApplicationTemplate'):]:
    raise SystemExit('PASS176_TEMPLATE_DIRTY_PATCH_INCOMPLETE')
path.write_text(source, encoding='utf-8')
print('PASS176_TEMPLATE_PROJECTS_MATERIALIZE_DIRTY')
