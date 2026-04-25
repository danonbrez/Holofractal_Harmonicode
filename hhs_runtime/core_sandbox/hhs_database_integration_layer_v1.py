from pathlib import Path
import runpy

_ROOT = Path(__file__).resolve().parents[2] / 'hhs_database_integration_layer_v1.py'
if _ROOT.exists():
    _ns = runpy.run_path(str(_ROOT))
    globals().update({k: v for k, v in _ns.items() if not k.startswith('__')})
else:
    raise ImportError('missing root compatibility source for hhs_database_integration_layer_v1')
