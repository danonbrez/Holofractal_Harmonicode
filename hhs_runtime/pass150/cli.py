from __future__ import annotations
import argparse, json, os
from pathlib import Path
from .genome import Hash216ImmuneSystem, KeyEpoch

def main(argv=None) -> int:
    p=argparse.ArgumentParser(prog="hhs-pass150")
    p.add_argument("--root", default=".hhs-pass150")
    sub=p.add_subparsers(dest="cmd", required=True)
    i=sub.add_parser("inspect"); i.add_argument("event"); i.add_argument("actor"); i.add_argument("payload")
    sub.add_parser("flush"); sub.add_parser("recover"); sub.add_parser("validate")
    args=p.parse_args(argv)
    key=os.environ.get("HHS_PASS150_KEY", "00"*32)
    sys=Hash216ImmuneSystem(Path(args.root), KeyEpoch.genesis(bytes.fromhex(key)))
    if args.cmd=="inspect": print(json.dumps(sys.echo_for_vm81(sys.inspect(args.event,args.actor,json.loads(args.payload))),sort_keys=True))
    elif args.cmd=="flush": print(sys.flush())
    elif args.cmd=="recover": print(json.dumps(sys.recover(),sort_keys=True))
    elif args.cmd=="validate": print(json.dumps({"valid":sys.validate_chain()}))
    return 0
if __name__ == "__main__": raise SystemExit(main())
