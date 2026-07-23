#!/usr/bin/env python3
from pathlib import Path
import argparse, json, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from hhs_runtime.pass133_release import execute_release

p=argparse.ArgumentParser()
p.add_argument("--prime-bits",type=int,default=64)
a=p.parse_args()
print(json.dumps(execute_release(ROOT,prime_bits=a.prime_bits),indent=2,sort_keys=True))
