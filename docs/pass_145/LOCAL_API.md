# Pass 145 Local API

The API binds to loopback only and requires `Authorization: Bearer <token>`. Cross-origin requests from non-loopback origins are rejected. Request bodies are bounded to 16 MiB.

## Operations

```text
GET  /api/v1/status
GET  /api/v1/database/status
GET  /api/v1/source/{id}
GET  /api/v1/object/{id}
GET  /api/v1/graph/{id}
GET  /api/v1/receipt/{id}
GET  /api/v1/ingest/{id}
POST /api/v1/ingest
POST /api/v1/query
POST /api/v1/search
POST /api/v1/analyze
POST /api/v1/validate
POST /api/v1/replay
POST /api/v1/backup
POST /api/v1/restore/preview
```

The API exposes no SQL endpoint and no unrestricted filesystem endpoint. HTML/JavaScript clients use this boundary rather than direct database access.
