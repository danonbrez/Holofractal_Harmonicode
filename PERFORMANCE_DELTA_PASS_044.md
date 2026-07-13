# Pass 044 — Performance Delta

- Repeated composition can reuse cached roots while dependency roots remain stable.
- Changed roots invalidate and rebuild only affected pipelines.
- Expanded state remains subject to Pass 043 decay/compaction; only compact residue persists.
- Semantic storage now functions as composition memory rather than ordinary search.
