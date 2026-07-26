CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -pedantic
ROOT := ../..
INCLUDES := -Iinclude -I$(ROOT)/hhs_runtime/include -I$(ROOT)/hhs_runtime/c
HASH_SRC := $(ROOT)/hhs_runtime/src/hhs_hash216.c
RUNTIME_SRC := $(ROOT)/hhs_runtime/c/hhs_runtime_abi.c
SRC := src/hhs_lshpvs.c src/hhs_lshpvs_vm81.c
DIST := dist

.PHONY: all test bindings sanitize verify clean

all: $(DIST)/hhs-lshpvs $(DIST)/test-hhs-lshpvs $(DIST)/libhhs_lshpvs.so

$(DIST):
	mkdir -p $(DIST)

$(DIST)/hhs-lshpvs: $(SRC) src/hhs_lshpvs_cli.c include/hhs_lshpvs.h $(HASH_SRC) $(RUNTIME_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) $(SRC) src/hhs_lshpvs_cli.c $(HASH_SRC) $(RUNTIME_SRC) -lm -o $@

$(DIST)/test-hhs-lshpvs: $(SRC) tests/test_hhs_lshpvs.c include/hhs_lshpvs.h $(HASH_SRC) $(RUNTIME_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) $(SRC) tests/test_hhs_lshpvs.c $(HASH_SRC) $(RUNTIME_SRC) -lm -o $@

$(DIST)/libhhs_lshpvs.so: $(SRC) include/hhs_lshpvs.h $(HASH_SRC) $(RUNTIME_SRC) | $(DIST)
	$(CC) $(CFLAGS) -fPIC -shared $(INCLUDES) $(SRC) $(HASH_SRC) $(RUNTIME_SRC) -lm -o $@

test: all
	$(DIST)/test-hhs-lshpvs | tee $(DIST)/test-report.txt
	$(DIST)/hhs-lshpvs verify | tee $(DIST)/verification.json
	printf 'decompose -7 5\nquit\n' | $(DIST)/hhs-lshpvs repl | tee $(DIST)/repl-report.txt
	grep -q 'HHS_PASS_156_1_LOCAL_CORE_VERIFIED' $(DIST)/test-report.txt
	grep -q '"replay":"MATCH"' $(DIST)/verification.json
	grep -q '"q":-2,"r":3' $(DIST)/repl-report.txt

bindings: all
	PYTHONPATH=bindings/python python3 -c "from hhs_pass156_1 import Library; assert Library('dist/libhhs_lshpvs.so').decompose_rotation(-7, 5) == (-2, 3)"
	@if command -v node >/dev/null 2>&1; then node --input-type=module -e "import { verify } from './bindings/js/index.mjs'; const r=verify('./dist/hhs-lshpvs'); if(r.replay!=='MATCH') process.exit(1);"; else echo 'node unavailable: JS wrapper source retained, runtime smoke skipped'; fi

sanitize: | $(DIST)
	$(CC) -std=c11 -O1 -g -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined -fno-omit-frame-pointer $(INCLUDES) $(SRC) tests/test_hhs_lshpvs.c $(HASH_SRC) $(RUNTIME_SRC) -lm -o $(DIST)/test-hhs-lshpvs-sanitized
	ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 $(DIST)/test-hhs-lshpvs-sanitized

verify: test bindings sanitize

clean:
	rm -rf $(DIST)
