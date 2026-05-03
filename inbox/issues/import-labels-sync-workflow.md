---
title: "Import labels-sync workflow + label config"
labels: [enhancement, ci, gitops]
status: draft
opened: 2026-05-02
---

## Summary

Import the labels-sync workflow from `kloehnwars-homelab` so the repo's label set stays in sync with the configured `labels.yml`. Pairs with the [auto-labeler import](./import-auto-labeler-workflow.md).

## What to import

From `C:\Users\petek\repos\kloehnwars-homelab\`:

- `.github/workflows/labels-sync.yml`
- `.github/labels.yml` (or current equivalent — also needed by auto-labeler)

Skip:

- `labels-hub.yml` and `labels-spoke.yml` — those are spoke-mesh-specific. We're a standalone consumer; collapse into a single `labels.yml`.
- `scripts/ci/merge_label_files.py` — only useful if combining hub/spoke label files. We don't need the merge.

## Why deferred

This repo doesn't yet have a `labels.yml`. Importing the workflow without the config file creates a broken workflow.

## Acceptance criteria

- [ ] `.github/labels.yml` defines the project's labels (start from klw's labels.yml; trim spoke-mesh-specific ones).
- [ ] Workflow runs on push to `main` and on `workflow_dispatch`.
- [ ] Labels get created/updated in the repo to match the config.
- [ ] No deletion of labels not in the config (safety; manual cleanup only).

## Source repo for sourcing decisions

`kloehnwars-homelab` has the most current workflow as of 2026-05-02; re-verify at import time.
