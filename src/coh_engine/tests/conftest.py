from pathlib import Path

import pytest

from coh_engine.maths import MathTables, load_maths

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def maths_path() -> Path:
    """Path to the Homecoming Maths.mhd fixture (verbatim copy from the MidsReborn fork)."""
    return FIXTURES / "Maths.mhd"


@pytest.fixture(scope="session")
def tables(maths_path: Path) -> MathTables:
    """Parsed Maths.mhd tables, shared across the suite (immutable dataclass)."""
    return load_maths(maths_path)
