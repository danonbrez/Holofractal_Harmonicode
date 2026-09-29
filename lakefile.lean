import Lake
open Lake DSL

package harmonicode where
  version := v!"0.220.56"

@[default_target]
lean_lib HHS where
  srcDir := "formal/lean"
