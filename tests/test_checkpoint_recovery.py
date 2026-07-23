import json
import zipfile
from pathlib import Path

import pytest

from tools.hhs_checkpoint_recovery import (
    build_child_checkpoint,
    compare_parent_child,
    inventory_zip,
)


def make_zip(path: Path, files: dict[str, bytes]):
    with zipfile.ZipFile(path, 'w') as zf:
        for name, data in files.items():
            zf.writestr(name, data)


def full_parent_files():
    files = {
        'hhs_runtime/core.py': b'core',
        'hhs_backend/server.py': b'server',
        'hhs_python/bridge.py': b'bridge',
        'hhs_gui/main.tsx': b'main',
        'hhs_foundation/invariants.py': b'inv',
        'tests/test_core.py': b'test',
        'contracts/root.md': b'contract',
        'schemas/root.json': b'{}',
        'tools/run.py': b'run',
    }
    for i in range(120):
        files[f'hhs_runtime/module_{i:03d}.py'] = f'x={i}'.encode()
    files['__pycache__/junk.pyc'] = b'cache'
    return files


def test_evidence_zip_rejected_as_parent(tmp_path: Path):
    evidence = tmp_path / 'evidence.zip'
    make_zip(evidence, {f'PASS_132_REPORT_{i}.json': b'{}' for i in range(50)})
    assert inventory_zip(evidence).archive_class == 'EVIDENCE_ONLY_OR_NONCHECKPOINT'
    delta = tmp_path / 'delta'; delta.mkdir(); (delta / 'new.py').write_text('x=1')
    with pytest.raises(ValueError):
        build_child_checkpoint(evidence, delta, tmp_path / 'out.zip')


def test_full_parent_is_copied_and_cache_is_excluded(tmp_path: Path):
    parent = tmp_path / 'parent.zip'
    make_zip(parent, full_parent_files())
    delta = tmp_path / 'delta'; delta.mkdir()
    (delta / 'hhs_runtime').mkdir(); (delta / 'hhs_runtime' / 'pass133.py').write_text('ok=True')
    out = tmp_path / 'child.zip'
    receipt = build_child_checkpoint(parent, delta, out)
    assert receipt['status'] == 'FULL_ANCESTOR_COPY_VERIFIED'
    comp = compare_parent_child(parent, out)
    assert comp['ancestry_complete'] is True
    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
    assert 'hhs_runtime/core.py' in names
    assert 'hhs_runtime/pass133.py' in names
    assert not any('__pycache__' in n for n in names)


def test_missing_system_file_fails_ancestry_comparison(tmp_path: Path):
    p = tmp_path / 'p.zip'; c = tmp_path / 'c.zip'
    files = full_parent_files(); make_zip(p, files)
    files.pop('hhs_runtime/core.py'); make_zip(c, files)
    comp = compare_parent_child(p, c)
    assert comp['ancestry_complete'] is False
    assert 'hhs_runtime/core.py' in comp['missing_parent_sample']
