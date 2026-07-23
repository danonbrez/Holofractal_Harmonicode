# Next Pass After 078

The next pass should resolve the typed VM81 ABI gap without editing frozen kernel semantics. It should determine whether the 15 declared `hhs_vm_*` functions are implemented in an omitted historical translation unit, can be linked through an existing bridge, or require a new external adapter translation unit that delegates to existing native behavior. No stub, approximation, or Python reimplementation should be admitted as native authority.
