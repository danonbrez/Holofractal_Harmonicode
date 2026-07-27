NATIVE_ARCHIVE := assets/source_capsule/pass160_native_source.tar.gz
REFERENCE_ARCHIVE := assets/source_capsule/pass160_reference_source.tar.gz
NATIVE_SHA256 := f14c0f49cd6cd0c627d546279c38066968140debcc3911c95af0b42f95a22270
REFERENCE_SHA256 := 7cf178736677024b0b3e00ba65d8bd08f5297b69db9993baf39c85b909096141
MATERIALIZED := .pass160-source-materialized

.PHONY: materialize all native-test cli-test python-test differential fuzz fault concurrency performance api-test inherited sanitizer verify evidence package clean

materialize: $(MATERIALIZED)

$(MATERIALIZED): $(NATIVE_ARCHIVE) $(REFERENCE_ARCHIVE)
	@printf '%s  %s\n' '$(NATIVE_SHA256)' '$(NATIVE_ARCHIVE)' | sha256sum -c -
	@printf '%s  %s\n' '$(REFERENCE_SHA256)' '$(REFERENCE_ARCHIVE)' | sha256sum -c -
	@tar -xzf $(NATIVE_ARCHIVE) -C .
	@tar -xzf $(REFERENCE_ARCHIVE) -C .
	@printf '%s\n%s\n' '$(NATIVE_SHA256)' '$(REFERENCE_SHA256)' > $@

all native-test cli-test python-test differential fuzz fault concurrency performance api-test inherited sanitizer verify evidence package: materialize
	@$(MAKE) -f Makefile.materialized $@

clean:
	@if test -f Makefile.materialized; then $(MAKE) -f Makefile.materialized clean || true; fi
	@rm -f $(MATERIALIZED) Makefile.materialized CMakeLists.txt
	@rm -rf include src python api schemas manifests examples tests tools dist evidence/pass160
