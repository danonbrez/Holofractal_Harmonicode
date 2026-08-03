# Pass 205 Validation Commands

```bash
python -m py_compile \
  scripts/pass205_multimodal_continuation_design_validation.py \
  scripts/pass205_gpu_translation_design_validation.py

python scripts/pass205_multimodal_continuation_design_validation.py \
  --ticks 120 \
  --seeds 1,72,216,5184,1259713 \
  --output evidence/pass205-ci/PASS205_MULTIMODAL_CONTINUATION_DESIGN_VALIDATION_RECEIPT.json

python scripts/pass205_gpu_translation_design_validation.py \
  --seed 216 \
  --batches 256 \
  --output evidence/pass205-ci/PASS205_GPU_TRANSLATION_DESIGN_VALIDATION_RECEIPT.json
```
