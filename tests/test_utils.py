from pathlib import Path

from pipdownload.utils import PythonPackage, get_file_links


def test_get_file_links(shared_datadir: Path):
    print(shared_datadir)
    with (shared_datadir / "click.html").open() as f:
        html_doc = f.read()
    base_url = "https://mirrors.aliyun.com/pypi/simple/click/"
    python_package_local = PythonPackage("Click", "7.0")
    res = get_file_links(html_doc, base_url, python_package_local)
    assert len(res) == 2
    python_package_local = PythonPackage("click", "6.7")
    res = get_file_links(html_doc, base_url, python_package_local)
    assert len(res) == 2
