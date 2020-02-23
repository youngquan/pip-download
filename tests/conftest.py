from pathlib import Path

import pytest

SRC_DIR = (Path(__file__).parent / "data").resolve()


@pytest.fixture(scope="module")
def requirement_file_redundant():
    return str(SRC_DIR / "requirements_redundant.txt")


@pytest.fixture(scope="module")
def requirement_file_normal():
    return str(SRC_DIR / "requirements_normal.txt")
