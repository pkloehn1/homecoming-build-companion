"""Supplemental tests for CLI scaffolding paths not covered by the imported upstream suites.

Upstream (kloehnwars-homelab) covers these lines via tests of tools not imported into
this repo (pr_upsert, issue helpers, ...). This file closes the gap locally:
``cli_utils.build_repo_pr_parser`` / ``resolve_repo`` / ``resolve_repo_pr`` and
``gh_cli.print_actionable_cli_error`` / ``run_actionable_main``.
"""

from __future__ import annotations

import argparse
import json
import sys

import pytest

from scripts.github.cli_utils import RepoPr, build_repo_pr_parser, resolve_repo, resolve_repo_pr
from scripts.github.conftest import make_call, make_runner
from scripts.github.gh_cli import (
    ActionableArgumentParser,
    GhCliError,
    GhRunner,
    print_actionable_cli_error,
    run_actionable_main,
)


class TestBuildRepoPrParser:
    def test_defaults_are_none(self) -> None:
        parser = build_repo_pr_parser("desc")
        args = parser.parse_args([])
        assert args.repo is None
        assert args.pr is None

    def test_explicit_values_parsed(self) -> None:
        parser = build_repo_pr_parser("desc")
        args = parser.parse_args(["--repo", "owner/name", "--pr", "5"])
        assert args.repo == "owner/name"
        assert args.pr == 5

    def test_parse_error_raises_value_error(self) -> None:
        parser = build_repo_pr_parser("desc")
        with pytest.raises(ValueError, match="invalid int value"):
            parser.parse_args(["--pr", "not-a-number"])


class TestResolveRepo:
    def test_arg_wins(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GITHUB_REPOSITORY", "env/repo")
        args = argparse.Namespace(repo="arg/repo")
        assert resolve_repo(args, make_runner()) == "arg/repo"

    def test_env_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GITHUB_REPOSITORY", "env/repo")
        args = argparse.Namespace(repo=None)
        assert resolve_repo(args, make_runner()) == "env/repo"

    def test_gh_repo_view_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
        runner = make_runner(
            make_call(
                ["gh", "repo", "view", "--json", "nameWithOwner"],
                {"nameWithOwner": "detected/repo"},
            )
        )
        args = argparse.Namespace(repo=None)
        assert resolve_repo(args, runner) == "detected/repo"


class TestResolveRepoPr:
    def test_explicit_pr(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GITHUB_REPOSITORY", "env/repo")
        args = argparse.Namespace(repo=None, pr=12)
        assert resolve_repo_pr(args, make_runner()) == RepoPr(repo="env/repo", pr_number=12)

    def test_active_pr_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GITHUB_REPOSITORY", "env/repo")
        runner = make_runner(make_call(["gh", "pr", "view", "--json", "number"], {"number": 7}))
        args = argparse.Namespace(repo=None, pr=None)
        assert resolve_repo_pr(args, runner) == RepoPr(repo="env/repo", pr_number=7)


class TestPrintActionableCliError:
    def test_prints_to_stderr(self, capsys: pytest.CaptureFixture[str]) -> None:
        parser = ActionableArgumentParser(description="tool")
        print_actionable_cli_error(ValueError("boom"), parser=parser, examples=["tool --x"])
        captured = capsys.readouterr()
        assert captured.out == ""
        assert "Error: boom" in captured.err
        assert "- tool --x" in captured.err

    def test_gh_cli_error_with_empty_stderr_omits_details(self, capsys: pytest.CaptureFixture[str]) -> None:
        parser = ActionableArgumentParser(description="tool")
        err = GhCliError("gh command failed", argv=["gh"], returncode=1, stdout="", stderr="  ")
        print_actionable_cli_error(err, parser=parser)
        captured = capsys.readouterr()
        assert "Details:" not in captured.err
        assert "GH_HELPERS_DEBUG=1" in captured.err


def build_parser_with_json() -> argparse.ArgumentParser:
    parser = ActionableArgumentParser(description="tool")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fail", choices=["none", "value"], default="none")
    return parser


def handler(args: argparse.Namespace, parser: argparse.ArgumentParser, runner: GhRunner) -> int:
    if args.fail == "value":
        raise ValueError("handler failed")
    return 0


class TestRunActionableMain:
    def run(self, argv: list[str], monkeypatch: pytest.MonkeyPatch) -> int:
        monkeypatch.setattr(sys, "argv", ["tool", *argv])
        return run_actionable_main(
            build_parser=build_parser_with_json,
            handler=handler,
            examples=["tool --fail none"],
            runner_factory=make_runner,
        )

    def test_success_returns_handler_result(self, monkeypatch: pytest.MonkeyPatch) -> None:
        assert self.run([], monkeypatch) == 0

    def test_error_prints_actionable_message(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert self.run(["--fail", "value"], monkeypatch) == 2
        assert "Error: handler failed" in capsys.readouterr().err

    def test_error_with_json_flag_prints_json(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert self.run(["--fail", "value", "--json"], monkeypatch) == 2
        payload = json.loads(capsys.readouterr().out)
        assert payload == {"ok": False, "error": "handler failed"}

    def test_parse_error_before_args_prints_actionable_message(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert self.run(["--fail", "bogus"], monkeypatch) == 2
        assert "invalid choice" in capsys.readouterr().err
