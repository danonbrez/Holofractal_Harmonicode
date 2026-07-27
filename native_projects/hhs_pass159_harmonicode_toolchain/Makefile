CAPSULE_PARTS := $(sort $(wildcard assets/source_capsule/part*.b64))
CAPSULE_ARCHIVE := .pass159_complete_source.tar.gz
CAPSULE_SHA256 := 48b2a82be1e1e8e41eb1013de83a498f262c2d7fdb710c44c8b41d832058d145
CROSS_HOST_OVERRIDE := assets/source_overrides/compare_cross_host.py
EVIDENCE_OVERRIDE := assets/source_overrides/generate_evidence.py

.PHONY: materialize all native-test cli-test fuzz inherited sanitizer verify evidence package clean

materialize:
	@test $(words $(CAPSULE_PARTS)) -eq 9
	@cat $(CAPSULE_PARTS) | base64 -d > $(CAPSULE_ARCHIVE).tmp
	@printf '%s  %s\n' '$(CAPSULE_SHA256)' '$(CAPSULE_ARCHIVE).tmp' | sha256sum -c -
	@mv $(CAPSULE_ARCHIVE).tmp $(CAPSULE_ARCHIVE)
	@tar -xzf $(CAPSULE_ARCHIVE) -C .
	@cp $(CROSS_HOST_OVERRIDE) tools/compare_cross_host.py
	@cp $(EVIDENCE_OVERRIDE) tools/generate_evidence.py
	@chmod +x tools/compare_cross_host.py tools/generate_evidence.py
	@printf '%s\n' '$(CAPSULE_SHA256)' > .pass159-source-materialized

all native-test cli-test fuzz inherited sanitizer verify evidence package: materialize
	@$(MAKE) $@

clean:
	rm -f $(CAPSULE_ARCHIVE) $(CAPSULE_ARCHIVE).tmp .pass159-source-materialized
	rm -rf dist evidence
