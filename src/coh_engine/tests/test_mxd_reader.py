"""Branch-level tests for the .mxd semantic reader using synthetic buffers.

The parity tests exercise the current-format happy path against real Mids output;
these cover the format variants (legacy/prior), empty entries, subpowers, and the
per-TypeID slot paths that the sample builds do not all hit.
"""

import struct
from typing import Self

import pytest

from coh_engine.buildfile.binary import Cursor
from coh_engine.buildfile.dbindex import EnhIndexEntry
from coh_engine.buildfile.mxd import (
    _MAGIC,
    _format_for_version,
    _read_slot_data,
    _scan_magic,
    read_mxd_build,
)
from coh_engine.maths import f32

POWER_INDEX = {100: "Test.Set.Power", 101: "Test.Set.SubPower"}
ENH_INDEX = {
    5: EnhIndexEntry(uid="Enh_Normal", type_id="Normal"),
    6: EnhIndexEntry(uid="Enh_Set", type_id="SetO"),
    7: EnhIndexEntry(uid="Enh_None", type_id="None"),
    8: EnhIndexEntry(uid="Enh_Special", type_id="SpecialO"),
}


class _Buf:
    """Minimal .NET BinaryWriter-style builder for synthetic .mxd buffers."""

    def __init__(self) -> None:
        self.b = bytearray()

    def raw(self, data: bytes) -> Self:
        self.b += data
        return self

    def i32(self, v: int) -> Self:
        self.b += struct.pack("<i", v)
        return self

    def f32(self, v: float) -> Self:
        self.b += struct.pack("<f", v)
        return self

    def boolean(self, v: bool) -> Self:
        self.b += b"\x01" if v else b"\x00"
        return self

    def sbyte(self, v: int) -> Self:
        self.b += struct.pack("<b", v)
        return self

    def string(self, s: str) -> Self:
        raw = s.encode("utf-8")
        n = len(raw)
        while True:
            byte = n & 0x7F
            n >>= 7
            self.b += bytes([byte | 0x80]) if n else bytes([byte])
            if not n:
                break
        self.b += raw
        return self


def _header(buf: _Buf, version: float, qualified: bool, has_sub: bool) -> _Buf:
    buf.raw(_MAGIC).f32(version).boolean(qualified).boolean(has_sub)
    buf.string("Class_Scrapper").string("Magic")
    if version > 1:
        buf.i32(0)  # alignment
    buf.string("Synthetic")
    buf.i32(0).string("Test.Set")  # 1 powerset (count-1 = 0)
    buf.i32(0)  # LastPower + 1 -> engine -1
    return buf


def test_format_for_version() -> None:
    assert _format_for_version(f32(3.0)) == "legacy"
    assert _format_for_version(f32(3.15)) == "prior"
    assert _format_for_version(f32(3.20)) == "current"
    with pytest.raises(ValueError, match="newer version"):
        _format_for_version(f32(9.0))


def test_scan_magic_skips_leading_garbage() -> None:
    assert _scan_magic(b"\x00\x01" + _MAGIC + b"rest") == 2 + 4
    with pytest.raises(ValueError, match="magic number"):
        _scan_magic(b"\x00" * 10)


@pytest.mark.parametrize(
    ("static_index", "type_id", "expect_uid", "expect_rel"),
    [
        (5, "Normal", "Enh_Normal", "PlusOne"),
        (8, "SpecialO", "Enh_Special", "PlusOne"),
        (7, "None", "Enh_None", "Even"),
    ],
)
def test_read_slot_data_variants(static_index: int, type_id: str, expect_uid: str, expect_rel: str) -> None:
    buf = _Buf().i32(static_index)
    if type_id in ("Normal", "SpecialO"):
        buf.sbyte(5).sbyte(1)  # RelativeLevel=PlusOne(5), Grade=TrainingO(1)
    enh = _read_slot_data(Cursor(bytes(buf.b)), ENH_INDEX, f32(3.20))
    assert enh is not None
    assert enh.uid == expect_uid
    assert enh.relative_level == expect_rel


