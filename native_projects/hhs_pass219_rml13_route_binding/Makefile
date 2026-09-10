ROOT := ../..
CC ?= cc
CFLAGS ?= -std=c11 -O3 -Wall -Wextra -Werror -pedantic
INCLUDES := -I$(ROOT)/hhs_runtime/include -I$(ROOT)/hhs_runtime/c
RUNTIME_LIB := $(ROOT)/hhs_runtime/builds/libhhs_runtime.so
OUT := $(ROOT)/hhs_runtime/builds/libhhs_pass219_rml13.so
SRC := $(ROOT)/hhs_runtime/c/hhs_pass219_rml13_native_route_witness_binding_1_26.c
HDR := $(ROOT)/hhs_runtime/include/hhs_pass219_rml13_native_route_witness_binding_1_26.h

.PHONY: all validate clean

all: $(OUT)

$(RUNTIME_LIB):
	$(MAKE) -C $(ROOT) c-abi

$(OUT): $(SRC) $(HDR) $(RUNTIME_LIB)
	$(CC) $(CFLAGS) $(INCLUDES) -fPIC -shared $(SRC) \
		-L$(ROOT)/hhs_runtime/builds -lhhs_runtime -lcrypto \
		-Wl,-rpath,'$$ORIGIN' -o $(OUT)

validate: $(OUT)
	test -f $(OUT)
	nm -D $(OUT) | grep ' hhs_exact_pass219_rml13_version$$'
	nm -D $(OUT) | grep ' hhs_exact_pass219_rml13_bind_route_pre_hash$$'
	ldd $(OUT) | grep 'libhhs_runtime.so'

clean:
	rm -f $(OUT)
