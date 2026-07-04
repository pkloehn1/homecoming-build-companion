"""Primitive .NET ``BinaryReader`` decoding for the ``.mxd`` binary build format.

All MidsReborn binary files use little-endian .NET ``BinaryReader``/``BinaryWriter``
(spec § data-and-build-formats, "Primitive encoding conventions"):

- ``Int32`` = 4 bytes LE signed; ``Single`` = 4 bytes IEEE-754 LE; ``Int64`` = 8 LE;
    ``Boolean`` = 1 byte; ``SByte`` = 1 byte signed.
- ``String`` = 7-bit-encoded (LEB128) unsigned byte length, then that many UTF-8 bytes.
- Array counts are written as ``length - 1`` and read back as ``read_int32() + 1``.

The :class:`Cursor` reproduces exactly these reads; a byte-length error raises
``EOFError`` rather than returning partial data.
"""

import struct

from coh_engine.maths import f32


class Cursor:
    """A forward-only reader over a ``.mxd`` binary buffer."""

    __slots__ = ("_buf", "_pos")

    def __init__(self, buffer: bytes, pos: int = 0) -> None:
        self._buf = buffer
        self._pos = pos

    @property
    def pos(self) -> int:
        """Current byte offset."""
        return self._pos

    def __len__(self) -> int:
        """Total buffer length in bytes."""
        return len(self._buf)

    def read_bytes(self, n: int) -> bytes:
        """Read ``n`` raw bytes."""
        end = self._pos + n
        if end > len(self._buf):
            raise EOFError(f"read past end of buffer at {self._pos} (+{n})")
        chunk = self._buf[self._pos : end]
        self._pos = end
        return chunk

    def read_boolean(self) -> bool:
        """Read a 1-byte boolean (0 -> False, non-zero -> True)."""
        return self.read_bytes(1)[0] != 0

    def read_sbyte(self) -> int:
        """Read a signed byte."""
        value: int = struct.unpack("<b", self.read_bytes(1))[0]
        return value

    def read_int32(self) -> int:
        """Read a little-endian signed 32-bit integer."""
        value: int = struct.unpack("<i", self.read_bytes(4))[0]
        return value

    def read_int64(self) -> int:
        """Read a little-endian signed 64-bit integer."""
        value: int = struct.unpack("<q", self.read_bytes(8))[0]
        return value

    def read_single(self) -> float:
        """Read a little-endian IEEE-754 single (already f32-precise)."""
        return f32(struct.unpack("<f", self.read_bytes(4))[0])

    def read_7bit_length(self) -> int:
        """Read a .NET 7-bit-encoded (LEB128) unsigned length prefix."""
        result = 0
        shift = 0
        while True:
            byte = self.read_bytes(1)[0]
            result |= (byte & 0x7F) << shift
            if (byte & 0x80) == 0:
                break
            shift += 7
            if shift > 35:
                raise ValueError("7-bit length prefix too long")
        return result

    def read_string(self) -> str:
        """Read a .NET length-prefixed UTF-8 string."""
        n = self.read_7bit_length()
        return self.read_bytes(n).decode("utf-8")

    def read_array_count(self) -> int:
        """Read the ``length - 1`` array-count idiom, returning the true count."""
        return self.read_int32() + 1
