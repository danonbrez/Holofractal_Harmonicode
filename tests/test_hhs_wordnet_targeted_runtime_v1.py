from __future__ import annotations

import csv
from pathlib import Path

from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import load_wordnet_relations


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> Path:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_targeted_wordnet_hydration_matches_full_entries_for_selected_words(tmp_path: Path):
    synonyms = _write_csv(
        tmp_path / "WordnetSynonyms.csv",
        ["Word", "Count", "POS", "Synonyms"],
        [
            {"Word": "remember", "Count": "2", "POS": "verb", "Synonyms": "recall;retain"},
            {"Word": "unrelated", "Count": "1", "POS": "adjective", "Synonyms": "separate"},
        ],
    )
    antonyms = _write_csv(
        tmp_path / "WordnetAntonyms.csv",
        ["Word", "Count", "POS", "Antonyms"],
        [
            {"Word": "remember", "Count": "1", "POS": "verb", "Antonyms": "forget"},
            {"Word": "unrelated", "Count": "1", "POS": "adjective", "Antonyms": "related"},
        ],
    )
    hypernyms = _write_csv(
        tmp_path / "WordnetHypernyms.csv",
        ["lemma", "Count", "part_of_speech", "hypernyms"],
        [
            {"lemma": "remember", "Count": "1", "part_of_speech": "verb", "hypernyms": "cognition"},
            {"lemma": "unrelated", "Count": "1", "part_of_speech": "adjective", "hypernyms": "relation"},
        ],
    )

    paths = [synonyms, antonyms, hypernyms]
    full = load_wordnet_relations(paths, require_all=False)
    targeted = load_wordnet_relations(
        paths,
        require_all=False,
        target_words={"Remember", "missing-token"},
    )

    assert set(full) == {"remember", "unrelated"}
    assert set(targeted) == {"remember"}
    assert targeted["remember"] == full["remember"]


def test_targeted_wordnet_hydration_allows_unknown_prompt_tokens(tmp_path: Path):
    synonyms = _write_csv(
        tmp_path / "WordnetSynonyms.csv",
        ["Word", "Count", "POS", "Synonyms"],
        [{"Word": "known", "Count": "1", "POS": "noun", "Synonyms": "recognized"}],
    )

    targeted = load_wordnet_relations(
        [synonyms],
        require_all=False,
        target_words={"not-present"},
    )

    assert targeted == {}
