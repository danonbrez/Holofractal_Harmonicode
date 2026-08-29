PYTHON ?= python3
NODE ?= node
ROOT := ../..

.PHONY: bytecode schemas core benchmark browser validate

bytecode:
	cd $(ROOT) && $(PYTHON) -m py_compile \
		hhs_runtime/pass187/__init__.py \
		hhs_runtime/pass187/composition.py \
		hhs_runtime/pass187/adapters.py \
		hhs_runtime/pass187/composition_server.py \
		tests/pass187/test_pass187_composition.py \
		native_projects/hhs_pass187_composition_fabric/tools/hhs_pass187_browser_fixture.py \
		native_projects/hhs_pass187_composition_fabric/tools/hhs_pass187_planner_benchmark.py

schemas:
	cd $(ROOT) && $(PYTHON) -c 'import glob,json; files=glob.glob("schemas/pass187/HHS_PASS_187_*_V1.schema.json"); assert len(files) >= 4; [json.load(open(path, encoding="utf-8")) for path in files]'
	cd $(ROOT) && test -s grammar/pass187/harmonicode_graph_grammar.ebnf

core:
	cd $(ROOT) && PYTHONPATH=. $(PYTHON) -m unittest discover -s tests/pass187 -p 'test_*.py' -v

benchmark:
	cd $(ROOT) && PYTHONPATH=. $(PYTHON) native_projects/hhs_pass187_composition_fabric/tools/hhs_pass187_planner_benchmark.py > /tmp/hhs-pass187-planner-benchmark.json
	$(PYTHON) -c 'import json; d=json.load(open("/tmp/hhs-pass187-planner-benchmark.json")); assert d["nodes"] == 100; assert d["executed_nodes"] == 100; assert d["timing_authority"] == "NONAUTHORITATIVE"; assert d["floating_point_canonical_authority"] is False'

browser:
	cd $(ROOT) && $(NODE) native_projects/hhs_pass187_composition_fabric/tools/hhs_pass187_browser_acceptance.mjs

validate: bytecode schemas core benchmark browser
