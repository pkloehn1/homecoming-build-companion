#!/usr/bin/env python3
"""Pre-commit hook to verify Git commit signing is configured.

Exit codes:
    0: Signing is configured or check is skipped
    1: Signing is not configured (blocks commit)
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from scripts.common.git_signing_utils import find_signing_key_path, git_config_value


def _test_signing(signingkey_path: Path) -> tuple[bool, str]:
    """Attempt a real signature to verify signing works end-to-end."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        test_file = Path(tmp.name)
        sig_file = Path(tmp.name + ".sig")
        tmp.write(b"signing-test\n")
    try:
        result = subprocess.run(
            ["ssh-keygen", "-Y", "sign", "-f", str(signingkey_path), "-n", "git", str(test_file)],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        if result.returncode == 0:
            return True, "Signing capability verified"
        return False, f"Signing capability check failed: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return False, (
            "Signing timed out (stale SSH_AUTH_SOCK?). "
            "Run: unset SSH_AUTH_SOCK (PowerShell: Remove-Item Env:SSH_AUTH_SOCK)"
        )
    except FileNotFoundError:
        return False, "ssh-keygen not found; cannot verify signing capability"
    finally:
        test_file.unlink(missing_ok=True)
        sig_file.unlink(missing_ok=True)


def _check_ssh_program() -> tuple[bool, str] | None:
    """Check gpg.ssh.program (e.g. 1Password op-ssh-sign) if configured.

    Returns a result tuple when gpg.ssh.program is set, or None to fall
    through to the ssh-keygen smoke test.
    """
    ssh_program = git_config_value("gpg.ssh.program")
    if not ssh_program:
        return None
    if not Path(ssh_program).exists() and not shutil.which(ssh_program):
        return False, f"gpg.ssh.program not found: {ssh_program}"
    return True, "Git commit signing is properly configured (via gpg.ssh.program)"


def check_git_signing() -> tuple[bool, str]:
    """Check if Git commit signing is properly configured."""
    try:
        commit_gpgsign = git_config_value("commit.gpgsign")
        gpg_format = git_config_value("gpg.format")
        user_signingkey = git_config_value("user.signingkey")

        if commit_gpgsign != "true":
            return False, "commit.gpgsign is not set to 'true'"

        if gpg_format != "ssh":
            return False, f"gpg.format is '{gpg_format}' (expected 'ssh')"

        if not user_signingkey:
            return False, "user.signingkey is not set"

        signingkey_path = find_signing_key_path(user_signingkey)

        if not signingkey_path or not signingkey_path.exists():
            return False, f"Signing key file not found: {user_signingkey}"

        program_result = _check_ssh_program()
        if program_result is not None:
            return program_result

        sign_ok, sign_msg = _test_signing(signingkey_path)
        if not sign_ok:
            return False, sign_msg

        return True, "Git commit signing is properly configured"

    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        return False, (f"Error checking git signing configuration ({type(exc).__name__}): {exc}")


def main() -> int:
    """Main entry point."""
    # Allow skipping this check via environment variable
    if "SKIP_GIT_SIGNING_CHECK" in os.environ:
        return 0

    is_configured, message = check_git_signing()

    if is_configured:
        return 0

    # Machine-parseable diagnostic first (error-output.md), remediation after.
    print(f".git/config:1:1: error: H-SIGN-001: git commit signing is not configured - {message}")
    print("\nThis repository requires all commits to be signed.")
    print("\nTo configure Git commit signing (preferred):")
    print("  # If using the repo virtualenv")
    print("  python -m scripts.devops.setup_git_signing")
    print("  # If the virtualenv is not available")
    print("  python3 -m scripts.devops.setup_git_signing")
    print("\nOr manually configure:")
    print("  git config --global gpg.format ssh")
    print("  git config --global user.signingkey ~/.ssh/id_ed25519_signing.pub")
    print("  git config --global commit.gpgsign true")
    print("\nSee: docs/automation/runbooks/fix-unsigned-commits-in-pr.md")
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
