"""Supplemental branch-coverage tests for scripts.dev.bootstrap_venv.

The imported upstream suite (kloehnwars-homelab) covers every statement; this
repo also gates on branch coverage, which leaves three branch directions
unexercised. Each test here pins one of them.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.dev.bootstrap_venv import (
    EXIT_OK,
    _check_pip_version,
    _load_dev_requirements_with_specifiers,
    run_bootstrap,
)


class TestLoadDevRequirementsSkipsNamelessEntries:
    def test_entry_without_extractable_name_is_skipped(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "x"\n[project.optional-dependencies]\ndev = ["pytest>=8.0.0", "==1.0"]\n',
            encoding="utf-8",
        )
        assert _load_dev_requirements_with_specifiers(tmp_path) == [("pytest", ">=8.0.0")]


class TestCheckPipVersionShortOutput:
    def test_single_token_version_output_returns_silently(self, capsys) -> None:
        proc = MagicMock(returncode=0, stdout="pip\n")
        with patch("scripts.dev.bootstrap_venv.subprocess.run", return_value=proc) as run:
            _check_pip_version(Path("python"))
        run.assert_called_once()
        assert "[WARN]" not in capsys.readouterr().out


class TestRunBootstrapWithoutPersistableState:
    def test_state_write_skipped_when_state_keys_missing(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n', encoding="utf-8")
        module = "scripts.dev.bootstrap_venv"
        with (
            patch(f"{module}.collect_state", return_value={"pyproject_present": True}),
            patch(f"{module}.build_plan", return_value=["install_dev_extras"]),
            patch(f"{module}.check_git_signing", return_value=(True, "signing ok")),
            patch(f"{module}._ensure_venv", return_value=(Path("python"), 0)),
            patch(f"{module}._run_bootstrap_actions", return_value=0),
            patch(f"{module}._run_local_bootstrap", return_value=0),
            patch(f"{module}.write_bootstrap_state") as write_state,
        ):
            rc = run_bootstrap(repo_root=tmp_path, platform="win32")
        assert rc == EXIT_OK
        write_state.assert_not_called()
