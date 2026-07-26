CC ?= cc
CXX ?= c++
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -pedantic
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -Werror -pedantic
ROOT := ../..
INCLUDES := -Iinclude -Isrc -I$(ROOT)/hhs_runtime/include -I$(ROOT)/hhs_runtime/c
HASH_SRC := $(ROOT)/hhs_runtime/src/hhs_hash216.c
RUNTIME_SRC := $(ROOT)/hhs_runtime/c/hhs_runtime_abi.c
SRC := src/hhs_pass158_helpers.c src/hhs_pass158_descriptors.c src/hhs_pass158_objects.c src/hhs_pass158_transition.c src/hhs_pass158_delta.c src/hhs_pass158_serialization.c
DIST := dist
JAVA_HOME ?= $(shell dirname $$(dirname $$(readlink -f $$(command -v javac 2>/dev/null))))
JNI_INCLUDES := -I$(JAVA_HOME)/include -I$(JAVA_HOME)/include/linux
PYTHONPATH158 := $(ROOT):bindings/python:api

.PHONY: all native-test python-test bindings service gui-projection evidence verify package clean

all: $(DIST)/libhhs_pass158.so $(DIST)/hhs-pass158 $(DIST)/test-pass158

$(DIST):
	mkdir -p $(DIST)

$(DIST)/libhhs_pass158.so: $(SRC) include/hhs_pass158_api.h include/hhs_pass158_types.h include/hhs_pass158_status.h include/hhs_pass158_opcodes.h $(HASH_SRC) $(RUNTIME_SRC) | $(DIST)
	$(CC) $(CFLAGS) -fPIC -shared $(INCLUDES) $(SRC) $(HASH_SRC) $(RUNTIME_SRC) -lm -o $@

$(DIST)/hhs-pass158: $(SRC) src/hhs_pass158_cli.c include/hhs_pass158_api.h $(HASH_SRC) $(RUNTIME_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) $(SRC) src/hhs_pass158_cli.c $(HASH_SRC) $(RUNTIME_SRC) -lm -o $@

$(DIST)/test-pass158: $(SRC) tests/test_pass158.c include/hhs_pass158_api.h $(HASH_SRC) $(RUNTIME_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) $(SRC) tests/test_pass158.c $(HASH_SRC) $(RUNTIME_SRC) -lm -o $@

$(DIST)/test-pass158-security: $(SRC) tests/test_pass158_security.c include/hhs_pass158_api.h $(HASH_SRC) $(RUNTIME_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) $(SRC) tests/test_pass158_security.c $(HASH_SRC) $(RUNTIME_SRC) -lm -o $@

$(DIST)/libhhs_pass158_jni.so: bindings/java/hhs_pass158_jni.c $(DIST)/libhhs_pass158.so | $(DIST)
	$(CC) $(CFLAGS) -fPIC -shared $(INCLUDES) $(JNI_INCLUDES) bindings/java/hhs_pass158_jni.c -L$(DIST) -lhhs_pass158 -Wl,-rpath,$(abspath $(DIST)) -o $@

native-test: all $(DIST)/test-pass158-security
	$(DIST)/test-pass158 | tee $(DIST)/native-test-report.json
	$(DIST)/test-pass158-security | tee $(DIST)/security-regression-report.json
	$(DIST)/hhs-pass158 verify | tee $(DIST)/native-verification.jsonl
	grep -q 'HHS_PASS_158_NATIVE_CORE_VERIFIED' $(DIST)/native-verification.jsonl
	grep -q '"positive_total":272' $(DIST)/native-test-report.json
	grep -q '"negative_total":81' $(DIST)/native-test-report.json
	grep -q 'HHS_PASS_158_SECURITY_REGRESSIONS_VERIFIED' $(DIST)/security-regression-report.json

python-test: all
	HHS_PASS158_LIBRARY=$(abspath $(DIST)/libhhs_pass158.so) PYTHONPATH=$(PYTHONPATH158) python3 -m unittest discover -s tests -p 'test_*.py' -v 2>&1 | tee $(DIST)/python-test-report.txt

bindings: all
	@set -e; { \
	  $(CXX) $(CXXFLAGS) $(INCLUDES) bindings/cpp/test_cpp.cpp -L$(DIST) -lhhs_pass158 -Wl,-rpath,$(abspath $(DIST)) -o $(DIST)/test-pass158-cpp; \
	  $(DIST)/test-pass158-cpp; \
	  if command -v rustc >/dev/null 2>&1; then rustc --edition=2021 bindings/rust/test_rust.rs -L native=$(DIST) -l dylib=hhs_pass158 -C link-arg=-Wl,-rpath,$(abspath $(DIST)) -o $(DIST)/test-pass158-rust && $(DIST)/test-pass158-rust; else echo RUST_UNAVAILABLE; exit 1; fi; \
	  if command -v javac >/dev/null 2>&1; then $(MAKE) $(DIST)/libhhs_pass158_jni.so && mkdir -p $(DIST)/java && javac -d $(DIST)/java bindings/java/HHS158.java bindings/java/Pass158JavaSmoke.java && LD_LIBRARY_PATH=$(abspath $(DIST)) java -Djava.library.path=$(abspath $(DIST)) -cp $(DIST)/java org.hhs.pass158.Pass158JavaSmoke; else echo JAVA_UNAVAILABLE; exit 1; fi; \
	  if command -v node >/dev/null 2>&1; then node bindings/wasm/test_wasm.mjs; else echo NODE_UNAVAILABLE; exit 1; fi; \
	} 2>&1 | tee $(DIST)/language-binding-report.txt
	grep -q 'HHS_PASS_158_CPP_BINDING_VERIFIED' $(DIST)/language-binding-report.txt
	grep -q 'HHS_PASS_158_RUST_BINDING_VERIFIED' $(DIST)/language-binding-report.txt
	grep -q 'HHS_PASS_158_JAVA_KOTLIN_JNI_BINDING_VERIFIED' $(DIST)/language-binding-report.txt
	grep -q 'HHS_PASS_158_WASM_SANDBOX_BINDING_VERIFIED' $(DIST)/language-binding-report.txt

service: python-test
	HHS_PASS158_LIBRARY=$(abspath $(DIST)/libhhs_pass158.so) PYTHONPATH=$(PYTHONPATH158) python3 api/pass158_service.py self-test | tee $(DIST)/service-report.json
	grep -q 'HHS_PASS_158_LOCAL_SERVICE_API_VERIFIED' $(DIST)/service-report.json

gui-projection: python-test
	HHS_PASS158_LIBRARY=$(abspath $(DIST)/libhhs_pass158.so) PYTHONPATH=$(PYTHONPATH158) python3 api/pass158_gui_projection_runtime.py self-test | tee $(DIST)/gui-projection-report.json
	grep -q 'HHS_PASS_158_HASH216_GUI_PROJECTION_SCHEDULER_VERIFIED' $(DIST)/gui-projection-report.json

evidence: native-test python-test bindings service gui-projection
	HHS_PASS158_LIBRARY=$(abspath $(DIST)/libhhs_pass158.so) PYTHONPATH=$(PYTHONPATH158) python3 tools/generate_evidence.py

verify: evidence

package: verify
	python3 tools/package_release.py

clean:
	rm -rf $(DIST) __pycache__ bindings/python/__pycache__ api/__pycache__ tests/__pycache__
