"""Tests for coh_engine.maths — Maths.mhd table loader.

Expected values transcribed from docs/engine/mids-port-spec.md
§ enhancement-value-pipeline (source: Databases/Homecoming/Maths.mhd via
DatabaseAPI.LoadMaths, MidsReborn fork).
"""

import struct
from pathlib import Path

import pytest

from coh_engine.maths import MathTables, _strip, load_maths


def f32(x: float) -> float:
    """Round-trip a value through IEEE-754 single precision (C# float storage)."""
    quantized: float = struct.unpack("f", struct.pack("f", x))[0]
    return quantized


@pytest.fixture(scope="module")
def tables(maths_path: Path) -> MathTables:
    return load_maths(maths_path)


class TestEDThresholds:
    """MultED[sched][thresh] — note the transposed read: file rows are thresholds."""

    def test_schedule_a(self, tables: MathTables) -> None:
        assert tables.mult_ed[0] == (f32(0.700), f32(0.900), f32(1.000))

    def test_schedule_b(self, tables: MathTables) -> None:
        assert tables.mult_ed[1] == (f32(0.400), f32(0.500), f32(0.600))

    def test_schedule_c(self, tables: MathTables) -> None:
        assert tables.mult_ed[2] == (f32(0.800), f32(1.000), f32(1.200))

    def test_schedule_d(self, tables: MathTables) -> None:
        assert tables.mult_ed[3] == (f32(1.200), f32(1.500), f32(1.800))


class TestGradeEffectiveness:
    def test_training_origin(self, tables: MathTables) -> None:
        assert tables.mult_to == (f32(0.083), f32(0.050), f32(0.100), f32(0.150))

    def test_dual_origin(self, tables: MathTables) -> None:
        assert tables.mult_do == (f32(0.167), f32(0.100), f32(0.200), f32(0.300))

    def test_single_origin(self, tables: MathTables) -> None:
        assert tables.mult_so == (f32(0.333), f32(0.200), f32(0.400), f32(0.600))

    def test_hamidon_origin(self, tables: MathTables) -> None:
        assert tables.mult_ho == (f32(0.333), f32(0.200), f32(0.400), f32(0.600))


class TestLevelIOEffectiveness:
    """MultIO[level-1][sched] — 53 rows, 0-based IO level index."""

    def test_row_count(self, tables: MathTables) -> None:
        assert len(tables.mult_io) == 53

    def test_levels_1_to_9_are_zero(self, tables: MathTables) -> None:
        for row in tables.mult_io[:9]:
            assert row == (0.0, 0.0, 0.0, 0.0)

    def test_level_10(self, tables: MathTables) -> None:
        assert tables.mult_io[9] == (f32(0.117), f32(0.070), f32(0.140), f32(0.210))

    def test_level_26(self, tables: MathTables) -> None:
        assert tables.mult_io[25] == (f32(0.333), f32(0.200), f32(0.400), f32(0.600))

    def test_level_50(self, tables: MathTables) -> None:
        """The everyday case: a level-50 IO reads MultIO[49]."""
        assert tables.mult_io[49] == (f32(0.424), f32(0.255), f32(0.509), f32(0.764))

    def test_level_53(self, tables: MathTables) -> None:
        assert tables.mult_io[52] == (f32(0.435), f32(0.261), f32(0.523), f32(0.784))


class TestLoaderErrors:
    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_maths(tmp_path / "nope.mhd")

    def test_missing_section_raises(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.mhd"
        bad.write_text("Enhancement Multiplier Data\nVersion:\t1.000\n", encoding="utf-8")
        with pytest.raises(ValueError, match="EDRT"):
            load_maths(bad)

    def test_missing_version_header_raises(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.mhd"
        bad.write_text("no version here\n", encoding="utf-8")
        with pytest.raises(ValueError, match=r"[Vv]ersion"):
            load_maths(bad)

    def test_truncated_table_raises(self, tmp_path: Path) -> None:
        """EOF mid-table (here: LBIOE with fewer than 53 rows) is an error."""
        bad = tmp_path / "truncated.mhd"
        bad.write_text(
            "Version:\t1.000\n"
            "EDRT\tA\tB\tC\tD\n"
            "EDThresh_1\t0.700\t0.400\t0.800\t1.200\n"
            "EDThresh_2\t0.900\t0.500\t1.000\t1.500\n"
            "EDThresh_3\t1.000\t0.600\t1.200\t1.800\n"
            "EGE\tA\tB\tC\tD\n"
            "TO:\t0.083\t0.050\t0.100\t0.150\n"
            "DO:\t0.167\t0.100\t0.200\t0.300\n"
            "SO:\t0.333\t0.200\t0.400\t0.600\n"
            "HO:\t0.333\t0.200\t0.400\t0.600\n"
            "LBIOE\tA\tB\tC\tD\n"
            "1\t0.000\t0.000\t0.000\t0.000\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match=r"end of file"):
            load_maths(bad)


class TestTokenStripping:
    """_strip mirrors FileIO.IOStrip (Core/FileIO.cs:35-40)."""

    def test_leading_apostrophe_dropped(self) -> None:
        assert _strip("'0.700") == "0.700"

    def test_leading_space_dropped(self) -> None:
        assert _strip(" 0.700") == "0.700"

    def test_trailing_space_dropped(self) -> None:
        assert _strip("0.700 ") == "0.700"

    def test_quotes_removed(self) -> None:
        assert _strip('"0.700"') == "0.700"

    def test_plain_token_unchanged(self) -> None:
        assert _strip("EDRT") == "EDRT"
