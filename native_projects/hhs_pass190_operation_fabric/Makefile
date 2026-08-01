PYTHON ?= python3

.PHONY: validate test compile no-private-eval clean

validate: test compile no-private-eval

test:
	PYTHONPATH=python:server $(PYTHON) -m unittest -v python/test_hhs_pass190.py

compile:
	$(PYTHON) -m py_compile python/hhs_pass190.py server/hhs_pass190_server.py python/test_hhs_pass190.py

no-private-eval:
	! grep -R -n -E '(^|[^A-Za-z_])(eval|exec)[[:space:]]*\(' python server

clean:
	rm -rf python/__pycache__ server/__pycache__
