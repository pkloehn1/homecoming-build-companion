---
title: "Import issue-priority-triage workflow"
labels: [enhancement, ci, gitops]
status: draft
opened: 2026-05-02
---

## Summary

Import the issue priority triage workflow from `kloehnwars-homelab` so
newly-opened issues get auto-categorized by priority based on labels
and content. Deferred from the initial import because it depends on
label infrastructure.

## What to import

From `C:\Users\petek\repos\kloehnwars-homelab\`:

- `.github/workflows/issue-priority-triage.yml`
- `scripts/ci/triage_issue_priority.py` and tests
- `scripts/ci/backfill_issue_priorities.py` and tests (one-time backfill helper)

Likely transitive dependencies:

- `scripts/github/cli_utils.py` (gh CLI wrapper)
- `scripts/github/gh_api_call.py`
- `scripts/github/gh_cli.py`

## Why deferred

Triage workflow operates on labels that don't yet exist here. Need
[auto-labeler](./import-auto-labeler-workflow.md) and
[labels-sync](./import-labels-sync-workflow.md) imports first to
establish the label set.

## Acceptance criteria

- [ ] Labels infrastructure imported first (the two label-related issues).
- [ ] Workflow runs on issue open / reopen and assigns a priority label.
- [ ] `triage_issue_priority.py` tests pass under this repo's pytest config.
- [ ] Priority criteria documented (or imported alongside as a runbook).

## Source repo for sourcing decisions

`kloehnwars-homelab` is the most current source as of 2026-05-02; re-verify at import time.
