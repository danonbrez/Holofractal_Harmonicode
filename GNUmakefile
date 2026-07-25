# Root extension surface for HHS repository-level development entrypoints.
# The complete inherited Makefile remains authoritative and is included unchanged.
include Makefile

.PHONY: test-gfcc test-gfcc-negative test-gfcc-replay verify-gfcc package-pass-152 verify-pass-152 setup start setup-start benchmark-ledger

test-gfcc:
	$(MAKE) -C native_projects/hhs_gfcc_pass152 test-gfcc

test-gfcc-negative:
	$(MAKE) -C native_projects/hhs_gfcc_pass152 test-gfcc-negative

test-gfcc-replay:
	$(MAKE) -C native_projects/hhs_gfcc_pass152 test-gfcc-replay

verify-gfcc:
	$(MAKE) -C native_projects/hhs_gfcc_pass152 verify-gfcc

package-pass-152:
	$(MAKE) -C native_projects/hhs_gfcc_pass152 package-pass-152

verify-pass-152:
	$(MAKE) pass152-full
	$(MAKE) -C native_projects/hhs_gfcc_pass152 verify-pass-152

setup:
	bash init.sh

start:
	bash start.sh

setup-start:
	bash init.sh --start

benchmark-ledger: c-kernel
	python3 tools/benchmark_hhs_ledger_append_v1.py --entries $${HHS_BENCHMARK_ENTRIES:-300}
