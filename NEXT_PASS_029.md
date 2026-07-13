# NEXT PASS — Pass 029 Recommendation

## Recommended Focus

Expose the read-only live plugin adapter through canonical API/GUI surfaces.

## Objectives

- Add backend route for read-only live adapter execution.
- Add GUI bridge method for read-only live plugin introspection.
- Ensure API responses use canonical response contracts and C `u^72` Hash72 witnesses.
- Preserve the no-bypass rules:
  - no arbitrary function body execution;
  - no mutation;
  - explicit allow-list only.

## Candidate Route

```text
POST /api/runtime/plugins/readonly-live/introspect
```

## Candidate GUI Method

```text
executeReadOnlyLivePluginIntrospection(target)
```
