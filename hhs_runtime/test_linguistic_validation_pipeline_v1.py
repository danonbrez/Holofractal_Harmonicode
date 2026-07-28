import json
import tempfile
from pathlib import Path

from hhs_runtime.hhs_linguistic_validation_pipeline_v1 import (
    DEFAULT_NLG_OPTIMAL_PROFILE,
    optimize_nlg_workload_profile,
    run_default_nlg_workload_validation,
    run_linguistic_validation_pipeline,
)


def _write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    import csv

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for r in rows:
            writer.writerow(r)


def test_pipeline_smoke_with_temp_csvs():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        # --- grammar CSV ---
        grammar_csv = root / "grammar.csv"
        _write_csv(
            grammar_csv,
            ["Serial Number", "Error Type", "Ungrammatical Statement", "Standard English"],
            [["1", "spacing", "bad  spacing", "bad spacing"]],
        )

        # --- WordNet CSV set (minimal valid rows for each file) ---
        wn_files = {
            "WordnetNouns.csv": (["Word", "Count", "POS", "Definition"], [["system", "1", "n", "a set of elements"]]),
            "WordnetVerbs.csv": (["Word", "Count", "Sense", "Definition", "Example 1", "Example 2"], [["preserves", "1", "", "keep", "", ""]]),
            "WordnetAdjectives.csv": (["Word", "Count", "Senses", "Definition", "Example 1", "Example 2", "Example 3", "Example 4"], [["valid", "1", "", "sound", "", "", "", ""]]),
            "WordnetAdverbs.csv": (["Word", "Count", "Senses", "Definition", "Example"], [["well", "1", "", "properly", ""]]),
            "WordnetSynonyms.csv": (["Word", "Count", "POS", "Synonyms"], [["system", "1", "n", "structure"]]),
            "WordnetAntonyms.csv": (["Word", "Count", "POS", "Antonyms"], [["valid", "1", "a", "invalid"]]),
            "WordnetHypernyms.csv": (["lemma", "Count", "part_of_speech", "hypernyms"], [["system", "1", "n", "entity"]]),
            "WordnetHyponyms.csv": (["lemma", "Count", "part_of_speech", "hyponyms"], [["system", "1", "n", "subsystem"]]),
        }

        wn_paths = []
        for name, (header, rows) in wn_files.items():
            p = root / name
            _write_csv(p, header, rows)
            wn_paths.append(p)

        # --- run pipeline ---
        text = "bad  spacing in system preserves valid meaning"
        receipt = run_linguistic_validation_pipeline(
            text,
            grammar_csv_path=grammar_csv,
            wordnet_paths=wn_paths,
            require_wordnet=True,
            max_steps=9,
        )

        data = receipt.to_dict()

        # --- assertions ---
        assert data["grammar_status"] == "READY"
        assert data["wordnet_status"] == "READY"
        assert "training_run" in data
        assert data["training_run"]["accepted"] >= 0
        assert len(data["preflight_feedback_records"]) >= 2

        # Ensure JSON serializable
        json.dumps(data)


def test_nlg_optimizer_sweep_selects_zero_rejection_profile():
    receipt = optimize_nlg_workload_profile(
        prompts=["No token is false.", "Every relation remains in scope."],
        require_grammar_options=(False,),
        require_wordnet_options=(True,),
        min_wordnet_known_ratio_options=(0.0, 0.8),
        max_steps_options=(9,),
        max_propositions_options=(64,),
        max_candidates_options=(8,),
        target_min_acceptance=0.5,
    )
    data = receipt.to_dict()
    assert data["status"] in {"LOCKED_OPTIMAL_PROFILE", "DEGRADED_PROFILE_FALLBACK"}
    assert data["selected_profile"]["require_wordnet"] is True
    assert data["selected_profile"]["max_propositions"] == 64
    assert data["selected_profile"]["max_candidates"] == 8
    assert len(data["evaluations"]) == 2
    assert all(item["rejection_code_incidence"] == 0 for item in data["evaluations"])


def test_default_nlg_workload_profile_runs_gate():
    receipt = run_default_nlg_workload_validation("No token is false.", profile=DEFAULT_NLG_OPTIMAL_PROFILE)
    data = receipt.to_dict()
    assert data["runtime_gate"]["status"] in {"ACCEPTED", "REJECTED"}
    assert data["runtime_gate"]["wordnet_required"] is True
