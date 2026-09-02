CC ?= cc
CFLAGS ?= -O2 -std=gnu11 -Wall -Wextra -Werror -pedantic
BUILD := build

all: $(BUILD)/libhhs178_physics.a $(BUILD)/libhhs178_physics.so

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/hhs178_physics.o: src/hhs178_physics.c include/hhs178_physics.h | $(BUILD)
	$(CC) $(CFLAGS) -fPIC -c src/hhs178_physics.c -o $@

$(BUILD)/libhhs178_physics.a: $(BUILD)/hhs178_physics.o
	ar rcs $@ $<

$(BUILD)/libhhs178_physics.so: $(BUILD)/hhs178_physics.o
	$(CC) -shared $< -o $@

clean:
	rm -rf $(BUILD)

.PHONY: all clean
