from __future__ import annotations

import csv
from pathlib import Path

from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import load_wordnet_relations
from hhs_runtime import hhs_pass220_i051_native_lean_alignment_v1 as alignment


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

def test_native_lean_runtime_hydrates_only_prompt_tokens(monkeypatch):
    observed: dict[str, object] = {}

    def fake_loader(paths, *, require_all=True, target_words=None):
        observed["require_all"] = require_all
        observed["target_words"] = tuple(target_words or ())
        return {}

    monkeypatch.setattr(alignment, "load_wordnet_relations", fake_loader)
    monkeypatch.setattr(
        alignment,
        "default_wordnet_paths",
        lambda: [Path("/tmp/hhs-wordnet-runtime-test.csv")],
    )
    alignment._relation_db_for_prompt_tokens.cache_clear()
    try:
        result = alignment.admit_native_lean_alignment_tensor(
            "Remember this exact token",
            "response-only-word",
        )
    finally:
        alignment._relation_db_for_prompt_tokens.cache_clear()

    assert observed["require_all"] is True
    assert set(observed["target_words"]) == {"remember", "this", "exact", "token"}
    assert "response-only-word" not in observed["target_words"]
    assert result["wordnet_geometry"]["relation_db_error"] is None

