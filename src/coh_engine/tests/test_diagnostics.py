"""Structured diagnostic output (``error-output.md`` format).

A :class:`~coh_engine.diagnostics.Diagnostic` renders both the machine-parseable
text line ``{path}:{line}:{column}: {severity}: {rule_id}: {message}`` and the
``--format=json`` object, and a list of them resolves to the standard exit code
(error -> 1, warning-only -> 2, clean -> 0).
"""

import pytest

from coh_engine.diagnostics import Diagnostic, exit_code, format_json, format_text


def _err() -> Diagnostic:
    return Diagnostic(
        rule_id="H-ENH-003",
        severity="error",
        message="enhancement class not accepted by power",
        path="build.json",
        line=42,
        column=1,
        fix="remove the piece or move it to a power that accepts this class",
        expected=[18],
        actual=[8, 11, 7, 19],
    )


def test_text_line_matches_error_output_format() -> None:
    """The text form is ``{path}:{line}:{column}: {severity}: {rule_id}: {message}``."""
    assert _err().format_text() == ("build.json:42:1: error: H-ENH-003: enhancement class not accepted by power")


def test_json_object_carries_every_field() -> None:
    """The JSON form exposes the structured fields ``--format=json`` emits."""
    obj = _err().to_json()
    assert obj == {
        "rule_id": "H-ENH-003",
        "severity": "error",
        "path": "build.json",
        "line": 42,
        "column": 1,
        "message": "enhancement class not accepted by power",
        "fix": "remove the piece or move it to a power that accepts this class",
        "expected": [18],
        "actual": [8, 11, 7, 19],
    }


def test_json_omits_blank_optional_fields() -> None:
    """A diagnostic with no fix/expected/actual emits only the required keys."""
    obj = Diagnostic(rule_id="P-SLOT-001", severity="warning", message="m").to_json()
    assert obj == {
        "rule_id": "P-SLOT-001",
        "severity": "warning",
        "path": "build.json",
        "line": 1,
        "column": 1,
        "message": "m",
    }


def test_default_location_is_build_json_line_1() -> None:
    """Location defaults to the whole-build anchor when no site is known."""
    d = Diagnostic(rule_id="H-ENH-002", severity="error", message="m")
    assert d.format_text() == "build.json:1:1: error: H-ENH-002: m"


def test_invalid_severity_is_rejected() -> None:
    """Only the three canonical severities are accepted."""
    with pytest.raises(ValueError, match=r"E10:.*severity"):
        Diagnostic(rule_id="X", severity="fatal", message="m")


def test_format_text_joins_a_list_one_per_line() -> None:
    """``format_text`` over a list yields one text line per diagnostic, in order."""
    diags = [
        Diagnostic(rule_id="A", severity="error", message="first"),
        Diagnostic(rule_id="B", severity="warning", message="second"),
    ]
    assert format_text(diags) == ("build.json:1:1: error: A: first\nbuild.json:1:1: warning: B: second")


def test_format_json_is_a_list_of_objects() -> None:
    """``format_json`` over a list yields the JSON objects in order."""
    diags = [Diagnostic(rule_id="A", severity="error", message="m")]
    assert format_json(diags) == [diags[0].to_json()]


@pytest.mark.parametrize(
    ("severities", "expected"),
    [
        ([], 0),
        (["info"], 0),
        (["warning"], 2),
        (["info", "warning"], 2),
        (["error"], 1),
        (["warning", "error"], 1),
    ],
)
def test_exit_code_prioritizes_error_then_warning(severities: list[str], expected: int) -> None:
    """Exit code: any error -> 1, else any warning -> 2, else 0."""
    diags = [Diagnostic(rule_id="R", severity=s, message="m") for s in severities]
    assert exit_code(diags) == expected
