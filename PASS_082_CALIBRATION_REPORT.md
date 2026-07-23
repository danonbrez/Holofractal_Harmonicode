# Pass 082 Calibration Report

Implemented W01 and branch-count scaling for 2, 4, 8, 16, 32, and 64 branches. Every branch uses a distinct non-amplifying lease and retains an independently addressable post-state root. Coordinate `i=0` is compared by exact canonical root equality. No branch merger is permitted.

Measured raw benchmark data is stored in `native_projects/hhs_bifurcation_calibration/artifacts/PASS_082_BRANCH_SCALING.json`.
