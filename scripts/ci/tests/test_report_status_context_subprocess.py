"""Supplemental coverage for scripts.ci.report_status_context._run_gh.

The imported upstream suite monkeypatches ``_run_gh`` everywhere, so the real
subprocess wrapper is never executed there. These tests pin its two paths.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from scripts.ci.report_status_context import _run_gh


class TestRunGh:
    def test_returns_stripped_stdout_on_success(self) -> None:
        proc = MagicMock(returncode=0, stdout="  abc123\n", stderr="")
        with patch("scripts.ci.report_status_context.subprocess.run", return_value=proc) as run:
            assert _run_gh(["gh", "api", "x"], env={"GH_TOKEN": "t"}) == "abc123"
        run.assert_called_once()

    def test_raises_runtime_error_with_stderr_on_failure(self) -> None:
        proc = MagicMock(returncode=1, stdout="", stderr="boom\n")
        with (
            patch("scripts.ci.report_status_context.subprocess.run", return_value=proc),
            pytest.raises(RuntimeError, match=r"exit code 1[\s\S]*boom"),
        ):
            _run_gh(["gh", "api", "x"], env={})

    def test_failure_with_no_stderr_still_raises(self) -> None:
        proc = MagicMock(returncode=2, stdout="", stderr=None)
        with (
            patch("scripts.ci.report_status_context.subprocess.run", return_value=proc),
            pytest.raises(RuntimeError, match="exit code 2"),
        ):
            _run_gh(["gh", "api", "x"], env={})
