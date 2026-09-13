SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
.SUFFIXES:

.PHONY: verify
verify:
	python tools/pass219/verify_generation_integrity_v1.py \
		--manifest contracts/pass219/PASS_219_GENERATION_INTEGRITY_MANIFEST_V1.json \
		--require-sealed
