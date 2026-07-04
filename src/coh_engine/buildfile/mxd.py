"""Reader for the ``.mxd`` legacy binary build format — shared-text decode layer.

Covers the format's outer envelope (spec § data-and-build-formats, B.1-B.2):

- **Share wrapper** (``BuildManager.cs:320-351``): a ``|MxDz;u;c;e;HEX;|`` header line
  followed by ``BreakString``-wrapped payload lines. Exactly 5 ``;``-items; integer
  sizes; payload is every line after the header joined with ``|`` bookends stripped.
- **Payload decode** (``BuildManager.cs:364-382`` + ``ModernZlib.cs``): validate hex,
  decode to bytes, reject if byte length != the header compressed size, then zlib
  (RFC1950, ``Z_BEST_COMPRESSION``) inflate and resize to the uncompressed size.

The semantic parse of the decompressed buffer (``MxDReadSaveData``) — power/slot
records, StaticIndex resolution, and the Homecoming migrations — is a separate
layer built on :class:`coh_engine.buildfile.binary.Cursor`; it needs an enhancement
StaticIndex->TypeID map from the oracle harness and is tracked separately.
"""

import re
import zlib
from dataclasses import dataclass

_MXD_HEADER = re.compile(r"^\|MxDz;[0-9]+;[0-9]+;[0-9]+;HEX;\|")
_MBD_HEADER = re.compile(r"^\|MBD;[0-9]+;[0-9]+;[0-9]+;BASE64;\|")
_UNK_BASE64 = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")
_HEX = re.compile(r"\A[0-9A-Fa-f]+\Z")


def classify(text: str) -> str | None:
    """Classify a pasted share block by its first line (``DataClassifier.cs:36-53``).

    Returns ``"mxd"``, ``"mbd"``, ``"unkbase64"``, or ``None`` if unrecognized.
    """
    first = text.lstrip().splitlines()[0] if text.strip() else ""
    if _MXD_HEADER.match(first):
        return "mxd"
    if _MBD_HEADER.match(first):
        return "mbd"
    if _UNK_BASE64.match(first):
        return "unkbase64"
    return None


@dataclass(frozen=True, slots=True)
class ShareBlock:
    """A parsed share-text envelope: header sizes plus the joined payload string."""

    magic: str
    uncompressed_size: int
    compressed_size: int
    encoded_size: int
    encoding: str
    payload: str


def decode_share_block(text: str) -> ShareBlock:
    """Parse a share-text envelope (``BuildManager.cs:320-351``).

    Raises:
        ValueError: if there are fewer than 2 lines, the header is not exactly 5
            ``;``-separated items, or the sizes are not integers.
    """
    lines = [ln for ln in re.split(r"[\r\n]+", text) if ln != ""]
    if len(lines) < 2:
        raise ValueError("share block needs a header line and at least one payload line")
    header = lines[0].strip("|").strip()
    items = [it for it in header.split(";") if it != ""]
    if len(items) != 5:
        raise ValueError(f"share header must have exactly 5 items, got {len(items)}")
    try:
        uncompressed = int(items[1])
        compressed = int(items[2])
        encoded = int(items[3])
    except ValueError as exc:
        raise ValueError("share header sizes must be integers") from exc
    payload = "".join(lines[1:]).replace("|", "")
    return ShareBlock(
        magic=items[0],
        uncompressed_size=uncompressed,
        compressed_size=compressed,
        encoded_size=encoded,
        encoding=items[4],
        payload=payload,
    )


def hex_decode(data: str) -> bytes:
    """Decode an uppercase/lowercase hex string to bytes (``ModernZlib.cs:71-83``).

    Raises:
        ValueError: if ``data`` is not valid hex.
    """
    if not _HEX.match(data):
        raise ValueError("mxd payload is not valid hex")
    return bytes.fromhex(data)


def decode_mxd(text: str) -> bytes:
    """Decode a ``.mxd`` share block to its decompressed binary buffer.

    Reproduces ``BuildManager.cs:364-382``: hex-decode, reject on a compressed-size
    mismatch, zlib inflate, then resize to the declared uncompressed size.

    Raises:
        ValueError: on wrong classification, invalid hex, a compressed-size
            mismatch, or a zlib inflate failure.
    """
    if classify(text) != "mxd":
        raise ValueError("not an mxd share block")
    block = decode_share_block(text)
    raw = hex_decode(block.payload)
    if len(raw) != block.compressed_size:
        raise ValueError(f"mxd compressed size mismatch: header {block.compressed_size}, actual {len(raw)}")
    try:
        buffer = zlib.decompress(raw)
    except zlib.error as exc:
        raise ValueError("mxd zlib inflate failed") from exc
    return buffer[: block.uncompressed_size]
