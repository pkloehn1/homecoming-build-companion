"""Conftest."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from scripts.github.gh_cli import GhResult

# ---------------------------------------------------------------------------
# Shared queue-based GhRunner stub (used across multiple test modules)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExpectedCall:
    """A single expected ``gh`` CLI invocation with optional input validation."""

    argv: list[str]
    stdout: str
    expected_input: str | None = None


class QueueRunner:
    """Mock GhRunner that pops expected calls from a queue.

    Validates ``argv`` for every call.  When ``expected_input`` is set on an
    :class:`ExpectedCall`, the ``input_text`` argument is also compared as
    parsed JSON (order-insensitive).
    """

    def __init__(self, calls: list[ExpectedCall]) -> None:
        """Initialize QueueRunner."""
        self._calls = list(calls)

    def run(self, argv: list[str], *, input_text: str | None = None) -> GhResult:
        """Run."""
        if not self._calls:
            raise AssertionError(f"Unexpected gh call (no calls left): {argv!r}")
        expected = self._calls.pop(0)
        assert argv == expected.argv
        if expected.expected_input is not None:
            assert input_text is not None, "Expected input_text but got None"
            assert json.loads(input_text) == json.loads(expected.expected_input)
        return GhResult(stdout=expected.stdout, stderr="")

    def assert_exhausted(self) -> None:
        """Assert exhausted."""
        assert not self._calls, f"Unused expected calls: {self._calls!r}"


def as_stdout(payload: Any) -> str:
    """Normalize payloads to JSON strings unless already a string."""
    if isinstance(payload, str):
        return payload
    return json.dumps(payload)


def make_call(argv: list[str], stdout: Any = "") -> ExpectedCall:
    """Build an :class:`ExpectedCall` with automatic JSON serialization."""
    return ExpectedCall(argv=argv, stdout=as_stdout(stdout))


def make_runner(*calls: ExpectedCall) -> QueueRunner:
    """Build a :class:`QueueRunner` from positional expected calls."""
    return QueueRunner(list(calls))
