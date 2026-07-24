REPO_ROOT := ../..
PYTHON ?= python
PYTHONPATH_ENV := PYTHONPATH=$(REPO_ROOT)/python

.PHONY: validate-spec build-parameters generate-c generate-shaders generate-collisions compile-native compile-shaders test-gfcc test-gfcc-negative test-gfcc-replay verify-gfcc verify-pass-152 package-pass-152 clean

validate-spec:
	$(PYTHONPATH_ENV) $(PYTHON) -m hhs_gfcc.cli validate-spec --repo $(REPO_ROOT) --output json

build-parameters:
	$(PYTHONPATH_ENV) $(PYTHON) -m hhs_gfcc.cli build-parameters --repo $(REPO_ROOT) --output json

generate-c:
	$(PYTHONPATH_ENV) $(PYTHON) -m hhs_gfcc.cli generate-c --repo $(REPO_ROOT) --output json

generate-shaders:
	$(PYTHONPATH_ENV) $(PYTHON) -m hhs_gfcc.cli generate-shaders --repo $(REPO_ROOT) --output json

generate-collisions:
	$(PYTHONPATH_ENV) $(PYTHON) -m hhs_gfcc.cli generate-collisions --repo $(REPO_ROOT) --output json

compile-native: generate-c
	$(PYTHONPATH_ENV) $(PYTHON) -m hhs_gfcc.cli compile-native --repo $(REPO_ROOT) --output json

compile-shaders: generate-shaders
	$(PYTHONPATH_ENV) $(PYTHON) -m hhs_gfcc.cli compile-shaders --repo $(REPO_ROOT) --output json

test-gfcc:
	$(PYTHONPATH_ENV) $(PYTHON) -m pytest -q $(REPO_ROOT)/tests/test_hhs_gfcc_pass152.py $(REPO_ROOT)/tests/test_hhs_gfcc_cross_lane.py -k 'not negative and not replay'

test-gfcc-negative:
	$(PYTHONPATH_ENV) $(PYTHON) -m pytest -q $(REPO_ROOT)/tests/test_hhs_gfcc_pass152.py -k negative

test-gfcc-replay:
	$(PYTHONPATH_ENV) $(PYTHON) -m pytest -q $(REPO_ROOT)/tests/test_hhs_gfcc_pass152.py $(REPO_ROOT)/tests/test_hhs_gfcc_cross_lane.py -k replay

verify-gfcc:
	$(PYTHONPATH_ENV) $(PYTHON) -m hhs_gfcc.cli verify --repo $(REPO_ROOT) --output json

package-pass-152:
	$(PYTHONPATH_ENV) $(PYTHON) -m hhs_gfcc.cli package --repo $(REPO_ROOT) --output json

verify-pass-152: validate-spec test-gfcc test-gfcc-negative test-gfcc-replay package-pass-152

clean:
	rm -rf build dist manifest receipts reports generated/c generated/maps generated/shaders
