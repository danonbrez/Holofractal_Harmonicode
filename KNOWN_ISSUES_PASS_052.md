# Known Issues — Pass 052

- OCR is deterministic and bounded; it is not a full external OCR engine.
- PDF parsing is lightweight and source-preserving; it does not attempt complete PDF standards coverage.
- Table extraction is represented in the projection/fusion model but not yet backed by a deep table detector.
- Browser Playwright execution was not added; GUI verification remains source-level.
- Document providers are local deterministic records, not remote/provider marketplace integrations.
