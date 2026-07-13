# KNOWN ISSUES PASS 019

- Full GUI TypeScript build still requires installing Node dependencies, which are not included in the ZIP.
- SRCG has backend/API and bridge reachability, but no dedicated polished GUI panel yet.
- Existing long-running persistence guard self-test can exceed the local command timeout in monolithic pytest runs.
