PYTHON ?= python3
CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -pedantic
BUILD := build
NATIVE_INCLUDE := native/include
NATIVE_SOURCE := native/src/hhs_pass190_abi.c
NATIVE_TEST_SOURCE := native/tests/test_hhs_pass190_abi.c
NATIVE_LIBRARY := $(BUILD)/libhhs_pass190_abi.so
NATIVE_TEST := $(BUILD)/test_hhs_pass190_abi

.PHONY: validate test compile no-private-eval sdk-check bindings-check gui-check deploy-check native-abi native-test native-generated-check iteration3-check iteration4-check iteration5-check iteration6-check iteration7-check clean

validate: native-abi native-test test compile no-private-eval sdk-check bindings-check gui-check deploy-check native-generated-check iteration3-check iteration4-check iteration5-check iteration6-check iteration7-check

$(BUILD):
	mkdir -p $(BUILD)

$(NATIVE_LIBRARY): $(NATIVE_SOURCE) $(NATIVE_INCLUDE)/hhs_pass190_abi.h native/generated/hhs_pass190_operation_table.inc | $(BUILD)
	$(CC) $(CFLAGS) -fPIC -I$(NATIVE_INCLUDE) -shared $(NATIVE_SOURCE) -o $(NATIVE_LIBRARY)

$(NATIVE_TEST): $(NATIVE_SOURCE) $(NATIVE_TEST_SOURCE) $(NATIVE_INCLUDE)/hhs_pass190_abi.h native/generated/hhs_pass190_operation_table.inc | $(BUILD)
	$(CC) $(CFLAGS) -I$(NATIVE_INCLUDE) $(NATIVE_SOURCE) $(NATIVE_TEST_SOURCE) -o $(NATIVE_TEST)

native-abi: $(NATIVE_LIBRARY)

native-test: $(NATIVE_TEST)
	./$(NATIVE_TEST)

test:
	PYTHONPATH=python:server:tools:worker HHS_PASS190_NATIVE_LIBRARY=$(NATIVE_LIBRARY) $(PYTHON) -m unittest -v python/test_hhs_pass190.py python/test_hhs_pass190_iteration2.py python/test_hhs_pass190_iteration3.py python/test_hhs_pass190_iteration3_hardening.py python/test_hhs_pass190_iteration4.py python/test_hhs_pass190_iteration5.py python/test_hhs_pass190_iteration5_runtime.py python/test_hhs_pass190_iteration6.py python/test_hhs_pass190_iteration7.py

compile:
	$(PYTHON) -m py_compile python/hhs_pass190.py python/hhs_pass190_capability.py python/hhs_pass190_iteration2.py python/hhs_pass190_iteration3.py python/hhs_pass190_iteration3_hardening.py python/hhs_pass190_iteration4.py python/hhs_pass190_iteration5.py python/hhs_pass190_iteration5_runtime.py python/hhs_pass190_iteration6_registry.py python/hhs_pass190_iteration6.py python/hhs_pass190_iteration6_runtime.py python/hhs_pass190_iteration6_compiler.py python/hhs_pass190_iteration7_registry.py python/hhs_pass190_iteration7.py python/hhs_pass190_iteration7_compiler.py server/hhs_pass190_server.py server/hhs_pass190_iteration2_server.py server/hhs_pass190_iteration3_server.py server/hhs_pass190_iteration4_server.py server/hhs_pass190_iteration5_server.py server/hhs_pass190_iteration6_server.py server/hhs_pass190_iteration7_server.py worker/hhs_pass190_iteration7_worker.py python/test_hhs_pass190.py python/test_hhs_pass190_iteration2.py python/test_hhs_pass190_iteration3.py python/test_hhs_pass190_iteration3_hardening.py python/test_hhs_pass190_iteration4.py python/test_hhs_pass190_iteration5.py python/test_hhs_pass190_iteration5_runtime.py python/test_hhs_pass190_iteration6.py python/test_hhs_pass190_iteration7.py tools/generate_sdks.py tools/generate_bindings.py tools/generate_native_abi.py tools/issue_capability.py tools/verify_iteration2_gui.py tools/verify_iteration3.py tools/verify_iteration3_gui.py tools/verify_iteration4.py tools/verify_iteration4_gui.py tools/verify_iteration5.py tools/verify_iteration5_gui.py tools/verify_iteration6.py tools/verify_iteration6_gui.py tools/verify_iteration7.py tools/verify_iteration7_gui.py tools/verify_deploy.py sdk/python/hhs_pass190_client.py

no-private-eval:
	! grep -R -n -E '(^|[^A-Za-z_])(eval|exec)[[:space:]]*\(' python server worker sdk/python

sdk-check:
	PYTHONPATH=python $(PYTHON) tools/generate_sdks.py --check

bindings-check:
	PYTHONPATH=python $(PYTHON) tools/generate_bindings.py --check

gui-check:
	$(PYTHON) tools/verify_iteration2_gui.py
	$(PYTHON) tools/verify_iteration3_gui.py
	$(PYTHON) tools/verify_iteration4_gui.py
	$(PYTHON) tools/verify_iteration5_gui.py
	$(PYTHON) tools/verify_iteration6_gui.py
	$(PYTHON) tools/verify_iteration7_gui.py

deploy-check:
	$(PYTHON) tools/verify_deploy.py

native-generated-check:
	$(PYTHON) tools/generate_native_abi.py --check

iteration3-check:
	$(PYTHON) tools/verify_iteration3.py

iteration4-check:
	$(PYTHON) tools/verify_iteration4.py

iteration5-check:
	$(PYTHON) tools/verify_iteration5.py

iteration6-check:
	$(PYTHON) tools/verify_iteration6.py

iteration7-check:
	$(PYTHON) tools/verify_iteration7.py

clean:
	rm -rf $(BUILD) python/__pycache__ server/__pycache__ tools/__pycache__ worker/__pycache__ sdk/python/__pycache__
