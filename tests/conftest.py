import re
from pathlib import Path

import pytest
import requests
from bs4 import BeautifulSoup

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


def get_file_num_from_site_pypi_org(packege_name: str, constraints: list = None, no_source: bool = False):
    """
    Get the number of files on the package's official download page from pypi.org.
    :param packege_name: the name of the package to be downloaded.
    :param constraints: some constraints of the packages to be downloaded.
    :param no_source: whether to download the source file.
    :return: the number of files to be downloaded.
    """
    base_url = "https://pypi.org/project/{}/#files"
    full_url = base_url.format(packege_name)
    r = requests.get(full_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    if no_source:
        num = 0
    else:
        num = 1
    if constraints:
        for link in soup.find_all(href=re.compile("files.pythonhosted.org.*whl")):
            flag = 0
            file_name = link.string.strip()
            for constraint in constraints:
                if constraint in file_name:
                    flag += 1
            if flag == len(constraints):
                num += 1
    else:
        num += len(soup.find_all(href=re.compile("files.pythonhosted.org.*whl")))
    return num


# @pytest.fixture(scope="function")
# def monkeypatch_config_file(monkeypatch):
#     monkeypatch.setattr(settings, "SETTINGS_FILE", str(SRC_DIR / "settings.json"))
