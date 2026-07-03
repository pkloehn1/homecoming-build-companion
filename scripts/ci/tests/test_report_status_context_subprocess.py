"""Supplemental coverage for scripts.ci.report_status_context local paths.

The imported upstream suite monkeypatches ``_run_gh`` everywhere, so the real
subprocess wrapper is never executed there; the GH_TOKEN env fallback is a
local adaptation (the action no longer passes the token via argv).
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from scripts.ci.report_status_context import _run_gh, main

_ARGS_WITHOUT_TOKEN = [
    "--pr-number",
    "42",
    "--job-status",
    "success",
    "--status-context",
    "ctx",
    "--target-url",
    "https://example.invalid/run",
]


class TestTokenFromEnv:
    def test_env_token_used_when_flag_absent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GITHUB_REPOSITORY", "octo/widgets")
        monkeypatch.setenv("GH_TOKEN", "env-token")
        seen_envs: list[dict[str, str]] = []

        def fake_run_gh(args: list[str], env: dict[str, str]) -> str:
            seen_envs.append(env)
            return "abc123" if "--jq" in args else ""

        with patch("scripts.ci.report_status_context._run_gh", side_effect=fake_run_gh):
            assert main(_ARGS_WITHOUT_TOKEN) == 0
        assert all(env["GH_TOKEN"] == "env-token" for env in seen_envs)

    def test_missing_token_everywhere_exits_2(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setenv("GITHUB_REPOSITORY", "octo/widgets")
        monkeypatch.delenv("GH_TOKEN", raising=False)
        assert main(_ARGS_WITHOUT_TOKEN) == 2
        assert "GH_TOKEN" in capsys.readouterr().err


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
