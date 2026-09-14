ROOT := ../..
CC ?= cc
CFLAGS ?= -std=c11 -O3 -Wall -Wextra -Werror -pedantic
INCLUDES := -I$(ROOT)/hhs_runtime/include -I$(ROOT)/hhs_runtime/c
TARGET := $(ROOT)/hhs_runtime/builds/libhhs_pass219_rml14.so
SRC := $(ROOT)/hhs_runtime/c/hhs_pass219_rml14_route_bound_receipt_successor_1_27.c

.PHONY: all clean validate

all: $(TARGET)

$(TARGET): $(SRC) $(ROOT)/hhs_runtime/include/hhs_pass219_rml14_route_bound_receipt_successor_1_27.h
	$(MAKE) -C ../hhs_pass219_rml13_route_binding validate
	$(CC) $(CFLAGS) $(INCLUDES) -fPIC -shared $(SRC) \
		-L$(ROOT)/hhs_runtime/builds -lhhs_pass219_rml13 -lhhs_runtime -lcrypto \
		-Wl,-rpath,'$$ORIGIN' -o $(TARGET)

validate: $(TARGET)
	test -f $(TARGET)
	nm -D $(TARGET) | grep ' hhs_exact_pass219_rml14_version$$'
	nm -D $(TARGET) | grep ' hhs_exact_pass219_rml14_bind_route_receipt_successor$$'
	nm -D $(ROOT)/hhs_runtime/builds/libhhs_runtime.so | grep ' hhs_hash72_compute$$'
	nm -D $(ROOT)/hhs_runtime/builds/libhhs_runtime.so | grep ' hhs_hash216_compute$$'
	ldd $(TARGET) | grep 'libhhs_pass219_rml13.so'
	ldd $(TARGET) | grep 'libhhs_runtime.so'

clean:
	rm -f $(TARGET)
