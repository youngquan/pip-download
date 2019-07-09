import os

import pytest
from click.testing import CliRunner

from pipdownload.cli import pipdownload
from pipdownload.utils import TempDirectory


@pytest.fixture(scope="module")
def requirement_file_redundant():
    return os.path.abspath(os.path.join(os.getcwd(), 'tests/test_requirements_redundant.txt'))


@pytest.fixture(scope="module")
def requirement_file_normal():
    return os.path.abspath(os.path.join(os.getcwd(), 'tests/test_requirements_normal.txt'))


def test_download_click_package():
    with TempDirectory(delete=True) as directory:
        runner = CliRunner()
        result = runner.invoke(pipdownload, ['click==7.0', '-d', directory.path])
        assert result.exit_code == 0
        files = os.listdir(directory.path)
        assert len(files) == 2


def test_download_from_requirement_file_redundant(requirement_file_redundant):
    with TempDirectory(delete=True) as directory:
        runner = CliRunner()
        result = runner.invoke(pipdownload, ['-r', requirement_file_redundant, '-d', directory.path])
        assert result.exit_code == 0
        files = os.listdir(directory.path)
        assert len(files) == 2


def test_download_from_requirement_file_normal(requirement_file_normal):
    with TempDirectory(delete=True) as directory:
        runner = CliRunner()
        result = runner.invoke(pipdownload, ['-r', requirement_file_normal, '-d', directory.path])
        assert result.exit_code == 0
        files = os.listdir(directory.path)
        assert len(files) == 2


def test_download_with_option_whl_suffixes():
    with TempDirectory(delete=True) as directory:
        runner = CliRunner()
        result = runner.invoke(pipdownload, ['grpcio==1.21.1', '-d', directory.path])
        assert result.exit_code == 0
        files = os.listdir(directory.path)
        assert len(files) == 14


def test_download_with_option_python_versions():
    with TempDirectory(delete=True) as directory:
        runner = CliRunner()
        result = runner.invoke(pipdownload, [
            ' MarkupSafe==1.1.1', '-py', 'cp37', '-d', directory.path
        ])
        assert result.exit_code == 0
        files = os.listdir(directory.path)
        assert len(files) == 3
