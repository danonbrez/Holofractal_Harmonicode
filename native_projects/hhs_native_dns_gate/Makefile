PYTHON ?= python3

.PHONY: validate test compile integration repository shell

validate: test compile integration repository shell

test:
	PYTHONPATH=python $(PYTHON) -m unittest -v python/test_hhs_dns_gate.py

integration:
	$(PYTHON) tools/verify_integration.py

repository:
	$(PYTHON) tools/verify_repository_assets.py

compile:
	$(PYTHON) -m py_compile python/hhs_dns_gate.py python/test_hhs_dns_gate.py tools/verify_integration.py tools/verify_repository_assets.py

shell:
	bash -n deploy/install.sh deploy/verify.sh
