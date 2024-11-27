import json
from pathlib import Path

from click.testing import CliRunner
from pipdownload import settings
from pipdownload.cli import pipdownload
from pipdownload.utils import resolve_package_file

from tests.conftest import get_file_num_from_site_pypi_org


# TODO: How to avoid the situation where there has already been a config file.
def test_download_colorama_package(tmp_path: Path):
    runner = CliRunner()
    package_name = "colorama"
    result = runner.invoke(pipdownload, [package_name, "-d", str(tmp_path)])
    assert result.exit_code == 0
    files = list(tmp_path.iterdir())
    assert len(files) == get_file_num_from_site_pypi_org(package_name)


# Add-on for ignoring unused version - Conflict between platform and version check #13
# --python-version py3 --python-version cp37 --platform-tag manylinux1_x86_64 --dest . --no-source beautifulsoup4==4.8.2
# Should download beautifulsoup4-4.8.2-py3-none-any.whl, soupsieve-2.0.1-py3-none-any.whl
# NOT TO BE DOWNLOADED :  beautifulsoup4-4.8.2-py2-none-any.whl
def test_download_bs4_package(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(pipdownload, ["--python-version", "py3", "--python-version", "cp37",
                                         "--platform-tag", "manylinux1_x86_64", "-d", str(tmp_path), "--no-source",
                                         "beautifulsoup4==4.8.2"])
    assert result.exit_code == 0
    files = list(tmp_path.iterdir())
    assert len(files) == 2


# Add-on for ignoring unused version - Conflict between platform and version check #13
# --python-version py3 --python-version cp37 --platform-tag manylinux1_x86_64 --dest . --no-source beautifulsoup4==4.8.2
# Should download beautifulsoup4-4.8.2-py3-none-any.whl, soupsieve-2.0.1-py3-none-any.whl
# NOT TO BE DOWNLOADED :  beautifulsoup4-4.8.2-py2-none-any.whl
def test_download_bs4_package_noparam(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(pipdownload, ["beautifulsoup4==4.8.2", "-d", str(tmp_path)])
    assert result.exit_code == 0
    files = list(tmp_path.iterdir())
    assert len(files) == 5


# Add-on for ignoring unused version - Conflict between platform and version check #13
# --python-version py3 --python-version cp37 --platform-tag manylinux1_x86_64 --dest . --no-source beautifulsoup4==4.8.2
# Should download beautifulsoup4-4.8.2-py3-none-any.whl, soupsieve-2.0.1-py3-none-any.whl
# NOT TO BE DOWNLOADED :  beautifulsoup4-4.8.2-py2-none-any.whl
def test_download_bs4_package_veronly(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(pipdownload, ["--python-version", "cp37", "beautifulsoup4==4.8.2", "-d", str(tmp_path)])
    assert result.exit_code == 0
    files = list(tmp_path.iterdir())
    assert len(files) == 2


# Add-on for ignoring unused version - Conflict between platform and version check #13
# --python-version py3 --python-version cp37 --platform-tag manylinux1_x86_64 --dest . --no-source beautifulsoup4==4.8.2
# Should download beautifulsoup4-4.8.2-py3-none-any.whl, soupsieve-2.0.1-py3-none-any.whl
# NOT TO BE DOWNLOADED :  beautifulsoup4-4.8.2-py2-none-any.whl
def test_download_pip20_2_3_package(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(pipdownload, ["--python-version", "py3", "pip==20.2.3", "-d", str(tmp_path)])
    assert result.exit_code == 0
    files = list(tmp_path.iterdir())
    assert len(files) == 2


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


def test_download_with_option_whl_suffixes(tmp_path):
    runner = CliRunner()
    package_name = "MarkupSafe"
    result = runner.invoke(
        pipdownload, [package_name, "--suffix", "win_amd64", "-d", tmp_path]
    )
    assert result.exit_code == 0
    files = list(tmp_path.iterdir())
    # TODO: This should be consider again!
    python_package = resolve_package_file(files[0].name)

    assert len(files) == get_file_num_from_site_pypi_org(package_name, ["win_amd64"], package_version=python_package.version)


def test_download_with_option_python_versions(tmp_path):
    runner = CliRunner()
    package_name = "MarkupSafe"
    result = runner.invoke(pipdownload, [package_name, "-py", "cp27", "-d", tmp_path])
    assert result.exit_code == 0
    files = list(tmp_path.iterdir())
    assert len(files) == get_file_num_from_site_pypi_org(package_name, ["cp27"])


# Added -no-source because other way round 4 files were returned
def test_download_with_option_python_versions_and_platform_tags(tmp_path):
    runner = CliRunner()
    package_name = "ujson"
    result = runner.invoke(
        pipdownload, [package_name, "-py", "cp36", "-p", "manylinux", "-d", tmp_path]
    )
    assert result.exit_code == 0
    files = list(tmp_path.iterdir())
    python_package = resolve_package_file(files[0].name)
    assert len(files) == get_file_num_from_site_pypi_org(
        package_name, ["cp36", "manylinux"], package_version=python_package.version
    )


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
    python_package = resolve_package_file(files[0].name)
    assert len(files) == get_file_num_from_site_pypi_org(package_name, ["win_amd64"],
                                                         package_version=python_package.version)


def test_option_on_source(tmp_path: Path):
    runner = CliRunner()
    package_name = "colorama"
    result = runner.invoke(
        pipdownload, [package_name, "--no-source", "-d", str(tmp_path)]
    )
    assert result.exit_code == 0
    files = list(tmp_path.iterdir())
    assert len(files) == get_file_num_from_site_pypi_org(package_name, no_source=True)


def test_option_no_source_no_wheel(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(
        pipdownload, ["pyusb==1.0.2", "--no-source", "-d", str(tmp_path)]
    )
    assert result.exit_code == 0
    files = list(tmp_path.iterdir())
    assert len(files) == 0


def test_option_no_source_no_wheel_source_as_fallback(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(
        pipdownload, ["pyusb==1.0.2", "--no-source", "--source-as-fallback", "-d", str(tmp_path)]
    )
    assert result.exit_code == 0
    files = list(tmp_path.iterdir())
    assert len(files) == 1


def test_packege_with_egg_file(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(pipdownload, ["protobuf==3.9.2", "-d", str(tmp_path)])
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
    assert len(files) == get_file_num_from_site_pypi_org(
        package_name, ["cp37", "win_amd64"]
    )
    Path(settings.SETTINGS_FILE).unlink()


def test_download_package_can_not_install_on_windows(tmp_path: Path):
    runner = CliRunner()
    package_name = "gnureadline"
    result = runner.invoke(pipdownload, [package_name, "-d", str(tmp_path)])
    assert result.exit_code == 0
    files = list(tmp_path.iterdir())
    assert len(files) == get_file_num_from_site_pypi_org(package_name)
