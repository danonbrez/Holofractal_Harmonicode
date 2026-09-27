CC ?= cc
CXX ?= c++
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -pedantic
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -Werror -pedantic
BUILD := build
C_TARGET := $(BUILD)/hhs_pass220_litert_native_model_runtime_v1_test
CPP_TARGET := $(BUILD)/hhs_pass220_litert_native_model_runtime_v1_cpp_test
SHARED := $(BUILD)/libhhs_litert_native_model_runtime_v1.so

.PHONY: all test shared clean

all: $(C_TARGET) $(CPP_TARGET) $(SHARED)

$(BUILD):
	mkdir -p $(BUILD)

$(C_TARGET): src/hhs_pass220_litert_native_model_runtime_v1.c include/hhs_pass220_litert_native_model_runtime_v1.h tests/hhs_pass220_litert_native_model_runtime_v1_test.c | $(BUILD)
	$(CC) $(CFLAGS) -Iinclude src/hhs_pass220_litert_native_model_runtime_v1.c tests/hhs_pass220_litert_native_model_runtime_v1_test.c -o $(C_TARGET)

$(CPP_TARGET): src/hhs_pass220_litert_native_model_runtime_v1.c include/hhs_pass220_litert_native_model_runtime_v1.h include/hhs_pass220_litert_native_model_runtime_v1.hpp tests/hhs_pass220_litert_native_model_runtime_v1_cpp_test.cpp | $(BUILD)
	$(CC) $(CFLAGS) -fPIC -Iinclude -c src/hhs_pass220_litert_native_model_runtime_v1.c -o $(BUILD)/litert_model.o
	$(CXX) $(CXXFLAGS) -Iinclude tests/hhs_pass220_litert_native_model_runtime_v1_cpp_test.cpp $(BUILD)/litert_model.o -o $(CPP_TARGET)

$(SHARED): src/hhs_pass220_litert_native_model_runtime_v1.c include/hhs_pass220_litert_native_model_runtime_v1.h | $(BUILD)
	$(CC) $(CFLAGS) -fPIC -shared -Iinclude src/hhs_pass220_litert_native_model_runtime_v1.c -o $(SHARED)

test: $(C_TARGET) $(CPP_TARGET)
	./$(C_TARGET)
	./$(CPP_TARGET)

shared: $(SHARED)

clean:
	rm -rf $(BUILD)
