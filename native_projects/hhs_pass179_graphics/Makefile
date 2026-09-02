CC ?= cc
CFLAGS ?= -O2 -std=c11 -Wall -Wextra -Werror -pedantic
ROOT := ../..
BUILD := build

all: $(BUILD)/libhhs179_graphics.a $(BUILD)/libhhs179_graphics.so

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/hhs179_graphics.o: src/hhs179_graphics.c include/hhs179_graphics.h | $(BUILD)
	$(CC) $(CFLAGS) -fPIC -c src/hhs179_graphics.c -o $@

$(BUILD)/libhhs179_graphics.a: $(BUILD)/hhs179_graphics.o
	ar rcs $@ $<

$(BUILD)/libhhs179_graphics.so: $(BUILD)/hhs179_graphics.o
	$(CC) -shared $< -o $@

clean:
	rm -rf $(BUILD)

.PHONY: all clean
