# Pass 146 Combined Local API

The server is authenticated and loopback-only. It combines inherited knowledge endpoints with Pass 146 security endpoints. Inherited requests are converted into `RUN_CLI_COMMAND` boundaries before dispatch.

## Security endpoints

```text
GET  /api/v1/security/status
GET  /api/v1/security/peers
GET  /api/v1/security/identity/{id}/public
GET  /api/v1/security/contract/{id}
GET  /api/v1/security/message/{id}
POST /api/v1/security/bootstrap
POST /api/v1/security/peer/trust
POST /api/v1/security/path/construct
POST /api/v1/security/path/execute
POST /api/v1/security/path/replay
POST /api/v1/security/message/receive
POST /api/v1/security/message/admit
```

`message/admit` takes receiver credentials and a complete signed envelope. The receiver validates peer trust and signature before constructing an independent receiving path.