def test_read_slot_data_set_io_clamps_level() -> None:
    buf = _Buf().i32(6).sbyte(53).sbyte(9)  # SetO: IOLevel 53 -> clamp 49, RelativeLevel PlusFive(9)
    enh = _read_slot_data(Cursor(bytes(buf.b)), ENH_INDEX, f32(3.20))
    assert enh is not None
    assert enh.uid == "Enh_Set"
    assert enh.io_level == 49
    assert enh.relative_level == "PlusFive"


def test_read_slot_data_empty_slot() -> None:
    assert _read_slot_data(Cursor(struct.pack("<i", -1)), ENH_INDEX, f32(3.20)) is None


def test_read_slot_data_set_io_legacy_version_no_relative() -> None:
    # fVersion <= 1.0 stores no RelativeLevel byte after IOLevel.
    buf = _Buf().i32(6).sbyte(40)
    enh = _read_slot_data(Cursor(bytes(buf.b)), ENH_INDEX, f32(1.0))
    assert enh is not None
    assert enh.io_level == 40
    assert enh.relative_level == "Even"


def test_current_format_with_empty_entry_and_subpower() -> None:
    buf = _header(_Buf(), f32(3.20), qualified=False, has_sub=True)
    buf.i32(1)  # power count-1 = 1 -> 2 entries
    # Entry 0: empty (static_index -1), still has a slot array (0 slots).
    buf.i32(-1).sbyte(-1)
    # Entry 1: real power, 1 subpower, 1 slot with a Normal enhancement.
    buf.i32(100).sbyte(5).boolean(True).boolean(False).i32(2).i32(1)
    buf.sbyte(0).i32(101).boolean(True)  # 1 subpower
    buf.sbyte(0)  # 1 slot
    buf.sbyte(5).boolean(False).i32(5).sbyte(5).sbyte(0).boolean(False)  # slot: Normal enh, no alt
    build = read_mxd_build(bytes(buf.b), POWER_INDEX, ENH_INDEX)
    assert build.format == "current"
    named = [p for p in build.power_entries if p.power_name]
    assert len(named) == 1
    power = named[0]
    assert power.power_name == "Test.Set.Power"
    assert power.level == 5
    assert power.variable_value == 2
    assert power.inherent_slots_used == 1
    assert len(power.sub_power_entries) == 1
    assert power.sub_power_entries[0].power_name == "Test.Set.SubPower"
    assert power.slot_entries[0].enhancement is not None
    assert power.slot_entries[0].enhancement.uid == "Enh_Normal"


def test_prior_format_reads_proc_but_not_inherent_slots() -> None:
    buf = _header(_Buf(), f32(3.15), qualified=False, has_sub=False)
    buf.i32(0)  # 1 entry
    buf.i32(100).sbyte(3).boolean(True).boolean(True).i32(0)  # prior: no InherentSlotsUsed
    buf.sbyte(-1)  # 0 slots
    build = read_mxd_build(bytes(buf.b), POWER_INDEX, ENH_INDEX)
    assert build.format == "prior"
    assert build.power_entries[0].proc_include is True
    assert build.power_entries[0].inherent_slots_used == 0


def test_legacy_format_reads_no_proc_no_inherent() -> None:
    buf = _header(_Buf(), f32(3.0), qualified=False, has_sub=False)
    buf.i32(0)  # 1 entry
    buf.i32(100).sbyte(2).boolean(True).i32(0)  # legacy: StatInclude, VariableValue only
    buf.sbyte(-1)  # 0 slots; legacy slots read no IsInherent bool
    build = read_mxd_build(bytes(buf.b), POWER_INDEX, ENH_INDEX)
    assert build.format == "legacy"
    assert build.power_entries[0].proc_include is False
    assert build.power_entries[0].stat_include is True


def test_qualified_names_uses_uid_strings() -> None:
    buf = _header(_Buf(), f32(3.20), qualified=True, has_sub=False)
    buf.i32(0)  # 1 entry
    buf.string("Test.Set.Power").sbyte(4).boolean(True).boolean(False).i32(0).i32(0)
    buf.sbyte(-1)  # 0 slots
    build = read_mxd_build(bytes(buf.b), POWER_INDEX, ENH_INDEX)
    assert build.power_entries[0].power_name == "Test.Set.Power"
