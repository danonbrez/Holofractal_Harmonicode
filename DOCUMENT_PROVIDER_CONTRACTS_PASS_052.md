# Document Provider Contracts — Pass 052

Document providers are capability-facing observation instruments, not document authorities. Each provider must preserve source identity, declare loss characteristics, return typed projections, and re-enter through Runtime canonical ingress.

## Rejection codes

- `REJECT_DOCUMENT_PROVIDER_AS_AUTHORITY`
- `REJECT_OCR_TEXT_AS_DOCUMENT_SOURCE`
- `REJECT_PDF_TEXT_AS_COMPLETE_DOCUMENT`
- `REJECT_TABLE_EXTRACTION_WITHOUT_REGION_SOURCE`
- `REJECT_DOCUMENT_FUSION_WITHOUT_PROVENANCE`
- `REJECT_UNMARKED_DOCUMENT_EXTRACTION_LOSS`
- `REJECT_PROVIDER_DISAGREEMENT_COLLAPSED_SILENTLY`
- `REJECT_DOCUMENT_PROJECTION_WITHOUT_RECONSTRUCTION`

## Contract count

`4`
