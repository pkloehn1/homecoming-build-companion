"""TDD contract tests for CalVer versioning module."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from scripts.common.git_runner import GitResult
from scripts.devops.calver import (
    CalVerResult,
    _DefaultGitRunner,
    compute_next_version,
    list_tags,
    main,
    parse_calver_tag,
)

# ---------------------------------------------------------------------------
# Stub GitRunner (follows _StubGhRunner pattern from scripts/github/conftest.py)
# ---------------------------------------------------------------------------


class _StubGitRunner:
    """Stub implementing GitRunner Protocol for deterministic tests."""

    def __init__(self, tag_output: str = "", returncode: int = 0) -> None:
        """Initialize _StubGitRunner."""
        self.tag_output = tag_output
        self.returncode = returncode

    def run_git(self, args: list[str], *, cwd: Path | None = None) -> GitResult:
        """Run git."""
        return GitResult(returncode=self.returncode, stdout=self.tag_output, stderr="")


# ---------------------------------------------------------------------------
# CalVerResult dataclass
# ---------------------------------------------------------------------------


class TestCalVerResult:
    """Test Cal Ver Result."""

    def test_frozen(self) -> None:
        """Test frozen."""
        result = CalVerResult(version="2026.03.0", tag="v2026.03.0", year=2026, month=3, micro=0)
        with pytest.raises(AttributeError):
            result.version = "other"  # type: ignore[misc]

    def test_iter_unpacking(self) -> None:
        """Test iter unpacking."""
        result = CalVerResult(version="2026.03.0", tag="v2026.03.0", year=2026, month=3, micro=0)
        version, tag, year, month, micro = result
        assert version == "2026.03.0"
        assert tag == "v2026.03.0"
        assert year == 2026
        assert month == 3
        assert micro == 0


# ---------------------------------------------------------------------------
# parse_calver_tag
# ---------------------------------------------------------------------------


class TestParseCalverTag:
    """Test Parse Calver Tag."""

    def test_valid_tag(self) -> None:
        """Test valid tag."""
        result = parse_calver_tag("v2026.03.0")
        assert result is not None
        assert result.version == "2026.03.0"
        assert result.tag == "v2026.03.0"
        assert result.year == 2026
        assert result.month == 3
        assert result.micro == 0

    def test_valid_tag_high_micro(self) -> None:
        """Test valid tag high micro."""
        result = parse_calver_tag("v2026.03.42")
        assert result is not None
        assert result.micro == 42

    def test_missing_v_prefix(self) -> None:
        """Test missing v prefix."""
        assert parse_calver_tag("2026.03.0") is None

    def test_non_zero_padded_month(self) -> None:
        """Test non zero padded month."""
        assert parse_calver_tag("v2026.3.0") is None

    def test_invalid_month_zero(self) -> None:
        """Test invalid month zero."""
        assert parse_calver_tag("v2026.00.0") is None

    def test_invalid_month_thirteen(self) -> None:
        """Test invalid month thirteen."""
        assert parse_calver_tag("v2026.13.0") is None

    def test_malformed_string(self) -> None:
        """Test malformed string."""
        assert parse_calver_tag("not-a-tag") is None

    def test_empty_string(self) -> None:
        """Test empty string."""
        assert parse_calver_tag("") is None

    def test_semver_tag_rejected(self) -> None:
        """Test semver tag rejected."""
        assert parse_calver_tag("v1.2.3") is None


# ---------------------------------------------------------------------------
# compute_next_version
# ---------------------------------------------------------------------------


class TestComputeNextVersion:
    """Test Compute Next Version."""

    def test_no_existing_tags(self) -> None:
        """Test no existing tags."""
        now = datetime(2026, 3, 1, tzinfo=UTC)
        result = compute_next_version([], now)
        assert result.version == "2026.03.0"
        assert result.tag == "v2026.03.0"
        assert result.year == 2026
        assert result.month == 3
        assert result.micro == 0

    def test_single_tag_same_month(self) -> None:
        """Test single tag same month."""
        now = datetime(2026, 3, 15, tzinfo=UTC)
        result = compute_next_version(["v2026.03.0"], now)
        assert result.version == "2026.03.1"
        assert result.micro == 1

    def test_multiple_tags_same_month(self) -> None:
        """Test multiple tags same month."""
        now = datetime(2026, 3, 20, tzinfo=UTC)
        tags = ["v2026.03.0", "v2026.03.1", "v2026.03.2"]
        result = compute_next_version(tags, now)
        assert result.version == "2026.03.3"
        assert result.micro == 3

    def test_month_rollover_resets_micro(self) -> None:
        """Test month rollover resets micro."""
        now = datetime(2026, 4, 1, tzinfo=UTC)
        tags = ["v2026.03.0", "v2026.03.1", "v2026.03.5"]
        result = compute_next_version(tags, now)
        assert result.version == "2026.04.0"
        assert result.micro == 0

    def test_year_rollover_resets_micro(self) -> None:
        """Test year rollover resets micro."""
        now = datetime(2027, 1, 1, tzinfo=UTC)
        tags = ["v2026.12.3"]
        result = compute_next_version(tags, now)
        assert result.version == "2027.01.0"
        assert result.micro == 0

    def test_ignores_invalid_tags(self) -> None:
        """Test ignores invalid tags."""
        now = datetime(2026, 3, 1, tzinfo=UTC)
        tags = ["v2026.03.0", "not-a-tag", "v1.2.3"]
        result = compute_next_version(tags, now)
        assert result.version == "2026.03.1"

    def test_ignores_different_month_tags(self) -> None:
        """Test ignores different month tags."""
        now = datetime(2026, 3, 1, tzinfo=UTC)
        tags = ["v2026.02.5", "v2026.03.0"]
        result = compute_next_version(tags, now)
        assert result.version == "2026.03.1"


# ---------------------------------------------------------------------------
# list_tags
# ---------------------------------------------------------------------------


class TestListTags:
    """Test List Tags."""

    def test_success(self) -> None:
        """Test success."""
        runner = _StubGitRunner(tag_output="v2026.03.0\nv2026.03.1\n")
        tags = list_tags(runner)
        assert tags == ["v2026.03.0", "v2026.03.1"]

    def test_empty_repo(self) -> None:
        """Test empty repo."""
        runner = _StubGitRunner(tag_output="")
        tags = list_tags(runner)
        assert tags == []

    def test_git_failure_returns_empty(self) -> None:
        """Test git failure returns empty."""
        runner = _StubGitRunner(returncode=128)
        tags = list_tags(runner)
        assert tags == []

    def test_default_runner_delegates_to_run_git(self) -> None:
        """Test default runner delegates to run git."""
        runner = _DefaultGitRunner()
        result = runner.run_git(["--version"])
        assert result.returncode == 0
        assert "git version" in result.stdout


# ---------------------------------------------------------------------------
# CLI main
# ---------------------------------------------------------------------------


class TestMain:
    """Test Main."""

    _FIXED_NOW = datetime(2026, 3, 15, tzinfo=UTC)
    _STUB_RUNNER = _StubGitRunner(tag_output="v2026.03.0\nv2026.03.1\n")

    def test_dry_run(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test dry run."""
        code = main(["--dry-run"], runner=self._STUB_RUNNER, now=self._FIXED_NOW)
        captured = capsys.readouterr()
        assert code == 0
        assert captured.out.strip() == "2026.03.2"

    def test_default_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test default output."""
        code = main([], runner=self._STUB_RUNNER, now=self._FIXED_NOW)
        captured = capsys.readouterr()
        assert code == 0
        lines = captured.out.strip().splitlines()
        assert "version=2026.03.2" in lines
        assert "tag=v2026.03.2" in lines
