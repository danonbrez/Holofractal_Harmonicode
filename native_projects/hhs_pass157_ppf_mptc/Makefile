CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -pedantic
ROOT := ../..
INCLUDES := -Iinclude -Isrc -I$(ROOT)/hhs_runtime/include -I$(ROOT)/hhs_runtime/c
HASH_SRC := $(ROOT)/hhs_runtime/src/hhs_hash216.c
RUNTIME_SRC := $(ROOT)/hhs_runtime/c/hhs_runtime_abi.c
SRC := src/hhs_pass157.c src/hhs_pass157_hash.c src/hhs_pass157_vm81.c
DIST := dist
.PHONY: all test python js fuzz sanitize dependency ledger evidence package verify clean
all: $(DIST)/hhs-pass157 $(DIST)/test-hhs-pass157 $(DIST)/libhhs_pass157.so
$(DIST):
	mkdir -p $(DIST)
$(DIST)/hhs-pass157: $(SRC) src/hhs_pass157_cli.c include/hhs_pass157.h $(HASH_SRC) $(RUNTIME_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) $(SRC) src/hhs_pass157_cli.c $(HASH_SRC) $(RUNTIME_SRC) -lm -o $@
$(DIST)/test-hhs-pass157: $(SRC) tests/test_hhs_pass157.c include/hhs_pass157.h $(HASH_SRC) $(RUNTIME_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) $(SRC) tests/test_hhs_pass157.c $(HASH_SRC) $(RUNTIME_SRC) -lm -o $@
$(DIST)/libhhs_pass157.so: $(SRC) include/hhs_pass157.h $(HASH_SRC) $(RUNTIME_SRC) | $(DIST)
	$(CC) $(CFLAGS) -fPIC -shared $(INCLUDES) $(SRC) $(HASH_SRC) $(RUNTIME_SRC) -lm -o $@
test: all
	$(DIST)/test-hhs-pass157 | tee $(DIST)/native-test-report.txt
	$(DIST)/hhs-pass157 verify | tee $(DIST)/native-verification.json
	grep -q 'HHS_PASS_157_NATIVE_CORE_VERIFIED' $(DIST)/native-test-report.txt
	grep -q '"replay":"MATCH"' $(DIST)/native-verification.json
python: all
	PYTHONPATH=python HHS_PASS157_NATIVE=$(DIST)/hhs-pass157 python3 -m unittest discover -s tests -p 'test_*.py' -v 2>&1 | tee $(DIST)/python-test-report.txt
	PYTHONPATH=python HHS_PASS157_NATIVE=$(DIST)/hhs-pass157 python3 -m hhs_pass157 verify > $(DIST)/verification.json
	printf 'a=b==c\nquit\n' | PYTHONPATH=python python3 -m hhs_pass157 repl > $(DIST)/repl-report.jsonl
	grep -q '"global_simultaneous_constraint":true' $(DIST)/repl-report.jsonl
js: all
	@if command -v node >/dev/null 2>&1; then node bindings/js/index.mjs $(DIST)/hhs-pass157 > $(DIST)/js-verification.json; else echo '{"status":"NODE_UNAVAILABLE_PRESERVED"}' > $(DIST)/js-verification.json; fi
fuzz: all
	PYTHONPATH=python python3 tools/fuzz_pass157.py

sanitize: | $(DIST)
	$(CC) -std=c11 -O1 -g -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined -fno-omit-frame-pointer $(INCLUDES) $(SRC) tests/test_hhs_pass157.c $(HASH_SRC) $(RUNTIME_SRC) -lm -o $(DIST)/test-hhs-pass157-sanitized
	ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 $(DIST)/test-hhs-pass157-sanitized > $(DIST)/sanitizer-report.txt
dependency: test
	python3 tools/verify_dependency.py

ledger:
	python3 tools/generate_obligation_ledger.py

evidence: test python js fuzz sanitize ledger
	python3 tools/verify_evidence.py

package:
	python3 tools/package_release.py

verify: test python js fuzz sanitize dependency evidence
clean:
	rm -rf $(DIST)
