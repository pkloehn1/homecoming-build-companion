"""Stub for git commit-signing check.

The full kloehnwars-homelab implementation walks `git config` for `commit.gpgsign`,
`gpg.format`, `user.signingkey`, verifies the key file exists, and runs a real
`ssh-keygen -Y sign` round-trip to confirm the agent works end-to-end. That
machinery depends on the project being a git repo with full signing wiring.

This stub returns a truthful "not yet configured" status so `bootstrap_venv.py`
can run without that dependency. Replace this module with the full implementation
once git-signing is wired up for homecoming-build-companion.

Reference: ``c:/Users/petek/repos/kloehnwars-homelab/scripts/testing/hooks/check_git_signing.py``
and ``c:/Users/petek/repos/kloehnwars-homelab/scripts/common/git_signing_utils.py``.
"""

from __future__ import annotations


def check_git_signing() -> tuple[bool, str]:
    """Return ``(is_configured, message)``.

    Returns:
        ``(False, message)`` until git-signing is wired up on this project.
    """
    return (
        False,
        "git signing not yet configured for homecoming-build-companion (stub)",
    )
