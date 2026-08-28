PYTHON ?= python3
ROOT := ../..

.PHONY: validate test bytecode cli-smoke schema-parse

test:
	cd $(ROOT) && PYTHONPATH=. $(PYTHON) -m unittest discover -s tests/pass188 -p 'test_*.py' -v

bytecode:
	cd $(ROOT) && $(PYTHON) -m py_compile 		hhs_runtime/pass188/__init__.py 		hhs_runtime/pass188/license_lineage.py 		hhs_runtime/pass188/license_server.py 		tests/pass188/test_pass188_license_lineage.py

schema-parse:
	cd $(ROOT) && $(PYTHON) -c 'import json,glob; files=glob.glob("schemas/pass188/HHS_PASS_188_*_V1.schema.json"); assert len(files) >= 5; [json.load(open(p, encoding="utf-8")) for p in files]'

cli-smoke:
	cd $(ROOT) && tmp=$$(mktemp -d); 		PYTHONPATH=. $(PYTHON) -m hhs_runtime.pass188.license_lineage --db $$tmp/pass188.sqlite3 verify > $$tmp/verify.json; 		$(PYTHON) -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["replay"]["valid"] is True; assert d["new_vm81_authority"] is False; assert d["new_hash72_clock"] is False' $$tmp/verify.json; 		rm -rf $$tmp

validate: bytecode schema-parse test cli-smoke
