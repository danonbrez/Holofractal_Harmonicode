ROOT := ../..
CC ?= cc
CFLAGS ?= -std=c11 -O3 -Wall -Wextra -Werror -pedantic
INCLUDES := -I$(ROOT)/hhs_runtime/include -I$(ROOT)/hhs_runtime/c
TARGET := $(ROOT)/hhs_runtime/builds/libhhs_pass219_rml15.so
SRC := $(ROOT)/hhs_runtime/c/hhs_pass219_rml15_route_reverse_replay_1_28.c

.PHONY: all clean validate

all: $(TARGET)

$(TARGET): $(SRC) $(ROOT)/hhs_runtime/include/hhs_pass219_rml15_route_reverse_replay_1_28.h
	$(MAKE) -C ../hhs_pass219_rml14_route_bound_receipt validate
	$(CC) $(CFLAGS) $(INCLUDES) -fPIC -shared $(SRC) \
		-L$(ROOT)/hhs_runtime/builds -lhhs_pass219_rml14 -lhhs_runtime -lcrypto \
		-Wl,-rpath,'$$ORIGIN' -o $(TARGET)

validate: $(TARGET)
	test -f $(TARGET)
	nm -D $(TARGET) | grep ' hhs_exact_pass219_rml15_version$$'
	nm -D $(TARGET) | grep ' hhs_exact_pass219_rml15_verify_route_reverse_replay$$'
	nm -D $(ROOT)/hhs_runtime/builds/libhhs_runtime.so | grep ' hhs_hash72_compute$$'
	nm -D $(ROOT)/hhs_runtime/builds/libhhs_runtime.so | grep ' hhs_hash216_compute$$'
	ldd $(TARGET) | grep 'libhhs_pass219_rml14.so'
	ldd $(TARGET) | grep 'libhhs_runtime.so'

clean:
	rm -f $(TARGET)
