/* Pass 207 native GPU driver is split into contiguous implementation segments
 * to keep each additive source artifact reviewable. The preprocessor joins
 * these segments into one C11 translation unit; no segment is compiled alone.
 */
#include "hhs_pass207_gpu_driver_part1.inc"
#include "hhs_pass207_gpu_driver_part2.inc"
#include "hhs_pass207_gpu_driver_part3.inc"
#include "hhs_pass207_gpu_driver_part4.inc"
#include "hhs_pass207_gpu_driver_part5.inc"
