# VM81 shared-shader repair entrypoint.
# GNU make selects this file before Makefile. The checksum-locked repair payload
# is expanded only when the canonical shared shader is absent or does not match.

VM81_REPO_ROOT := ../..
VM81_REPAIR_PARTS := $(sort $(wildcard $(VM81_REPO_ROOT)/.github/vm81-shared-shader-repair/*.b64))
VM81_SHADER_HEADER := include/hhs_vm81_game_shader.h
VM81_SHADER_SHA256 := 31fa627d4bb34e4e52362cc755116270c945b6b3fab4f700740340cc6e89e331
VM81_CURRENT_SHADER_SHA256 := $(shell test -f $(VM81_SHADER_HEADER) && sha256sum $(VM81_SHADER_HEADER) | awk '{print $$1}')

ifneq ($(VM81_CURRENT_SHADER_SHA256),$(VM81_SHADER_SHA256))
ifeq ($(strip $(VM81_REPAIR_PARTS)),)
$(error Missing checksum-locked VM81 shared-shader repair payload)
endif
VM81_MATERIALIZE_STATUS := $(shell \
	tmp=$$(mktemp); \
	cat $(VM81_REPAIR_PARTS) | base64 --decode > $$tmp 2>/dev/null || true; \
	tar -xzf $$tmp -C $(VM81_REPO_ROOT) >/dev/null 2>&1; \
	rc=$$?; rm -f $$tmp; echo $$rc)
ifneq ($(VM81_MATERIALIZE_STATUS),0)
$(error VM81 shared-shader repair materialization failed)
endif
VM81_MATERIALIZED_SHADER_SHA256 := $(shell sha256sum $(VM81_SHADER_HEADER) | awk '{print $$1}')
ifneq ($(VM81_MATERIALIZED_SHADER_SHA256),$(VM81_SHADER_SHA256))
$(error VM81 shared-shader repair identity mismatch)
endif
endif

include Makefile
