import os

import pytest
from click.testing import CliRunner

from pipdownload.cli import pipdownload
from pipdownload.utils import TempDirectory


@pytest.fixture(scope="module")
def requirement_file_path():
    return os.path.abspath(os.path.join(os.getcwd(), 'tests/test_requirements.txt'))


def test_download_click_package():
    with TempDirectory(delete=True) as directory:
        runner = CliRunner()
        result = runner.invoke(pipdownload, ['click==7.0', '-d', directory.path])
        assert result.exit_code == 0
        files = os.listdir(directory.path)
        assert len(files) == 2


def test_download_from_requirement_file(requirement_file_path):
    with TempDirectory(delete=True) as directory:
        runner = CliRunner()
        result = runner.invoke(pipdownload, ['-r', requirement_file_path, '-d', directory.path])
        print(requirement_file_path)
        print(result.output)
        print(result)
        assert result.exit_code == 0
        files = os.listdir(directory.path)
        assert len(files) == 2

