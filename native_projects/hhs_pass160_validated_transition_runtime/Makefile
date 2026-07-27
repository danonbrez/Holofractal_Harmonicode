NATIVE_ARCHIVE := assets/source_capsule/pass160_native_source.tar.gz
REFERENCE_ARCHIVE := assets/source_capsule/pass160_reference_source.tar.gz
NATIVE_SHA256 := f14c0f49cd6cd0c627d546279c38066968140debcc3911c95af0b42f95a22270
REFERENCE_SHA256 := 7cf178736677024b0b3e00ba65d8bd08f5297b69db9993baf39c85b909096141
MATERIALIZED := .pass160-source-materialized

.PHONY: materialize all native-test cli-test python-test differential fuzz fault concurrency performance api-test inherited sanitizer verify evidence package clean

materialize: $(MATERIALIZED)

$(MATERIALIZED): $(NATIVE_ARCHIVE) $(REFERENCE_ARCHIVE)
	@native_actual=$$(sha256sum '$(NATIVE_ARCHIVE)' | awk '{print $$1}'); \
	 echo "PASS160_NATIVE_ARCHIVE bytes=$$(wc -c < '$(NATIVE_ARCHIVE)') expected=$(NATIVE_SHA256) actual=$$native_actual"; \
	 test "$$native_actual" = '$(NATIVE_SHA256)'
	@reference_actual=$$(sha256sum '$(REFERENCE_ARCHIVE)' | awk '{print $$1}'); \
	 echo "PASS160_REFERENCE_ARCHIVE bytes=$$(wc -c < '$(REFERENCE_ARCHIVE)') expected=$(REFERENCE_SHA256) actual=$$reference_actual"; \
	 test "$$reference_actual" = '$(REFERENCE_SHA256)'
	@gzip -t '$(NATIVE_ARCHIVE)'
	@gzip -t '$(REFERENCE_ARCHIVE)'
	@tar -tzf '$(NATIVE_ARCHIVE)' >/dev/null
	@tar -tzf '$(REFERENCE_ARCHIVE)' >/dev/null
	@tar -xzf '$(NATIVE_ARCHIVE)' -C .
	@tar -xzf '$(REFERENCE_ARCHIVE)' -C .
	@printf '%s\n%s\n' '$(NATIVE_SHA256)' '$(REFERENCE_SHA256)' > $@

all native-test cli-test python-test differential fuzz fault concurrency performance api-test inherited sanitizer verify evidence package: materialize
	@$(MAKE) -f Makefile.materialized $@

clean:
	@if test -f Makefile.materialized; then $(MAKE) -f Makefile.materialized clean || true; fi
	@rm -f $(MATERIALIZED) Makefile.materialized CMakeLists.txt
	@rm -rf include src python api schemas manifests examples tests tools dist evidence/pass160
