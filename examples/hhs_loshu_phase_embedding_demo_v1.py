"""
Demo: HHS Lo Shu Phase Embedding
--------------------------------

Runs a small deterministic embedding and prints the resulting receipt.
"""

import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import embed_sequence


def main() -> None:
    tokens = ["Holofractal", "Harmonicode", "Hash72", "LoShu"]
    receipt = embed_sequence(tokens, d_model=72, dimensions=4)
    print(json.dumps(receipt.to_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
