from pathlib import Path
import runpy

# Canonical module body is loaded from the compatibility-preserved root source
# during this migration step. This file is the authoritative import target for
# new code; root-level hhs_general_runtime_layer_v1.py is now only a shim.
_ROOT = Path(__file__).resolve().parents[2] / 'hhs_general_runtime_layer_v1.py'
if _ROOT.exists():
    _ns = runpy.run_path(str(_ROOT))
    globals().update({k: v for k, v in _ns.items() if not k.startswith('__')})
else:
    raise ImportError('missing root compatibility source for hhs_general_runtime_layer_v1')
