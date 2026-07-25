from __future__ import annotations

import argparse
import json

from .environment import build_default_environment


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="hhs-pass153")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    chat = sub.add_parser("chat")
    chat.add_argument("prompt")
    chat.add_argument("--max-tokens", type=int, default=32)
    args = parser.parse_args(argv)
    env = build_default_environment()
    if args.command == "status":
        payload = env.status()
    else:
        session = env.create_session("hhs-reference-open-model-v1", session_id="cli")
        payload = env.chat(session.session_id, args.prompt, max_tokens=args.max_tokens)
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
