"""Loader for MidsReborn's Maths.mhd enhancement-multiplier tables.

Mirrors ``DatabaseAPI.LoadMaths`` (MidsReborn ``Core/DatabaseAPI.cs:2412-2549``) and the
``FileIO.IOGrab``/``IOSeek`` tokenizer (``Core/FileIO.cs``): tab-delimited text, sections
located by first-column label, values stored as IEEE-754 single precision (C# ``float``).
Spec: docs/engine/mids-port-spec.md § enhancement-value-pipeline.
"""

import struct
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

Row3 = tuple[float, float, float]
Row4 = tuple[float, float, float, float]


def f32(value: float) -> float:
    """Quantize to IEEE-754 single precision, matching C# ``float`` storage."""
    quantized: float = struct.unpack("f", struct.pack("f", value))[0]
    return quantized


@dataclass(frozen=True, slots=True)
class MathTables:
    """The Maths.mhd tables, indexed exactly as MidsReborn stores them.

    Attributes:
        mult_ed: ``MultED[schedule][threshold]`` — ED thresholds per schedule A..D (0..3).
        mult_to: ``MultTO[0][schedule]`` — Training Origin effectiveness per schedule.
        mult_do: ``MultDO[0][schedule]`` — Dual Origin effectiveness per schedule.
        mult_so: ``MultSO[0][schedule]`` — Single Origin effectiveness per schedule
            (also used for SpecialO / Hami-O in the value pipeline).
        mult_ho: ``MultHO[0][schedule]`` — loaded but unused by ``GetScheduleMult``.
        mult_io: ``MultIO[io_level_0based][schedule]`` — 53 rows; a level-50 IO reads
            row index 49.
    """

    mult_ed: tuple[Row3, Row3, Row3, Row3]
    mult_to: Row4
    mult_do: Row4
    mult_so: Row4
    mult_ho: Row4
    mult_io: tuple[Row4, ...]


def _grab(stream: TextIO) -> list[str]:
    """Read one line and tokenize like ``FileIO.IOGrab``: tab-split, strip quotes/edges."""
    line = stream.readline()
    if line == "":
        raise ValueError("unexpected end of file while reading Maths.mhd tables")
    tokens = line.rstrip("\r\n").split("\t")
    return [_strip(t) for t in tokens]


def _strip(token: str) -> str:
    """Mirror ``FileIO.IOStrip`` exactly, including its quirk (FileIO.cs:35-40).

    In the C# source the ``Substring(1)`` leading-strip result feeds only the
    ``EndsWith(" ")`` test — both return branches use the ORIGINAL string. Mids
    therefore never removes a leading apostrophe/space from the returned token
    and strips at most one trailing character. Reproduce, don't fix: an
    apostrophe-prefixed cell must fail numeric parsing here exactly as it fails
    ``float.TryParse`` in Mids.
    """
    probe = token[1:] if token.startswith(("'", " ")) else token
    if probe.endswith(" "):
        token = token[:-1]
    return token.replace('"', "")


def _try_parse_float(token: str) -> float:
    """Mirror C# ``float.TryParse`` as the loaders use it: parse failure yields 0.0.

    ``DatabaseAPI.LoadMaths`` records a load-error flag on TryParse failure but
    keeps the default 0 value and continues loading; matching that keeps the
    port's tables identical to the oracle's for the same quirky input file.
    """
    try:
        return f32(float(token))
    except ValueError:
        return 0.0


def _seek(stream: TextIO, label: str) -> None:
    """Skip lines until the first tab-column equals ``label`` (``FileIO.IOSeek``)."""
    for line in stream:
        first = _strip(line.rstrip("\r\n").split("\t")[0])
        if first == label:
            return
    raise ValueError(f"section header {label!r} not found in Maths.mhd")


def _row4(stream: TextIO) -> Row4:
    tokens = _grab(stream)
    a, b, c, d = (_try_parse_float(t) for t in tokens[1:5])
    return (a, b, c, d)


def load_maths(path: Path | str) -> MathTables:
    """Parse a Maths.mhd file into :class:`MathTables`.

    Raises:
        FileNotFoundError: if ``path`` does not exist.
        ValueError: if the version header or a section header is missing, or a
            table row is malformed.
    """
    with open(path, encoding="utf-8") as stream:
        _seek(stream, "Version:")
        _seek(stream, "EDRT")
        # File rows are thresholds 1..3; columns are schedules A..D. Mids stores the
        # transpose: MultED[schedule][threshold] (DatabaseAPI.cs:2461 index order).
        threshold_rows = [_grab(stream) for _ in range(3)]
        mult_ed = tuple(tuple(_try_parse_float(threshold_rows[t][s + 1]) for t in range(3)) for s in range(4))
        _seek(stream, "EGE")
        mult_to = _row4(stream)
        mult_do = _row4(stream)
        mult_so = _row4(stream)
        mult_ho = _row4(stream)
        _seek(stream, "LBIOE")
        mult_io = tuple(_row4(stream) for _ in range(53))
    return MathTables(
        mult_ed=mult_ed,  # type: ignore[arg-type]
        mult_to=mult_to,
        mult_do=mult_do,
        mult_so=mult_so,
        mult_ho=mult_ho,
        mult_io=mult_io,
    )
