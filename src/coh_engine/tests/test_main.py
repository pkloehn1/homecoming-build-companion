"""CLI entry point — registry introspection and the ``validate`` subcommand."""

import json
from pathlib import Path

import pytest

from coh_engine.__main__ import _emit, main, run_validate

FIXTURES = Path(__file__).parent / "fixtures"
BUILD_DIR = FIXTURES / "mids" / "builds" / "shield_scrapper_set_bonuses"


def test_rules_lists_all_three_registries(capsys: pytest.CaptureFixture[str]) -> None:
    """`rules` prints the legality rules, hard-limit rules, and scoring metrics."""
    assert main(["rules"]) == 0
    out = capsys.readouterr().out
    assert "legality rules" in out
    assert "_rule_placement" in out  # a registered legality rule
    assert "hard-limit rules" in out
    assert "_rule_total_added_slots" in out  # a registered hard-limit rule
    assert "enhancement aspect handlers" in out
    assert "RechargeTime" in out  # a registered aspect handler
    assert "scoring metrics" in out
    assert "perma_hasten" in out  # a registered metric


def test_no_command_prints_status(capsys: pytest.CaptureFixture[str]) -> None:
    """No subcommand prints the engine status line."""
    assert main([]) == 0
    assert "coh_engine: MidsReborn build-math port." in capsys.readouterr().out


def test_run_validate_returns_diagnostics() -> None:
    """run_validate loads the dumped build and folds both registries over it."""
    diags = run_validate(BUILD_DIR, FIXTURES / "mids")
    # The authored totals-fixture is not slot-schedule-legal, so it has findings.
    assert any(d.rule_id.startswith("H-") for d in diags)


def test_validate_subcommand_text(capsys: pytest.CaptureFixture[str]) -> None:
    """`validate <build>` runs both registries and exits 1 when findings exist (text)."""
    code = main(["validate", str(BUILD_DIR)])
    out = capsys.readouterr().out
    assert code == 1
    assert "H-SLOT" in out


def test_validate_subcommand_json(capsys: pytest.CaptureFixture[str]) -> None:
    """`validate --format json` emits a parseable diagnostics array."""
    code = main(["validate", str(BUILD_DIR), "--format", "json"])
    payload = json.loads(capsys.readouterr().out)
    assert code == 1
    assert isinstance(payload, list) and payload and "rule_id" in payload[0]


def test_emit_no_violations(capsys: pytest.CaptureFixture[str]) -> None:
    """An empty diagnostics list prints the clean-build message and exits 0 (text)."""
    assert _emit([], as_json=False) == 0
    assert "no violations" in capsys.readouterr().out


def test_emit_empty_json(capsys: pytest.CaptureFixture[str]) -> None:
    """An empty diagnostics list emits an empty JSON array and exits 0."""
    assert _emit([], as_json=True) == 0
    assert json.loads(capsys.readouterr().out) == []
