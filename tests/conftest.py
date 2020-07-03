from pathlib import Path

import pytest
from pipdownload import settings

SRC_DIR = (Path(__file__).parent / "data").resolve()

# this is a monkey patch of config file
settings.SETTINGS_FILE = str(SRC_DIR / "settings.json")


@pytest.fixture(scope="module")
def requirement_file_redundant():
    return str(SRC_DIR / "requirements_redundant.txt")


@pytest.fixture(scope="module")
def requirement_file_normal():
    return str(SRC_DIR / "requirements_normal.txt")


# @pytest.fixture(scope="function")
# def monkeypatch_config_file(monkeypatch):
#     monkeypatch.setattr(settings, "SETTINGS_FILE", str(SRC_DIR / "settings.json"))
