"""Tests for gh_cli module."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

import pytest

from scripts.github.gh_cli import (
    ActionableArgumentParser,
    GhCliError,
    GhResult,
    SubprocessGhRunner,
    active_pr_number,
    as_dict,
    as_list,
    current_login,
    current_repo,
    default_repo_from_env,
    format_actionable_cli_error,
    format_gh_cli_error,
    gh_diagnostics_enabled,
    gh_diagnostics_max_chars,
    parse_repo,
    print_gh_cli_error,
    run_json,
    run_text,
)

# -- Stub runner -------------------------------------------------------------


@dataclass(frozen=True)
class _StubResult:
    stdout: str
    stderr: str = ""


class _StubRunner:
    """Minimal GhRunner that returns canned stdout."""

    def __init__(self, stdout: str = "", stderr: str = "") -> None:
        """Initialize _StubRunner."""
        self._stdout = stdout
        self._stderr = stderr
        self.last_argv: list[str] = []

    def run(self, argv: list[str], *, input_text: str | None = None) -> GhResult:
        """Run."""
        self.last_argv = argv
        return GhResult(stdout=self._stdout, stderr=self._stderr)


# -- parse_repo --------------------------------------------------------------


def test_parse_repo_valid() -> None:
    """Test parse repo valid."""
    assert parse_repo("owner/name") == ("owner", "name")


def test_parse_repo_strips_whitespace() -> None:
    """Test parse repo strips whitespace."""
    assert parse_repo(" owner / name ") == ("owner", "name")


@pytest.mark.parametrize("bad", ["", "no-slash", "/name", "owner/"])
def test_parse_repo_rejects_invalid(bad: str) -> None:
    """Test parse repo rejects invalid."""
    with pytest.raises(ValueError):
        parse_repo(bad)


# -- as_dict / as_list --------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ({"a": 1}, {"a": 1}),
        ([], {}),
        ("str", {}),
        (None, {}),
        (42, {}),
    ],
)
def test_as_dict(value: Any, expected: dict[str, Any]) -> None:
    """Test as dict."""
    assert as_dict(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ([1, 2], [1, 2]),
        ({}, []),
        ("str", []),
        (None, []),
    ],
)
def test_as_list(value: Any, expected: list[Any]) -> None:
    """Test as list."""
    assert as_list(value) == expected


# -- gh_diagnostics_enabled ---------------------------------------------------


@pytest.mark.parametrize("raw", ["1", "true", "yes", "y", "on", "  TRUE  "])
def test_diagnostics_enabled_truthy(raw: str) -> None:
    """Test diagnostics enabled truthy."""
    assert gh_diagnostics_enabled(environ={"GH_HELPERS_DEBUG": raw}) is True


@pytest.mark.parametrize("raw", ["0", "false", "no", "", "anything"])
def test_diagnostics_enabled_falsy(raw: str) -> None:
    """Test diagnostics enabled falsy."""
    assert gh_diagnostics_enabled(environ={"GH_HELPERS_DEBUG": raw}) is False


def test_diagnostics_enabled_missing() -> None:
    """Test diagnostics enabled missing."""
    assert gh_diagnostics_enabled(environ={}) is False


# -- gh_diagnostics_max_chars -------------------------------------------------


def test_max_chars_default_when_missing() -> None:
    """Test max chars default when missing."""
    assert gh_diagnostics_max_chars(environ={}) == 50_000


def test_max_chars_default_when_empty() -> None:
    """Test max chars default when empty."""
    assert gh_diagnostics_max_chars(environ={"GH_HELPERS_DEBUG_MAX_CHARS": "  "}) == 50_000


@pytest.mark.parametrize("raw", ["none", "null", "unlimited"])
def test_max_chars_unlimited(raw: str) -> None:
    """Test max chars unlimited."""
    assert gh_diagnostics_max_chars(environ={"GH_HELPERS_DEBUG_MAX_CHARS": raw}) is None


def test_max_chars_positive_int() -> None:
    """Test max chars positive int."""
    assert gh_diagnostics_max_chars(environ={"GH_HELPERS_DEBUG_MAX_CHARS": "100"}) == 100


def test_max_chars_invalid_string() -> None:
    """Test max chars invalid string."""
    assert gh_diagnostics_max_chars(environ={"GH_HELPERS_DEBUG_MAX_CHARS": "abc"}) == 50_000


def test_max_chars_zero_falls_back() -> None:
    """Test max chars zero falls back."""
    assert gh_diagnostics_max_chars(environ={"GH_HELPERS_DEBUG_MAX_CHARS": "0"}) == 50_000


def test_max_chars_negative_falls_back() -> None:
    """Test max chars negative falls back."""
    assert gh_diagnostics_max_chars(environ={"GH_HELPERS_DEBUG_MAX_CHARS": "-5"}) == 50_000


# -- GhCliError ---------------------------------------------------------------


def test_gh_cli_error_attributes() -> None:
    """Test gh cli error attributes."""
    err = GhCliError("boom", argv=["gh", "api"], returncode=1, stdout="out", stderr="err")
    assert err.argv == ["gh", "api"]
    assert err.returncode == 1
    assert err.stdout == "out"
    assert err.stderr == "err"
    assert str(err) == "boom"


# -- format_gh_cli_error ------------------------------------------------------


def test_format_gh_cli_error_basic() -> None:
    """Test format gh cli error basic."""
    err = GhCliError("fail", argv=["gh", "pr"], returncode=2, stdout="ok", stderr="bad")
    text = format_gh_cli_error(err)
    assert "gh command failed" in text
    assert "returncode: 2" in text
    assert "gh pr" in text
    assert "ok" in text
    assert "bad" in text


def test_format_gh_cli_error_clips_long_output() -> None:
    """Test format gh cli error clips long output."""
    err = GhCliError("fail", argv=["gh"], returncode=1, stdout="x" * 200, stderr="")
    text = format_gh_cli_error(err, max_chars=50)
    assert "clipped to 50 chars" in text


def test_format_gh_cli_error_empty_streams() -> None:
    """Test format gh cli error empty streams."""
    err = GhCliError("fail", argv=["gh"], returncode=1, stdout="", stderr="")
    text = format_gh_cli_error(err)
    assert "(empty)" in text


# -- format_actionable_cli_error -----------------------------------------------


def test_format_actionable_cli_error_basic() -> None:
    """Test format actionable cli error basic."""
    parser = argparse.ArgumentParser(description="test")
    err = ValueError("bad input")
    text = format_actionable_cli_error(err, parser=parser)
    assert "Error: bad input" in text
    assert "Available options:" in text


def test_format_actionable_cli_error_with_gh_cli_error() -> None:
    """Test format actionable cli error with gh cli error."""
    parser = argparse.ArgumentParser(description="test")
    err = GhCliError("fail", argv=["gh"], returncode=1, stdout="", stderr="details here")
    text = format_actionable_cli_error(err, parser=parser)
    assert "details here" in text
    assert "GH_HELPERS_DEBUG" in text


def test_format_actionable_cli_error_examples_and_see_also() -> None:
    """Test format actionable cli error examples and see also."""
    parser = argparse.ArgumentParser(description="test")
    err = ValueError("oops")
    text = format_actionable_cli_error(
        err,
        parser=parser,
        examples=["example1"],
        see_also=["see1"],
    )
    assert "example1" in text
    assert "see1" in text


# -- ActionableArgumentParser --------------------------------------------------


def test_actionable_parser_raises_value_error() -> None:
    """Test actionable parser raises value error."""
    parser = ActionableArgumentParser()
    parser.add_argument("--required", required=True)
    with pytest.raises(ValueError):
        parser.parse_args([])


# -- run_text / run_json -------------------------------------------------------


def test_run_text_returns_stdout() -> None:
    """Test run text returns stdout."""
    runner = _StubRunner(stdout="hello\n")
    assert run_text(runner, ["gh", "api"]) == "hello\n"


def test_run_json_parses_json() -> None:
    """Test run json parses json."""
    runner = _StubRunner(stdout='{"key": "value"}\n')
    assert run_json(runner, ["gh", "api"]) == {"key": "value"}


def test_run_json_returns_null_for_empty() -> None:
    """Test run json returns null for empty."""
    runner = _StubRunner(stdout="  \n  ")
    assert run_json(runner, ["gh", "api"]) is None


# -- current_repo --------------------------------------------------------------


def test_current_repo_returns_name_with_owner() -> None:
    """Test current repo returns name with owner."""
    runner = _StubRunner(stdout='{"nameWithOwner": "owner/repo"}\n')
    assert current_repo(runner) == "owner/repo"


def test_current_repo_raises_on_missing_field() -> None:
    """Test current repo raises on missing field."""
    runner = _StubRunner(stdout="{}\n")
    with pytest.raises(ValueError, match="Unable to determine current repo"):
        current_repo(runner)


def test_current_repo_raises_on_non_dict() -> None:
    """Test current repo raises on non dict."""
    runner = _StubRunner(stdout="null\n")
    with pytest.raises(ValueError, match="Unable to determine current repo"):
        current_repo(runner)


# -- current_login -------------------------------------------------------------


def test_current_login_returns_login() -> None:
    """Test current login returns login."""
    runner = _StubRunner(stdout='{"login": "octocat"}\n')
    assert current_login(runner) == "octocat"


def test_current_login_raises_on_missing() -> None:
    """Test current login raises on missing."""
    runner = _StubRunner(stdout="{}\n")
    with pytest.raises(ValueError, match="Unable to determine current login"):
        current_login(runner)


# -- default_repo_from_env ----------------------------------------------------


def test_default_repo_from_env_present(monkeypatch: Any) -> None:
    """Test default repo from env present."""
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    assert default_repo_from_env() == "owner/repo"


def test_default_repo_from_env_empty(monkeypatch: Any) -> None:
    """Test default repo from env empty."""
    monkeypatch.setenv("GITHUB_REPOSITORY", "  ")
    assert default_repo_from_env() is None


def test_default_repo_from_env_missing(monkeypatch: Any) -> None:
    """Test default repo from env missing."""
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    assert default_repo_from_env() is None


# -- print_gh_cli_error -------------------------------------------------------


def test_print_gh_cli_error_writes_to_stderr(capsys: Any) -> None:
    """Test print gh cli error writes to stderr."""
    err = GhCliError("fail", argv=["gh", "api"], returncode=1, stdout="out", stderr="err")
    print_gh_cli_error(err)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "gh command failed" in captured.err


# -- SubprocessGhRunner -------------------------------------------------------


def test_subprocess_gh_runner_success(monkeypatch: Any) -> None:
    """Test subprocess gh runner success."""

    @dataclass(frozen=True)
    class _FakeCompletedProcess:
        returncode: int = 0
        stdout: str = "hello"
        stderr: str = ""

    monkeypatch.setattr("subprocess.run", lambda *_args, **_kwargs: _FakeCompletedProcess())
    runner = SubprocessGhRunner()
    result = runner.run(["gh", "api", "/user"])
    assert result.stdout == "hello"
    assert result.stderr == ""


def test_subprocess_gh_runner_error_raises(monkeypatch: Any) -> None:
    """Test subprocess gh runner error raises."""

    @dataclass(frozen=True)
    class _FakeCompletedProcess:
        returncode: int = 1
        stdout: str = ""
        stderr: str = "not found"

    monkeypatch.setattr("subprocess.run", lambda *_args, **_kwargs: _FakeCompletedProcess())
    runner = SubprocessGhRunner()
    with pytest.raises(GhCliError) as exc_info:
        runner.run(["gh", "api", "/missing"])
    assert exc_info.value.returncode == 1
    assert exc_info.value.stderr == "not found"


def test_subprocess_gh_runner_error_with_diagnostics(monkeypatch: Any) -> None:
    """Test subprocess gh runner error with diagnostics."""

    @dataclass(frozen=True)
    class _FakeCompletedProcess:
        returncode: int = 1
        stdout: str = ""
        stderr: str = "bad request"

    monkeypatch.setattr("subprocess.run", lambda *_args, **_kwargs: _FakeCompletedProcess())
    monkeypatch.setenv("GH_HELPERS_DEBUG", "1")
    runner = SubprocessGhRunner()
    with pytest.raises(GhCliError):
        runner.run(["gh", "api", "/fail"])


# -- active_pr_number ----------------------------------------------------------


def test_active_pr_number_returns_number() -> None:
    """Test active pr number returns number."""
    runner = _StubRunner(stdout='{"number": 42}\n')
    assert active_pr_number(runner) == 42


def test_active_pr_number_raises_on_non_int() -> None:
    """Test active pr number raises on non int."""
    runner = _StubRunner(stdout='{"number": "not-a-number"}\n')
    with pytest.raises(ValueError, match="Unable to determine active PR"):
        active_pr_number(runner)


def test_active_pr_number_raises_on_zero() -> None:
    """Test active pr number raises on zero."""
    runner = _StubRunner(stdout='{"number": 0}\n')
    with pytest.raises(ValueError, match="Unable to determine active PR"):
        active_pr_number(runner)


def test_active_pr_number_raises_on_negative() -> None:
    """Test active pr number raises on negative."""
    runner = _StubRunner(stdout='{"number": -1}\n')
    with pytest.raises(ValueError, match="Unable to determine active PR"):
        active_pr_number(runner)


def test_active_pr_number_raises_on_non_dict() -> None:
    """Test active pr number raises on non dict."""
    runner = _StubRunner(stdout="null\n")
    with pytest.raises(ValueError, match="Unable to determine active PR"):
        active_pr_number(runner)
