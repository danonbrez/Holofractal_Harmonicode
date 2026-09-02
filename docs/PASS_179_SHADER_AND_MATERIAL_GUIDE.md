# Pass 179 Shader IR and exact material guide

Pass 179 does not treat raw WGSL, GLSL, Three.js materials, Canvas gradients, or GPU buffers as canonical graphics state.

## Typed Shader IR

Schema:

`contracts/pass179/PASS_179_SHADER_IR_SCHEMA.json`

Current I147 node operations:

- `INPUT_POSITION`
- `CONST_RGBA16`
- `PHASE_COLOR`
- `ADD`
- `MUL`
- `OUTPUT_COLOR`

Inputs must reference already-declared nodes. RGBA values are exact 16-bit integers. Phase values are bounded to 0–215. Raw backend source is not accepted by the authoritative IR.

The WGSL and GLSL strings emitted by `compile_shader_ir` are deterministic disposable projections and explicitly carry zero canonical mutation authority.

## Exact materials

`hhs_runtime/pass179/materials.py` provides:

- exact RGBA16 material colors;
- 216-phase deterministic palette projection;
- exact Q16 gradient-stop positions;
- integer-only gradient interpolation.

No backend material object can write into the admitted scene. Renderer-derived values must re-enter as new candidates through the inherited VM81 authority if they are ever to affect canonical state.
