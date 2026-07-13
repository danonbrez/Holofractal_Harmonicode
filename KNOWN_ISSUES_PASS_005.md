# KNOWN ISSUES PASS 005

1. The guarded registry currently exposes a conservative default service set. Broader backend/semantic/ML services still need classification before registration.
2. GUI TypeScript build still requires local Node dependency installation.
3. Backend routes still need explicit binding to the service registry rather than direct runtime calls.
4. Existing C warnings remain non-blocking but should be cleaned before release candidate.
5. Existing diagnostic scripts with `if __name__ == "__main__"` remain diagnostic-only until registered or archived.
