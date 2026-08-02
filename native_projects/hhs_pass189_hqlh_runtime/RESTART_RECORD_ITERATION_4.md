# Pass 189 Iteration 4 restart record

- Authoritative base: `1d3c7588a242e3a83304f5083c2ec5a974f19399`
- Parent merge: `f3ceba745ce5b478ca850c14a543a18189cc7d6c`
- Branch: `agent/pass189-iteration4-driver-provenance`
- Merge target: `main`
- Deployment authority: DigitalOcean Ubuntu; Vercel excluded
- Local validation completed: 12 unit tests, HTTP/SSE/WebSocket/visual smoke, bytecode compilation, shell syntax
- Full repository validation: required through GitHub workflow `make validate`
- External DigitalOcean mutation: not performed
- Real hardware dispatch: denied by token schema and runtime
- Next host action after merge: run `deployment/digitalocean/install.sh`, install nginx include, verify ports 8189–8192
