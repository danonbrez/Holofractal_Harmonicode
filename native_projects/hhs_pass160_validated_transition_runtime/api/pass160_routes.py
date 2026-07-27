#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.pass160_suite import api_serve

if __name__ == '__main__':
    raise SystemExit(api_serve('127.0.0.1', 9160))
