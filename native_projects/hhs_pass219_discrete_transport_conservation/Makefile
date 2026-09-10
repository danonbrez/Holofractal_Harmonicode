ROOT := ../..
CXX ?= c++
CXXFLAGS ?= -std=c++20 -O3 -Wall -Wextra -Werror -pedantic
CPPFLAGS := -I$(ROOT)/hhs_runtime/include
BUILD := build
RUNTIME := $(ROOT)/hhs_runtime/builds/libhhs_runtime.so
HEADER := $(ROOT)/hhs_runtime/include/hhs_pass219_discrete_transport_conservation_1_29.hpp
ABI_HEADER := $(ROOT)/hhs_runtime/include/hhs_pass219_rml17_transport_abi_1_30.h
SRC := src/hhs_pass219_discrete_transport_conservation.cpp
ABI_SRC := src/hhs_pass219_rml17_transport_abi.cpp
OBJ := $(BUILD)/hhs_pass219_discrete_transport_conservation.o
PIC_OBJ := $(BUILD)/hhs_pass219_discrete_transport_conservation.pic.o
ABI_OBJ := $(BUILD)/hhs_pass219_rml17_transport_abi.o
LIB := $(BUILD)/libhhs_pass219_discrete_transport_conservation.a
SO := $(BUILD)/libhhs_pass219_rml17_transport_abi.so
TEST := $(BUILD)/test_hhs_pass219_discrete_transport_conservation
OUT ?= $(ROOT)/artifacts/pass219/discrete-transport-conservation/native_contract.json

.PHONY: all test audit validate clean runtime

all: $(LIB) $(SO) $(TEST)

$(BUILD):
	mkdir -p $(BUILD)

runtime: $(RUNTIME)

$(RUNTIME):
	$(MAKE) -C $(ROOT) c-abi

$(OBJ): $(SRC) $(HEADER) | $(BUILD)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $(SRC) -o $(OBJ)

$(PIC_OBJ): $(SRC) $(HEADER) | $(BUILD)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -fPIC -c $(SRC) -o $(PIC_OBJ)

$(ABI_OBJ): $(ABI_SRC) $(ABI_HEADER) $(HEADER) | $(BUILD)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -fPIC -c $(ABI_SRC) -o $(ABI_OBJ)

$(LIB): $(OBJ)
	ar rcs $(LIB) $(OBJ)

$(SO): $(PIC_OBJ) $(ABI_OBJ) $(RUNTIME)
	$(CXX) -shared $(PIC_OBJ) $(ABI_OBJ) \
		-L$(ROOT)/hhs_runtime/builds -lhhs_runtime -lcrypto \
		-Wl,-rpath,'$$ORIGIN/../../../hhs_runtime/builds' -o $(SO)

$(TEST): tests/test_hhs_pass219_discrete_transport_conservation.cpp $(OBJ) $(RUNTIME)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) \
		tests/test_hhs_pass219_discrete_transport_conservation.cpp $(OBJ) \
		-L$(ROOT)/hhs_runtime/builds -lhhs_runtime -lcrypto \
		-Wl,-rpath,'$$ORIGIN/../../../hhs_runtime/builds' -o $(TEST)

test: $(TEST)
	LD_LIBRARY_PATH=$(ROOT)/hhs_runtime/builds ./$(TEST)

audit: $(TEST)
	mkdir -p $(dir $(OUT))
	LD_LIBRARY_PATH=$(ROOT)/hhs_runtime/builds ./$(TEST) > $(OUT)
	test -s $(OUT)

validate: $(LIB) $(SO) audit
	nm $(LIB) | grep 'audit_entire_address_manifold'
	nm -D $(SO) | grep ' hhs_pass219_rml17_transport_flatten$$'
	nm -D $(SO) | grep ' hhs_pass219_rml17_transport_successor$$'
	nm -D $(SO) | grep ' hhs_pass219_rml17_transport_audit$$'
	nm -D $(SO) | grep ' hhs_pass219_rml17_transport_has_transition_authority$$'
	nm -D $(RUNTIME) | grep ' hhs_exact_pass219_rna_admit_composed$$'
	nm -D $(RUNTIME) | grep ' hhs_exact_uqcel_source_sha256$$'
	nm -D $(RUNTIME) | grep ' hhs_exact_pass219_hash216_indexes_complete$$'

clean:
	rm -rf $(BUILD)
