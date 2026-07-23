import json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_parent_tree_is_immutable():
    result=subprocess.run([sys.executable,str(ROOT/'tools/verify_pass144_parent_immutability.py')],cwd=ROOT,capture_output=True,text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    report=json.loads((ROOT/'reports/pass_144/PASS_144_PARENT_IMMUTABILITY_REPORT.json').read_text())
    assert report['status']=='VERIFIED_IMMUTABLE'
    assert report['errors']==[]

def test_documentation_and_lemma_corpus_present():
    required=[
      'docs/pass_144/README.md','docs/pass_144/USER_GUIDE.md','docs/pass_144/CLI_MANUAL.md',
      'docs/pass_144/API_MANUAL.md','docs/pass_144/INVARIANT_ALGEBRA_GUIDE.md',
      'docs/pass_144/RECEIPTS_AND_AUTHORITY.md','docs/pass_144/PROOF_LEMMA_CORPUS_GUIDE.md',
      'docs/pass_144/GLOSSARY.md','formal/lemmas/pass_144/LEMMA_CORPUS.json'
    ]
    for rel in required:
        assert (ROOT/rel).is_file(), rel
    corpus=json.loads((ROOT/'formal/lemmas/pass_144/LEMMA_CORPUS.json').read_text())
    ids=[x['id'] for x in corpus['lemmas']]
    assert len(ids)==len(set(ids))
    assert len(ids)>=10
