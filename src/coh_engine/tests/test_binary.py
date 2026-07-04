"""Tests for the .mxd binary primitive reader (CP2)."""

import struct

import pytest

from coh_engine.buildfile.binary import Cursor
from coh_engine.maths import f32


def _dotnet_string(s: str) -> bytes:
    """Encode a string as .NET does: 7-bit length prefix + UTF-8 bytes."""
    raw = s.encode("utf-8")
    n = len(raw)
    out = bytearray()
    while True:
        byte = n & 0x7F
        n >>= 7
        if n:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            break
    return bytes(out) + raw


def test_scalars_round_trip() -> None:
    buf = (
        struct.pack("<i", -12345)
        + struct.pack("<q", 9_000_000_000)
        + struct.pack("<f", 1.5)
        + b"\x01"
        + struct.pack("<b", -7)
    )
    cur = Cursor(buf)
    assert cur.read_int32() == -12345
    assert cur.read_int64() == 9_000_000_000
    assert cur.read_single() == f32(1.5)
    assert cur.read_boolean() is True
    assert cur.read_sbyte() == -7


def test_string_short_and_long() -> None:
    short = _dotnet_string("Pool.Leaping")
    # A string >= 128 bytes exercises the multi-byte 7-bit length prefix.
    long_val = "X" * 200
    long_bytes = _dotnet_string(long_val)
    cur = Cursor(short + long_bytes)
    assert cur.read_string() == "Pool.Leaping"
    assert cur.read_string() == long_val


def test_array_count_idiom() -> None:
    # Stored length-1; a stored 0 means one element.
    cur = Cursor(struct.pack("<i", 0) + struct.pack("<i", 4))
    assert cur.read_array_count() == 1
    assert cur.read_array_count() == 5


def test_boolean_zero_is_false() -> None:
    assert Cursor(b"\x00").read_boolean() is False


def test_read_past_end_raises() -> None:
    cur = Cursor(b"\x01\x02")
    with pytest.raises(EOFError):
        cur.read_int32()


def test_seven_bit_length_overflow_raises() -> None:
    # Five continuation bytes (a 6th would exceed a 32-bit value) -> rejected,
    # matching .NET's Read7BitEncodedInt, which throws before reading a 6th byte.
    cur = Cursor(b"\x80\x80\x80\x80\x80")
    assert len(cur) == 5
    with pytest.raises(ValueError, match="7-bit length"):
        cur.read_7bit_length()


def test_pos_tracks_reads() -> None:
    cur = Cursor(struct.pack("<i", 1) + struct.pack("<i", 2))
    assert cur.pos == 0
    cur.read_int32()
    assert cur.pos == 4
    assert len(cur) == 8
