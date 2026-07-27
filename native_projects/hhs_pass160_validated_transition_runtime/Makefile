CHUNK_DIR := assets/source_capsule/chunks
NATIVE_PARTS := \
	$(CHUNK_DIR)/pass160_native_source.tar.gz.part-00 \
	$(CHUNK_DIR)/pass160_native_source.tar.gz.part-01 \
	$(CHUNK_DIR)/pass160_native_source.tar.gz.part-02
REFERENCE_PARTS := \
	$(CHUNK_DIR)/pass160_reference_source.tar.gz.part-00 \
	$(CHUNK_DIR)/pass160_reference_source.tar.gz.part-01 \
	$(CHUNK_DIR)/pass160_reference_source.tar.gz.part-02
NATIVE_PART_SHA256 := \
	68017ec7746df4341593013a473000cfd3bbdbcc1ab40b109ebcf02fc7030d6f \
	cc499cea47e2e3b80684fe29b8130b135a8be9c45528fdf606cfa5e01e15ed05 \
	1f53377d0f54e3c484ca880b81573c663e55f261d0244ab86ba6e3fd51f0c682
REFERENCE_PART_SHA256 := \
	a816840263b5a9e4bdd498528f7552d52af92bb2776334d9297f7a96af38ed8f \
	0e4cc4ea0ee0962f7c0e00cdf6429f52bfe4fce214ac582833e75d1354917405 \
	8d7997a3710740a080286ad6ee60a4fb7c8c8eded6ae41180b944904b3131c49
NATIVE_SHA256 := f14c0f49cd6cd0c627d546279c38066968140debcc3911c95af0b42f95a22270
REFERENCE_SHA256 := 7cf178736677024b0b3e00ba65d8bd08f5297b69db9993baf39c85b909096141
RECONSTRUCT_DIR := .pass160-reconstructed
NATIVE_ARCHIVE := $(RECONSTRUCT_DIR)/pass160_native_source.tar.gz
REFERENCE_ARCHIVE := $(RECONSTRUCT_DIR)/pass160_reference_source.tar.gz
MATERIALIZED := .pass160-source-materialized

.PHONY: materialize verify-transport all native-test cli-test python-test differential fuzz fault concurrency performance api-test inherited sanitizer verify evidence package clean

verify-transport:
	@set -eu; \
	set -- $(NATIVE_PART_SHA256); \
	for part in $(NATIVE_PARTS); do expected=$$1; shift; actual=$$(sha256sum "$$part" | awk '{print $$1}'); echo "PASS160_CHUNK file=$$part expected=$$expected actual=$$actual bytes=$$(wc -c < "$$part")"; test "$$actual" = "$$expected"; done; \
	set -- $(REFERENCE_PART_SHA256); \
	for part in $(REFERENCE_PARTS); do expected=$$1; shift; actual=$$(sha256sum "$$part" | awk '{print $$1}'); echo "PASS160_CHUNK file=$$part expected=$$expected actual=$$actual bytes=$$(wc -c < "$$part")"; test "$$actual" = "$$expected"; done

materialize: $(MATERIALIZED)

$(MATERIALIZED): $(NATIVE_PARTS) $(REFERENCE_PARTS) | verify-transport
	@mkdir -p '$(RECONSTRUCT_DIR)'
	@cat $(NATIVE_PARTS) > '$(NATIVE_ARCHIVE).tmp'
	@cat $(REFERENCE_PARTS) > '$(REFERENCE_ARCHIVE).tmp'
	@native_actual=$$(sha256sum '$(NATIVE_ARCHIVE).tmp' | awk '{print $$1}'); echo "PASS160_NATIVE_ARCHIVE bytes=$$(wc -c < '$(NATIVE_ARCHIVE).tmp') expected=$(NATIVE_SHA256) actual=$$native_actual"; test "$$native_actual" = '$(NATIVE_SHA256)'
	@reference_actual=$$(sha256sum '$(REFERENCE_ARCHIVE).tmp' | awk '{print $$1}'); echo "PASS160_REFERENCE_ARCHIVE bytes=$$(wc -c < '$(REFERENCE_ARCHIVE).tmp') expected=$(REFERENCE_SHA256) actual=$$reference_actual"; test "$$reference_actual" = '$(REFERENCE_SHA256)'
	@gzip -t '$(NATIVE_ARCHIVE).tmp'
	@gzip -t '$(REFERENCE_ARCHIVE).tmp'
	@tar -tzf '$(NATIVE_ARCHIVE).tmp' >/dev/null
	@tar -tzf '$(REFERENCE_ARCHIVE).tmp' >/dev/null
	@mv '$(NATIVE_ARCHIVE).tmp' '$(NATIVE_ARCHIVE)'
	@mv '$(REFERENCE_ARCHIVE).tmp' '$(REFERENCE_ARCHIVE)'
	@tar -xzf '$(NATIVE_ARCHIVE)' -C .
	@tar -xzf '$(REFERENCE_ARCHIVE)' -C .
	@printf '%s\n%s\n' '$(NATIVE_SHA256)' '$(REFERENCE_SHA256)' > '$@'

all native-test cli-test python-test differential fuzz fault concurrency performance api-test inherited sanitizer verify evidence package: materialize
	@$(MAKE) -f Makefile.materialized $@

clean:
	@if test -f Makefile.materialized; then $(MAKE) -f Makefile.materialized clean || true; fi
	@rm -f '$(MATERIALIZED)' Makefile.materialized CMakeLists.txt
	@rm -rf '$(RECONSTRUCT_DIR)' include src python api schemas manifests examples tests tools dist evidence/pass160
