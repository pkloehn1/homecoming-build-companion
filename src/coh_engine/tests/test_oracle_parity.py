"""Oracle-parity goldens: the Python loader vs MidsReborn's own in-memory tables.

``fixtures/oracle/*.json`` is dumped by ``tools/oracle-dump`` (a headless C# harness
referencing the MidsReborn fork) from the same Homecoming database the ``Maths.mhd``
fixture was copied from. Every cell must match at IEEE-754 single precision —
.NET serializes ``float`` with shortest-round-trip strings, so both sides are
quantized through :func:`coh_engine.maths.f32` before comparison.

Re-baseline (re-run the dump and refresh these fixtures) after any Homecoming DB update.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from coh_engine.maths import MathTables, f32, load_maths

ORACLE = Path(__file__).parent / "fixtures" / "oracle"


@pytest.fixture(scope="module")
def oracle_maths() -> dict[str, Any]:
    with open(ORACLE / "maths.json", encoding="utf-8") as fh:
        data: dict[str, Any] = json.load(fh)
    return data


@pytest.fixture(scope="module")
def tables(maths_path: Path) -> MathTables:
    return load_maths(maths_path)


def test_mult_ed_matches_oracle(oracle_maths: dict[str, Any], tables: MathTables) -> None:
    for sched in range(4):
        for thresh in range(3):
            assert f32(oracle_maths["MultED"][sched][thresh]) == tables.mult_ed[sched][thresh], (
                f"MultED[{sched}][{thresh}]"
            )


@pytest.mark.parametrize(
    "name,attr", [("MultTO", "mult_to"), ("MultDO", "mult_do"), ("MultSO", "mult_so"), ("MultHO", "mult_ho")]
)
def test_grade_tables_match_oracle(oracle_maths: dict[str, Any], tables: MathTables, name: str, attr: str) -> None:
    port_row = getattr(tables, attr)
    for sched in range(4):
        assert f32(oracle_maths[name][0][sched]) == port_row[sched], f"{name}[0][{sched}]"


def test_mult_io_matches_oracle(oracle_maths: dict[str, Any], tables: MathTables) -> None:
    assert len(oracle_maths["MultIO"]) == len(tables.mult_io) == 53
    for row in range(53):
        for sched in range(4):
            assert f32(oracle_maths["MultIO"][row][sched]) == tables.mult_io[row][sched], f"MultIO[{row}][{sched}]"


def test_server_data_constants() -> None:
    """Hard-limit constants the repo rules cite, straight from the oracle dump."""
    with open(ORACLE / "server_data.json", encoding="utf-8") as fh:
        sd = json.load(fh)
    assert sd["BaseToHit"] == 0.75
    assert sd["MaxSlots"] == 67
    assert sd["EnableInherentSlotting"] is False


def test_oracle_dump_is_version_stamped() -> None:
    with open(ORACLE / "version.json", encoding="utf-8") as fh:
        version = json.load(fh)
    assert version["DatabaseName"] == "Homecoming"
    assert version["DatabaseVersion"]
