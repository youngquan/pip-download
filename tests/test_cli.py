import json
import os.path
import subprocess
import sys
from pathlib import Path

from click.testing import CliRunner
from pipdownload import settings
from pipdownload.cli import pipdownload
from pipdownload.utils import (
    Hashes,
)

from tests.conftest import get_file_num_from_site_pypi_org


# TODO: How to avoid the situation where there has already been a config file.
def test_download_click_package(tmp_path: Path):
    runner = CliRunner()
    package_name = "colorama"
    result = runner.invoke(pipdownload, [package_name, "-d", str(tmp_path)])
    assert result.exit_code == 0
    files = list(tmp_path.iterdir())
    assert len(files) == get_file_num_from_site_pypi_org(package_name)


# "redundant" means there are redundant blank lines in requirement file.
def test_download_from_requirement_file_redundant(
    requirement_file_redundant, tmp_path: Path
):
    runner = CliRunner()
    result = runner.invoke(
        pipdownload, ["-r", requirement_file_redundant, "-d", tmp_path]
    )
    assert result.exit_code == 0
    files = list(tmp_path.iterdir())
    assert len(files) == 2


def test_download_from_requirement_file_normal(requirement_file_normal, tmp_path):
    runner = CliRunner()
    result = runner.invoke(pipdownload, ["-r", requirement_file_normal, "-d", tmp_path])
    assert result.exit_code == 0
    files = list(tmp_path.iterdir())
    assert len(files) == 2


def test_download_using_find_links(tmp_path):
    """
    Test using --find-links to ensure we use local files instead of index when needed (ie: for local builds).
    Uses aiohttp 3.7.4 package as it has numerous pre-compiled architecture-specific dependencies that we want to check.
    """
    runner = CliRunner()

    local_links = tmp_path / "local_links"
    dest_path = tmp_path / "dest"

    # Download base version into local links (simulate having local files)
    # Using `aiohttp` because it includes multiple sub-dependencies with platform specific builds
    command = [
        sys.executable,
        "-m",
        "pip",
        "download",
        "--dest",
        local_links,
        "aiohttp==3.7.4",
    ]
    subprocess.check_call(command)

    files = list(local_links.iterdir())
    assert len(files) > 1, [f.name for f in files]

    # Modify local packages (one primary and one dependency) with extraneous data (zip/whl/pip doesn't care)
    # so we can validate that pip_download uses it later.  This mimics as if we had a different/newer local build of
    # a package.
    local_main_pkg_file = next(Path(local_links).glob("aiohttp*.whl"))
    with open(local_main_pkg_file, "a+b") as f:
        f.write(b'RandomData')
    local_main_pkg_hash = Hashes.from_path(str(local_main_pkg_file)).sha256

    local_dep_pkg_file = next(Path(local_links).glob("attrs-*.whl"))
    with open(local_dep_pkg_file, "a+b") as f:
        f.write(b'RandomData')
    local_dep_pkg_hash = Hashes.from_path(str(local_dep_pkg_file)).sha256


    req_file = tmp_path / "requirements.txt"
    with open(req_file, "w") as f:
        f.write("aiohttp==3.7.4")

    # Download with main package requirement to include our "custom build"
    result = runner.invoke(pipdownload, ["-d", dest_path,
                                         "--find-links", local_links,
                                         "-p", "manylinux",
                                         "-r", str(req_file)])
    assert result.exit_code == 0, result.exception

    files = list(dest_path.iterdir())
    assert len(files) > 2, [f.name for f in files]

    # Validate dest path includes our modified local links (instead of downloading from index)
    for local_file, local_hash in [
        (local_main_pkg_file, local_main_pkg_hash),
        (local_dep_pkg_file, local_dep_pkg_hash),
    ]:
        dest_pkg_file = next(Path(dest_path).glob(os.path.basename(local_file)))
        dest_pkg_hash = Hashes.from_path(str(dest_pkg_file)).sha256
        assert local_hash == dest_pkg_hash, f"Destination {dest_pkg_file} did not match local link at {local_file}"




def test_download_with_option_whl_suffixes(tmp_path):
    runner = CliRunner()
    package_name = "MarkupSafe"
    result = runner.invoke(
        pipdownload, [package_name, "--suffix", "win_amd64", "-d", tmp_path]
    )
    assert result.exit_code == 0
    files = list(tmp_path.iterdir())
    # TODO: This should be consider again!
    assert len(files) == get_file_num_from_site_pypi_org(package_name, ["win_amd64"])


def test_download_with_option_python_versions(tmp_path):
    runner = CliRunner()
    package_name = "MarkupSafe"
    result = runner.invoke(
        pipdownload, [package_name, "-py", "cp27", "-d", tmp_path]
    )
    assert result.exit_code == 0
    files = list(tmp_path.iterdir())
    assert len(files) == get_file_num_from_site_pypi_org(package_name, ["cp27"])


def test_download_with_option_python_versions_and_platform_tags(tmp_path):
    runner = CliRunner()
    package_name = "ujson"
    result = runner.invoke(
        pipdownload, [package_name, "-py", "cp36", "-p", "manylinux", "-d", tmp_path]
    )
    assert result.exit_code == 0
    files = list(tmp_path.iterdir())
    assert len(files) == get_file_num_from_site_pypi_org(package_name, ["cp36", "manylinux"])


def test_download_when_dest_dir_does_not_exists(tmp_path: Path):
    runner = CliRunner()
    dir_name = "tmp"
    package_name = "colorama"
    result = runner.invoke(pipdownload, ["colorama", "-d", str(tmp_path / dir_name)])
    assert result.exit_code == 0
    dirs = list(tmp_path.iterdir())
    assert len(dirs) == 1
    files = list((tmp_path / dir_name).iterdir())
    assert len(files) == get_file_num_from_site_pypi_org(package_name)


def test_option_platform_tag(tmp_path):
    runner = CliRunner()
    package_name = "ujson"
    result = runner.invoke(
        pipdownload, [package_name, "-p", "win_amd64", "-d", tmp_path]
    )
    assert result.exit_code == 0
    files = list(tmp_path.iterdir())
    assert len(files) == get_file_num_from_site_pypi_org(package_name, ["win_amd64"])


def test_option_on_source(tmp_path: Path):
    runner = CliRunner()
    package_name = "colorama"
    result = runner.invoke(
        pipdownload, [package_name, "--no-source", "-d", str(tmp_path)]
    )
    assert result.exit_code == 0
    files = list(tmp_path.iterdir())
    assert len(files) == get_file_num_from_site_pypi_org(package_name, no_source=True)


def test_packege_with_egg_file(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(
        pipdownload, ["protobuf==3.9.2", "-d", str(tmp_path)]
    )
    assert result.exit_code == 0
    # files = list(tmp_path.iterdir())
    # assert len(files) == 1


def test_download_with_config_file(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(pipdownload, ["--show-config"])
    assert result.exit_code == 0

    runner = CliRunner()
    settings_dict = {"python-versions": ["cp37"], "platform-tags": ["win_amd64"]}
    with open(settings.SETTINGS_FILE, "w") as f:
        json.dump(settings_dict, f, indent=True)

    package_name = "MarkupSafe"
    result = runner.invoke(pipdownload, [package_name, "-d", str(tmp_path)])

    files = list(tmp_path.iterdir())
    assert len(files) == get_file_num_from_site_pypi_org(package_name, ["cp37", "win_amd64"])
    Path(settings.SETTINGS_FILE).unlink()
