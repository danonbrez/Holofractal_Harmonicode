CC ?= cc
AR ?= ar
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -pedantic
ROOT := ../..
INCLUDES := -Iinclude -Isrc -I$(ROOT)/hhs_runtime/include
HASH_SRC := $(ROOT)/hhs_runtime/src/hhs_hash216.c
CORE_SRC := src/hhs159_core.c
CLI_SRC := src/hhs159_cli.c
TEST_SRC := tests/test_pass159.c
DIST := dist
GENERATED_SRC := $(CORE_SRC) $(CLI_SRC) $(TEST_SRC)

.PHONY: all materialize test verify evidence clean

all: materialize $(DIST)/libhhs_pass159.so $(DIST)/libhhs_pass159.a $(DIST)/harmonicode $(DIST)/harmonicodec $(DIST)/vm81-as $(DIST)/vm81-ld $(DIST)/hhs-pass159-verify

materialize: $(GENERATED_SRC)

src/%.c: src/%.c.gz
	gzip -dc $< > $@.tmp
	mv $@.tmp $@

tests/%.c: tests/%.c.gz
	gzip -dc $< > $@.tmp
	mv $@.tmp $@

$(DIST):
	mkdir -p $(DIST)

$(DIST)/hhs159_core.o: $(CORE_SRC) include/hhs_pass159_api.h src/hhs159_internal.h | $(DIST)
	$(CC) $(CFLAGS) -fPIC $(INCLUDES) -c $(CORE_SRC) -o $@

$(DIST)/hhs_hash216.o: $(HASH_SRC) | $(DIST)
	$(CC) $(CFLAGS) -fPIC $(INCLUDES) -c $(HASH_SRC) -o $@

$(DIST)/libhhs_pass159.so: $(DIST)/hhs159_core.o $(DIST)/hhs_hash216.o
	$(CC) -shared $^ -o $@

$(DIST)/libhhs_pass159.a: $(DIST)/hhs159_core.o $(DIST)/hhs_hash216.o
	$(AR) rcs $@ $^

$(DIST)/harmonicode: $(CLI_SRC) $(DIST)/libhhs_pass159.a
	$(CC) $(CFLAGS) $(INCLUDES) $(CLI_SRC) $(DIST)/libhhs_pass159.a -o $@

$(DIST)/harmonicodec: $(DIST)/harmonicode
	cp $< $@

$(DIST)/vm81-as: $(DIST)/harmonicode
	cp $< $@

$(DIST)/vm81-ld: $(DIST)/harmonicode
	cp $< $@

$(DIST)/hhs-pass159-verify: $(TEST_SRC) $(DIST)/libhhs_pass159.a
	$(CC) $(CFLAGS) $(INCLUDES) $(TEST_SRC) $(DIST)/libhhs_pass159.a -o $@

test: all
	$(DIST)/hhs-pass159-verify | tee $(DIST)/P159_FOUNDATION_VALIDATION_REPORT.json
	grep -q '"failures":0' $(DIST)/P159_FOUNDATION_VALIDATION_REPORT.json
	grep -q '"interpreter_compiler_equivalence":true' $(DIST)/P159_FOUNDATION_VALIDATION_REPORT.json
	grep -q '"fallback_used":false' $(DIST)/P159_FOUNDATION_VALIDATION_REPORT.json

verify: test
	$(DIST)/harmonicode doctor | tee $(DIST)/P159_CLI_REPORT.json
	grep -q 'HHS_PASS_159_FOUNDATION_IMPLEMENTED_PENDING_FULL_CLOSURE' $(DIST)/P159_CLI_REPORT.json

evidence: verify
	python3 tools/generate_foundation_evidence.py

clean:
	rm -rf $(DIST)
	rm -f $(GENERATED_SRC)
