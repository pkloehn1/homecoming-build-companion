from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def maths_path() -> Path:
    """Path to the Homecoming Maths.mhd fixture (verbatim copy from the MidsReborn fork)."""
    return FIXTURES / "Maths.mhd"
