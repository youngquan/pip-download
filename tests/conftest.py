import os
from pathlib import Path

import pytest

SRC_DIR = Path(__file__).resolve().parent


@pytest.fixture(scope="module")
def requirement_file_redundant():
    return str(SRC_DIR / 'test_requirements_redundant.txt')


@pytest.fixture(scope="module")
def requirement_file_normal():
    return str(SRC_DIR / 'test_requirements_normal.txt')
