CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -pedantic
BUILD := build
TARGET := $(BUILD)/hhs_pass220_fastapi_native_route_kernel_v1_test
SHARED := $(BUILD)/libhhs_fastapi_native_route_kernel_v1.so

.PHONY: all test shared clean

all: $(TARGET) $(SHARED)

$(BUILD):
	mkdir -p $(BUILD)

$(TARGET): src/hhs_pass220_fastapi_native_route_kernel_v1.c include/hhs_pass220_fastapi_native_route_kernel_v1.h tests/hhs_pass220_fastapi_native_route_kernel_v1_test.c | $(BUILD)
	$(CC) $(CFLAGS) -Iinclude src/hhs_pass220_fastapi_native_route_kernel_v1.c tests/hhs_pass220_fastapi_native_route_kernel_v1_test.c -o $(TARGET)

$(SHARED): src/hhs_pass220_fastapi_native_route_kernel_v1.c include/hhs_pass220_fastapi_native_route_kernel_v1.h | $(BUILD)
	$(CC) $(CFLAGS) -fPIC -shared -Iinclude src/hhs_pass220_fastapi_native_route_kernel_v1.c -o $(SHARED)

test: $(TARGET)
	./$(TARGET)

shared: $(SHARED)

clean:
	rm -rf $(BUILD)
