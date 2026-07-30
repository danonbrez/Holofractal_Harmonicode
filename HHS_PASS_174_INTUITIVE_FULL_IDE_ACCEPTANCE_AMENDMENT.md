# HHS PASS 174 — INTUITIVE FULL IDE ACCEPTANCE AMENDMENT

## Binding scope

This amendment is additive to every inherited repository pass, contract, implementation, evidence record, and pre-pass commit lineage. It does not replace or narrow any prior constraint.

The final public application SHALL be a fully functioning integrated development environment. It SHALL NOT be accepted as a landing page, static demonstration, receipt viewer, diagnostic-only console, or proof-of-life shell.

## Primary user workflow

A user with no prior knowledge of HHS internals SHALL be able to complete the following visible workflow:

```text
NEW APP
→ ADD FILES OR FOLDER
→ EDIT
→ BUILD & PREVIEW
→ TEST
→ EXPORT ZIP
```

The primary surface SHALL use ordinary application-development language. Exact HHS ingress, Hash216, 5,184-bit VM snapshot, interpretation, compiler, VM81, replay, receipt, and repository-lineage controls SHALL remain available as advanced and inspectable layers without becoming prerequisites for creating an application.

## Required functional surfaces

The front-and-center IDE SHALL expose and keep operational:

- project and registered-object explorer;
- nested path-aware file tree;
- editable source workspace;
- non-destructive project templates;
- text, code, PDF, image, audio, video, and binary ingress;
- folder import with relative structure preservation;
- selectable compiler targets and backend lifecycle execution;
- sandboxed web application preview with project-local HTML, CSS, and JavaScript;
- native browser preview for image, audio, video, PDF, text, and preserved binary sources;
- application console output;
- bounded test execution;
- ZIP export containing source, build artifacts, evidence, receipts, and manifest;
- persistent natural-language development assistant access from desktop and mobile IDE controls;
- runtime service and object registry;
- repository pass-contract, constraint, evidence, and legacy commit lineage navigation.

## Interaction safety

Dragging files into the workspace SHALL add them without silently replacing existing project paths. Name collisions SHALL be resolved by preserving both files under distinct paths.

Internal file entries SHALL NOT move, overwrite, or delete merely because a pointer or touch gesture drifts. Destructive actions require explicit commands. Template creation and file imports SHALL support bounded undo of the latest project changes.

Mobile controls SHALL remain tap-safe, scroll-safe, and reachable without exposing raw implementation metadata as the only interaction method.

## Assistant requirement

The natural-language development assistant SHALL remain a primary IDE utility pane. It SHALL be reachable through persistent desktop, mobile, and floating controls while the editor, preview, compiler, terminal, and project files remain visible and active.

Assistant availability SHALL NOT replace direct controls. Direct controls SHALL NOT remove or hide the assistant.

## Visual requirement

The warm charcoal, amber, gold, restrained-glow visual layer SHALL bootstrap independently of later IDE, assistant, registry, or provider initialization. A failure in an optional module SHALL NOT revert the application to an unthemed or legacy demonstration surface.

## Acceptance boundary

Completion requires browser-verified end-to-end behavior against the deployed production server. Source code or controls existing only on an unmerged branch do not satisfy delivery.
