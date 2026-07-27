CHUNK_DIR := assets/source_capsule/chunks
NATIVE_PARTS := \
	$(CHUNK_DIR)/pass160_native_source.tar.gz.part-00 \
	$(CHUNK_DIR)/pass160_native_source.tar.gz.part-01 \
	$(CHUNK_DIR)/pass160_native_source.tar.gz.part-02
NATIVE_PART_SHA256 := \
	68017ec7746df4341593013a473000cfd3bbdbcc1ab40b109ebcf02fc7030d6f \
	cc499cea47e2e3b80684fe29b8130b135a8be9c45528fdf606cfa5e01e15ed05 \
	1f53377d0f54e3c484ca880b81573c663e55f261d0244ab86ba6e3fd51f0c682
NATIVE_SHA256 := f14c0f49cd6cd0c627d546279c38066968140debcc3911c95af0b42f95a22270
REFERENCE_SUMS := assets/source_capsule/REFERENCE_SOURCE_SHA256SUMS.txt
REFERENCE_SUMS_SHA256 := dd352e0cf922a481843f082de0d603c4ee621bc0bfaee6b01e0b7431851a9839
RECONSTRUCT_DIR := .pass160-reconstructed
NATIVE_ARCHIVE := $(RECONSTRUCT_DIR)/pass160_native_source.tar.gz
MATERIALIZED := .pass160-source-materialized

.PHONY: materialize verify-native-transport verify-reference-source verify-transport all native-test cli-test python-test differential fuzz fault concurrency performance api-test inherited sanitizer verify evidence package clean

verify-native-transport:
	@set -eu; \
	set -- $(NATIVE_PART_SHA256); \
	for part in $(NATIVE_PARTS); do expected=$$1; shift; actual=$$(sha256sum "$$part" | awk '{print $$1}'); echo "PASS160_NATIVE_CHUNK file=$$part expected=$$expected actual=$$actual bytes=$$(wc -c < "$$part")"; test "$$actual" = "$$expected"; done

verify-reference-source:
	@set -eu; \
	actual=$$(sha256sum '$(REFERENCE_SUMS)' | awk '{print $$1}'); \
	echo "PASS160_REFERENCE_SUMS expected=$(REFERENCE_SUMS_SHA256) actual=$$actual"; \
	test "$$actual" = '$(REFERENCE_SUMS_SHA256)'; \
	sha256sum -c '$(REFERENCE_SUMS)'

verify-transport: verify-native-transport verify-reference-source

materialize: $(MATERIALIZED)

$(MATERIALIZED): $(NATIVE_PARTS) $(REFERENCE_SUMS) | verify-transport
	@mkdir -p '$(RECONSTRUCT_DIR)'
	@cat $(NATIVE_PARTS) > '$(NATIVE_ARCHIVE).tmp'
	@native_actual=$$(sha256sum '$(NATIVE_ARCHIVE).tmp' | awk '{print $$1}'); echo "PASS160_NATIVE_ARCHIVE bytes=$$(wc -c < '$(NATIVE_ARCHIVE).tmp') expected=$(NATIVE_SHA256) actual=$$native_actual"; test "$$native_actual" = '$(NATIVE_SHA256)'
	@gzip -t '$(NATIVE_ARCHIVE).tmp'
	@tar -tzf '$(NATIVE_ARCHIVE).tmp' >/dev/null
	@mv '$(NATIVE_ARCHIVE).tmp' '$(NATIVE_ARCHIVE)'
	@tar -xzf '$(NATIVE_ARCHIVE)' -C .
	@cp assets/source_capsule/Makefile.materialized.repair-forward Makefile.materialized
	@printf '%s\n%s\n' '$(NATIVE_SHA256)' '$(REFERENCE_SUMS_SHA256)' > '$@'

all native-test cli-test python-test differential fuzz fault concurrency performance api-test inherited sanitizer verify evidence package: materialize
	@$(MAKE) -f Makefile.materialized $@

clean:
	@if test -f Makefile.materialized; then $(MAKE) -f Makefile.materialized clean || true; fi
	@rm -f '$(MATERIALIZED)' Makefile.materialized CMakeLists.txt
	@rm -rf '$(RECONSTRUCT_DIR)' include src dist evidence/pass160
