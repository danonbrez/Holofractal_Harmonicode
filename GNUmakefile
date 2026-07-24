# Root extension surface for the HHS Pass 152 GFCC constructor.
# The complete inherited Makefile remains authoritative and is included unchanged.
include Makefile

.PHONY: test-gfcc test-gfcc-negative test-gfcc-replay verify-gfcc package-pass-152 verify-pass-152

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
