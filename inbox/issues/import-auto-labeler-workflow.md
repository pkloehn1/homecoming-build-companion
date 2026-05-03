---
title: "Import auto-labeler workflow + label config"
labels: [enhancement, ci, gitops]
status: draft
opened: 2026-05-02
---

## Summary

Import the auto-labeler workflow from `kloehnwars-homelab` so PRs get
automatically labeled by file paths and type. Deferred from the initial
GitOps import because it requires label infrastructure (`labels.yml`,
`labels-hub.yml`, `labels-spoke.yml`) and the helper scripts that drive
labeling.

## What to import

From `C:\Users\petek\repos\kloehnwars-homelab\`:

- `.github/workflows/auto-labeler.yml`
- `.github/labels.yml` (or its current equivalent)
- `.github/labeler.yml` (path-based label rules)
- `scripts/ci/keyword_labeler.py` and tests (if needed by the workflow)

Also import [`.github/workflows/labels-sync.yml`](./import-labels-sync-workflow.md) at the same time — they're a pair: `labels-sync.yml` keeps labels in sync, `auto-labeler.yml` applies them.

## Why deferred

The workflows need helper scripts (`scripts/ci/keyword_labeler.py`,
`scripts/ci/manual_relabel_issues.py`, etc.) and a label-config file.
Standalone-consumer model means we adapt rather than join the spoke
mesh, so the import has to be careful about which scripts are essential
vs which are spoke-mesh-only.

## Acceptance criteria

- [ ] Workflow runs on PR open / reopen and labels the PR appropriately.
- [ ] Labels in the repo match `.github/labels.yml`.
- [ ] No reliance on spoke-mesh sync mechanisms (sync-directives, etc.).
- [ ] Tests for `keyword_labeler.py` (if imported) pass under this repo's pytest config.

## Source repo for sourcing decisions

`kloehnwars-homelab` is the most current source for the workflow + labeler scripts as of 2026-05-02; verify mtime/hash diffs again at import time.
