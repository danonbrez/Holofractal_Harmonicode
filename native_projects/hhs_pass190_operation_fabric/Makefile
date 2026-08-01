PYTHON ?= python3

.PHONY: validate test compile no-private-eval sdk-check bindings-check gui-check deploy-check clean

validate: test compile no-private-eval sdk-check bindings-check gui-check deploy-check

test:
	PYTHONPATH=python:server:tools $(PYTHON) -m unittest -v python/test_hhs_pass190.py python/test_hhs_pass190_iteration2.py

compile:
	$(PYTHON) -m py_compile python/hhs_pass190.py python/hhs_pass190_iteration2.py server/hhs_pass190_server.py server/hhs_pass190_iteration2_server.py python/test_hhs_pass190.py python/test_hhs_pass190_iteration2.py tools/generate_sdks.py tools/generate_bindings.py tools/verify_iteration2_gui.py tools/verify_deploy.py sdk/python/hhs_pass190_client.py

no-private-eval:
	! grep -R -n -E '(^|[^A-Za-z_])(eval|exec)[[:space:]]*\(' python server sdk/python

sdk-check:
	PYTHONPATH=python $(PYTHON) tools/generate_sdks.py --check

bindings-check:
	PYTHONPATH=python $(PYTHON) tools/generate_bindings.py --check

gui-check:
	$(PYTHON) tools/verify_iteration2_gui.py

deploy-check:
	$(PYTHON) tools/verify_deploy.py

clean:
	rm -rf python/__pycache__ server/__pycache__ tools/__pycache__ sdk/python/__pycache__
