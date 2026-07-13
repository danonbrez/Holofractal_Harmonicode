# Known Issues — Pass 031

- Authorized execution is intentionally narrow.  Only two pure helper functions are promoted in this pass.
- Static purity scanning is conservative and does not prove mathematical purity for arbitrary code.  It is used only as a promotion gate in combination with the explicit allow-list.
- Functions requiring persistence, network access, runtime mutation, or service dispatch remain blocked until dedicated mutation-safe adapters with rollback and closure-harness coverage are introduced.
- The broader full pytest suite was not run in this environment; targeted affected tests and make targets passed.
- GUI TypeScript verification still requires Node dependencies outside the packaged ZIP.
