"""CLI entry point — the registry-introspection surface."""

import pytest

from coh_engine.__main__ import main


def test_rules_lists_both_registries(capsys: pytest.CaptureFixture[str]) -> None:
    """`rules` prints the registered legality rules and scoring metrics."""
    assert main(["rules"]) == 0
    out = capsys.readouterr().out
    assert "legality rules" in out
    assert "_rule_placement" in out  # a registered legality rule
    assert "scoring metrics" in out
    assert "perma_hasten" in out  # a registered metric


def test_no_command_prints_status(capsys: pytest.CaptureFixture[str]) -> None:
    """No subcommand prints the engine status line."""
    assert main([]) == 0
    assert "coh_engine: MidsReborn build-math port." in capsys.readouterr().out
