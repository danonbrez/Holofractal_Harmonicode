# Pass 179 native exact graphics nucleus

This C11 library is the deterministic scene → immutable command-stream → fixed-point software-rendering core for Pass 179.

It intentionally has **no VM81, Hash72, Hash216, GPU, browser, filesystem, networking, or persistence mutation authority**. Canonical scene admission is performed by the inherited VM81 authority in `hhs_runtime/pass179/runtime.py` before this renderer is used as a projection.

Build:

```sh
make -C native_projects/hhs_pass179_graphics
```

The current I147 nucleus supports exact RGBA16 clear, rectangle, and point commands, stable layer/node ordering, bounded scene capacity, deterministic integer alpha composition, a typed bounded Shader IR validator, and deterministic command fingerprints. It is not the terminal Pass 179 graphics library.
