# Known Issues — Pass 049

- This pass implements a thin complete vertical slice, not the final full IDE/editor/compiler feature set.
- Browser-level verification remains dependency-free source verification; Playwright/Chromium automation is still deferred.
- PDF and image ingress are canonical source-preserving adapter skeletons; deep OCR/vision extraction remains future adapter work.
- Interpreter mode is intentionally bounded to safe exact arithmetic in this pass.
- Closure harness execution was attempted separately but the container terminated the command before completion, so it is not claimed as a Pass 049 verification result.
